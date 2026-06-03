# 储蓄方法建议的结果


class SavingsPlan:
    """储蓄方法建议的结果。52周每周存款计划。"""

    def __init__(self, weekly_amounts: list[float], annual_total: float,
                 description: str):
        self.weekly_amounts = weekly_amounts  # 52项，第i项为第i+1周建议存款
        self.annual_total = annual_total      # 年储蓄总额
        self.description = description        # 方法说明文本
