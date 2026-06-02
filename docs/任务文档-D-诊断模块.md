# 任务文档 — D（诊断策略模块）

> 本文档只包含你需要关心的内容。全局设计见 `设计文档.md`，接口契约见 `接口文档.md`。

---

## 你的职责

1. **接口定义**：`DiagnosticStrategy` 抽象基类
2. **P0 三个策略实现**：`SavingRateStrategy`、`CategoryOverrunStrategy`、`ConsumptionStructureStrategy`
3. **诊断结果类**：`DiagnosisReport`、`DimensionDetail`、`HealthLevel` 枚举
4. **P1 复合策略**：`CompositeDiagnosis`（加权聚合）

---

## 你需要交付的文件

```
models/
└── diagnosis_report.py    # DiagnosisReport + DimensionDetail + HealthLevel

strategies/
├── __init__.py
├── diagnostic_strategy.py  # DiagnosticStrategy 接口
├── saving_rate.py          # SavingRateStrategy
├── category_overrun.py     # CategoryOverrunStrategy
├── consumption_structure.py # ConsumptionStructureStrategy
└── composite.py            # CompositeDiagnosis (P1)
```

---

## P0 实现详规

### 文件 1：`strategies/diagnostic_strategy.py`

```python
from abc import ABC, abstractmethod
from models.transaction import Transaction
from models.budget import Budget
from models.diagnosis_report import DiagnosisReport


class DiagnosticStrategy(ABC):
    @abstractmethod
    def diagnose(
        self,
        transactions: list[Transaction],
        budgets: list[Budget]
    ) -> DiagnosisReport:
        ...
```

### 文件 2：`models/diagnosis_report.py`

```python
from dataclasses import dataclass, field
from enum import Enum
from models.suggestion import Suggestion


class HealthLevel(Enum):
    HEALTHY = "健康"
    WARNING = "预警"
    CRITICAL = "严重"


@dataclass
class DimensionDetail:
    strategy_name: str
    score: float            # 0~100
    level: HealthLevel
    suggestion: Suggestion | None  # None 表示该维度无建议


@dataclass
class DiagnosisReport:
    overall_level: HealthLevel
    overall_score: float
    dimensions: list[DimensionDetail] = field(default_factory=list)
    suggestions: list[Suggestion] = field(default_factory=list)

    def __post_init__(self):
        # 确保 suggestions 按 impact_amount 降序
        self.suggestions.sort(key=lambda s: s.impact_amount, reverse=True)
```

### 文件 3：`strategies/saving_rate.py`

**算法**：
```
total_income = sum(t.amount for t in transactions if t.is_income())
total_expense = sum(t.amount for t in transactions if t.is_expense())

if total_income == 0:
    saving_rate = 0
else:
    saving_rate = (total_income - total_expense) / total_income

score = min(saving_rate / 0.3 * 100, 100)

if saving_rate < 0:
    level = CRITICAL
    desc = "入不敷出！本月支出超过收入，正在消耗储蓄或负债。"
elif saving_rate < 0.1:
    level = WARNING
    desc = f"储蓄率仅 {saving_rate:.0%}，低于建议下限 10%。建议控制弹性支出。"
elif saving_rate < 0.2:
    level = WARNING
    desc = f"储蓄率 {saving_rate:.0%}，接近健康线。建议提升至 20% 以上。"
else:
    level = HEALTHY
    desc = f"储蓄率 {saving_rate:.0%}，财务状态健康。继续保持。"

monthly_saving = total_income - total_expense
suggestion = Suggestion(
    priority=2 if level != HEALTHY else 3,
    impact_amount=max(0, total_income * 0.2 - monthly_saving),
    category="全部",
    description=desc + (
        f"月结余 ¥{monthly_saving:.0f}，建议月储蓄目标 ¥{total_income*0.2:.0f}。"
        if level != HEALTHY else ""
    ),
)

return DiagnosisReport(
    overall_level=level,
    overall_score=score,
    dimensions=[DimensionDetail("储蓄率诊断", score, level, suggestion)],
    suggestions=[suggestion] if level != HEALTHY else [],
)
```

### 文件 4：`strategies/category_overrun.py`

**算法**：
```
遍历所有 budgets：
  若 budget.is_exceeded():
    overrun_ratio = (budget.current_spent - budget.monthly_limit) / budget.monthly_limit
    over_amount = budget.current_spent - budget.monthly_limit
    记录该类别超支信息

若没有超支类别：
  score = 100, level = HEALTHY, 无建议
否则：
  max_overrun_ratio = max(所有超支类别的 overrun_ratio)
  score = max(0, 100 - max_overrun_ratio * 100)
  level = CRITICAL if max_overrun_ratio > 0.3 else WARNING

  为每个超支类别生成 Suggestion:
    priority=1, impact_amount=over_amount, category=category
    description="该类别超支 ¥{over_amount:.0f}（限额 ¥{limit:.0f}，已支出 ¥{spent:.0f}），超支 {overrun_ratio:.0%}。"
```

**要点**：
- 遍历的是 `budgets` 列表，不是交易列表
- 如果 `budgets` 为空（未设置预算），score=100, level=HEALTHY, 无建议
- 同一维度下多个类别超支 → 每个都生成 Suggestion

### 文件 5：`strategies/consumption_structure.py`

**改造版恩格尔系数**（学生适配）：

```
步骤1: 分类汇总
  basic_food = sum(t.amount for t in transactions
      if t.is_expense() and t.category == "餐饮" and ("食堂" in t.note or "食材" in t.note or "超市" in t.note))
  social_food = sum(t.amount for t in transactions
      if t.is_expense() and t.category == "餐饮" and ("外卖" in t.note or "聚餐" in t.note or not _is_basic(t)))
  entertainment = sum(t.amount for t in transactions if t.is_expense() and t.category == "娱乐")
  study = sum(t.amount for t in transactions if t.is_expense() and t.category == "学习")
  total_expense = sum(t.amount for t in transactions if t.is_expense())

步骤2: 计算占比
  basic_ratio = basic_food / total_expense
  social_ratio = social_food / total_expense
  entertainment_ratio = entertainment / total_expense
  study_ratio = study / total_expense

步骤3: 与健康区间比较
  健康区间：basic<=25%, social<=15%, entertainment<=15%, study>=5%

  对每个维度：
    if 比率 超出 健康上限:
      deviation = 比率 - 上限
      生成 Suggestion（含具体金额和优化建议）
    score 根据偏差扣分

步骤4: 综合
  overall_score = min(各维度得分)
  或 各维度得分取平均
```

**简化处理**（如果备注字段不足以区分基础/社交饮食）：
- 先按类别区分：`category == "学习"` → study，`category == "娱乐"` → entertainment
- 餐饮无法细分时：全部归入 `food_ratio`，健康区间设为 ≤30%（学生整体的合理上限）
- 总支出为 0 → score=100, HEALTHY

**核心**：Suggestion 中的数字（超了多少、建议省多少）从数据算出来，不是硬编码。

---

## P1 实现详规

### 文件 6：`strategies/composite.py`

```python
class CompositeDiagnosis(DiagnosticStrategy):
    def __init__(self, strategies: list[tuple[DiagnosticStrategy, float]]):
        """
        strategies: [(strategy, weight), ...]
        权重之和应为 1.0
        """
        self._strategies = strategies

    def add_strategy(self, strategy: DiagnosticStrategy, weight: float):
        self._strategies.append((strategy, weight))

    def diagnose(self, transactions, budgets) -> DiagnosisReport:
        # 运行全部子策略
        reports = []
        for strategy, weight in self._strategies:
            report = strategy.diagnose(transactions, budgets)
            reports.append((report, weight))

        # 加权综合分
        overall_score = sum(r.overall_score * w for r, w in reports)

        # 综合等级
        if overall_score >= 80:
            overall_level = HealthLevel.HEALTHY
        elif overall_score >= 50:
            overall_level = HealthLevel.WARNING
        else:
            overall_level = HealthLevel.CRITICAL

        # 汇总所有维度和建议
        all_dimensions = []
        all_suggestions = []
        for r, w in reports:
            all_dimensions.extend(r.dimensions)
            all_suggestions.extend(r.suggestions)

        # 建议去重（同 category + 同 description 只保留一个）
        unique = _dedup_suggestions(all_suggestions)

        return DiagnosisReport(
            overall_level=overall_level,
            overall_score=overall_score,
            dimensions=all_dimensions,
            suggestions=sorted(unique, key=lambda s: s.impact_amount, reverse=True),
        )
```

---

## 你与 C 的接口

| 你需要 | C 提供（models/） | 何时可用 |
|---|---|---|
| `Transaction` 数据类 | `models/transaction.py` | 第 1 周前半 |
| `Budget` 数据类 | `models/budget.py` | 第 1 周前半 |
| `Suggestion` 值对象 | `models/suggestion.py` | 第 1 周前半 |

| 你提供 | 谁需要 | 何时需要 |
|---|---|---|
| `DiagnosisReport` + `HealthLevel` | C（Controller 返回类型）、A（GUI 展示） | 第 2 周 |
| `DiagnosticStrategy` 接口 | C（Controller 持有引用） | 第 1 周末 |
| 3 个具体策略 | C/B（设置到 Controller 中测试） | 第 2 周 |

---

## 时间线

| 周 | 任务 |
|---|---|
| 第 1 周 | 定义 `DiagnosticStrategy` 接口 + `DiagnosisReport` + `HealthLevel` + `DimensionDetail`。三个策略的算法伪代码和数据结构对齐 |
| 第 2 周 | 实现 `SavingRateStrategy`、`CategoryOverrunStrategy`、`ConsumptionStructureStrategy`。每个策略独立单元测试（造一组假 transactions/budgets，验证输出合理） |
| 第 3 周 | 实现 `CompositeDiagnosis` + 和 B 联调（用 CSV 真实数据跑诊断） |
| 第 4 周 | 配合 A 调整报告展示格式，参与答辩准备 |

---

## 注意事项

- 每个策略的 `diagnose()` 是纯函数：不修改传入的 transactions/budgets，不依赖外部状态
- `score` 统一为 0~100，方便 Composite 加权聚合
- 边界情况：
  - 空交易列表 → 所有 ratio=0 → score=100, HEALTHY
  - 全收入无支出 → score=100
  - 全支出无收入 → saving_rate 为负 → CRITICAL
- `ConsumptionStructureStrategy` 的餐饮分类依赖备注字段做"基础/社交"区分。如果 CSV 数据中没有足够信息，简化为"餐饮总占比 ≤30%"
- 策略类的 `__init__` 可以接收可配置参数（如阈值），方便答辩时调参演示
