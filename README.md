# 个人财务管理系统

面向对象程序设计课程大作业。PySide6 写的桌面记账程序，能记收支、导入微信和支付宝的
账单 CSV、做预算、生成消费诊断和储蓄计划。

代码分在几个目录里：`models/` 放数据类，`services/` 放业务逻辑，`strategies/`、`rules/`、
`methods/` 各放一族策略。每族都是「一个抽象基类加若干实现」，由 `FinanceController` 持有，
换实现不用改调用方。

## 功能

### 交易管理

记录收支，字段有金额、收支类型、类别、支付账户、日期和备注；账户分微信、支付宝、银行卡。
列表可以按月份、类型、类别、账户筛。

账单导入支持微信支付账单和支付宝交易明细两种导出格式。程序读文件开头判断来源，再按
对应的列布局解析。某一行解析失败只跳过那一行并打印行号，其余继续导。

数据存成 JSON，下次启动读回来。

### 预算管理

按类别设月度限额，表格里同时显示已支出、剩余和超支状态。录入支出时检查该类别是否超支，
超了就告警。分配规则有两个：固定预算，和 50/30/20。

### 消费健康度诊断

诊断策略族里有 5 个实现：储蓄率、类别超支、消费结构、储蓄目标，以及把前几个加权合并的
组合策略。默认走组合策略，取前三个维度打分：

| 维度 | 算法 |
| --- | --- |
| 储蓄率 | (总收入 − 总支出) / 总收入，低于阈值扣分 |
| 类别超支 | 遍历预算类别，算出超出限额多少 |
| 消费结构 | 算基础饮食、社交饮食、娱乐、学习四类的占比，和设定的健康区间比 |

合成一份报告：等级（健康 / 预警 / 严重）、各维度得分、按优先级排的建议。

### 储蓄管理

目标是储蓄倒推：输入目标金额和计划月数，按历史收支算每月要存多少，差额按比例摊到各类别。

储蓄方法族有 3 个实现：固定金额、52 周存款法、按收入比例。52 周那个带一个开关，
可以在递增（第 N 周存 N×基数）和递减两种版本之间切。

## 环境要求

Python 3.10 以上。`services/finance_controller.py` 的类型标注用了 `str | None`，这是 3.10 才有的
写法，项目里也没有 `from __future__ import annotations` 兜底。

PySide6 6.5 以上。除此之外没有别的第三方依赖。

## 安装与运行

```bash
git clone https://github.com/DubheTony/oop2-finance-tracker.git
cd oop2-finance-tracker

python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

pip install -r requirements.txt
python main_gui.py
```

第一次添加交易或者改设置的时候，程序会在根目录生成 `transactions.json` 和 `app_settings.json`。
这两个文件只装你自己的数据，已经在 `.gitignore` 里，不会提交。

### 试一试：导入示例账单

`sample_data/` 下两个 CSV 的格式和真实导出一致，内容是程序生成的假数据：

```text
sample_data/微信支付账单_示例.csv
sample_data/支付宝交易明细_示例.csv
```

打开程序，在交易管理页点「导入CSV」，选其中一个。两个文件合计 116 条记录会全部导入，
0 条跳过，并自动按商户名分类。

## 目录结构

```text
oop2-finance-tracker/
├── main_gui.py                  # 程序入口，主窗口和四个页面的业务逻辑
├── main_gui.ui                  # Qt Designer 界面文件
├── add_transaction_dialog.ui
├── set_budget_dialog.ui
├── ui_main_gui.py               # .ui 经 pyside6-uic 生成的 Python 类
├── ui_add_transaction_dialog.py
├── ui_set_budget_dialog.py
├── requirements.txt             # 唯一依赖：PySide6
├── models/                      # Transaction、Budget、Suggestion 等数据类
├── services/                    # FinanceController、CSV 解析、分类规则、储蓄计算
├── strategies/                  # 诊断策略族
├── rules/                       # 预算规则族
├── methods/                     # 储蓄方法族
├── sample_data/                 # 示例账单
├── docs/                        # 设计文档、接口文档、UML 图
├── work_log.md                  # 早期开发记录
├── .github/workflows/           # PR 自动通过的 workflow
└── .gitignore
```

### 改完界面要重新生成代码

界面改动在 Qt Designer 里编辑 `.ui` 文件，然后重新生成 `.py`：

```bash
pyside6-uic main_gui.ui                -o ui_main_gui.py
pyside6-uic add_transaction_dialog.ui  -o ui_add_transaction_dialog.py
pyside6-uic set_budget_dialog.ui       -o ui_set_budget_dialog.py
```

## 文档

| 文件 | 内容 |
| --- | --- |
| [设计文档.md](docs/设计文档.md) | 总体设计、模块划分与职责 |
| [接口文档.md](docs/接口文档.md) | 各类与方法的签名约定 |
| [架构构思-CSV导入模块.md](docs/架构构思-CSV导入模块.md) | CSV 导入的格式适配设计 |
| [功能说明.md](docs/功能说明.md) | 功能清单与实现范围 |
| [项目描述.md](docs/项目描述.md) | 项目定位与几个差异点 |
| [知识点梳理.md](docs/知识点梳理.md) | 项目涉及的面向对象知识点 |
| [题目.md](docs/题目.md) | 课程布置的原始题目 |
| [UML类图展示.html](docs/UML类图展示.html) | UML 类图，浏览器直接打开 |

## 几处实现上的取舍

三个策略族写法一样：抽象基类加若干子类，`FinanceController` 里存基类引用。诊断 5 个实现，
预算规则 2 个，储蓄方法 3 个。

商户名到类别的映射没写在代码里，放在 `services/category_rules.json`。加一条映射不用动 Python。

CSV 导入按行容错：单行解析失败只跳该行并打印行号，不中断整个导入。

## 关于 AI 辅助

开发时用了 AI 编程助手（模型是 DeepSeek，通过 Claude Code 调用），主要做文档撰写、
代码整理和仓库规范化。

## 关于数据

仓库里的示例账单是程序生成的假数据，不含任何真实个人信息，只用来试导入功能。
真实账单不要提交到这个仓库。
