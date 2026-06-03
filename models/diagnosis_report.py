# 诊断报告 — DiagnosisReport + DimensionDetail + HealthLevel
from enum import Enum
from typing import Optional
from models.suggestion import Suggestion


class HealthLevel(Enum):
    """健康等级"""
    HEALTHY = "健康"
    WARNING = "预警"
    CRITICAL = "严重"


class DimensionDetail:
    """单一诊断维度的评分与建议"""

    def __init__(self, strategy_name: str, score: float, level: HealthLevel,
                 suggestion: Optional[Suggestion] = None):
        self.strategy_name = strategy_name  # 策略名，如 "储蓄率诊断"
        self.score = score                  # 0~100 得分
        self.level = level                  # 该维度等级
        self.suggestion = suggestion        # 该维度的建议（None 表示无需建议）


class DiagnosisReport:
    """诊断报告。suggestions 按 impact_amount 降序排列。"""

    def __init__(self, overall_level: HealthLevel, overall_score: float,
                 dimensions: list[DimensionDetail] = None,
                 suggestions: list[Suggestion] = None):
        self.overall_level = overall_level    # 综合等级
        self.overall_score = overall_score    # 0~100 综合评分
        self.dimensions = dimensions or []
        self.suggestions = suggestions or []
        # 确保 suggestions 按影响金额降序
        self.suggestions.sort(key=lambda s: s.impact_amount, reverse=True)
