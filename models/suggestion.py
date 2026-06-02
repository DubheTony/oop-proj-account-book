# Suggestion — 一条可执行的改善建议
from dataclasses import dataclass


@dataclass
class Suggestion:
    """一条可操作的建议。所有数字由策略根据实际数据计算，不使用模板句。"""
    priority: int          # 1=高优先级(必须改) / 2=中优先级 / 3=低优先级
    impact_amount: float   # 执行此建议预计每月可改善的金额
    category: str          # 关联的支出类别
    description: str       # 策略生成的描述文本，含具体数字
