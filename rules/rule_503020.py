# Rule503020 — 50/30/20 预算规则
from models.transaction import Transaction
from .budget_rule import BudgetRule


class Rule503020(BudgetRule):
    """50/30/20预算规则。50%必要支出，30%想要支出，20%储蓄。"""

    def __init__(self, sub_necessities: list[str] = None, sub_wants: list[str] = None):
        """
        sub_necessities: 必要支出子类别，默认 ["餐饮", "交通", "日用"]
        sub_wants: 想要支出子类别，默认 ["娱乐", "其他"]
        储蓄不映射到支出类别，仅作目标标记
        """
        self.necessities_cats = sub_necessities or ["餐饮", "交通", "日用"]
        self.wants_cats = sub_wants or ["娱乐", "其他"]

    def allocate(self, income: float, history: list[Transaction]) -> dict[str, float]:
        budget: dict[str, float] = {}

        # 50% 必要
        necessity_total = income * 0.5
        budget.update(self._distribute(necessity_total, self.necessities_cats, history))

        # 30% 想要
        wants_total = income * 0.3
        budget.update(self._distribute(wants_total, self.wants_cats, history))

        # 20% 储蓄（标记用途，不分配支出类别）
        budget["储蓄"] = income * 0.2

        return budget

    def _distribute(self, total: float, categories: list[str],
                    history: list[Transaction]) -> dict[str, float]:
        """按历史各子类支出比例分配总额。无历史数据时均分。"""
        if not history or not categories:
            each = total / len(categories)
            return {cat: each for cat in categories}

        # 统计各类别历史支出
        cat_totals = {cat: 0.0 for cat in categories}
        all_total = 0.0
        for t in history:
            if t.is_expense() and t.category in categories:
                cat_totals[t.category] += t.amount
                all_total += t.amount

        if all_total == 0:
            each = total / len(categories)
            return {cat: each for cat in categories}

        return {cat: total * (cat_totals[cat] / all_total) for cat in categories}
