# 储蓄目标达成率诊断策略
# 将用户设置的月度储蓄目标与实际储蓄对比
# score = min(实际月储蓄 / 目标月储蓄 * 100, 100)
from models.transaction import Transaction
from models.budget import Budget
from models.diagnosis_report import DiagnosisReport, DimensionDetail, HealthLevel
from models.suggestion import Suggestion
from .diagnostic_strategy import DiagnosticStrategy


class SavingsGoalStrategy(DiagnosticStrategy):
    """储蓄目标达成率：判断实际储蓄是否达到用户设定的月度目标。

    需要在 controller 中设置 monthly_savings_target（通过 set_savings_target）。
    未设置目标时返回满分（不适用）。
    """

    def __init__(self, get_target: callable = None):
        """
        get_target: 可调用对象，返回 float|None（月度储蓄目标）。
                    为 None 时从 controller 读取。
        """
        self._get_target = get_target

    @property
    def target(self) -> float | None:
        if self._get_target:
            return self._get_target()
        return None

    def diagnose(
        self,
        transactions: list[Transaction],
        budgets: list[Budget]
    ) -> DiagnosisReport:
        target = self.target

        # ----- 未设置储蓄目标 -----
        if target is None or target <= 0:
            dim = DimensionDetail(
                "储蓄目标达成率", 100, HealthLevel.HEALTHY,
                Suggestion(3, 0, "储蓄",
                           "尚未设置储蓄目标。可在「储蓄管理」页设置目标后获得更精准的诊断。")
            )
            return DiagnosisReport(HealthLevel.HEALTHY, 100, [dim], [dim.suggestion])

        # ----- 计算实际月储蓄 -----
        total_income = sum(t.amount for t in transactions if t.is_income())
        total_expense = sum(t.amount for t in transactions if t.is_expense())

        # 无收入时无法判断
        if total_income == 0:
            dim = DimensionDetail(
                "储蓄目标达成率", 0, HealthLevel.WARNING,
                Suggestion(2, target, "全部",
                           f"月度储蓄目标 ¥{target:.0f}，但本月无收入记录，"
                           f"无法判断达成情况。请先录入收入。")
            )
            return DiagnosisReport(HealthLevel.WARNING, 0, [dim], [dim.suggestion])

        actual_saving = total_income - total_expense
        achievement_rate = actual_saving / target
        score = max(0, min(achievement_rate * 100, 100))

        # ----- 等级判定 -----
        if achievement_rate >= 1.0:
            level = HealthLevel.HEALTHY
            desc = (
                f"月度储蓄 ¥{actual_saving:.0f}，达成目标的 {achievement_rate:.0%}"
                f"（目标 ¥{target:.0f}）。继续保持！"
            )
            suggestion = Suggestion(
                3, 0, "储蓄",
                desc + " 储蓄目标已达成，财务状况良好。"
            )
        elif achievement_rate >= 0.5:
            level = HealthLevel.WARNING
            gap = target - actual_saving
            desc = (
                f"月度储蓄 ¥{actual_saving:.0f}，仅达成目标的 {achievement_rate:.0%}"
                f"（目标 ¥{target:.0f}），缺口 ¥{gap:.0f}。"
            )
            suggestion = Suggestion(
                2, gap, "全部",
                desc + " 建议控制弹性支出或检查收入是否低于预期。"
            )
        else:
            level = HealthLevel.CRITICAL
            gap = target - actual_saving
            if actual_saving < 0:
                desc = (
                    f"月度入不敷出（¥{actual_saving:.0f}），远未达到储蓄目标 ¥{target:.0f}。"
                )
            else:
                desc = (
                    f"月度储蓄仅 ¥{actual_saving:.0f}，达成率 {achievement_rate:.0%}"
                    f"（目标 ¥{target:.0f}），缺口 ¥{gap:.0f}。"
                )
            suggestion = Suggestion(
                1, gap, "全部",
                desc + " 迫切需要削减非必要支出或增加收入来源。"
            )

        dim = DimensionDetail("储蓄目标达成率", score, level, suggestion)
        return DiagnosisReport(
            overall_level=level,
            overall_score=score,
            dimensions=[dim],
            suggestions=[suggestion] if level != HealthLevel.HEALTHY else [],
        )
