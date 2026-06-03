# Rule503020 — 50/30/20 预算规则
# 50%必要支出，30%想要支出，20%储蓄
# 子类别（如餐饮食品）不独立分配预算，其支出归入父类别（如餐饮）
from models.transaction import Transaction
from .budget_rule import BudgetRule
from services.category_normalizer import CATEGORY_PARENTS


class Rule503020(BudgetRule):
    """50/30/20 预算规则。根据月收入按比例分配各类别预算。"""

    def __init__(self, sub_necessities=None, sub_wants=None):
        """sub_necessities: 必要支出子类别列表
        sub_wants: 想要支出子类别列表
        储蓄不映射到支出类别，仅作目标标记
        """
        self.necessities_cats = sub_necessities or [
            "餐饮", "交通", "家居日用", "个人护理", "医疗健康", "学习"
        ]
        self.wants_cats = sub_wants or [
            "娱乐", "数码电子", "运动户外", "服饰配饰", "其他"
        ]

    def allocate(self, income: float, history: list[Transaction]) -> dict[str, float]:
        budget = {}

        # 50% 必要支出 → 按历史比例分配给各子类
        necessity_total = income * 0.5
        budget.update(self._distribute(necessity_total, self.necessities_cats, history))

        # 30% 想要支出 → 按历史比例分配给各子类
        wants_total = income * 0.3
        budget.update(self._distribute(wants_total, self.wants_cats, history))

        # 20% 储蓄（标记用途，不分配支出类别）
        budget["储蓄"] = income * 0.2

        return budget

    def _distribute(self, total, categories, history):
        """按历史各子类支出比例分配总额。无历史数据时均分。
        子类别（如餐饮食品）不独立分配，归入父类别。
        """
        # 过滤掉子类别
        categories = [c for c in categories if c not in CATEGORY_PARENTS]

        if not history or not categories:
            each = total / max(len(categories), 1)
            return {cat: each for cat in categories}

        # 统计各类别历史支出（子类别支出归入父类别）
        cat_totals = {cat: 0.0 for cat in categories}
        all_total = 0.0
        for t in history:
            if not t.is_expense():
                continue
            matched_cat = t.category
            # 子类别归入父类别
            if matched_cat in CATEGORY_PARENTS:
                matched_cat = CATEGORY_PARENTS[matched_cat]
            if matched_cat in categories:
                cat_totals[matched_cat] += t.amount
                all_total += t.amount

        if all_total == 0:
            each = total / len(categories)
            return {cat: each for cat in categories}

        return {cat: total * (cat_totals[cat] / all_total) for cat in categories}
