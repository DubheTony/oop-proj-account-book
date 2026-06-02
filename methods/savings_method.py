# SavingsMethod — 储蓄方法接口
from abc import ABC, abstractmethod
from models.transaction import Transaction
from models.savings_plan import SavingsPlan


class SavingsMethod(ABC):
    """储蓄方法接口。根据月收入和历史，生成储蓄节奏计划。"""

    @abstractmethod
    def calculate(self, monthly_income: float,
                  history: list[Transaction]) -> SavingsPlan:
        ...
