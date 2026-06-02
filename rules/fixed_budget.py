# FixedBudgetRule — 固定预算规则
from models.transaction import Transaction
from .budget_rule import BudgetRule


class FixedBudgetRule(BudgetRule):
    """固定预算规则。直接返回预设的各类别限额。"""

    def __init__(self):
        self._budgets: dict[str, float] = {}

    def set_budget(self, category: str, limit: float):
        """设置某类别的预算上限"""
        self._budgets[category] = limit

    def allocate(self, income: float, history: list[Transaction]) -> dict[str, float]:
        return dict(self._budgets)
