# MonthlyPlan — 储蓄倒推的结果
from dataclasses import dataclass, field
from models.suggestion import Suggestion


@dataclass
class MonthlyPlan:
    """储蓄目标倒推计算的结果"""
    required_monthly_saving: float   # 每月需存
    current_natural_saving: float    # 当前自然月结余
    extra_cut_needed: float          # 每月需额外削减金额
    category_cuts: dict[str, float]  # {"餐饮": 300.0, "娱乐": 200.0}
    suggestions: list[Suggestion] = field(default_factory=list)

    def __post_init__(self):
        self.suggestions.sort(key=lambda s: s.impact_amount, reverse=True)
