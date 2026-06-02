# Week52Method — 52周存款法
from models.transaction import Transaction
from models.savings_plan import SavingsPlan
from .savings_method import SavingsMethod


class Week52Method(SavingsMethod):
    """52周存款法。每周递增（或递减）存款金额。"""

    def __init__(self, base_amount: float = 10.0, reversed: bool = False):
        """
        base_amount: 基数，默认10元
        reversed: False=标准版(递增)，True=反向版(递减)
        """
        self.base = base_amount
        self.reversed = reversed

    def calculate(self, monthly_income: float,
                  history: list[Transaction]) -> SavingsPlan:
        if self.reversed:
            # 反向版：第1周存最多，递减
            amounts = [(53 - n) * self.base for n in range(1, 53)]
            desc = (
                f"反向52周存款法：第1周存 ¥{amounts[0]:.0f}，"
                f"递减至第52周 ¥{amounts[51]:.0f}。"
            )
        else:
            # 标准版：第1周存最少，递增
            amounts = [n * self.base for n in range(1, 53)]
            desc = (
                f"标准52周存款法：第1周存 ¥{amounts[0]:.0f}，"
                f"递增至第52周 ¥{amounts[51]:.0f}。"
            )

        annual = sum(amounts)
        desc += f"年累计 ¥{annual:.0f}。"

        return SavingsPlan(
            weekly_amounts=amounts,
            annual_total=annual,
            description=desc,
        )
