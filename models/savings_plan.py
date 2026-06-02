# SavingsPlan — 储蓄方法建议的结果
from dataclasses import dataclass


@dataclass
class SavingsPlan:
    """储蓄方法建议的结果。52周每周存款计划。"""
    weekly_amounts: list[float]   # 52项，第i项为第i+1周建议存款
    annual_total: float           # 年储蓄总额
    description: str              # 方法说明文本
