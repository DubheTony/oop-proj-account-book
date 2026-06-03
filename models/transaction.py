# 交易实体 + 支付账户枚举
from enum import Enum
from datetime import date


class AccountType(Enum):
    """支付账户类型"""
    WECHAT = "微信"
    ALIPAY = "支付宝"
    CASH = "现金"
    BANK_CARD = "银行卡"


class Transaction:
    """一笔交易记录"""

    def __init__(self, amount: float, type: str, category: str,
                 account: AccountType, date: date, note: str = ""):
        self.amount = amount      # 金额
        self.type = type          # "收入" 或 "支出"
        self.category = category  # 类别：餐饮/交通/娱乐/学习/日用/其他
        self.account = account    # 支付账户
        self.date = date          # 交易日期
        self.note = note          # 备注

    def is_expense(self):
        """是否是支出"""
        return self.type == "支出"

    def is_income(self):
        """是否是收入"""
        return self.type == "收入"
