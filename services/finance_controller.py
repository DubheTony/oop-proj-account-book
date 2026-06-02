# FinanceController — 个人财务管理系统的总协调器
#
# 交易按月份分组存储，数据跨越多个月时：
#   - get_transactions() 返回全部交易（扁平化）
#   - get_transactions("2025-09") 只返回指定月份
#   - generate_diagnosis() 默认使用最新月份的数据
from models.transaction import Transaction
from models.budget import Budget


class FinanceController:
    """总协调器。持有所有数据，对CLI/GUI提供统一API。"""

    def __init__(self):
        # 交易按月分组: {"2025-03": [t1, t2, ...], "2025-04": [...]}
        self._transactions: dict[str, list[Transaction]] = {}
        self._budgets: list[Budget] = []
        self._alert_messages: list[str] = []

        # 策略引用 —— 调用方通过 set_* 方法设置
        self.diagnosis_strategy = None    # DiagnosticStrategy | None
        self.budget_rule = None           # BudgetRule | None (P1)
        self.savings_method = None        # SavingsMethod | None (P1)

        # 领域服务 —— E 交付后改为顶部 import
        self._saving_calculator = None    # 懒加载

    # ================================================================
    # 交易管理
    # ================================================================

    def add_transaction(self, t: Transaction) -> None:
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
        """解析CSV文件，返回成功导入的条数。委托给B的csv_importer模块。"""
        from services.csv_importer import import_csv
        transactions, skipped = import_csv(path)
        for t in transactions:
            self.add_transaction(t)
        return len(transactions)

    def get_transactions(self, month: str | None = None) -> list[Transaction]:
        """返回交易列表。指定month（"YYYY-MM"）则只返回该月；不指定则返回全部。"""
        if month is not None:
            return self._transactions.get(month, []).copy()
        # 返回全部（按月排序拼接）
        result = []
        for m in sorted(self._transactions.keys()):
            result.extend(self._transactions[m])
        return result

    def delete_transaction(self, t: Transaction) -> bool:
        """删除一笔交易。匹配全部字段。返回True表示成功删除。"""
        month_key = t.date.strftime("%Y-%m")
        if month_key not in self._transactions:
            return False
        txns = self._transactions[month_key]
        for i, existing in enumerate(txns):
            if (existing.date == t.date and existing.amount == t.amount
                    and existing.type == t.type and existing.category == t.category
                    and existing.account == t.account and existing.note == t.note):
                txns.pop(i)
                if not txns:  # 该月空了就删key
                    del self._transactions[month_key]
                return True
        return False

    def recalculate_budget_spent(self, month: str | None = None) -> None:
        """根据当前交易重新计算每个预算的已支出金额。
        month为None时使用全部交易，否则仅用指定月份。
        """
        txns = self.get_transactions(month)
        for b in self._budgets:
            b.current_spent = sum(
                t.amount for t in txns
                if t.is_expense() and t.category == b.category
            )

    def check_budget_alerts(self) -> None:
        """扫描所有预算，对已超支的类别生成预警（去重）。"""
        existing_msgs = set(self._alert_messages)
        for b in self._budgets:
            if b.is_exceeded():
                over = b.current_spent - b.monthly_limit
                msg = (
                    f"[预警] {b.category} 预算超支！"
                    f"限额 ¥{b.monthly_limit:.0f}，已支出 ¥{b.current_spent:.0f}，超出 ¥{over:.0f}"
                )
                if msg not in existing_msgs:
                    self._alert_messages.append(msg)
                    existing_msgs.add(msg)

    def get_months(self) -> list[str]:
        """返回所有有数据的月份列表（按时间排序）"""
        return sorted(self._transactions.keys())

    # ================================================================
    # 预算管理
    # ================================================================

    def set_budget(self, b: Budget) -> None:
        """添加或更新一个类别的预算（按 category 去重）"""
        for i, existing in enumerate(self._budgets):
            if existing.category == b.category:
                self._budgets[i] = b
                return
        self._budgets.append(b)

    def get_budgets(self) -> list[Budget]:
        return self._budgets.copy()

    # ================================================================
    # 诊断
    # ================================================================

    def set_diagnosis_strategy(self, s) -> None:
        """设置诊断策略（D提供）"""
        self.diagnosis_strategy = s

    def generate_diagnosis(self, month: str | None = None):
        """生成诊断报告。month为None时使用最新月份。

        先用指定月份的交易重算每个Budget的current_spent，
        再委托给diagnosis_strategy。
        """
        if self.diagnosis_strategy is None:
            raise RuntimeError("DiagnosticStrategy 未设置。请先调用 set_diagnosis_strategy()")

        # 确定要诊断的月份
        if month is None:
            months = self.get_months()
            if not months:
                raise RuntimeError("无交易数据，无法生成诊断")
            month = months[-1]  # 默认最新月份

        txns = self.get_transactions(month)

        # 根据该月交易重算每个预算的 current_spent
        for b in self._budgets:
            b.current_spent = sum(
                t.amount for t in txns
                if t.is_expense() and t.category == b.category
            )

        report = self.diagnosis_strategy.diagnose(txns, self._budgets)
        self.check_budget_alerts()
        return report

    # ================================================================
    # 预算规则（P1）
    # ================================================================

    def set_budget_rule(self, r) -> None:
        self.budget_rule = r

    def apply_budget_rule(self, income: float) -> dict[str, float]:
        """使用当前 BudgetRule 计算各类别建议预算（P1）"""
        if self.budget_rule is None:
            raise RuntimeError("BudgetRule 未设置。请先调用 set_budget_rule()")
        return self.budget_rule.allocate(income, self.get_transactions())

    # ================================================================
    # 储蓄（P1）
    # ================================================================

    def set_savings_method(self, m) -> None:
        self.savings_method = m

    def get_savings_plan(self, income: float):
        """使用当前 SavingsMethod 生成储蓄方法建议（P1）"""
        if self.savings_method is None:
            raise RuntimeError("SavingsMethod 未设置。请先调用 set_savings_method()")
        return self.savings_method.calculate(income, self.get_transactions())

    def generate_saving_plan(self, target: float, months: int):
        """储蓄倒推计划。委托给 SavingGoalCalculator（E提供）。"""
        calc = self._get_saving_calculator()
        return calc.calculate_plan(target, months, self.get_transactions())

    def _get_saving_calculator(self):
        """懒加载 SavingGoalCalculator（E可能尚未交付）"""
        if self._saving_calculator is None:
            try:
                from services.saving_calculator import SavingGoalCalculator
                self._saving_calculator = SavingGoalCalculator()
            except ImportError:
                raise RuntimeError(
                    "SavingGoalCalculator 尚未实现（E未交付）。"
                    "请等待储蓄计算模块完成后重试。"
                )
        return self._saving_calculator

    # ================================================================
    # 告警
    # ================================================================

    def get_alert_messages(self) -> list[str]:
        return self._alert_messages.copy()

    def clear_alerts(self) -> None:
        self._alert_messages.clear()

    # ================================================================
    # 内部
    # ================================================================

    def _find_budget(self, category: str) -> Budget | None:
        for b in self._budgets:
            if b.category == category:
                return b
        return None
