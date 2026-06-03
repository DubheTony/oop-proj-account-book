# FixedBudgetRule — 固定预算规则
# 用户手动设定各类别固定限额
from models.transaction import Transaction
from .budget_rule import BudgetRule


class FixedBudgetRule(BudgetRule):
    """固定预算规则。直接返回预设的各类别限额。"""

    def __init__(self):
        self._budgets = {}

    def set_budget(self, category: str, limit: float):
        """设置某类别的预算上限"""
        self._budgets[category] = limit

    def allocate(self, income: float, history: list[Transaction]) -> dict[str, float]:
        return dict(self._budgets)
