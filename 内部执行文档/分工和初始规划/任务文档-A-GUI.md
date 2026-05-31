# 任务文档 — A（GUI — PySide6）

> 本文档只包含你需要关心的内容。全局设计见 `设计文档.md`，接口契约见 `接口文档.md`。

---

## 你的职责

1. **PySide6 全部界面**：主窗口、交易录入页、诊断报告页、预算设置页、储蓄计划页
2. **图表绘制**（P1）：月度消费趋势折线图、类别占比饼图
3. **信号/槽绑定**：连接 GUI 控件与 `FinanceController` 方法

---

## 你需要交付的文件

```
gui/
├── __init__.py
├── main_window.py         # 主窗口（导航容器）
├── transaction_page.py    # 交易录入 + 交易列表
├── diagnosis_page.py      # 诊断报告展示
├── budget_page.py         # 预算设置
├── saving_page.py         # 储蓄计划展示
└── charts.py              # matplotlib 图表（P1）
```

---

## 各页面要求

### 3.1 主窗口（main_window.py）

- 顶部导航栏或侧边 tab 切换：交易管理 | 诊断报告 | 预算设置 | 储蓄计划
- 底部状态栏显示最新一条告警消息（如有）
- 接收一个 `FinanceController` 实例，传递给各子页面

```python
class MainWindow(QMainWindow):
    def __init__(self, controller: FinanceController):
        ...
        self._tabs = QTabWidget()
        self._tabs.addTab(TransactionPage(controller), "交易管理")
        self._tabs.addTab(DiagnosisPage(controller), "诊断报告")
        self._tabs.addTab(BudgetPage(controller), "预算设置")
        self._tabs.addTab(SavingPage(controller), "储蓄计划")
        self.setCentralWidget(self._tabs)

        # 状态栏显示最新告警
        self._status_bar = self.statusBar()
        self._refresh_alert_status()
```

### 3.2 交易录入页（transaction_page.py）

**功能**：
- 表单录入：金额（QDoubleSpinBox）、类型（QComboBox: 收入/支出）、类别（QComboBox: 餐饮/交通/娱乐/学习/日用/其他）、账户（QComboBox: 微信/支付宝/现金/银行卡）、日期（QDateEdit，默认今天）、备注（QLineEdit）
- "添加交易"按钮 → 创建 `Transaction` → 调用 `controller.add_transaction(t)`
- 交易列表（QTableWidget）：显示所有交易，支持按日期/类别/账户筛选
- "导入CSV"按钮 → QFileDialog 选文件 → 调用 `controller.import_csv(path)` → 弹窗显示导入条数 → 刷新列表
- 添加交易后自动刷新告警状态栏

**控件建议**：
```
┌──────────────────────────────────────────┐
│  金额: [____]  类型: [收入▼]  账户: [微信▼] │
│  类别: [餐饮▼]  日期: [2025-03-15]         │
│  备注: [________________]                │
│  [添加交易]  [导入CSV]                    │
├──────────────────────────────────────────┤
│  筛选: 类别[全部▼] 账户[全部▼] 月份[3月▼]  │
│  ┌────────────────────────────────────┐  │
│  │ 日期   │金额  │类型│类别│账户│备注   │  │
│  │ 03-15  │35.5 │支出│餐饮│微信│食堂   │  │
│  │ 03-15  │2000 │收入│其他│银行卡│生活费│  │
│  │ ...    │     │    │    │    │      │  │
│  └────────────────────────────────────┘  │
└──────────────────────────────────────────┘
```

### 3.3 诊断报告页（diagnosis_page.py）

**功能**：
- "生成诊断"按钮 → 调用 `controller.generate_diagnosis()` → 展示 `DiagnosisReport`
- 综合评分：大号数字 + HealthLevel 颜色标签（绿色 HEALTHY / 黄色 WARNING / 红色 CRITICAL）
- 各维度明细（QGroupBox 列表）：每个维度显示策略名、得分、等级、建议文本
- 建议列表按 priority 分组（高优红色边框、中优黄色、低优灰色），impact_amount 标注
- P1：如果 controller 设置了 CompositeDiagnosis，显示各子策略权重

**布局建议**：
```
┌──────────────────────────────────────────┐
│  [生成诊断]        综合评分: 62  WARNING  │
├──────────────────────────────────────────┤
│  ▸ 储蓄率诊断               得分:80 HEALTHY│
│    当前储蓄率 25%，月结余 ¥600。保持现状。 │
│  ▸ 消费结构分析             得分:55 WARNING│
│    社交饮食占比 22%，超过建议上限 15%。     │
│    月均外卖+聚餐 ¥880，每周减少 1 次聚餐     │
│    (约¥60)，月省 ¥240，年省 ¥2880。         │
│  ▸ 类别超支检查             得分:45 CRITICAL│
│    娱乐超出预算 ¥120（限额 ¥300，已花 ¥420）│
├──────────────────────────────────────────┤
│  🔴 高优先级                             │
│  · 娱乐月超支 ¥120，建议削减至预算内        │
│  🟡 中优先级                             │
│  · 社交饮食占比偏高，月均可优化 ¥240        │
└──────────────────────────────────────────┘
```

### 3.4 预算设置页（budget_page.py）

**功能**：
- 预算列表（QTableWidget）：类别 | 月度限额 | 已支出 | 剩余 | 进度条
- "添加/修改预算"按钮 → 弹窗输入类别、限额
- P1：预算规则选择（QComboBox: 手动设置 / 50-30-20法则）+ "应用"按钮 → 调用 `controller.apply_budget_rule(income)`
- 预算超支行红色高亮

### 3.5 储蓄计划页（saving_page.py）

**功能**：
- 储蓄倒推：输入框（目标金额、计划月数）+ "计算"按钮 → 调用 `controller.generate_saving_plan(target, months)`
- 展示 `MonthlyPlan`：自然月结余、所需月储蓄、差额、各类别削减建议
- P1：储蓄方法选择（QComboBox: 固定金额 / 52周存款 / 比例储蓄）+ 参数输入 + "生成计划"按钮 → 调用 `controller.get_savings_plan(income)`
- 52 周存款法展示 52 周存款曲线（P1 charts）

### 3.6 图表（charts.py，P1）

使用 `matplotlib` + `FigureCanvasQTAgg` 嵌入 PySide6：

- **月度消费趋势折线图**：x 轴 = 月份，y 轴 = 金额。两条线：总支出（红色）、总收入（绿色）
- **类别占比饼图**：当前筛选月份的各类别支出占比
- **52 周存款曲线**（如有）：x 轴 = 周数，y 轴 = 累计存款

```python
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self):
        self.fig = Figure(figsize=(5, 3), dpi=100)
        super().__init__(self.fig)
```

---

## 你与后端的接口

你只需要和 `FinanceController` 交互。所有方法签名见 `接口文档.md` 第六章。

**第 1 周（后端未就绪）**：
- 用硬编码假数据设计界面布局
- 写一个 `FakeController` 或直接构造假的 `Transaction` 列表来填充表格

```python
# 第 1 周测试用
class FakeController:
    def get_transactions(self):
        return [
            Transaction(35.5, "支出", "餐饮", AccountType.WECHAT, date(2025,3,15), "食堂午饭"),
            Transaction(2000, "收入", "其他", AccountType.BANK_CARD, date(2025,3,15), "生活费"),
        ]
    def get_budgets(self): ...
    def generate_diagnosis(self): ...
    # ... stub 方法
```

第 2 周替换为真实的 `FinanceController`。

---

## 时间线

| 周 | 任务 |
|---|---|
| 第 1 周 | 学习 PySide6 基础（如果不会）；用 `FakeController` 设计所有页面布局；确保控件交互正常 |
| 第 2 周 | 替换为真实 `FinanceController`；实现数据绑定和信号/槽；交易录入和诊断报告功能完整 |
| 第 3 周 | 图表绑定（matplotlib 嵌入）；预算规则/储蓄方法的 P1 页面功能；美化样式 |
| 第 4 周 | 最终打磨、bug 修复、配合联调 |

---

## 注意事项

- PySide6 的信号/槽用 `@Slot()` 装饰器或无装饰器的自动连接均可
- 表格数据更新后调用 `table.viewport().update()` 或 `model.layoutChanged.emit()`
- `FinanceController` 的方法返回数据副本（`list.copy()`），可以安全读取
- 图片嵌入用 `matplotlib.backends.backend_qtagg.FigureCanvasQTAgg`
- 长文本建议用 `QTextEdit`（只读模式）而非 `QLabel`，以支持滚动
