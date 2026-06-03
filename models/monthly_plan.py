# 月度储蓄计划 — 储蓄倒推的结果
from models.suggestion import Suggestion


class MonthlyPlan:
    """储蓄目标倒推计算的结果"""

    def __init__(self, required_monthly_saving: float,
                 current_natural_saving: float, extra_cut_needed: float,
                 category_cuts: dict[str, float],
                 suggestions: list[Suggestion] = None):
        self.required_monthly_saving = required_monthly_saving    # 每月需存
        self.current_natural_saving = current_natural_saving      # 当前自然月结余
        self.extra_cut_needed = extra_cut_needed                  # 每月需额外削减金额
        self.category_cuts = category_cuts                        # {"餐饮": 300, "娱乐": 200}
        self.suggestions = suggestions or []
        self.suggestions.sort(key=lambda s: s.impact_amount, reverse=True)
