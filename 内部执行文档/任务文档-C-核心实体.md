# 任务文档 — C（核心实体 + 主控骨架）

> 本文档只包含你需要关心的内容。全局设计见 `设计文档.md`，接口契约见 `接口文档.md`。

---

## 你的职责

1. **核心实体**：`Transaction`、`Budget`、`AccountType` 枚举
2. **值对象**：`Suggestion`
3. **主控骨架**：`FinanceController`（所有方法签名 + 预警逻辑 + 交易/预算管理）
4. 你的代码是**所有其他人的基础依赖**，必须第 1 周优先完成

---

## 你需要交付的文件

```
models/
├── __init__.py
├── transaction.py      # Transaction 数据类 + AccountType 枚举
├── budget.py           # Budget 数据类
└── suggestion.py       # Suggestion 值对象

services/
├── __init__.py
└── finance_controller.py  # FinanceController（完整实现）
```

---

## 文件 1：`models/transaction.py`

```python
from dataclasses import dataclass
from datetime import date
from enum import Enum


class AccountType(Enum):
    WECHAT = "微信"
    ALIPAY = "支付宝"
    CASH = "现金"
    BANK_CARD = "银行卡"


@dataclass
class Transaction:
    amount: float
    type: str              # "收入" 或 "支出"
    category: str          # "餐饮"/"交通"/"娱乐"/"学习"/"日用"/"其他"
    account: AccountType
    date: date
    note: str = ""

    def is_expense(self) -> bool:
        return self.type == "支出"

    def is_income(self) -> bool:
        return self.type == "收入"
```

**要点**：
- 用 `@dataclass`，不用手写 `__init__`
- `type` 只接受 `"收入"` 或 `"支出"`（调用方自行保证，Controller 中可做校验）
- `category` 是标准化后的类别名（CSV 导入时由 B 的 `CategoryNormalizer` 标准化）

---

## 文件 2：`models/budget.py`

```python
from dataclasses import dataclass


@dataclass
class Budget:
    category: str
    monthly_limit: float
    current_spent: float = 0.0

    def is_exceeded(self) -> bool:
        return self.current_spent > self.monthly_limit

    def get_remaining(self) -> float:
        return self.monthly_limit - self.current_spent

    def add_expense(self, amount: float) -> None:
        self.current_spent += amount
```

**要点**：
- **不要**加观察者相关代码（attach/detach/notify/observers/alreadyNotified）——这些已废弃
- `add_expense` 只做累加，不判断超支（超支判断在 Controller）

---

## 文件 3：`models/suggestion.py`

```python
from dataclasses import dataclass


@dataclass
class Suggestion:
    """一条可操作的建议。所有数字由策略根据实际数据计算。"""
    priority: int          # 1=高优(必须改) / 2=中优 / 3=低优
    impact_amount: float   # 预计每月可改善的金额
    category: str          # 关联的支出类别
    description: str       # 含具体数字的建议文本（策略生成）
```

**要点**：
- `description` 中的数字由策略计算填入，你不需要在这里写生成逻辑
- 建议列表展示时按 `impact_amount` 降序排列（在 `DiagnosisReport` 或 GUI 层排序）

---

## 文件 4：`services/finance_controller.py`

这是最复杂的文件。完整签名和逻辑如下：

```python
from models.transaction import Transaction
from models.budget import Budget


class FinanceController:
    """个人财务管理系统的总协调器。"""

    def __init__(self):
        self._transactions: list[Transaction] = []
        self._budgets: list[Budget] = []
        self._alert_messages: list[str] = []

        # 策略引用 —— 由调用方设置
        self.diagnosis_strategy = None    # DiagnosticStrategy | None
        self.budget_rule = None           # BudgetRule | None (P1)
        self.savings_method = None        # SavingsMethod | None (P1)

        # 领域服务 —— 由 E 提供，你在这里只是 import 并实例化
        from services.saving_calculator import SavingGoalCalculator
        self.saving_calculator = SavingGoalCalculator()

    # ==================== 交易管理 ====================

    def add_transaction(self, t: Transaction) -> None:
        self._transactions.append(t)

        # 如果是支出，更新对应类别预算并检查预警
        if t.is_expense():
            budget = self._find_budget(t.category)
            if budget is not None:
                was_exceeded_before = budget.is_exceeded()
                budget.add_expense(t.amount)
                # 只在首次超支时告警（避免重复）
                if not was_exceeded_before and budget.is_exceeded():
                    over = budget.current_spent - budget.monthly_limit
                    self._alert_messages.append(
                        f"[预警] {t.date} | {t.category} 预算超支！"
                        f"限额 ¥{budget.monthly_limit:.0f}，已支出 ¥{budget.current_spent:.0f}，超出 ¥{over:.0f}"
                    )

    def import_csv(self, path: str) -> int:
        """委托给 csv_importer 模块（B 实现）"""
        from services.csv_importer import import_csv
        new_transactions = import_csv(path)
        for t in new_transactions:
            self.add_transaction(t)
        return len(new_transactions)

    def get_transactions(self) -> list[Transaction]:
        return self._transactions.copy()

    # ==================== 预算管理 ====================

    def set_budget(self, b: Budget) -> None:
        """添加或更新一个类别的预算（按 category 去重）"""
        for i, existing in enumerate(self._budgets):
            if existing.category == b.category:
                self._budgets[i] = b
                return
        self._budgets.append(b)

    def get_budgets(self) -> list[Budget]:
        return self._budgets.copy()

    def apply_budget_rule(self, income: float) -> dict[str, float]:
        """P1。委托给 BudgetRule"""
        if self.budget_rule is None:
            raise RuntimeError("BudgetRule 未设置。请先调用 set_budget_rule()")
        return self.budget_rule.allocate(income, self._transactions)

    # ==================== 诊断 ====================

    def set_diagnosis_strategy(self, s) -> None:
        self.diagnosis_strategy = s

    def generate_diagnosis(self):
        if self.diagnosis_strategy is None:
            raise RuntimeError("DiagnosticStrategy 未设置。请先调用 set_diagnosis_strategy()")
        return self.diagnosis_strategy.diagnose(self._transactions, self._budgets)

    # ==================== 储蓄 ====================

    def set_budget_rule(self, r) -> None:
        self.budget_rule = r

    def set_savings_method(self, m) -> None:
        self.savings_method = m

    def generate_saving_plan(self, target: float, months: int):
        return self.saving_calculator.calculate_plan(target, months, self._transactions)

    def get_savings_plan(self, income: float):
        """P1。委托给 SavingsMethod"""
        if self.savings_method is None:
            raise RuntimeError("SavingsMethod 未设置。请先调用 set_savings_method()")
        return self.savings_method.calculate(income, self._transactions)

    # ==================== 告警 ====================

    def get_alert_messages(self) -> list[str]:
        return self._alert_messages.copy()

    def clear_alerts(self) -> None:
        self._alert_messages.clear()

    # ==================== 内部 ====================

    def _find_budget(self, category: str):
        for b in self._budgets:
            if b.category == category:
                return b
        return None
```

**要点**：
- 策略引用（diagnosis_strategy/budget_rule/savings_method）使用 duck typing，不 import 接口类。类型注解用 `# DiagnosticStrategy | None` 注释说明即可
- `import_csv` 委托给 B 的模块，你写调用框架即可
- `saving_calculator` 用延迟 import（在 `__init__` 内 import）避免 E 还没写好时导入报错。E 交付后改为顶部 import
- `add_transaction` 中的预警逻辑：只在"从非超支变为超支"时告警一次，避免重复刷屏

---

## 你与其他人的接口

| 你提供 | 谁需要 | 何时需要 |
|---|---|---|
| `Transaction` 类 | D（诊断策略需要遍历交易数据）、E（储蓄计算需要分析历史）、B（CSV 导入要创建 Transaction 对象） | 第 1 周 |
| `Budget` 类 | D（类别超支策略需要读预算）、E（储蓄倒推可能需要参考预算） | 第 1 周 |
| `AccountType` 枚举 | B（CSV 导入时解析账户列） | 第 1 周 |
| `Suggestion` 类 | D（策略生成建议）、E（MonthlyPlan 含建议） | 第 1 周 |
| `FinanceController` | A（GUI 通过 Controller 调用一切）、B（CLI 原型通过 Controller 验证 API） | 第 2 周初 |

| 你需要 | 谁提供 | 何时可用 |
|---|---|---|
| `SavingGoalCalculator` | E | 第 1 周末 |
| `csv_importer.import_csv()` | B | 第 2 周 |
| `DiagnosticStrategy`（设置用） | D | 第 2 周 |
| `BudgetRule`（设置用） | E | 第 2 周 |
| `SavingsMethod`（设置用） | E | 第 2 周 |

---

## 第 1 周时间线

| 天 | 任务 |
|---|---|
| 1-2 | 写 `Transaction`、`AccountType`、`Budget`、`Suggestion` 四个文件，跑通基本单元测试 |
| 3-4 | 写 `FinanceController`（add_transaction、set_budget、get_*、预警逻辑、_find_budget） |
| 5 | 写 `import_csv` 调用框架 + `generate_diagnosis`/`generate_saving_plan` 委托框架 |
| 6-7 | 和 B 联调：B 用你的 Controller + 假数据写 CLI 原型，验证 API 是否合理 |

---

## 注意事项

- 使用 `@dataclass` 而非手写 `__init__`，保持简洁
- `list.copy()` 返回副本，防止外部直接修改内部列表
- 预警只在首次超支时告警（`was_exceeded_before` 判断），不重复
- 第 1 周你的模型类必须稳定，因为 D 和 E 第 2 周开始就要依赖它们
- 如果接口需要修改，务必通知 D+E 确认后更新 `接口文档.md`
