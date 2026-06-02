# 复合诊断策略 — 加权聚合多个子策略 (P1)
# 持有多个 (DiagnosticStrategy, 权重) 元组
# diagnose() 时运行全部子策略，加权计算综合分
from models.transaction import Transaction
from models.budget import Budget
from models.diagnosis_report import DiagnosisReport, HealthLevel
from .diagnostic_strategy import DiagnosticStrategy


class CompositeDiagnosis(DiagnosticStrategy):
    """复合诊断：持有多个子策略，加权聚合评分。

    用法：
        composite = CompositeDiagnosis([
            (SavingRateStrategy(), 0.4),
            (CategoryOverrunStrategy(), 0.3),
            (ConsumptionStructureStrategy(), 0.3),
        ])
        report = composite.diagnose(transactions, budgets)
    """

    def __init__(self, strategies: list[tuple[DiagnosticStrategy, float]]):
        """
        strategies: [(策略实例, 权重), ...]
        权重之和建议为 1.0
        """
        self._strategies = strategies

    def add_strategy(self, strategy: DiagnosticStrategy, weight: float):
        """动态添加子策略"""
        self._strategies.append((strategy, weight))

    def diagnose(
        self,
        transactions: list[Transaction],
        budgets: list[Budget]
    ) -> DiagnosisReport:
        # ----- 边界：无子策略 -----
        if not self._strategies:
            return DiagnosisReport(HealthLevel.HEALTHY, 100, [], [])

        # ----- 运行全部子策略 -----
        reports_and_weights = []
        for strategy, weight in self._strategies:
            report = strategy.diagnose(transactions, budgets)
            reports_and_weights.append((report, weight))

        # ----- 加权综合分 -----
        overall_score = sum(r.overall_score * w for r, w in reports_and_weights)

        # 综合等级映射
        if overall_score >= 80:
            overall_level = HealthLevel.HEALTHY
        elif overall_score >= 50:
            overall_level = HealthLevel.WARNING
        else:
            overall_level = HealthLevel.CRITICAL

        # ----- 汇总所有维度和建议 -----
        all_dimensions = []
        all_suggestions = []
        for r, w in reports_and_weights:
            all_dimensions.extend(r.dimensions)
            all_suggestions.extend(r.suggestions)

        # ----- 建议去重（同 category + 同 description 只保留一个）-----
        seen = set()
        unique_suggestions = []
        for s in all_suggestions:
            key = (s.category, s.description)
            if key not in seen:
                seen.add(key)
                unique_suggestions.append(s)

        return DiagnosisReport(
            overall_level=overall_level,
            overall_score=overall_score,
            dimensions=all_dimensions,
            suggestions=unique_suggestions,
        )
