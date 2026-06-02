# SavingGoalCalculator — 储蓄目标倒推计算器
from collections import defaultdict
from datetime import date, timedelta
from models.transaction import Transaction
from models.monthly_plan import MonthlyPlan
from models.suggestion import Suggestion


class SavingGoalCalculator:
    """储蓄目标倒推计算器。根据目标金额和交易历史，逆推每月需储蓄额度。"""

    def __init__(self):
        self._cut_ratios: dict[str, float] = {
            "餐饮": 0.40,
            "娱乐": 0.60,
        }

    def set_cut_ratio(self, category: str, ratio: float):
        """设置某类别的削减比例（0~1之间）"""
        self._cut_ratios[category] = ratio

    def calculate_plan(
        self,
        target: float,
        months: int,
        history: list[Transaction]
    ) -> MonthlyPlan:
        if not history:
            raise ValueError("无历史数据，无法计算储蓄计划。请至少提供1个月的交易记录。")

        # 1. 计算时间跨度和月均收支
        dates = [t.date for t in history]
        span_days = (max(dates) - min(dates)).days
        span_months = max(span_days / 30.0, 1.0)

        total_income = sum(t.amount for t in history if t.is_income())
        total_expense = sum(t.amount for t in history if t.is_expense())

        monthly_income = total_income / span_months
        monthly_expense = total_expense / span_months
        natural_saving = monthly_income - monthly_expense

        # 2. 计算所需和差额
        required = target / months
        extra_needed = max(0.0, required - natural_saving)

        # 3. 如果无需额外削减
        if extra_needed <= 0:
            return MonthlyPlan(
                required_monthly_saving=required,
                current_natural_saving=natural_saving,
                extra_cut_needed=0.0,
                category_cuts={},
                suggestions=[
                    Suggestion(
                        priority=3,
                        impact_amount=0,
                        category="全部",
                        description=(
                            f"当前月自然结余 ¥{natural_saving:.0f}，"
                            f"已超过目标所需月储蓄 ¥{required:.0f}。"
                            "无需额外削减，保持当前消费习惯即可达成目标。"
                        ),
                    )
                ],
            )

        # 4. 按 cut_ratios 分配削减
        category_cuts: dict[str, float] = {}
        suggestions: list[Suggestion] = []

        for category, ratio in self._cut_ratios.items():
            cut = extra_needed * ratio
            category_cuts[category] = cut

            # 检查该类别是否有足够的支出可削减
            cat_expense = sum(t.amount for t in history
                            if t.is_expense() and t.category == category) / span_months
            actual_cut = min(cut, cat_expense * 0.8)  # 最多削减该类支出的80%

            if actual_cut > 0:
                suggestions.append(Suggestion(
                    priority=1,
                    impact_amount=actual_cut,
                    category=category,
                    description=(
                        f"建议每月削减 {category} 支出 ¥{actual_cut:.0f}"
                        f"（当前月均 ¥{cat_expense:.0f} → 目标 ¥{cat_expense - actual_cut:.0f}）。"
                        f"削减比例 {ratio:.0%}，月省 ¥{actual_cut:.0f}，"
                        f"{months}个月累计 ¥{actual_cut * months:.0f}。"
                    ),
                ))

        return MonthlyPlan(
            required_monthly_saving=required,
            current_natural_saving=natural_saving,
            extra_cut_needed=extra_needed,
            category_cuts=category_cuts,
            suggestions=suggestions,
        )
