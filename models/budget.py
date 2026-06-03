# 预算实体


class Budget:
    """某个类别的月度预算"""

    def __init__(self, category: str, monthly_limit: float, current_spent: float = 0.0):
        self.category = category          # 预算类别
        self.monthly_limit = monthly_limit  # 月度限额
        self.current_spent = current_spent  # 当月已支出

    def is_exceeded(self):
        """是否超支"""
        return self.current_spent > self.monthly_limit

    def get_remaining(self):
        """剩余额度"""
        return self.monthly_limit - self.current_spent

    def add_expense(self, amount):
        """记录一笔支出到当月累计"""
        self.current_spent += amount
