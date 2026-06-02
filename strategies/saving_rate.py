# 储蓄率诊断策略
# 算法：储蓄率 = (总收入 - 总支出) / 总收入
# score = min(saving_rate / 0.3 * 100, 100)
from models.transaction import Transaction
from models.budget import Budget
from models.diagnosis_report import DiagnosisReport, DimensionDetail, HealthLevel
from models.suggestion import Suggestion
from .diagnostic_strategy import DiagnosticStrategy


class SavingRateStrategy(DiagnosticStrategy):
    """储蓄率诊断：判断月结余是否达到健康水平（储蓄率≥20%）。"""

    # 可配置阈值（方便答辩调参）
    HEALTHY_THRESHOLD = 0.20   # 储蓄率 ≥20% 视为健康
    WARNING_THRESHOLD = 0.10   # 储蓄率 ≥10% 但 <20% 为预警（注释掉未使用，保留供答辩演示）
    TARGET_RATE = 0.30         # 满分线：储蓄率达到 30% 即满分

    def diagnose(
        self,
        transactions: list[Transaction],
        budgets: list[Budget]
    ) -> DiagnosisReport:
        # 计算总收入和总支出
        total_income = sum(t.amount for t in transactions if t.is_income())
        total_expense = sum(t.amount for t in transactions if t.is_expense())

        # ----- 边界：空数据 -----
        if total_income == 0 and total_expense == 0:
            dim = DimensionDetail(
                "储蓄率诊断", 0, HealthLevel.WARNING,
                Suggestion(2, 0, "全部",
                           "暂无交易数据，无法计算储蓄率。请先导入账单或录入交易。")
            )
            return DiagnosisReport(HealthLevel.WARNING, 0, [dim], [])

        # ----- 边界：全支出无收入（极端入不敷出）-----
        if total_income == 0:
            dim = DimensionDetail(
                "储蓄率诊断", 0, HealthLevel.CRITICAL,
                Suggestion(1, total_expense, "全部",
                           f"无收入记录但支出了 ¥{total_expense:.0f}，"
                           f"正在消耗储蓄或负债。请检查是否有未录入的收入。")
            )
            return DiagnosisReport(HealthLevel.CRITICAL, 0, [dim], [])

        # ----- 正常计算 -----
        monthly_saving = total_income - total_expense
        saving_rate = monthly_saving / total_income
        score = max(0, min(saving_rate / self.TARGET_RATE * 100, 100))

        # 等级判定
        if saving_rate < 0:
            level = HealthLevel.CRITICAL
            desc = (
                f"入不敷出！本月支出 ¥{total_expense:.0f} 超过收入 ¥{total_income:.0f}，"
                f"正在消耗储蓄或负债。"
            )
        elif saving_rate < self.WARNING_THRESHOLD:
            level = HealthLevel.WARNING
            desc = (
                f"储蓄率仅 {saving_rate:.0%}，远低于建议下限 {self.WARNING_THRESHOLD:.0%}。"
                f"建议大幅控制弹性支出。"
            )
        elif saving_rate < self.HEALTHY_THRESHOLD:
            level = HealthLevel.WARNING
            desc = (
                f"储蓄率 {saving_rate:.0%}，接近健康线。"
                f"建议提升至 {self.HEALTHY_THRESHOLD:.0%} 以上。"
            )
        else:
            level = HealthLevel.HEALTHY
            desc = f"储蓄率 {saving_rate:.0%}，财务状态健康。继续保持。"

        # impact_amount = 要达到 20% 储蓄率还需多存多少
        target_saving = total_income * self.HEALTHY_THRESHOLD
        suggestion = Suggestion(
            priority=2 if level != HealthLevel.HEALTHY else 3,
            impact_amount=max(0, target_saving - monthly_saving),
            category="全部",
            description=desc + (
                f"月结余 ¥{monthly_saving:+.0f}，建议月储蓄目标 ¥{target_saving:.0f}。"
                if level != HealthLevel.HEALTHY else ""
            ),
        )

        dim = DimensionDetail("储蓄率诊断", score, level, suggestion)
        return DiagnosisReport(
            overall_level=level,
            overall_score=score,
            dimensions=[dim],
            suggestions=[suggestion] if level != HealthLevel.HEALTHY else [],
        )
