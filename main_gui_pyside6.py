# main_gui_pyside6.py — 个人财务管理系统 PySide6 图形化界面
import sys
from pathlib import Path
from datetime import date

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QTextEdit, QPushButton,
    QLabel, QLineEdit, QComboBox, QRadioButton, QButtonGroup, QDialog,
    QFormLayout, QDialogButtonBox, QMessageBox, QStatusBar, QGroupBox,
    QSplitter, QAbstractItemView,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from models.transaction import Transaction, AccountType
from models.budget import Budget
from models.diagnosis_report import HealthLevel
from services import FinanceController

# ---------- 全局控制器 + 启动时自动导入CSV ----------
ctrl = FinanceController()

_script_dir = Path(__file__).parent
_csv_files = sorted(_script_dir.glob("*.csv"))
_auto_import_log = []
for _csv_path in _csv_files:
    try:
        _count = ctrl.import_csv(str(_csv_path))
        _auto_import_log.append(f"{_csv_path.name}: {_count} 条")
    except Exception as _e:
        _auto_import_log.append(f"{_csv_path.name}: 失败({_e})")

# 初始化诊断策略
from strategies import (
    SavingRateStrategy, CategoryOverrunStrategy,
    ConsumptionStructureStrategy, CompositeDiagnosis,
)
ctrl.set_diagnosis_strategy(CompositeDiagnosis([
    (SavingRateStrategy(), 0.4),
    (CategoryOverrunStrategy(), 0.3),
    (ConsumptionStructureStrategy(), 0.3),
]))

# 规则/方法引用
from rules.fixed_budget import FixedBudgetRule
from rules.rule_503020 import Rule503020
from methods.fixed_amount import FixedAmountMethod
from methods.week52 import Week52Method
from methods.percentage import PercentageMethod


# ================================================================
# 对话框
# ================================================================

class AddTransactionDialog(QDialog):
    """添加交易对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加交易")
        self.setMinimumWidth(350)
        layout = QFormLayout(self)

        self.date_edit = QLineEdit(date.today().isoformat())
        self.amount_edit = QLineEdit()
        self.type_combo = QComboBox()
        self.type_combo.addItems(["支出", "收入"])
        self.cat_combo = QComboBox()
        self.cat_combo.addItems(["餐饮", "交通", "娱乐", "学习", "日用", "其他"])
        self.cat_combo.setEditable(True)
        self.acc_combo = QComboBox()
        self.acc_combo.addItems(["微信", "支付宝", "现金", "银行卡"])
        self.note_edit = QLineEdit()

        layout.addRow("日期 (YYYY-MM-DD):", self.date_edit)
        layout.addRow("金额:", self.amount_edit)
        layout.addRow("类型:", self.type_combo)
        layout.addRow("类别:", self.cat_combo)
        layout.addRow("账户:", self.acc_combo)
        layout.addRow("备注:", self.note_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_ok)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def _on_ok(self):
        try:
            d = date.fromisoformat(self.date_edit.text().strip())
            amount = float(self.amount_edit.text().strip())
            t_type = self.type_combo.currentText()
            cat = self.cat_combo.currentText().strip() or "其他"
            acc_map = {"微信": AccountType.WECHAT, "支付宝": AccountType.ALIPAY,
                       "现金": AccountType.CASH, "银行卡": AccountType.BANK_CARD}
            acc = acc_map.get(self.acc_combo.currentText(), AccountType.WECHAT)
            note = self.note_edit.text().strip()
            self._result = Transaction(amount, t_type, cat, acc, d, note)
            self.accept()
        except ValueError as e:
            QMessageBox.critical(self, "格式错误", str(e))

    def get_transaction(self) -> Transaction:
        return self._result


class SetBudgetDialog(QDialog):
    """设置预算对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置预算")
        self.setMinimumWidth(300)
        layout = QFormLayout(self)

        self.cat_combo = QComboBox()
        self.cat_combo.addItems(["餐饮", "交通", "娱乐", "学习", "日用", "其他"])
        self.cat_combo.setEditable(True)
        self.limit_edit = QLineEdit()

        layout.addRow("类别:", self.cat_combo)
        layout.addRow("月度限额:", self.limit_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_ok)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def _on_ok(self):
        cat = self.cat_combo.currentText().strip()
        try:
            limit = float(self.limit_edit.text().strip())
        except ValueError:
            QMessageBox.critical(self, "错误", "限额必须是数字")
            return
        self._result = Budget(cat, limit)
        self.accept()

    def get_budget(self) -> Budget:
        return self._result


# ================================================================
# Tab 页
# ================================================================

class TransactionTab(QWidget):
    """交易管理 Tab"""
    data_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        # 表格
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["日期", "类型", "类别", "金额", "账户", "备注"])
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        # 按钮行
        btn_layout = QHBoxLayout()
        btn_refresh = QPushButton("刷新列表")
        btn_refresh.clicked.connect(self.refresh)
        btn_add = QPushButton("添加交易")
        btn_add.clicked.connect(self._add)
        btn_import = QPushButton("导入CSV")
        btn_import.clicked.connect(self._import_csv)
        btn_delete = QPushButton("删除选中")
        btn_delete.clicked.connect(self._delete)

        btn_layout.addWidget(btn_refresh)
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_import)
        btn_layout.addWidget(btn_delete)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def refresh(self, month=None):
        self.table.setRowCount(0)
        txns = ctrl.get_transactions(month)
        self.table.setRowCount(len(txns))
        for i, t in enumerate(txns):
            self.table.setItem(i, 0, QTableWidgetItem(str(t.date)))
            self.table.setItem(i, 1, QTableWidgetItem(t.type))
            self.table.setItem(i, 2, QTableWidgetItem(t.category))
            self.table.setItem(i, 3, QTableWidgetItem(f"{t.amount:.2f}"))
            self.table.setItem(i, 4, QTableWidgetItem(t.account.value))
            self.table.setItem(i, 5, QTableWidgetItem(t.note))

    def _add(self):
        dlg = AddTransactionDialog(self)
        if dlg.exec() == QDialog.Accepted:
            ctrl.add_transaction(dlg.get_transaction())
            self.refresh()
            self.data_changed.emit()

    def _import_csv(self):
        from PySide6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getOpenFileName(self, "选择CSV文件", "", "CSV文件 (*.csv);;所有文件 (*)")
        if not path:
            return
        try:
            count = ctrl.import_csv(path)
            QMessageBox.information(self, "导入完成", f"成功导入 {count} 条交易")
            self.refresh()
            self.data_changed.emit()
        except Exception as e:
            QMessageBox.critical(self, "导入失败", str(e))

    def _delete(self):
        rows = set(idx.row() for idx in self.table.selectedIndexes())
        if not rows:
            QMessageBox.warning(self, "未选择", "请先选中要删除的交易行")
            return
        reply = QMessageBox.question(self, "确认删除",
                                     f"确定要删除选中的 {len(rows)} 条交易吗？此操作不可撤销。",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        month = _get_current_month()
        txns = ctrl.get_transactions(month)
        deleted = 0
        for row in sorted(rows, reverse=True):
            if row < len(txns):
                if ctrl.delete_transaction(txns[row]):
                    deleted += 1
        self.refresh(month)
        self.data_changed.emit()


class BudgetTab(QWidget):
    """预算管理 Tab"""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        # 预算表格
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["类别", "月度限额", "已支出", "剩余", "状态"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        # 按钮行
        btn_layout = QHBoxLayout()
        btn_refresh = QPushButton("刷新列表")
        btn_refresh.clicked.connect(self.refresh)
        btn_set = QPushButton("设置预算")
        btn_set.clicked.connect(self._set_budget)
        btn_layout.addWidget(btn_refresh)
        btn_layout.addWidget(btn_set)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # 预算规则区
        rule_group = QGroupBox("预算规则（P1）")
        rule_layout = QHBoxLayout(rule_group)

        rule_layout.addWidget(QLabel("规则类型:"))
        self.rule_group = QButtonGroup(self)
        self.radio_503020 = QRadioButton("50/30/20")
        self.radio_fixed = QRadioButton("固定预算")
        self.rule_group.addButton(self.radio_503020, 1)
        self.rule_group.addButton(self.radio_fixed, 2)
        self.radio_503020.setChecked(True)

        rule_layout.addWidget(self.radio_503020)
        rule_layout.addWidget(self.radio_fixed)

        rule_layout.addWidget(QLabel("  月收入:"))
        self.income_edit = QLineEdit("5000")
        self.income_edit.setMaximumWidth(80)
        rule_layout.addWidget(self.income_edit)

        btn_apply = QPushButton("应用规则")
        btn_apply.clicked.connect(self._apply_rule)
        rule_layout.addWidget(btn_apply)
        rule_layout.addStretch()

        layout.addWidget(rule_group)

    def refresh(self, month=None):
        ctrl.recalculate_budget_spent(month)
        budgets = ctrl.get_budgets()
        self.table.setRowCount(len(budgets))
        for i, b in enumerate(budgets):
            remaining = b.get_remaining()
            status = "!!超支!!" if b.is_exceeded() else "正常"
            self.table.setItem(i, 0, QTableWidgetItem(b.category))
            self.table.setItem(i, 1, QTableWidgetItem(f"{b.monthly_limit:.0f}"))
            self.table.setItem(i, 2, QTableWidgetItem(f"{b.current_spent:.0f}"))
            self.table.setItem(i, 3, QTableWidgetItem(f"{remaining:.0f}"))
            self.table.setItem(i, 4, QTableWidgetItem(status))

    def _set_budget(self):
        dlg = SetBudgetDialog(self)
        if dlg.exec() == QDialog.Accepted:
            ctrl.set_budget(dlg.get_budget())
            self.refresh()

    def _apply_rule(self):
        try:
            income = float(self.income_edit.text().strip())
        except ValueError:
            QMessageBox.critical(self, "错误", "请输入有效收入金额")
            return

        if self.radio_503020.isChecked():
            ctrl.set_budget_rule(Rule503020())
        else:
            rule = FixedBudgetRule()
            for cat, lim in [("餐饮", 1500), ("交通", 300), ("娱乐", 500), ("日用", 300), ("学习", 200)]:
                rule.set_budget(cat, lim)
            ctrl.set_budget_rule(rule)

        try:
            result = ctrl.apply_budget_rule(income)
            msg = "建议预算分配:\n"
            for cat, amt in result.items():
                msg += f"  {cat}: ¥{amt:.0f}\n"
            QMessageBox.information(self, "预算规则结果", msg)
            for cat, amt in result.items():
                if cat != "储蓄":
                    ctrl.set_budget(Budget(cat, amt))
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))


class DiagnosisTab(QWidget):
    """诊断报告 Tab"""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.text.setFont(QFont("Microsoft YaHei", 10))
        layout.addWidget(self.text)

        btn_layout = QHBoxLayout()
        btn_run = QPushButton("生成诊断报告")
        btn_run.clicked.connect(self.run)
        btn_layout.addWidget(btn_run)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def run(self, month=None):
        self.text.clear()
        months = ctrl.get_months()
        if not months:
            self.text.append("(暂无交易数据，请先导入CSV或录入交易)")
            return

        if month is None:
            month = _get_current_month() or months[-1]

        self.text.append(f"诊断月份: {month}")
        self.text.append("=" * 60)
        try:
            report = ctrl.generate_diagnosis(month)
        except RuntimeError as e:
            self.text.append(f"诊断失败: {e}")
            return

        emoji = {HealthLevel.HEALTHY: "[健康]", HealthLevel.WARNING: "[预警]", HealthLevel.CRITICAL: "[严重]"}
        self.text.append(f"综合评分: {report.overall_score:.0f}/100  {emoji.get(report.overall_level, '')}")
        self.text.append("")

        self.text.append(f"各维度明细 ({len(report.dimensions)}项):")
        self.text.append("-" * 50)
        for dim in report.dimensions:
            mark = emoji.get(dim.level, "")
            self.text.append(f"  {dim.strategy_name}: {dim.score:.0f}分  {mark}")
            if dim.suggestion:
                self.text.append(f"    -> {dim.suggestion.description}")
        self.text.append("")

        if report.suggestions:
            priority_map = {1: "高优先级", 2: "中优先级", 3: "低优先级"}
            self.text.append(f"改进建议 ({len(report.suggestions)}条，按影响金额降序):")
            self.text.append("-" * 50)
            for i, s in enumerate(report.suggestions, 1):
                label = priority_map.get(s.priority, "")
                self.text.append(f"  {i}. [{label}] {s.category}")
                self.text.append(f"     {s.description}")
                self.text.append(f"     预计月改善: ¥{s.impact_amount:.0f}")
        else:
            self.text.append("无改进建议，财务状况健康！")
        self.text.append("=" * 60)


class SavingsTab(QWidget):
    """储蓄管理 Tab"""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        # 储蓄目标倒推
        goal_group = QGroupBox("储蓄目标倒推（P0）")
        goal_layout = QVBoxLayout(goal_group)

        goal_input = QHBoxLayout()
        goal_input.addWidget(QLabel("目标金额:"))
        self.target_edit = QLineEdit("12000")
        self.target_edit.setMaximumWidth(80)
        goal_input.addWidget(self.target_edit)
        goal_input.addWidget(QLabel("  月数:"))
        self.months_edit = QLineEdit("12")
        self.months_edit.setMaximumWidth(60)
        goal_input.addWidget(self.months_edit)
        btn_goal = QPushButton("计算倒推计划")
        btn_goal.clicked.connect(self._run_goal)
        goal_input.addWidget(btn_goal)
        goal_input.addStretch()
        goal_layout.addLayout(goal_input)

        self.goal_text = QTextEdit()
        self.goal_text.setReadOnly(True)
        self.goal_text.setFont(QFont("Microsoft YaHei", 10))
        self.goal_text.setMaximumHeight(220)
        goal_layout.addWidget(self.goal_text)
        layout.addWidget(goal_group)

        # 储蓄方法
        method_group = QGroupBox("储蓄方法选择（P1）")
        method_layout = QVBoxLayout(method_group)

        method_input = QHBoxLayout()
        method_input.addWidget(QLabel("储蓄方法:"))
        self.method_group = QButtonGroup(self)
        radio_fixed = QRadioButton("固定金额")
        radio_52w = QRadioButton("52周递增")
        radio_52wr = QRadioButton("52周递减")
        radio_pct = QRadioButton("收入%")
        self.method_group.addButton(radio_fixed, 0)
        self.method_group.addButton(radio_52w, 1)
        self.method_group.addButton(radio_52wr, 2)
        self.method_group.addButton(radio_pct, 3)
        radio_fixed.setChecked(True)

        method_input.addWidget(radio_fixed)
        method_input.addWidget(radio_52w)
        method_input.addWidget(radio_52wr)
        method_input.addWidget(radio_pct)

        method_input.addWidget(QLabel("  参数:"))
        self.method_param = QLineEdit("500")
        self.method_param.setMaximumWidth(60)
        method_input.addWidget(self.method_param)

        method_input.addWidget(QLabel("  月收入:"))
        self.saving_income = QLineEdit("5000")
        self.saving_income.setMaximumWidth(80)
        method_input.addWidget(self.saving_income)

        btn_method = QPushButton("计算储蓄计划")
        btn_method.clicked.connect(self._run_method)
        method_input.addWidget(btn_method)
        method_input.addStretch()
        method_layout.addLayout(method_input)

        self.method_text = QTextEdit()
        self.method_text.setReadOnly(True)
        self.method_text.setFont(QFont("Microsoft YaHei", 10))
        method_layout.addWidget(self.method_text)
        layout.addWidget(method_group)

    def _run_goal(self):
        self.goal_text.clear()
        try:
            target = float(self.target_edit.text().strip())
            months = int(self.months_edit.text().strip())
        except ValueError:
            self.goal_text.append("请输入有效数字")
            return
        try:
            plan = ctrl.generate_saving_plan(target, months)
        except Exception as e:
            self.goal_text.append(f"计算失败: {e}")
            return

        self.goal_text.append("=" * 55)
        self.goal_text.append(f"  储蓄目标: ¥{target:.0f} / {months} 个月")
        self.goal_text.append(f"  每月需存: ¥{plan.required_monthly_saving:.0f}")
        self.goal_text.append(f"  当前自然月结余: ¥{plan.current_natural_saving:.0f}")
        self.goal_text.append(f"  每月需额外削减: ¥{plan.extra_cut_needed:.0f}")
        self.goal_text.append("-" * 55)
        if plan.category_cuts:
            self.goal_text.append("  建议削减:")
            for cat, cut in plan.category_cuts.items():
                self.goal_text.append(f"    {cat}: ¥{cut:.0f}")
        else:
            self.goal_text.append("  无需额外削减")
        self.goal_text.append("-" * 55)
        self.goal_text.append("  建议:")
        for s in plan.suggestions:
            self.goal_text.append(f"    [{s.priority}] {s.description}")
        self.goal_text.append("=" * 55)

    def _run_method(self):
        self.method_text.clear()
        try:
            income = float(self.saving_income.text().strip())
            param = float(self.method_param.text().strip())
        except ValueError:
            self.method_text.append("请输入有效数字")
            return

        method_id = self.method_group.checkedId()
        if method_id == 0:
            method = FixedAmountMethod(param)
        elif method_id == 1:
            method = Week52Method(base_amount=param, reversed=False)
        elif method_id == 2:
            method = Week52Method(base_amount=param, reversed=True)
        elif method_id == 3:
            method = PercentageMethod(rate=param / 100.0)
        else:
            return

        ctrl.set_savings_method(method)
        try:
            plan = ctrl.get_savings_plan(income)
        except Exception as e:
            self.method_text.append(f"计算失败: {e}")
            return

        self.method_text.append(f"方法说明: {plan.description}")
        self.method_text.append(f"年储蓄总额: ¥{plan.annual_total:.0f}")
        self.method_text.append("-" * 55)
        self.method_text.append("52周储蓄计划（前12周）:")
        for i in range(12):
            self.method_text.insertPlainText(f"  第{i+1:>2}周: ¥{plan.weekly_amounts[i]:>8.0f}")
            if i % 3 == 2:
                self.method_text.append("")
        self.method_text.append("  ...")
        for i in range(48, 52):
            self.method_text.insertPlainText(f"  第{i+1:>2}周: ¥{plan.weekly_amounts[i]:>8.0f}")
            if i % 3 == 2:
                self.method_text.append("")
        self.method_text.append("")


class AlertTab(QWidget):
    """预警消息 Tab"""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.text.setFont(QFont("Microsoft YaHei", 10))
        layout.addWidget(self.text)

        btn_layout = QHBoxLayout()
        btn_refresh = QPushButton("刷新")
        btn_refresh.clicked.connect(self.refresh)
        btn_check = QPushButton("检测预警")
        btn_check.clicked.connect(self._check)
        btn_clear = QPushButton("清空预警")
        btn_clear.clicked.connect(self._clear)

        btn_layout.addWidget(btn_refresh)
        btn_layout.addWidget(btn_check)
        btn_layout.addWidget(btn_clear)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def refresh(self):
        self.text.clear()
        alerts = ctrl.get_alert_messages()
        if not alerts:
            self.text.append("(暂无预警 — 请先设置预算，然后点击「检测预警」或运行诊断)")
        else:
            for a in alerts:
                self.text.append(a)

    def _check(self):
        month = _get_current_month()
        ctrl.recalculate_budget_spent(month)
        ctrl.check_budget_alerts()
        self.refresh()

    def _clear(self):
        ctrl.clear_alerts()
        self.refresh()


# ================================================================
# 主窗口
# ================================================================

# 模块级变量，供 Tab 页获取当前选中月份
def _get_current_month():
    m = current_month()
    return m if m else None

current_month = lambda: None


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("个人财务管理系统 — PySide6 图形化检查")
        self.resize(1100, 750)
        self.setMinimumSize(900, 600)

        # 中央 tabs
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.txn_tab = TransactionTab()
        self.budget_tab = BudgetTab()
        self.diag_tab = DiagnosisTab()
        self.saving_tab = SavingsTab()
        self.alert_tab = AlertTab()

        self.tabs.addTab(self.txn_tab, "交易管理")
        self.tabs.addTab(self.budget_tab, "预算管理")
        self.tabs.addTab(self.diag_tab, "诊断报告")
        self.tabs.addTab(self.saving_tab, "储蓄管理")
        self.tabs.addTab(self.alert_tab, "预警消息")

        # 工具栏：月份选择
        toolbar = self.addToolBar("月份")
        toolbar.addWidget(QLabel("月份: "))
        self.month_combo = QComboBox()
        self.month_combo.setMinimumWidth(100)
        self.month_combo.currentTextChanged.connect(self._on_month_changed)
        toolbar.addWidget(self.month_combo)

        btn_refresh_month = QPushButton("刷新月份")
        btn_refresh_month.clicked.connect(self._refresh_months)
        toolbar.addWidget(btn_refresh_month)

        # 全局 current_month
        global current_month
        current_month = lambda: self.month_combo.currentText()

        # 数据变更时刷新月份列表
        self.txn_tab.data_changed.connect(self._refresh_months)

        # 状态栏
        self.statusBar().showMessage(
            f"自动导入: {'; '.join(_auto_import_log)}" if _auto_import_log
            else "就绪（未找到CSV文件，可手动导入或添加交易）"
        )

        # 初始加载
        self._refresh_months()
        self.txn_tab.refresh()
        self.budget_tab.refresh()
        self.alert_tab.refresh()

    def _refresh_months(self):
        months = ctrl.get_months()
        current = self.month_combo.currentText()
        self.month_combo.clear()
        self.month_combo.addItems(months)
        if current in months:
            self.month_combo.setCurrentText(current)
        elif months:
            self.month_combo.setCurrentText(months[-1])

    def _on_month_changed(self, month):
        if month:
            self.txn_tab.refresh(month)
            self.budget_tab.refresh(month)
            self.statusBar().showMessage(f"当前月份: {month}")


# ================================================================
# 启动
# ================================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
