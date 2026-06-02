# PercentageMethod — 收入百分比储蓄法
from models.transaction import Transaction
from models.savings_plan import SavingsPlan
from .savings_method import SavingsMethod


class PercentageMethod(SavingsMethod):
    """按收入百分比储蓄。例如 20% 即每月存收入的20%。"""

    def __init__(self, rate: float = 0.2):
        self.rate = rate

    def calculate(self, monthly_income: float,
                  history: list[Transaction]) -> SavingsPlan:
        monthly = monthly_income * self.rate
        annual = monthly * 12
        weekly = annual / 52
        return SavingsPlan(
            weekly_amounts=[weekly] * 52,
            annual_total=annual,
            description=(
                f"每月储蓄收入的 {self.rate:.0%}（¥{monthly:.0f}），"
                f"年累计 ¥{annual:.0f}。"
            ),
        )
