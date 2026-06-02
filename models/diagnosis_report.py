# 诊断报告 — DiagnosisReport + DimensionDetail + HealthLevel
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from models.suggestion import Suggestion


class HealthLevel(Enum):
    """健康等级"""
    HEALTHY = "健康"
    WARNING = "预警"
    CRITICAL = "严重"


@dataclass
class DimensionDetail:
    """单一诊断维度的评分与建议"""
    strategy_name: str                        # 策略名，如 "储蓄率诊断"
    score: float                              # 0~100 得分
    level: HealthLevel                        # 该维度等级
    suggestion: Optional[Suggestion] = None   # 该维度的建议（None 表示无需建议）


@dataclass
class DiagnosisReport:
    """诊断报告。suggestions 按 impact_amount 降序排列。"""
    overall_level: HealthLevel
    overall_score: float                         # 0~100 综合评分
    dimensions: list[DimensionDetail] = field(default_factory=list)
    suggestions: list[Suggestion] = field(default_factory=list)

    def __post_init__(self):
        # 确保 suggestions 按 impact_amount 降序
        self.suggestions.sort(key=lambda s: s.impact_amount, reverse=True)
