# 个人财务管理系统

面向对象程序设计课程大作业。一个基于 **PySide6** 的桌面记账应用：支持多账户收支记录、
微信/支付宝账单 CSV 导入、消费健康度诊断、预算管理和储蓄规划。

项目重点不在功能堆砌，而在**用面向对象的方式组织代码**：三个可替换的策略族（诊断策略、
预算规则、储蓄方法）共享同一套 Strategy 模式骨架，实体之间通过控制器解耦。

---

## 功能

### 交易管理
- 记录收支：金额、类型（收入/支出）、类别、支付账户、日期、备注
- 支付账户分为微信 / 支付宝 / 银行卡
- **CSV 账单导入**：自动识别微信支付账单与支付宝交易明细两种导出格式
- 按月份、类型、类别、账户筛选交易列表
- 数据持久化到 JSON，下次启动自动载入

### 预算管理
- 按类别设定月度限额，实时显示已支出、剩余与超支状态
- 可在录入支出时自动检测超支并告警
- 两种预算规则（Strategy 模式）：**50/30/20 法则**、**固定预算**

### 消费健康度诊断
三个诊断维度，各自是一个策略对象，可加权组合成综合评分：
- **储蓄率**：`(总收入 − 总支出) / 总收入`，低于阈值告警
- **类别超支**：遍历预算类别，输出超支明细
- **消费结构**：分析基础饮食 / 社交饮食 / 娱乐 / 学习四类占比，与健康区间比较

输出统一的诊断报告：综合等级（健康 / 预警 / 严重）、各维度评分、按优先级排列的建议。

### 储蓄管理
- **目标倒推**：输入目标金额与计划月数，结合历史收支逆推每月所需储蓄额，
  差额按可配置比例分摊到各类别
- **储蓄方法**（Strategy 模式）：固定金额法、52 周递增法、52 周递减法、收入比例法

---

## 环境要求

- Python 3.9+
- PySide6 6.5+（唯一的第三方依赖）

## 安装与运行

```bash
git clone <仓库地址>
cd oop2-finance-tracker

python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

pip install -r requirements.txt
python main_gui.py
```

首次启动时程序会自动创建 `transactions.json` 与 `app_settings.json` 用于保存数据，
这两个文件属于运行时产物，已在 `.gitignore` 中忽略。

### 试一试：导入示例账单

`sample_data/` 下有两份**格式与真实导出一致**的示例账单（内容为程序生成的合成数据）：

```
sample_data/微信支付账单_示例.csv
sample_data/支付宝交易明细_示例.csv
```

在「交易管理」选项卡点击 **导入CSV**，选中其中之一即可看到完整的导入与自动分类效果。

---

## 目录结构

```
oop2-finance-tracker/
├── main_gui.py                  # 程序入口（主窗口与各选项卡的业务逻辑）
├── main_gui.ui                  # Qt Designer 界面文件
├── add_transaction_dialog.ui
├── set_budget_dialog.ui
├── ui_main_gui.py               # ← 由 .ui 经 pyside6-uic 生成的 Python 类
├── ui_add_transaction_dialog.py #    （生成产物，一并提交，方便直接运行）
├── ui_set_budget_dialog.py
├── models/                      # 实体：Transaction、Budget、Suggestion、
│                                #       DiagnosisReport、MonthlyPlan、SavingsPlan
├── services/                    # 业务层：FinanceController（总控）
│                                #       csv_importer（账单解析）
│                                #       category_normalizer + category_rules.json（分类规则）
│                                #       saving_calculator（储蓄计算）
├── strategies/                  # 诊断策略族（Strategy 模式）
├── rules/                       # 预算规则族（Strategy 模式）
├── methods/                     # 储蓄方法族（Strategy 模式）
├── sample_data/                 # 合成示例账单
└── docs/                        # 设计文档、接口文档、UML 类图与开发日志
```

### 修改界面后重新生成代码

界面改动请在 Qt Designer 里编辑 `.ui` 文件，然后重新生成对应的 `.py`：

```bash
pyside6-uic main_gui.ui                -o ui_main_gui.py
pyside6-uic add_transaction_dialog.ui  -o ui_add_transaction_dialog.py
pyside6-uic set_budget_dialog.ui       -o ui_set_budget_dialog.py
```

---

## 文档

`docs/` 目录下：

| 文件 | 内容 |
|---|---|
| [设计文档.md](docs/设计文档.md) | 总体设计、模块划分与职责 |
| [接口文档.md](docs/接口文档.md) | 各类与方法的签名约定 |
| [架构构思-CSV导入模块.md](docs/架构构思-CSV导入模块.md) | CSV 导入的格式适配设计 |
| [uml-class-diagram.md](docs/uml-class-diagram.md) | UML 类图（文字版） |
| [UML类图展示.html](docs/UML类图展示.html) | UML 类图（可直接用浏览器打开） |
| [知识点梳理.md](docs/知识点梳理.md) | 项目涉及的面向对象知识点 |
| [工作日志.md](docs/工作日志.md) | 开发过程记录 |
| 任务文档-A~E.md | 按模块拆分的学习与答辩材料 |

---

## 代码组织上的几个设计选择

- **三个策略族统一骨架**：诊断策略、预算规则、储蓄方法都遵循「抽象基类 + 多个具体实现 +
  由控制器持有」的写法。切换具体策略不需要改动调用方，这是多态在项目里的主要落点。
- **规则与代码分离**：分类映射规则放在 `services/category_rules.json`，
  扩充映射不需要改 Python 代码。
- **容错优先的导入器**：CSV 解析中单行出错只跳过该行并打印提示，不中断整个导入。

---

## 关于 AI 辅助

本项目在开发过程中使用了 AI 编程助手（底层模型为 DeepSeek，经由 Claude Code 命令行工具调用），
主要用于文档撰写、代码整理与仓库规范化。

---

## 关于数据

仓库中的示例账单（`sample_data/`）为**程序生成的合成数据**，不含任何真实个人信息，
仅用于演示导入与分类功能。真实账单请勿提交到公开仓库。
