# main_cli — 最小CLI原型（第1周）
# 目的：用假数据验证Controller API，提前发现设计问题
from datetime import date
from models.transaction import Transaction, AccountType
from models.budget import Budget


# ============================================================
# 简易 Controller（C 交付正式版后替换）
# ============================================================

class FinanceController:
    """临时Controller骨架，C交付后替换"""

    def __init__(self):
        self._transactions = []
        self._budgets = []
        self._alert_messages = []

    def add_transaction(self, t: Transaction):
        self._transactions.append(t)
        if t.is_expense():
            b = self._find_budget(t.category)
            if b:
                was_exceeded = b.is_exceeded()
                b.add_expense(t.amount)
                if not was_exceeded and b.is_exceeded():
                    over = b.current_spent - b.monthly_limit
                    self._alert_messages.append(
                        f"[预警] {t.date} | {t.category}预算超支！"
                        f"限额¥{b.monthly_limit:.0f}，已支出¥{b.current_spent:.0f}，超出¥{over:.0f}"
                    )

    def get_transactions(self):
        return self._transactions.copy()

    def set_budget(self, b: Budget):
        for i, old in enumerate(self._budgets):
            if old.category == b.category:
                self._budgets[i] = b
                return
        self._budgets.append(b)

    def get_budgets(self):
        return self._budgets.copy()

    def import_csv(self, path: str) -> int:
        from services.csv_importer import import_csv
        transactions, skipped = import_csv(path)
        for t in transactions:
            self.add_transaction(t)
        return len(transactions)

    def get_alerts(self):
        msgs = self._alert_messages.copy()
        self._alert_messages.clear()
        return msgs

    def _find_budget(self, category: str):
        for b in self._budgets:
            if b.category == category:
                return b
        return None


# ============================================================
# 预设假数据
# ============================================================

def load_demo_data(ctrl: FinanceController):
    """加载演示用假数据"""
    ctrl.add_transaction(Transaction(
        35.5, "支出", "餐饮", AccountType.WECHAT,
        date(2025, 3, 15), "食堂午饭"))
    ctrl.add_transaction(Transaction(
        2000, "收入", "其他", AccountType.BANK_CARD,
        date(2025, 3, 15), "三月生活费"))
    ctrl.add_transaction(Transaction(
        89, "支出", "娱乐", AccountType.ALIPAY,
        date(2025, 3, 16), "电影票"))
    ctrl.add_transaction(Transaction(
        12, "支出", "交通", AccountType.CASH,
        date(2025, 3, 17), "地铁通勤"))
    ctrl.add_transaction(Transaction(
        150, "支出", "餐饮", AccountType.WECHAT,
        date(2025, 3, 18), "周末聚餐"))
    ctrl.add_transaction(Transaction(
        200, "支出", "学习", AccountType.ALIPAY,
        date(2025, 3, 19), "买教材"))
    ctrl.add_transaction(Transaction(
        66, "支出", "日用", AccountType.WECHAT,
        date(2025, 3, 20), "超市采购"))
    # 设置预算
    ctrl.set_budget(Budget("餐饮", 1500))
    ctrl.set_budget(Budget("娱乐", 300))
    ctrl.set_budget(Budget("交通", 200))
    ctrl.set_budget(Budget("学习", 500))
    ctrl.set_budget(Budget("日用", 400))


# ============================================================
# 菜单界面
# ============================================================

def print_menu():
    print()
    print("=== 个人财务管理系统（CLI原型） ===")
    print("1. 查看交易列表")
    print("2. 添加交易")
    print("3. 查看预算")
    print("4. 设置预算")
    print("5. 生成诊断报告（需D的Strategy）")
    print("6. 生成储蓄计划（需E的SavingGoalCalculator）")
    print("7. 导入CSV")
    print("8. 查看预警消息")
    print("0. 退出")
    print()


def print_transactions(ctrl: FinanceController):
    txns = ctrl.get_transactions()
    if not txns:
        print("  (暂无交易)")
        return
    print(f"  共 {len(txns)} 条交易:")
    for t in txns:
        print(f"  {t.date} | {t.type} | {t.category} | "
              f"{t.amount:>8.2f} | {t.account.value} | {t.note}")


def add_transaction_interactive(ctrl: FinanceController):
    print("  请输入交易信息:")
    try:
        raw_date = input("  日期(YYYY-MM-DD): ").strip()
        d = date.fromisoformat(raw_date)

        raw_amount = input("  金额: ").strip()
        amount = float(raw_amount)

        t_type = input("  类型(收入/支出): ").strip()
        if t_type not in ("收入", "支出"):
            print("  类型必须为'收入'或'支出'")
            return

        category = input("  类别(餐饮/交通/娱乐/学习/日用/其他): ").strip()

        print("  账户: 1.微信 2.支付宝 3.现金 4.银行卡")
        acc_choice = input("  选择(1-4): ").strip()
        acc_map = {"1": AccountType.WECHAT, "2": AccountType.ALIPAY,
                    "3": AccountType.CASH, "4": AccountType.BANK_CARD}
        account = acc_map.get(acc_choice, AccountType.WECHAT)

        note = input("  备注(可选): ").strip()

        ctrl.add_transaction(Transaction(amount, t_type, category, account, d, note))
        print("  已添加！")
    except ValueError as e:
        print(f"  输入格式错误: {e}")


def print_budgets(ctrl: FinanceController):
    budgets = ctrl.get_budgets()
    if not budgets:
        print("  (暂无预算)")
        return
    for b in budgets:
        remaining = b.get_remaining()
        status = "!!超支!!" if b.is_exceeded() else "正常"
        print(f"  {b.category}: 限额{b.monthly_limit:>8.0f} | "
              f"已支出{b.current_spent:>8.0f} | 剩余{remaining:>8.0f} | {status}")


def set_budget_interactive(ctrl: FinanceController):
    category = input("  类别: ").strip()
    try:
        limit = float(input("  月度限额: ").strip())
    except ValueError:
        print("  金额格式错误")
        return
    ctrl.set_budget(Budget(category, limit))
    print(f"  已设置 {category} 预算 ¥{limit:.0f}")


def import_csv_interactive(ctrl: FinanceController):
    path = input("  CSV文件路径: ").strip()
    try:
        count = ctrl.import_csv(path)
        print(f"  导入成功，共 {count} 条交易")
    except (FileNotFoundError, ValueError) as e:
        print(f"  导入失败: {e}")


def print_alerts(ctrl: FinanceController):
    alerts = ctrl.get_alerts()
    if not alerts:
        print("  (暂无预警)")
        return
    for a in alerts:
        print(f"  {a}")


# ============================================================
# 主循环
# ============================================================

def main():
    ctrl = FinanceController()
    load_demo_data(ctrl)

    # 菜单路由表
    handlers = {
        "1": lambda: print_transactions(ctrl),
        "2": lambda: add_transaction_interactive(ctrl),
        "3": lambda: print_budgets(ctrl),
        "4": lambda: set_budget_interactive(ctrl),
        "7": lambda: import_csv_interactive(ctrl),
        "8": lambda: print_alerts(ctrl),
    }

    while True:
        print_menu()
        choice = input("请选择: ").strip()

        if choice == "0":
            print("再见！")
            break
        elif choice == "5":
            print("  (待D的诊断策略模块完成后对接)")
        elif choice == "6":
            print("  (待E的储蓄计算模块完成后对接)")
        elif choice in handlers:
            handlers[choice]()
        else:
            print("  无效选项，请重新选择")


if __name__ == "__main__":
    main()
