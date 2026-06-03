# 改进建议 — 值对象


class Suggestion:
    """一条可操作的改善建议。
    所有数字由策略根据实际数据计算，不使用模板句。
    """

    def __init__(self, priority: int, impact_amount: float,
                 category: str, description: str):
        self.priority = priority          # 1=高优先级(必须改) / 2=中 / 3=低
        self.impact_amount = impact_amount  # 执行此建议预计每月可改善的金额
        self.category = category          # 关联的支出类别
        self.description = description    # 策略生成的描述文本，含具体数字
