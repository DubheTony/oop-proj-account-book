# 类别超支诊断策略
# 遍历所有预算记录，检查各类别是否超出月度限额
# score = max(0, 100 - 最严重超支比例 * 100)
from models.transaction import Transaction
from models.budget import Budget
from models.diagnosis_report import DiagnosisReport, DimensionDetail, HealthLevel
from models.suggestion import Suggestion
from .diagnostic_strategy import DiagnosticStrategy


class CategoryOverrunStrategy(DiagnosticStrategy):
    """类别超支诊断：遍历所有预算，检测各类别是否超支。"""

    # 可配置阈值
    CRITICAL_OVERRUN = 0.30   # 超支超过 30% 视为严重

    def diagnose(
        self,
        transactions: list[Transaction],
        budgets: list[Budget]
    ) -> DiagnosisReport:
        # ----- 边界：无预算 -----
        if not budgets:
            dim = DimensionDetail("类别超支诊断", 100, HealthLevel.HEALTHY, None)
            return DiagnosisReport(HealthLevel.HEALTHY, 100, [dim], [])

        # ----- 遍历预算，收集超支类别 -----
        exceeded = []  # [(category, spent, limit, overrun_ratio, over_amount), ...]
        for b in budgets:
            if not b.is_exceeded():
                continue
            if b.monthly_limit <= 0:
                continue  # 跳过限额为 0 的无效预算
            overrun_ratio = (b.current_spent - b.monthly_limit) / b.monthly_limit
            over_amount = b.current_spent - b.monthly_limit
            exceeded.append((b.category, b.current_spent, b.monthly_limit,
                             overrun_ratio, over_amount))

        # ----- 无超支 -----
        if not exceeded:
            dim = DimensionDetail("类别超支诊断", 100, HealthLevel.HEALTHY, None)
            return DiagnosisReport(HealthLevel.HEALTHY, 100, [dim], [])

        # ----- 有超支：基于最严重超支评分 -----
        max_ratio = max(e[3] for e in exceeded)
        score = max(0, 100 - max_ratio * 100)

        if max_ratio > self.CRITICAL_OVERRUN:
            level = HealthLevel.CRITICAL
        else:
            level = HealthLevel.WARNING

        # 为每个超支类别生成 Suggestion
        suggestions = []
        for cat, spent, limit, ratio, over in exceeded:
            s = Suggestion(
                priority=1,
                impact_amount=over,
                category=cat,
                description=(
                    f"该类别超支 ¥{over:.0f}"
                    f"（限额 ¥{limit:.0f}，已支出 ¥{spent:.0f}），"
                    f"超支 {ratio:.0%}。"
                    f"建议削减该类别支出或调整预算限额。"
                )
            )
            suggestions.append(s)

        # 维度名包含超支类别信息
        if len(exceeded) == 1:
            dim_name = f"类别超支-{exceeded[0][0]}"
        else:
            cats = "、".join(e[0] for e in exceeded)
            dim_name = f"类别超支({cats})"

        # 第一个超支类别的建议作为维度建议
        first_s = suggestions[0] if suggestions else None
        dim = DimensionDetail(dim_name, score, level, first_s)

        return DiagnosisReport(
            overall_level=level,
            overall_score=score,
            dimensions=[dim],
            suggestions=suggestions,
        )
