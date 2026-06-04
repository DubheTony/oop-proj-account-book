# 工作日志

## 2026-06-04: main_gui_pyside6.py → .ui 文件拆分

**操作**: 将 PySide6 硬编码 UI 改写为 Qt Designer 兼容的 .ui 文件 + loader 模式。

**做法**:
- 创建 `main_gui.ui`（主窗口5个Tab）、`add_transaction_dialog.ui`、`set_budget_dialog.ui`
- 创建 `main_gui_ui_loader.py` 作为加载器，用 QUiLoader 加载 .ui 并衔接业务逻辑
- 原 `main_gui_pyside6.py` 保持不变

**踩坑**: PySide6 QUiLoader 不支持 `<buttongroups>` XML 元素，改为 loader 中用 `QButtonGroup()` 代码创建

**结果**: 三个 .ui 文件可用 Qt Designer 可视化编辑；loader 包含全部业务逻辑，与原版行为一致
