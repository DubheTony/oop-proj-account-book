# BudgetRule — 预算分配策略接口
from abc import ABC, abstractmethod
from models.transaction import Transaction


class BudgetRule(ABC):
    """预算分配策略接口。根据收入和消费历史，计算各类别的建议预算。"""

    @abstractmethod
    def allocate(self, income: float, history: list[Transaction]) -> dict[str, float]:
        """返回各类别建议预算，如 {"餐饮": 1500, "交通": 300, ...}"""
        ...
