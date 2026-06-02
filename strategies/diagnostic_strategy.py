# 诊断策略接口 — Strategy 模式抽象基类
from abc import ABC, abstractmethod
from models.transaction import Transaction
from models.budget import Budget
from models.diagnosis_report import DiagnosisReport


class DiagnosticStrategy(ABC):
    """诊断策略抽象基类。
    每个具体策略封装一种诊断算法。
    diagnose() 必须是纯函数：
    - 不修改传入的 transactions/budgets
    - 不依赖外部状态
    score 统一为 0~100，方便 Composite 加权聚合。
    """

    @abstractmethod
    def diagnose(
        self,
        transactions: list[Transaction],
        budgets: list[Budget]
    ) -> DiagnosisReport:
        """执行诊断，返回诊断报告。"""
        ...
