# main_gui.py — 个人财务管理系统 PySide6 图形界面
# UI 由 Qt Designer 制作 .ui 文件，经 pyside6-uic 编译为 Python 类
# 用法: python main_gui.py
import sys
from pathlib import Path
from datetime import date

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QDialog, QMessageBox, QFileDialog,
    QTableWidgetItem, QComboBox, QPushButton, QLabel, QButtonGroup,
)

from models.transaction import Transaction, AccountType
from models.budget import Budget
from models.diagnosis_report import HealthLevel
from services import FinanceController
from services.category_normalizer import STANDARD_CATEGORIES

# 生成的 UI 类
from ui_main_gui import Ui_MainWindow
from ui_add_transaction_dialog import Ui_AddTransactionDialog
from ui_set_budget_dialog import Ui_SetBudgetDialog

# ====== 全局控制器 + 启动时加载持久化数据 ======
ctrl = FinanceController()

_script_dir = Path(__file__).parent
_settings_path = _script_dir / "app_settings.json"
_transactions_path = _script_dir / "transactions.json"

# 加载设置
_startup_log = []
try:
    ctrl.load_settings(str(_settings_path))
    _startup_log.append("设置已加载")
except Exception as _e:
    _startup_log.append(f"设置加载失败({_e})")

# 加载交易记录
try:
    _txn_count = ctrl.load_transactions(str(_transactions_path))
    if _txn_count > 0:
        _startup_log.append(f"交易记录: {_txn_count} 条(来自JSON)")
    else:
        _startup_log.append("暂无交易记录")
except Exception as _e:
    _startup_log.append(f"交易加载失败({_e})")

# 初始化诊断策略
from strategies import (
    SavingRateStrategy, CategoryOverrunStrategy,
    ConsumptionStructureStrategy, SavingsGoalStrategy, CompositeDiagnosis,
)
_savings_goal_strategy = SavingsGoalStrategy(
    get_target=lambda: ctrl.get_savings_target()
)
ctrl.set_diagnosis_strategy(CompositeDiagnosis([
    (SavingRateStrategy(), 0.35),
    (CategoryOverrunStrategy(), 0.25),
    (ConsumptionStructureStrategy(), 0.2),
    (_savings_goal_strategy, 0.2),
]))

# 规则/方法引用
from rules.fixed_budget import FixedBudgetRule
from rules.rule_503020 import Rule503020
from methods.fixed_amount import FixedAmountMethod
from methods.week52 import Week52Method
from methods.percentage import PercentageMethod


# ====== 辅助 ======

def _save_settings():
    try:
        ctrl.save_settings(str(_settings_path))
    except Exception:
        pass


def _save_transactions():
    try:
        ctrl.save_transactions(str(_transactions_path))
    except Exception:
        pass


# ====== 对话框 ======

class AddTransactionDialog(QDialog, Ui_AddTransactionDialog):
    """添加交易对话框 — UI 由 pyside6-uic 从 add_transaction_dialog.ui 编译"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self._result = None

        # 初始化
        self.date_edit.setText(date.today().isoformat())
        self.cat_combo.addItems(STANDARD_CATEGORIES)

        # 信号
        self.button_box.accepted.connect(self._on_ok)
        self.button_box.rejected.connect(self.reject)

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

    def get_transaction(self):
        return self._result


class SetBudgetDialog(QDialog, Ui_SetBudgetDialog):
    """设置预算对话框 — UI 由 pyside6-uic 从 set_budget_dialog.ui 编译"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self._result = None

        self.cat_combo.addItems(STANDARD_CATEGORIES)

        self.button_box.accepted.connect(self._on_ok)
        self.button_box.rejected.connect(self.reject)

    def _on_ok(self):
        cat = self.cat_combo.currentText().strip()
        try:
            limit = float(self.limit_edit.text().strip())
        except ValueError:
            QMessageBox.critical(self, "错误", "限额必须是数字")
            return
        self._result = Budget(cat, limit)
        self.accept()

    def get_budget(self):
        return self._result


# ====== 主窗口 ======

class MainWindow(QMainWindow, Ui_MainWindow):
    """主窗口 — UI 由 pyside6-uic 从 main_gui.ui 编译"""

    data_changed = Signal()

    def __init__(self):
        super().__init__()
        # setupUi() 创建所有控件并设为 self 属性（如 self.tabs, self.txn_table...）
        self.setupUi(self)

        # ---- 创建 QButtonGroup（.ui 中无法定义，在代码中补建） ----
        self._create_button_groups()

        # ---- 工具栏：添加月份选择控件 ----
        self._setup_toolbar()

        # ---- 信号/槽连接 ----
        self._connect_signals()

        # ---- 状态栏消息 ----
        self.statusbar.showMessage(
            f"启动: {'; '.join(_startup_log)}" if _startup_log
            else "就绪（无数据，可添加交易或手动导入CSV账单）"
        )

        # ---- 初始加载 ----
        self._refresh_months()
        latest = self.month_combo.currentText() if self.month_combo.count() > 0 else None
        self._refresh_txn_table(latest)
        self._refresh_budget_table(latest)
        self._refresh_alert()
        self._update_method_desc()

    # ===================== 初始化辅助 =====================

    def _create_button_groups(self):
        """创建 QButtonGroup（.ui 文件限制，必须在代码中创建）"""
        # 预算规则按钮组
        self.rule_group = QButtonGroup(self)
        self.rule_group.addButton(self.radio_503020, 1)
        self.rule_group.addButton(self.radio_fixed, 2)

        # 储蓄方法按钮组
        self.method_group = QButtonGroup(self)
        self.method_group.addButton(self.radio_fixed_amount, 0)
        self.method_group.addButton(self.radio_52w_inc, 1)
        self.method_group.addButton(self.radio_52w_dec, 2)
        self.method_group.addButton(self.radio_pct, 3)

    def _setup_toolbar(self):
        """给工具栏添加月份选择控件"""
        self.toolbar_month.addWidget(QLabel("月份: "))
        self.month_combo = QComboBox()
        self.month_combo.setMinimumWidth(100)
        self.month_combo.currentTextChanged.connect(self._on_month_changed)
        self.toolbar_month.addWidget(self.month_combo)

        btn_refresh = QPushButton("刷新月份")
        btn_refresh.clicked.connect(self._refresh_months)
        self.toolbar_month.addWidget(btn_refresh)

    def _connect_signals(self):
        """连接所有信号/槽"""
        # -- 交易管理 --
        self.btn_add_txn.clicked.connect(self._on_add_txn)
        self.btn_import_csv.clicked.connect(self._on_import_csv)
        self.btn_delete_txn.clicked.connect(self._on_delete_txn)

        # -- 预算管理 --
        self.budget_table.cellChanged.connect(self._on_budget_cell_changed)
        self.btn_add_budget.clicked.connect(self._on_add_budget_row)
        self.btn_delete_budget.clicked.connect(self._on_delete_budget)
        self.btn_apply_503020.clicked.connect(lambda: self._apply_budget_rule("503020"))
        self.btn_apply_fixed.clicked.connect(lambda: self._apply_budget_rule("fixed"))

        # -- 诊断报告 --
        self.btn_run_diag.clicked.connect(lambda: self._run_diagnosis())

        # -- 储蓄管理 --
        self.btn_run_goal.clicked.connect(self._run_goal)
        self.btn_run_method.clicked.connect(self._run_method)
        for rb in [self.radio_fixed_amount, self.radio_52w_inc,
                    self.radio_52w_dec, self.radio_pct]:
            rb.toggled.connect(
                lambda checked, _rb=rb: self._update_method_desc() if checked else None
            )

        # -- 预警消息 --
        self.btn_refresh_alert.clicked.connect(self._refresh_alert)
        self.btn_check_alert.clicked.connect(self._on_check_alert)
        self.btn_clear_alert.clicked.connect(self._on_clear_alert)

        # 交易数据变更时刷新月份列表
        self.data_changed.connect(self._refresh_months)

    def _get_current_month(self):
        m = self.month_combo.currentText() if hasattr(self, 'month_combo') else ""
        return m if m else None

    # ===================== 月份 / 工具栏 =====================

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
            self._refresh_txn_table(month)
            self._refresh_budget_table(month)
            self.statusbar.showMessage(f"当前月份: {month}")

    # ===================== Tab 1: 交易管理 =====================

    def _refresh_txn_table(self, month=None):
        self.txn_table.setRowCount(0)
        txns = ctrl.get_transactions(month)
        self.txn_table.setRowCount(len(txns))
        for i, t in enumerate(txns):
            self.txn_table.setItem(i, 0, QTableWidgetItem(str(t.date)))
            self.txn_table.setItem(i, 1, QTableWidgetItem(t.type))
            self.txn_table.setItem(i, 2, QTableWidgetItem(t.category))
            self.txn_table.setItem(i, 3, QTableWidgetItem(f"{t.amount:.2f}"))
            self.txn_table.setItem(i, 4, QTableWidgetItem(t.account.value))
            self.txn_table.setItem(i, 5, QTableWidgetItem(t.note))

    def _on_add_txn(self):
        dlg = AddTransactionDialog(self)
        if dlg.exec() == QDialog.Accepted:
            ctrl.add_transaction(dlg.get_transaction())
            _save_transactions()
            self._refresh_txn_table(self._get_current_month())
            self.data_changed.emit()

    def _on_import_csv(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择CSV文件", "", "CSV文件 (*.csv);;所有文件 (*)")
        if not path:
            return
        try:
            count = ctrl.import_csv(path)
            _save_transactions()
            QMessageBox.information(self, "导入完成", f"成功导入 {count} 条交易")
            self._refresh_txn_table(self._get_current_month())
            self.data_changed.emit()
        except Exception as e:
            QMessageBox.critical(self, "导入失败", str(e))

    def _on_delete_txn(self):
        rows = set(idx.row() for idx in self.txn_table.selectedIndexes())
        if not rows:
            QMessageBox.warning(self, "未选择", "请先选中要删除的交易行")
            return
        reply = QMessageBox.question(self, "确认删除",
                                     f"确定要删除选中的 {len(rows)} 条交易吗？此操作不可撤销。",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        month = self._get_current_month()
        txns = ctrl.get_transactions(month)
        for row in sorted(rows, reverse=True):
            if row < len(txns):
                ctrl.delete_transaction(txns[row])
        _save_transactions()
        self._refresh_txn_table(month)
        self.data_changed.emit()

    # ===================== Tab 2: 预算管理 =====================

    _budget_updating = False

    def _refresh_budget_table(self, month=None):
        if month is None:
            month = self._get_current_month()
        ctrl.recalculate_budget_spent(month)
        budgets = ctrl.get_budgets()
        self._budget_updating = True
        self.budget_table.setRowCount(len(budgets))
        for i, b in enumerate(budgets):
            remaining = b.get_remaining()
            status = "!!超支!!" if b.is_exceeded() else "正常"
            self.budget_table.setItem(i, 0, QTableWidgetItem(b.category))
            self.budget_table.setItem(i, 1, QTableWidgetItem(f"{b.monthly_limit:.0f}"))
            self.budget_table.setItem(i, 2, QTableWidgetItem(f"{b.current_spent:.0f}"))
            self.budget_table.setItem(i, 3, QTableWidgetItem(f"{remaining:.0f}"))
            self.budget_table.setItem(i, 4, QTableWidgetItem(status))
        self._budget_updating = False

        # 汇总标签
        total_limit = sum(b.monthly_limit for b in budgets)
        total_spent = sum(b.current_spent for b in budgets)
        try:
            income = float(self.income_edit.text().strip())
        except ValueError:
            income = 0.0
        if income > 0:
            surplus = income - total_limit
            tag = f"余额: ¥{surplus:+.0f}（预算在收入范围内）" if surplus >= 0 \
                else f"!! 超额: ¥{surplus:+.0f} 预算已超月收入 !!"
            self.budget_summary_label.setText(
                f"预算总额: ¥{total_limit:.0f}  |  月收入: ¥{income:.0f}  |  {tag}"
            )
        else:
            self.budget_summary_label.setText(
                f"预算总额: ¥{total_limit:.0f}  |  已支出: ¥{total_spent:.0f}"
            )

    def _on_budget_cell_changed(self, row, col):
        if self._budget_updating or col != 1:
            return
        try:
            cat_item = self.budget_table.item(row, 0)
            limit_item = self.budget_table.item(row, 1)
            if not cat_item or not limit_item:
                return
            cat = cat_item.text().strip()
            if not cat:
                return
            limit = float(limit_item.text().strip())
            ctrl.set_budget(Budget(cat, limit))
            _save_settings()
        except ValueError:
            pass

    def _on_add_budget_row(self):
        row = self.budget_table.rowCount()
        self._budget_updating = True
        self.budget_table.setRowCount(row + 1)
        self.budget_table.setItem(row, 0, QTableWidgetItem("双击编辑类别"))
        self.budget_table.setItem(row, 1, QTableWidgetItem("0"))
        self.budget_table.setItem(row, 2, QTableWidgetItem("0"))
        self.budget_table.setItem(row, 3, QTableWidgetItem("0"))
        self.budget_table.setItem(row, 4, QTableWidgetItem("正常"))
        self._budget_updating = False
        ctrl.set_budget(Budget("双击编辑类别", 0))
        _save_settings()

    def _on_delete_budget(self):
        rows = set(idx.row() for idx in self.budget_table.selectedIndexes())
        if not rows:
            QMessageBox.warning(self, "未选择", "请先选中要删除的预算行")
            return
        budgets = ctrl.get_budgets()
        to_remove = [budgets[row].category
                     for row in sorted(rows, reverse=True) if row < len(budgets)]
        if not to_remove:
            return
        reply = QMessageBox.question(self, "确认删除",
                                     f"确定要删除 {len(to_remove)} 个预算类别吗？\n"
                                     f"{', '.join(to_remove)}",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        for cat in to_remove:
            ctrl.remove_budget(cat)
        _save_settings()
        self._refresh_budget_table()

    def _apply_budget_rule(self, method="503020"):
        try:
            income = float(self.income_edit.text().strip())
        except ValueError:
            QMessageBox.critical(self, "错误", "请输入有效收入金额")
            return
        if method == "503020":
            ctrl.set_budget_rule(Rule503020())
        else:
            rule = FixedBudgetRule()
            # 从表格读取用户当前设定的类别和限额
            for row in range(self.budget_table.rowCount()):
                cat_item = self.budget_table.item(row, 0)
                limit_item = self.budget_table.item(row, 1)
                if cat_item and limit_item:
                    cat = cat_item.text().strip()
                    if not cat or cat == "双击编辑类别":
                        continue
                    try:
                        lim = float(limit_item.text().strip())
                    except ValueError:
                        continue
                    rule.set_budget(cat, lim)
            ctrl.set_budget_rule(rule)
        try:
            result = ctrl.apply_budget_rule(income)
            total_allocated = sum(v for k, v in result.items() if k != "储蓄")
            if method == "fixed" and total_allocated > income:
                reply = QMessageBox.warning(
                    self, "预算超收",
                    f"固定预算总额 ¥{total_allocated:.0f} 超过月收入 ¥{income:.0f}。\n"
                    f"超支 ¥{total_allocated - income:.0f}，建议调低预算或确认收入金额。\n\n"
                    "是否仍要应用？",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return
            for cat, amt in result.items():
                if cat != "储蓄":
                    ctrl.set_budget(Budget(cat, amt))
            _save_settings()
            self._refresh_budget_table()
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))

    # ===================== Tab 3: 诊断报告 =====================

    def _run_diagnosis(self, month=None):
        self.diag_text.clear()
        months = ctrl.get_months()
        if not months:
            self.diag_text.append("(暂无交易数据，请先录入交易或导入CSV账单)")
            return

        if month is None:
            month = self._get_current_month()
        if not month or month not in months:
            month = months[-1]

        self.diag_text.append(f"诊断月份: {month}")
        txns_check = ctrl.get_transactions(month)
        if not txns_check:
            self.diag_text.append(f"(注意: 月份 {month} 暂无交易记录，诊断结果仅供参考)")
            self.diag_text.append("=" * 60)
            return

        expense_total = sum(t.amount for t in txns_check if t.is_expense())
        income_total = sum(t.amount for t in txns_check if t.is_income())
        if len(txns_check) < 5 or expense_total < 100:
            self.diag_text.append(
                f"(警告: 该月仅 {len(txns_check)} 笔记录、支出 ¥{expense_total:.0f}、"
                f"收入 ¥{income_total:.0f}，数据量不足以支撑可靠诊断，以下结果仅供参考)"
            )
        self.diag_text.append("=" * 60)

        try:
            report = ctrl.generate_diagnosis(month)
        except RuntimeError as e:
            self.diag_text.append(f"诊断失败: {e}")
            return

        emoji = {HealthLevel.HEALTHY: "[健康]", HealthLevel.WARNING: "[预警]",
                 HealthLevel.CRITICAL: "[严重]"}
        self.diag_text.append(
            f"综合评分: {report.overall_score:.0f}/100  {emoji.get(report.overall_level, '')}"
        )
        self.diag_text.append("")
        self.diag_text.append(f"各维度明细 ({len(report.dimensions)}项):")
        self.diag_text.append("-" * 50)
        for dim in report.dimensions:
            mark = emoji.get(dim.level, "")
            self.diag_text.append(f"  {dim.strategy_name}: {dim.score:.0f}分  {mark}")
            if dim.suggestion:
                self.diag_text.append(f"    -> {dim.suggestion.description}")
        self.diag_text.append("")

        if report.suggestions:
            priority_map = {1: "高优先级", 2: "中优先级", 3: "低优先级"}
            self.diag_text.append(f"改进建议 ({len(report.suggestions)}条，按影响金额降序):")
            self.diag_text.append("-" * 50)
            for i, s in enumerate(report.suggestions, 1):
                label = priority_map.get(s.priority, "")
                self.diag_text.append(f"  {i}. [{label}] {s.category}")
                self.diag_text.append(f"     {s.description}")
                self.diag_text.append(f"     预计月改善: ¥{s.impact_amount:.0f}")
        else:
            self.diag_text.append("无改进建议，财务状况健康！")
        self.diag_text.append("=" * 60)

    # ===================== Tab 4: 储蓄管理 =====================

    def _update_method_desc(self):
        method_id = self.method_group.checkedId()
        try:
            param = float(self.method_param_edit.text().strip() or "0")
            income = float(self.saving_income_edit.text().strip() or "0")
        except ValueError:
            param, income = 0.0, 0.0

        if method_id == 0:  # 固定金额
            annual = param * 12
            weekly = annual / 52
            self.method_desc_label.setText(
                f"固定金额法：每月存 ¥{param:.0f} → 年总额 ¥{annual:.0f}（52周均分，每周 ¥{weekly:.0f}）"
            )
        elif method_id == 1:  # 52周递增
            annual = param * 1378
            self.method_desc_label.setText(
                f"52周递增法：基数 ¥{param:.0f}，第N周存 N×¥{param:.0f} → 年总额 ¥{annual:.0f}"
            )
        elif method_id == 2:  # 52周递减
            annual = param * 1378
            self.method_desc_label.setText(
                f"52周递减法：基数 ¥{param:.0f}，第1周存 ¥{param*52:.0f} "
                f"递减至第52周 ¥{param:.0f} → 年总额 ¥{annual:.0f}"
            )
        elif method_id == 3:  # 收入%
            rate = param / 100.0
            monthly = income * rate
            annual = monthly * 12
            self.method_desc_label.setText(
                f"收入百分比法：每月存收入的 {param:.0f}%（¥{monthly:.0f}）→ 年总额 ¥{annual:.0f}"
            )

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

        ctrl.set_savings_target(plan.required_monthly_saving)
        _save_settings()

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
            income = float(self.saving_income_edit.text().strip())
            param = float(self.method_param_edit.text().strip())
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

        ctrl.set_savings_target(plan.annual_total / 12)
        _save_settings()

        self.method_text.append(f"方法说明: {plan.description}")
        self.method_text.append("")
        self.method_text.append(f"==== 年储蓄总额: ¥{plan.annual_total:.0f} ====")
        self.method_text.append("")
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

    # ===================== Tab 5: 预警消息 =====================

    def _refresh_alert(self):
        self.alert_text.clear()
        alerts = ctrl.get_alert_messages()
        if not alerts:
            self.alert_text.append("(暂无预警 — 请先设置预算，然后点击「检测预警」或运行诊断)")
        else:
            for a in alerts:
                self.alert_text.append(a)

    def _on_check_alert(self):
        month = self._get_current_month()
        ctrl.recalculate_budget_spent(month)
        ctrl.check_budget_alerts()
        self._refresh_alert()

    def _on_clear_alert(self):
        ctrl.clear_alerts()
        self._refresh_alert()


# ====== 启动入口 ======

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
