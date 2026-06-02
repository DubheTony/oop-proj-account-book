# FixedAmountMethod — 每月固定金额储蓄
from models.transaction import Transaction
from models.savings_plan import SavingsPlan
from .savings_method import SavingsMethod


class FixedAmountMethod(SavingsMethod):
    """每月固定金额储蓄法。52周均分。"""

    def __init__(self, monthly_amount: float):
        self.monthly_amount = monthly_amount

    def calculate(self, monthly_income: float,
                  history: list[Transaction]) -> SavingsPlan:
        annual = self.monthly_amount * 12
        weekly = annual / 52
        return SavingsPlan(
            weekly_amounts=[weekly] * 52,
            annual_total=annual,
            description=(
                f"每月固定储蓄 ¥{self.monthly_amount:.0f}，年累计 ¥{annual:.0f}。"
                f"占月收入 {self.monthly_amount / monthly_income:.0%}。"
            ) if monthly_income > 0 else (
                f"每月固定储蓄 ¥{self.monthly_amount:.0f}，年累计 ¥{annual:.0f}。"
            ),
        )
