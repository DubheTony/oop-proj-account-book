# FinanceController — 个人财务管理系统的总协调器
# 持有所有数据（交易、预算、预警），对 GUI 提供统一 API
import json
from pathlib import Path
from datetime import date as date_type

from models.transaction import Transaction, AccountType
from models.budget import Budget
from services.category_normalizer import LEGACY_CATEGORY_MAP, CATEGORY_PARENTS


class FinanceController:
    """总协调器。持有所有数据，对 GUI 提供统一操作接口。"""

    def __init__(self):
        # 交易按月分组: {"2025-03": [t1, t2, ...], "2025-04": [...]}
        self._transactions = {}
        self._budgets = []
        self._alert_messages = []

        # 策略引用 —— GUI 通过 set_* 方法注入
        self.diagnosis_strategy = None    # DiagnosticStrategy
        self.budget_rule = None           # BudgetRule (P1)
        self.savings_method = None        # SavingsMethod (P1)

        # 领域服务 —— 懒加载
        self._saving_calculator = None
        self._savings_target = None

    # ================================================================
    # 交易管理
    # ================================================================

    def add_transaction(self, t: Transaction):
        """保存交易，按日期自动归入对应月份。若为支出则更新预算并检查预警。"""
        month_key = t.date.strftime("%Y-%m")
        if month_key not in self._transactions:
            self._transactions[month_key] = []
        self._transactions[month_key].append(t)

        # 如果是支出，更新对应类别预算并检查预警
        if t.is_expense():
            b = self._find_budget(t.category)
            if b is not None:
                was_exceeded = b.is_exceeded()
                b.add_expense(t.amount)
                # 只在首次超支时告警（避免重复刷屏）
                if not was_exceeded and b.is_exceeded():
                    over = b.current_spent - b.monthly_limit
                    self._alert_messages.append(
                        f"[预警] {t.date} | {t.category} 预算超支！"
                        f"限额 ¥{b.monthly_limit:.0f}，已支出 ¥{b.current_spent:.0f}，超出 ¥{over:.0f}"
                    )

    def import_csv(self, path: str) -> int:
        """解析CSV文件，返回成功导入的条数。委托给 csv_importer 模块。"""
        from services.csv_importer import import_csv
        transactions, skipped = import_csv(path)
        for t in transactions:
            self.add_transaction(t)
        return len(transactions)

    def get_transactions(self, month: str | None = None) -> list[Transaction]:
        """返回交易列表。指定 month（"YYYY-MM"）则只返回该月；不指定则返回全部。"""
        if month is not None:
            return self._transactions.get(month, []).copy()
        # 返回全部（按月排序拼接）
        result = []
        for m in sorted(self._transactions.keys()):
            result.extend(self._transactions[m])
        return result

    def delete_transaction(self, t: Transaction) -> bool:
        """删除一笔交易。匹配全部字段。返回 True 表示成功删除。"""
        month_key = t.date.strftime("%Y-%m")
        if month_key not in self._transactions:
            return False
        txns = self._transactions[month_key]
        for i, existing in enumerate(txns):
            if (existing.date == t.date and existing.amount == t.amount
                    and existing.type == t.type and existing.category == t.category
                    and existing.account == t.account and existing.note == t.note):
                txns.pop(i)
                if not txns:
                    del self._transactions[month_key]
                return True
        return False

    def recalculate_budget_spent(self, month: str | None = None):
        """根据交易重新计算每个预算的已支出金额。
        支持旧类别名自动匹配（如"日用"→"家居日用"）。
        """
        txns = self.get_transactions(month)
        for b in self._budgets:
            b.current_spent = sum(
                t.amount for t in txns
                if t.is_expense() and self._category_matches(t.category, b.category)
            )

    def check_budget_alerts(self):
        """扫描所有预算，对已超支的类别生成预警（去重）。"""
        existing_msgs = set(self._alert_messages)
        for b in self._budgets:
            if b.is_exceeded():
                over = b.current_spent - b.monthly_limit
                msg = (f"[预警] {b.category} 预算超支！"
                       f"限额 ¥{b.monthly_limit:.0f}，已支出 ¥{b.current_spent:.0f}，超出 ¥{over:.0f}")
                if msg not in existing_msgs:
                    self._alert_messages.append(msg)
                    existing_msgs.add(msg)

    def get_months(self) -> list[str]:
        """返回所有有数据的月份列表（按时间排序）"""
        return sorted(self._transactions.keys())

    # ================================================================
    # 预算管理
    # ================================================================

    def set_budget(self, b: Budget):
        """添加或更新一个类别的预算（按 category 去重）"""
        for i, existing in enumerate(self._budgets):
            if existing.category == b.category:
                self._budgets[i] = b
                return
        self._budgets.append(b)

    def get_budgets(self) -> list[Budget]:
        return self._budgets.copy()

    def remove_budget(self, category: str) -> bool:
        """删除指定类别的预算。返回 True 表示成功删除。"""
        for i, b in enumerate(self._budgets):
            if b.category == category:
                self._budgets.pop(i)
                return True
        return False

    # ================================================================
    # 持久化：设置（app_settings.json）—— 预算 + 储蓄目标
    # ================================================================

    def save_settings(self, path: str):
        """将所有设置持久化到单个 JSON 文件"""
        data = {
            "budgets": [{"category": b.category, "monthly_limit": b.monthly_limit}
                        for b in self._budgets],
            "savings_target": self.get_savings_target(),
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_settings(self, path: str):
        """从 JSON 文件加载所有设置。文件不存在则跳过。
        兼容旧 budgets.json 自动迁移。
        """
        if not Path(path).exists():
            # 尝试从旧 budgets.json 迁移
            old_path = Path(path).parent / "budgets.json"
            if old_path.exists():
                self._migrate_old_settings(str(old_path), path)
            return
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for item in data.get("budgets", []):
            self.set_budget(Budget(item["category"], item["monthly_limit"]))
        if data.get("savings_target") is not None:
            self._savings_target = data["savings_target"]

    def _migrate_old_settings(self, old_path: str, new_path: str):
        """从旧 budgets.json 迁移到 app_settings.json"""
        with open(old_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            for item in data:
                self.set_budget(Budget(item["category"], item["monthly_limit"]))
        self.save_settings(new_path)
        try:
            Path(old_path).unlink()
        except Exception:
            pass

    # ================================================================
    # 持久化：交易记录（transactions.json）—— 按月分组
    # ================================================================

    def save_transactions(self, path: str):
        """将所有交易持久化到 JSON 文件（按月分组）"""
        data = {}
        for month, txns in self._transactions.items():
            data[month] = [{
                "amount": t.amount, "type": t.type, "category": t.category,
                "account": t.account.value, "date": t.date.isoformat(),
                "note": t.note,
            } for t in txns]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_transactions(self, path: str) -> int:
        """从 JSON 文件加载交易记录。返回加载条数。文件不存在返回 0。"""
        if not Path(path).exists():
            return 0
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        count = 0
        for month, txns in data.items():
            for item in txns:
                t = Transaction(
                    amount=item["amount"], type=item["type"],
                    category=item["category"],
                    account=AccountType(item["account"]),
                    date=date_type.fromisoformat(item["date"]),
                    note=item.get("note", ""),
                )
                # 直接插入内部字典，跳过 add_transaction 的预算预警逻辑
                #（加载历史数据不应触发实时预警）
                if month not in self._transactions:
                    self._transactions[month] = []
                self._transactions[month].append(t)
                count += 1
        return count

    # ================================================================
    # 诊断
    # ================================================================

    def set_diagnosis_strategy(self, s):
        """设置诊断策略"""
        self.diagnosis_strategy = s

    def generate_diagnosis(self, month: str | None = None):
        """生成诊断报告。month为None时使用最新月份。
        先用指定月份的交易重算每个Budget的current_spent，再委托给诊断策略。
        """
        if self.diagnosis_strategy is None:
            raise RuntimeError("诊断策略未设置。请先调用 set_diagnosis_strategy()")

        # 确定要诊断的月份
        if month is None:
            months = self.get_months()
            if not months:
                raise RuntimeError("无交易数据，无法生成诊断")
            month = months[-1]

        txns = self.get_transactions(month)

        # 根据该月交易重算每个预算的已支出（支持旧类别名）
        for b in self._budgets:
            b.current_spent = sum(
                t.amount for t in txns
                if t.is_expense() and self._category_matches(t.category, b.category)
            )

        report = self.diagnosis_strategy.diagnose(txns, self._budgets)
        self.check_budget_alerts()
        return report

    # ================================================================
    # 预算规则（P1）—— BudgetRule 策略族
    # ================================================================

    def set_budget_rule(self, r):
        self.budget_rule = r

    def apply_budget_rule(self, income: float) -> dict[str, float]:
        """使用当前 BudgetRule 计算各类别建议预算"""
        if self.budget_rule is None:
            raise RuntimeError("预算规则未设置。请先调用 set_budget_rule()")
        return self.budget_rule.allocate(income, self.get_transactions())

    # ================================================================
    # 储蓄方法（P1）—— SavingsMethod 策略族
    # ================================================================

    def set_savings_method(self, m):
        self.savings_method = m

    def get_savings_plan(self, income: float):
        """使用当前 SavingsMethod 生成储蓄方法建议"""
        if self.savings_method is None:
            raise RuntimeError("储蓄方法未设置。请先调用 set_savings_method()")
        return self.savings_method.calculate(income, self.get_transactions())

    # ================================================================
    # 储蓄目标（供诊断策略使用）
    # ================================================================

    def set_savings_target(self, monthly_target: float):
        """设置月度储蓄目标（由 SavingsTab 在计算后调用）"""
        self._savings_target = monthly_target

    def get_savings_target(self):
        """获取月度储蓄目标，未设置返回 None"""
        return getattr(self, '_savings_target', None)

    def generate_saving_plan(self, target: float, months: int):
        """储蓄倒推计划。委托给 SavingGoalCalculator。"""
        calc = self._get_saving_calculator()
        return calc.calculate_plan(target, months, self.get_transactions())

    def _get_saving_calculator(self):
        """懒加载 SavingGoalCalculator"""
        if self._saving_calculator is None:
            try:
                from services.saving_calculator import SavingGoalCalculator
                self._saving_calculator = SavingGoalCalculator()
            except ImportError:
                raise RuntimeError("储蓄计算模块尚未实现，请等待 E 组交付。")
        return self._saving_calculator

    # ================================================================
    # 告警
    # ================================================================

    def get_alert_messages(self) -> list[str]:
        return self._alert_messages.copy()

    def clear_alerts(self):
        self._alert_messages.clear()

    # ================================================================
    # 内部方法
    # ================================================================

    def _find_budget(self, category: str):
        """查找类别对应的预算。支持旧类别名自动映射。"""
        for b in self._budgets:
            if self._category_matches(category, b.category):
                return b
        return None

    @staticmethod
    def _category_matches(txn_category: str, budget_category: str) -> bool:
        """判断交易类别是否匹配预算类别。
        支持三种匹配：
          1. 直接相等
          2. 旧类别名映射（如"日用"→"家居日用"）
          3. 父子类别匹配（如"餐饮食品"的支出计入"餐饮"预算）
        """
        if txn_category == budget_category:
            return True
        # 旧类别名 → 新类别名
        mapped = LEGACY_CATEGORY_MAP.get(txn_category, txn_category)
        if mapped == budget_category:
            return True
        # 父子类别：交易是子类别，预算属于父类别
        parent = CATEGORY_PARENTS.get(mapped)
        if parent is not None and parent == budget_category:
            return True
        return False
