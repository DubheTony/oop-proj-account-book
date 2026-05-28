# 任务文档 — E（预算规则 + 储蓄方法 + 储蓄倒推）

> 本文档只包含你需要关心的内容。全局设计见 `设计文档.md`，接口契约见 `接口文档.md`。

---

## 你的职责

1. **P0 储蓄倒推**：`SavingGoalCalculator` + `MonthlyPlan`
2. **P1 预算规则族**：`BudgetRule` 接口 + `FixedBudgetRule` + `Rule503020`
3. **P1 储蓄方法族**：`SavingsMethod` 接口 + `FixedAmountMethod` + `Week52Method` + `PercentageMethod` + `SavingsPlan`

---

## 你需要交付的文件

```
models/
└── monthly_plan.py         # MonthlyPlan
  (+ savings_plan.py        # SavingsPlan, P1)

services/
└── saving_calculator.py    # SavingGoalCalculator

rules/                       # P1
├── __init__.py
├── budget_rule.py           # BudgetRule 接口
├── fixed_budget.py          # FixedBudgetRule
└── rule_503020.py           # Rule503020

methods/                     # P1
├── __init__.py
├── savings_method.py        # SavingsMethod 接口
├── fixed_amount.py          # FixedAmountMethod
├── week52.py                # Week52Method
└── percentage.py            # PercentageMethod
```

---

## P0 实现详规

### 文件 1：`models/monthly_plan.py`

```python
from dataclasses import dataclass, field
from models.suggestion import Suggestion


@dataclass
class MonthlyPlan:
    required_monthly_saving: float   # 每月需存
    current_natural_saving: float    # 当前自然月结余
    extra_cut_needed: float          # 每月需额外削减金额
    category_cuts: dict[str, float]  # {"餐饮": 300.0, "娱乐": 200.0}
    suggestions: list[Suggestion] = field(default_factory=list)

    def __post_init__(self):
        self.suggestions.sort(key=lambda s: s.impact_amount, reverse=True)
```

### 文件 2：`services/saving_calculator.py`

```python
from collections import defaultdict
from datetime import date, timedelta
from models.transaction import Transaction
from models.monthly_plan import MonthlyPlan
from models.suggestion import Suggestion


class SavingGoalCalculator:
    """
    储蓄目标倒推计算器。
    根据目标金额和交易历史，逆推每月需储蓄额度。
    """

    def __init__(self):
        self._cut_ratios: dict[str, float] = {
            "餐饮": 0.40,
            "娱乐": 0.60,
        }

    def set_cut_ratio(self, category: str, ratio: float):
        self._cut_ratios[category] = ratio

    def calculate_plan(
        self,
        target: float,
        months: int,
        history: list[Transaction]
    ) -> MonthlyPlan:
        if not history:
            raise ValueError("无历史数据，无法计算储蓄计划。请至少提供 1 个月的交易记录。")

        # 1. 计算时间跨度和月均收支
        dates = [t.date for t in history]
        span_days = (max(dates) - min(dates)).days
        span_months = max(span_days / 30.0, 1.0)

        total_income = sum(t.amount for t in history if t.is_income())
        total_expense = sum(t.amount for t in history if t.is_expense())

        monthly_income = total_income / span_months
        monthly_expense = total_expense / span_months
        natural_saving = monthly_income - monthly_expense

        # 2. 计算所需和差额
        required = target / months
        extra_needed = max(0.0, required - natural_saving)

        # 3. 如果无需额外削减
        if extra_needed <= 0:
            return MonthlyPlan(
                required_monthly_saving=required,
                current_natural_saving=natural_saving,
                extra_cut_needed=0.0,
                category_cuts={},
                suggestions=[
                    Suggestion(
                        priority=3,
                        impact_amount=0,
                        category="全部",
                        description=(
                            f"当前月自然结余 ¥{natural_saving:.0f}，"
                            f"已超过目标所需月储蓄 ¥{required:.0f}。"
                            "无需额外削减，保持当前消费习惯即可达成目标。"
                        ),
                    )
                ],
            )

        # 4. 按 cut_ratios 分配削减
        category_cuts: dict[str, float] = {}
        suggestions: list[Suggestion] = []
        remaining_extra = extra_needed

        for category, ratio in self._cut_ratios.items():
            cut = extra_needed * ratio
            category_cuts[category] = cut

            # 检查该类别是否有足够的支出可削减
            cat_expense = sum(t.amount for t in history
                            if t.is_expense() and t.category == category) / span_months
            actual_cut = min(cut, cat_expense * 0.8)  # 最多削减该类支出的 80%

            if actual_cut > 0:
                suggestions.append(Suggestion(
                    priority=1,
                    impact_amount=actual_cut,
                    category=category,
                    description=(
                        f"建议每月削减 {category} 支出 ¥{actual_cut:.0f}"
                        f"（当前月均 ¥{cat_expense:.0f} → 目标 ¥{cat_expense - actual_cut:.0f}）。"
                        f"削减比例 {ratio:.0%}，月省 ¥{actual_cut:.0f}，{months}个月累计 ¥{actual_cut*months:.0f}。"
                    ),
                ))

        return MonthlyPlan(
            required_monthly_saving=required,
            current_natural_saving=natural_saving,
            extra_cut_needed=extra_needed,
            category_cuts=category_cuts,
            suggestions=suggestions,
        )
```

**要点**：
- `span_months` 用天数/30 估算，不要求精确到日历月
- `cut_ratios` 默认 {"餐饮": 0.40, "娱乐": 0.60}，可通过 `set_cut_ratio()` 调整
- 削减建议有上限（不超过该类别月均支出的 80%），避免给出"餐饮砍到 0"的不合理建议
- `history` 为空时抛异常（Controller 可以 catch 并提示用户）

---

## P1 实现详规

### 预算规则族（rules/）

#### `rules/budget_rule.py` — 接口

```python
from abc import ABC, abstractmethod

class BudgetRule(ABC):
    @abstractmethod
    def allocate(self, income: float, history: list[Transaction]) -> dict[str, float]:
        """返回各类别建议预算 {"餐饮": 1500, "交通": 300, ...}"""
        ...
```

#### `rules/fixed_budget.py`

```python
class FixedBudgetRule(BudgetRule):
    def __init__(self):
        self._budgets: dict[str, float] = {}

    def set_budget(self, category: str, limit: float):
        self._budgets[category] = limit

    def allocate(self, income: float, history: list[Transaction]) -> dict[str, float]:
        return dict(self._budgets)
```

#### `rules/rule_503020.py`

```python
class Rule503020(BudgetRule):
    def __init__(self, sub_necessities: list[str] = None, sub_wants: list[str] = None):
        """
        sub_necessities: 必要支出子类别，默认 ["餐饮", "交通", "日用"]
        sub_wants: 想要支出子类别，默认 ["娱乐", "其他"]
        储蓄不映射到支出类别，仅作目标标记
        """
        self.necessities_cats = sub_necessities or ["餐饮", "交通", "日用"]
        self.wants_cats = sub_wants or ["娱乐", "其他"]

    def allocate(self, income: float, history: list[Transaction]) -> dict[str, float]:
        budget: dict[str, float] = {}

        # 50% 必要
        necessity_total = income * 0.5
        budget.update(self._distribute(necessity_total, self.necessities_cats, history))

        # 30% 想要
        wants_total = income * 0.3
        budget.update(self._distribute(wants_total, self.wants_cats, history))

        # 20% 储蓄（标记用途，不分配支出类别）
        budget["储蓄"] = income * 0.2

        return budget

    def _distribute(self, total: float, categories: list[str], history: list[Transaction]) -> dict[str, float]:
        """按历史各子类支出比例分配总额"""
        if not history or not categories:
            # 无历史数据 → 均分
            each = total / len(categories)
            return {cat: each for cat in categories}

        # 统计各类别历史支出
        cat_totals = {cat: 0.0 for cat in categories}
        all_total = 0.0
        for t in history:
            if t.is_expense() and t.category in categories:
                cat_totals[t.category] += t.amount
                all_total += t.amount

        if all_total == 0:
            each = total / len(categories)
            return {cat: each for cat in categories}

        return {cat: total * (cat_totals[cat] / all_total) for cat in categories}
```

### 储蓄方法族（methods/）

#### `methods/savings_method.py` — 接口

```python
from abc import ABC, abstractmethod
from models.savings_plan import SavingsPlan

class SavingsMethod(ABC):
    @abstractmethod
    def calculate(self, monthly_income: float, history: list[Transaction]) -> SavingsPlan:
        ...
```

#### `models/savings_plan.py`（P1，E 负责）

```python
from dataclasses import dataclass

@dataclass
class SavingsPlan:
    weekly_amounts: list[float]   # 52 项，第 i 项为第 i+1 周建议存款
    annual_total: float
    description: str
```

#### `methods/fixed_amount.py`

```python
class FixedAmountMethod(SavingsMethod):
    def __init__(self, monthly_amount: float):
        self.monthly_amount = monthly_amount

    def calculate(self, monthly_income: float, history: list[Transaction]) -> SavingsPlan:
        annual = self.monthly_amount * 12
        weekly = annual / 52
        return SavingsPlan(
            weekly_amounts=[weekly] * 52,
            annual_total=annual,
            description=f"每月固定储蓄 ¥{self.monthly_amount:.0f}，年累计 ¥{annual:.0f}。"
                         f"占月收入 {self.monthly_amount/monthly_income:.0%}。" if monthly_income > 0 else "",
        )
```

#### `methods/week52.py`

```python
class Week52Method(SavingsMethod):
    def __init__(self, base_amount: float = 10.0, reversed: bool = False):
        """
        base_amount: 基数，默认 10 元
        reversed: False=标准版(递增), True=反向版(递减)
        """
        self.base = base_amount
        self.reversed = reversed

    def calculate(self, monthly_income: float, history: list[Transaction]) -> SavingsPlan:
        if self.reversed:
            amounts = [(53 - n) * self.base for n in range(1, 53)]
            desc = f"反向52周存款法：第 1 周存 ¥{amounts[0]:.0f}，递减至第 52 周 ¥{amounts[51]:.0f}。"
        else:
            amounts = [n * self.base for n in range(1, 53)]
            desc = f"标准52周存款法：第 1 周存 ¥{amounts[0]:.0f}，递增至第 52 周 ¥{amounts[51]:.0f}。"

        annual = sum(amounts)
        desc += f"年累计 ¥{annual:.0f}。"

        return SavingsPlan(
            weekly_amounts=amounts,
            annual_total=annual,
            description=desc,
        )
```

#### `methods/percentage.py`

```python
class PercentageMethod(SavingsMethod):
    def __init__(self, rate: float = 0.2):
        self.rate = rate

    def calculate(self, monthly_income: float, history: list[Transaction]) -> SavingsPlan:
        monthly = monthly_income * self.rate
        annual = monthly * 12
        weekly = annual / 52
        return SavingsPlan(
            weekly_amounts=[weekly] * 52,
            annual_total=annual,
            description=f"每月储蓄收入的 {self.rate:.0%}（¥{monthly:.0f}），年累计 ¥{annual:.0f}。",
        )
```

---

## 你与 C / D 的接口

| 你需要 | 谁提供 | 何时可用 |
|---|---|---|
| `Transaction` 数据类 | C（models/transaction.py） | 第 1 周前半 |
| `Suggestion` 值对象 | C（models/suggestion.py） | 第 1 周前半 |

| 你提供 | 谁需要 | 何时需要 |
|---|---|---|
| `SavingGoalCalculator` | C（Controller 中实例化）、A/B（GUI/CLI 调用 generate_saving_plan） | 第 1 周末 |
| `MonthlyPlan` | C（Controller 返回类型）、A（GUI 展示） | 第 1 周末 |
| `BudgetRule` 接口 + 实现 | C（Controller 持有引用）、A/B | 第 2 周 |
| `SavingsMethod` 接口 + 实现 | C（Controller 持有引用）、A/B | 第 2 周 |
| `SavingsPlan` | C/A/B | 第 2 周 |

---

## 时间线

| 周 | 任务 |
|---|---|
| 第 1 周 | 实现 `SavingGoalCalculator` + `MonthlyPlan`。用假数据验证：不同 target 输出不同 plan。 |
| 第 2 周 | 实现 `BudgetRule` 族（接口 + Fixed + 503020）+ `SavingsMethod` 族（接口 + FixedAmount + Week52 + Percentage）+ `SavingsPlan` |
| 第 3 周 | 和 B 联调（用真实 CSV 数据验证储蓄倒推和预算分配结果合理） |
| 第 4 周 | 配合 A 联调（GUI 储蓄页面的展示）。可选：实现 P2 的 `EnvelopeRule`、`PayYourselfFirstRule` |

---

## 注意事项

- `SavingGoalCalculator` 的 `span_months` 用天数/30 估算，这是合理的简化。不要引入 calendar month 的复杂计算
- `Rule503020._distribute` 按历史各类别支出比例分配——无历史数据时退化为均分
- `Week52Method` 的 `base_amount` 默认 10 元，可在构造时调整
- 所有 SavingsMethod 的 `weekly_amounts` 长度固定为 52，方便 GUI 画折线图
- `MonthlyPlan` 和 `SavingsPlan` 是不同的东西：前者是"倒推需要存多少"，后者是"推荐怎么存"。不要混淆
