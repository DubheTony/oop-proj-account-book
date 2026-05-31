# Budget — 预算实体
from dataclasses import dataclass


@dataclass
class Budget:
    """某个类别的月度预算"""
    category: str                # 预算类别
    monthly_limit: float         # 月度限额
    current_spent: float = 0.0   # 当月已支出

    def is_exceeded(self) -> bool:
        """是否超支"""
        return self.current_spent > self.monthly_limit

    def get_remaining(self) -> float:
        """剩余额度"""
        return self.monthly_limit - self.current_spent

    def add_expense(self, amount: float) -> None:
        """记录一笔支出到当月累计"""
        self.current_spent += amount
