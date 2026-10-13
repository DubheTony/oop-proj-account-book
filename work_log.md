# 工作日志

## 2026-06-04: main_gui_pyside6.py → .ui 文件拆分

**操作**: 将 PySide6 硬编码 UI 改写为 Qt Designer 兼容的 .ui 文件 + loader 模式。

**做法**:
- 创建 `main_gui.ui`（主窗口5个Tab）、`add_transaction_dialog.ui`、`set_budget_dialog.ui`
- 创建 `main_gui_ui_loader.py` 作为加载器，用 QUiLoader 加载 .ui 并衔接业务逻辑
- 原 `main_gui_pyside6.py` 保持不变

**踩坑**: PySide6 QUiLoader 不支持 `<buttongroups>` XML 元素，改为 loader 中用 `QButtonGroup()` 代码创建

**结果**: 三个 .ui 文件可用 Qt Designer 可视化编辑；loader 包含全部业务逻辑，与原版行为一致

## 2026-06-04: 五人分工文件夹生成

**操作**：在桌面 `<桌面>\coursework-分工\` 创建 5 个文件夹，按设计文档中的五人分工分配代码文件和需求文档。

**分工依据**（来自设计文档第六章）：
| 编号 | 文件夹 | 核心职责 |
| A | A-GUI | PySide6 界面 + 信号槽绑定 |
| B | B-CSV集成 | CSV 导入 + 类别标准化 |
| C | C-核心实体 | Transaction/Budget/Suggestion + FinanceController |
| D | D-诊断模块 | DiagnosticStrategy + 4个策略 + DiagnosisReport |
| E | E-预算储蓄 | SavingGoalCalculator + BudgetRule族 + SavingsMethod族 |

**要求文档特点**：
- 每个文档含：文件清单、全流程位置、代码语法要点、函数功能详解
- 自检问答（Grill Section）：每份 10-15 个问题覆盖全流程理解/语法/功能/边界/设计判断
- 检查清单：可逐项勾选的学习目标

**关键设计决策**：
- 每个人除了自己负责的文件，还复制了共享的 models/ 依赖文件
- 每个人复制了 docs/ 中的设计文档和接口文档
- 要求文档中的 grill 问题从代码实际逻辑出发，不是模板句

### 2026-06-04 补充：为每个要求文档新增"面向对象基本原理体现"章节

**操作**：在每个要求文档中新增第五节，分析该人负责代码如何体现 OOP 四大原则。

**各人 OOP 侧重点**：
| 人员 | 主要体现 | 次要体现 |
|---|---|---|
| A-GUI | 继承（QMainWindow/QDialog子类化） + 封装（_private方法） | 多态（信号/槽机制） |
| B-CSV | 封装（_private函数） + 抽象（import_csv对外接口） | 数据驱动（规则与代码分离） |
| C-核心实体 | 封装（_private属性 + .copy()防御性复制） + 抽象（API简化） | 继承（Enum） + 多态（鸭子类型策略引用） |
| D-诊断模块 | 抽象（ABC） + 继承（4个策略子类） + 多态（同一diagnose()不同行为） | 方法覆盖 |
| E-预算储蓄 | 抽象（2个ABC接口） + 继承（2个独立继承树） + 多态（切换策略不改Controller） | 封装（SavingGoalCalculator内部逻辑） |

**设计考量**：
- 每个 OOP 概念都关联到具体的代码行和教材作业编号（作业7-封装/8-继承/9-多态）
- 对不够OOP的地方给出建设性批评（如实指出B是最不OOP的但恰恰是对的）
- D和E都用了策略模式，强调对比和复用
