# Transaction + AccountType — 核心交易实体
from enum import Enum
from dataclasses import dataclass
from datetime import date


class AccountType(Enum):
    """支付账户类型"""
    WECHAT = "微信"
    ALIPAY = "支付宝"
    CASH = "现金"
    BANK_CARD = "银行卡"


@dataclass
class Transaction:
    """一笔交易记录"""
    amount: float          # 金额
    type: str              # "收入" 或 "支出"
    category: str          # 类别：餐饮/交通/娱乐/学习/日用/其他
    account: AccountType   # 支付账户
    date: date             # 交易日期
    note: str = ""         # 备注

    def is_expense(self) -> bool:
        return self.type == "支出"

    def is_income(self) -> bool:
        return self.type == "收入"
