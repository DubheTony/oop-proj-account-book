# main_cli — 个人财务管理系统命令行入口
from datetime import date
from models.transaction import Transaction, AccountType
from models.budget import Budget
from services import FinanceController


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
    print("5. 生成诊断报告")
    print("6. 生成储蓄计划（需E的SavingGoalCalculator）")
    print("7. 导入CSV")
    print("8. 查看预警消息")
    print("0. 退出")
    print()


def print_transactions(ctrl: FinanceController):
    months = ctrl.get_months()
    if not months:
        print("  (暂无交易)")
        return

    txns = ctrl.get_transactions()
    print(f"  共 {len(txns)} 条交易，覆盖 {len(months)} 个月 ({months[0]} ~ {months[-1]}):")
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
    alerts = ctrl.get_alert_messages()
    if not alerts:
        print("  (暂无预警)")
        return
    for a in alerts:
        print(f"  {a}")


def run_diagnosis(ctrl: FinanceController):
    """运行综合诊断并打印报告"""
    from models.diagnosis_report import HealthLevel

    months = ctrl.get_months()
    if not months:
        print("  (暂无交易数据，无法生成诊断报告。请先导入CSV或录入交易。)")
        return

    # 默认诊断最新月份
    month = months[-1]
    print(f"  诊断月份: {month}（共 {len(months)} 个月可选: {', '.join(months)}）")

    try:
        report = ctrl.generate_diagnosis(month)
    except RuntimeError as e:
        print(f"  诊断失败: {e}")
        return

    # 打印报告
    emoji = {HealthLevel.HEALTHY: "[健康]", HealthLevel.WARNING: "[预警]", HealthLevel.CRITICAL: "[严重]"}
    print()
    print("=" * 60)
    print(f"  诊断报告 — {month}")
    print("=" * 60)
    print(f"  综合评分: {report.overall_score:.0f}/100  {emoji.get(report.overall_level, '')}")
    print()

    # 各维度明细
    print(f"  各维度明细 ({len(report.dimensions)}项):")
    print("  " + "-" * 50)
    for dim in report.dimensions:
        mark = emoji.get(dim.level, "")
        print(f"  {dim.strategy_name}: {dim.score:.0f}分  {mark}")
        if dim.suggestion:
            desc = dim.suggestion.description
            if len(desc) > 80:
                desc = desc[:80] + "..."
            print(f"    -> {desc}")
    print()

    # 改进建议
    if report.suggestions:
        print(f"  改进建议 ({len(report.suggestions)}条，按影响金额降序):")
        print("  " + "-" * 50)
        priority_map = {1: "高优先级", 2: "中优先级", 3: "低优先级"}
        for i, s in enumerate(report.suggestions, 1):
            label = priority_map.get(s.priority, "")
            print(f"  {i}. [{label}] {s.category}")
            print(f"     {s.description}")
            print(f"     预计月改善: ¥{s.impact_amount:.0f}")
    else:
        print("  无改进建议，财务状况健康！")

    print("=" * 60)


# ============================================================
# 主循环
# ============================================================

def main():
    ctrl = FinanceController()

    # 设置诊断策略（D提供的CompositeDiagnosis）
    from strategies import (
        SavingRateStrategy,
        CategoryOverrunStrategy,
        ConsumptionStructureStrategy,
        CompositeDiagnosis,
    )
    ctrl.set_diagnosis_strategy(CompositeDiagnosis([
        (SavingRateStrategy(), 0.4),
        (CategoryOverrunStrategy(), 0.3),
        (ConsumptionStructureStrategy(), 0.3),
    ]))

    # 菜单路由表
    handlers = {
        "1": lambda: print_transactions(ctrl),
        "2": lambda: add_transaction_interactive(ctrl),
        "3": lambda: print_budgets(ctrl),
        "4": lambda: set_budget_interactive(ctrl),
        "5": lambda: run_diagnosis(ctrl),
        "6": lambda: print("  (待E的储蓄计算模块完成后对接)"),
        "7": lambda: import_csv_interactive(ctrl),
        "8": lambda: print_alerts(ctrl),
    }

    while True:
        print_menu()
        choice = input("请选择: ").strip()

        if choice == "0":
            print("再见！")
            break
        elif choice in handlers:
            handlers[choice]()
        else:
            print("  无效选项，请重新选择")


if __name__ == "__main__":
    main()
