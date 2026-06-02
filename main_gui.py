# main_gui — 个人财务管理系统图形化检查页面
# 基于 tkinter，覆盖项目全部功能模块
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date
from pathlib import Path
from models.transaction import Transaction, AccountType
from models.budget import Budget
from models.diagnosis_report import HealthLevel
from services import FinanceController

# ---------- 全局控制器 ----------
ctrl = FinanceController()

# ---------- 启动时自动导入同级目录CSV ----------
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
    SavingRateStrategy,
    CategoryOverrunStrategy,
    ConsumptionStructureStrategy,
    CompositeDiagnosis,
)
ctrl.set_diagnosis_strategy(CompositeDiagnosis([
    (SavingRateStrategy(), 0.4),
    (CategoryOverrunStrategy(), 0.3),
    (ConsumptionStructureStrategy(), 0.3),
]))

# 初始化预算规则与储蓄方法
from rules.budget_rule import BudgetRule
from rules.fixed_budget import FixedBudgetRule
from rules.rule_503020 import Rule503020
from methods.savings_method import SavingsMethod
from methods.fixed_amount import FixedAmountMethod
from methods.week52 import Week52Method
from methods.percentage import PercentageMethod

# ---------- 主窗口 ----------
root = tk.Tk()
root.title("个人财务管理系统 — 图形化检查")
root.geometry("1000x700")
root.minsize(800, 600)

# ---------- 全局状态变量 ----------
current_month_var = tk.StringVar()
status_var = tk.StringVar(value="就绪")

# ---------- 工具栏 ----------
toolbar = ttk.Frame(root)
toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=3)

ttk.Label(toolbar, text="月份:").pack(side=tk.LEFT, padx=2)
month_combo = ttk.Combobox(toolbar, textvariable=current_month_var, width=10, state="readonly")
month_combo.pack(side=tk.LEFT, padx=2)

def refresh_month_list():
    months = ctrl.get_months()
    month_combo["values"] = months
    if months:
        current_month_var.set(months[-1])

refresh_month_list()

ttk.Button(toolbar, text="刷新月份", command=refresh_month_list).pack(side=tk.LEFT, padx=5)

# 右侧状态栏
ttk.Label(toolbar, textvariable=status_var, foreground="gray").pack(side=tk.RIGHT, padx=5)

# ---------- 主 Notebook ----------
notebook = ttk.Notebook(root)
notebook.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=3)

# ============================================================
# Tab 1: 交易管理
# ============================================================
tab_txn = ttk.Frame(notebook)
notebook.add(tab_txn, text="交易管理")

# 交易列表（Treeview）
txn_frame = ttk.LabelFrame(tab_txn, text="交易记录")
txn_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

txn_cols = ("日期", "类型", "类别", "金额", "账户", "备注")
txn_tree = ttk.Treeview(txn_frame, columns=txn_cols, show="headings", height=15)
for c in txn_cols:
    txn_tree.heading(c, text=c)
    txn_tree.column(c, width=100, anchor="center")
txn_tree.column("备注", width=200, anchor="w")
txn_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

txn_scroll = ttk.Scrollbar(txn_frame, orient=tk.VERTICAL, command=txn_tree.yview)
txn_tree.configure(yscrollcommand=txn_scroll.set)
txn_scroll.pack(side=tk.RIGHT, fill=tk.Y)

def refresh_txn_list():
    txn_tree.delete(*txn_tree.get_children())
    month = current_month_var.get()
    txns = ctrl.get_transactions(month) if month else ctrl.get_transactions()
    for t in txns:
        txn_tree.insert("", tk.END, values=(t.date, t.type, t.category, f"{t.amount:.2f}", t.account.value, t.note))
    status_var.set(f"共 {len(txns)} 条交易")

# 交易操作按钮
txn_btn_frame = ttk.Frame(tab_txn)
txn_btn_frame.pack(fill=tk.X, padx=5, pady=3)

ttk.Button(txn_btn_frame, text="刷新列表", command=refresh_txn_list).pack(side=tk.LEFT, padx=2)

def add_txn_dialog():
    """弹出添加交易对话框"""
    dlg = tk.Toplevel(root)
    dlg.title("添加交易")
    dlg.geometry("380x320")
    dlg.resizable(False, False)
    dlg.transient(root)
    dlg.grab_set()

    fields = {}
    row = 0
    ttk.Label(dlg, text="日期 (YYYY-MM-DD):").grid(row=row, column=0, padx=5, pady=3, sticky="e")
    fields["date"] = ttk.Entry(dlg, width=25)
    fields["date"].insert(0, date.today().isoformat())
    fields["date"].grid(row=row, column=1, padx=5, pady=3)
    row += 1

    ttk.Label(dlg, text="金额:").grid(row=row, column=0, padx=5, pady=3, sticky="e")
    fields["amount"] = ttk.Entry(dlg, width=25)
    fields["amount"].grid(row=row, column=1, padx=5, pady=3)
    row += 1

    ttk.Label(dlg, text="类型:").grid(row=row, column=0, padx=5, pady=3, sticky="e")
    fields["type"] = ttk.Combobox(dlg, values=["支出", "收入"], width=23, state="readonly")
    fields["type"].current(0)
    fields["type"].grid(row=row, column=1, padx=5, pady=3)
    row += 1

    ttk.Label(dlg, text="类别:").grid(row=row, column=0, padx=5, pady=3, sticky="e")
    fields["category"] = ttk.Combobox(dlg, values=["餐饮", "交通", "娱乐", "学习", "日用", "其他"], width=23)
    fields["category"].grid(row=row, column=1, padx=5, pady=3)
    row += 1

    ttk.Label(dlg, text="账户:").grid(row=row, column=0, padx=5, pady=3, sticky="e")
    fields["account"] = ttk.Combobox(dlg, values=["微信", "支付宝", "现金", "银行卡"], width=23, state="readonly")
    fields["account"].current(0)
    fields["account"].grid(row=row, column=1, padx=5, pady=3)
    row += 1

    ttk.Label(dlg, text="备注:").grid(row=row, column=0, padx=5, pady=3, sticky="e")
    fields["note"] = ttk.Entry(dlg, width=25)
    fields["note"].grid(row=row, column=1, padx=5, pady=3)
    row += 1

    def do_add():
        try:
            d = date.fromisoformat(fields["date"].get().strip())
            amount = float(fields["amount"].get().strip())
            t_type = fields["type"].get()
            cat = fields["category"].get().strip() or "其他"
            acc_map = {"微信": AccountType.WECHAT, "支付宝": AccountType.ALIPAY, "现金": AccountType.CASH, "银行卡": AccountType.BANK_CARD}
            acc = acc_map.get(fields["account"].get(), AccountType.WECHAT)
            note = fields["note"].get().strip()
            ctrl.add_transaction(Transaction(amount, t_type, cat, acc, d, note))
            messagebox.showinfo("成功", "交易已添加")
            dlg.destroy()
            refresh_txn_list()
            refresh_month_list()
        except ValueError as e:
            messagebox.showerror("格式错误", str(e))

    ttk.Button(dlg, text="确认添加", command=do_add).grid(row=row, column=0, columnspan=2, pady=10)

ttk.Button(txn_btn_frame, text="添加交易", command=add_txn_dialog).pack(side=tk.LEFT, padx=2)

def import_csv_action():
    path = filedialog.askopenfilename(filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")])
    if not path:
        return
    try:
        count = ctrl.import_csv(path)
        messagebox.showinfo("导入完成", f"成功导入 {count} 条交易")
        refresh_txn_list()
        refresh_month_list()
    except Exception as e:
        messagebox.showerror("导入失败", str(e))

ttk.Button(txn_btn_frame, text="导入CSV", command=import_csv_action).pack(side=tk.LEFT, padx=2)

def delete_selected_txn():
    """删除选中的交易"""
    sel = txn_tree.selection()
    if not sel:
        messagebox.showwarning("未选择", "请先在列表中选中要删除的交易")
        return
    if not messagebox.askyesno("确认删除", f"确定要删除选中的 {len(sel)} 条交易吗？此操作不可撤销。"):
        return
    deleted = 0
    for item in sel:
        vals = txn_tree.item(item, "values")
        # 重建 Transaction 以匹配删除
        try:
            d = date.fromisoformat(vals[0])
            amount = float(vals[3])
            t_type = vals[1]
            cat = vals[2]
            acc_map = {"微信": AccountType.WECHAT, "支付宝": AccountType.ALIPAY, "现金": AccountType.CASH, "银行卡": AccountType.BANK_CARD}
            acc = acc_map.get(vals[4], AccountType.WECHAT)
            note = vals[5]
            t = Transaction(amount, t_type, cat, acc, d, note)
            if ctrl.delete_transaction(t):
                deleted += 1
        except (ValueError, IndexError):
            continue
    refresh_txn_list()
    refresh_month_list()
    refresh_budget_list()
    refresh_alerts()
    status_var.set(f"已删除 {deleted} 条交易")

ttk.Button(txn_btn_frame, text="删除选中", command=delete_selected_txn).pack(side=tk.LEFT, padx=2)

# ============================================================
# Tab 2: 预算管理
# ============================================================
tab_budget = ttk.Frame(notebook)
notebook.add(tab_budget, text="预算管理")

# 预算列表
budget_frame = ttk.LabelFrame(tab_budget, text="当前预算")
budget_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

budget_cols = ("类别", "月度限额", "已支出", "剩余", "状态")
budget_tree = ttk.Treeview(budget_frame, columns=budget_cols, show="headings", height=10)
for c in budget_cols:
    budget_tree.heading(c, text=c)
    budget_tree.column(c, width=100, anchor="center")
budget_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

budget_scroll = ttk.Scrollbar(budget_frame, orient=tk.VERTICAL, command=budget_tree.yview)
budget_tree.configure(yscrollcommand=budget_scroll.set)
budget_scroll.pack(side=tk.RIGHT, fill=tk.Y)

def refresh_budget_list():
    # 先根据当前选中月份的交易重算已支出
    month = current_month_var.get() or None
    ctrl.recalculate_budget_spent(month)
    budget_tree.delete(*budget_tree.get_children())
    for b in ctrl.get_budgets():
        remaining = b.get_remaining()
        status = "!!超支!!" if b.is_exceeded() else "正常"
        budget_tree.insert("", tk.END, values=(b.category, f"{b.monthly_limit:.0f}", f"{b.current_spent:.0f}", f"{remaining:.0f}", status))

# 预算操作按钮
budget_btn = ttk.Frame(tab_budget)
budget_btn.pack(fill=tk.X, padx=5, pady=3)

ttk.Button(budget_btn, text="刷新列表", command=refresh_budget_list).pack(side=tk.LEFT, padx=2)

def set_budget_dialog():
    dlg = tk.Toplevel(root)
    dlg.title("设置预算")
    dlg.geometry("300x180")
    dlg.resizable(False, False)
    dlg.transient(root)
    dlg.grab_set()

    ttk.Label(dlg, text="类别:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    cat_entry = ttk.Combobox(dlg, values=["餐饮", "交通", "娱乐", "学习", "日用", "其他"], width=20)
    cat_entry.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(dlg, text="月度限额:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    limit_entry = ttk.Entry(dlg, width=22)
    limit_entry.grid(row=1, column=1, padx=5, pady=5)

    def do_set():
        cat = cat_entry.get().strip()
        try:
            limit = float(limit_entry.get().strip())
        except ValueError:
            messagebox.showerror("错误", "限额必须是数字")
            return
        ctrl.set_budget(Budget(cat, limit))
        messagebox.showinfo("成功", f"已设置 {cat} 预算 ¥{limit:.0f}")
        dlg.destroy()
        refresh_budget_list()

    ttk.Button(dlg, text="确认", command=do_set).grid(row=2, column=0, columnspan=2, pady=10)

ttk.Button(budget_btn, text="设置预算", command=set_budget_dialog).pack(side=tk.LEFT, padx=2)

# 预算规则区
rule_frame = ttk.LabelFrame(tab_budget, text="预算规则（P1）")
rule_frame.pack(fill=tk.X, padx=5, pady=5)

rule_row = ttk.Frame(rule_frame)
rule_row.pack(fill=tk.X, padx=5, pady=5)

ttk.Label(rule_row, text="规则类型:").pack(side=tk.LEFT)
rule_type_var = tk.StringVar(value="503020")
ttk.Radiobutton(rule_row, text="50/30/20", variable=rule_type_var, value="503020").pack(side=tk.LEFT, padx=3)
ttk.Radiobutton(rule_row, text="固定预算", variable=rule_type_var, value="fixed").pack(side=tk.LEFT, padx=3)

ttk.Label(rule_row, text="  月收入:").pack(side=tk.LEFT)
income_entry = ttk.Entry(rule_row, width=10)
income_entry.insert(0, "5000")
income_entry.pack(side=tk.LEFT, padx=3)

def apply_budget_rule():
    try:
        income = float(income_entry.get().strip())
    except ValueError:
        messagebox.showerror("错误", "请输入有效收入金额")
        return
    if rule_type_var.get() == "503020":
        ctrl.set_budget_rule(Rule503020())
    else:
        rule = FixedBudgetRule()
        # 简单预设一些固定预算
        for cat, lim in [("餐饮", 1500), ("交通", 300), ("娱乐", 500), ("日用", 300), ("学习", 200)]:
            rule.set_budget(cat, lim)
        ctrl.set_budget_rule(rule)
    try:
        result = ctrl.apply_budget_rule(income)
        msg = "建议预算分配:\n"
        for cat, amt in result.items():
            msg += f"  {cat}: ¥{amt:.0f}\n"
        messagebox.showinfo("预算规则结果", msg)
        # 同时更新到控制器预算列表
        for cat, amt in result.items():
            if cat != "储蓄":
                ctrl.set_budget(Budget(cat, amt))
        refresh_budget_list()
    except Exception as e:
        messagebox.showerror("错误", str(e))

ttk.Button(rule_row, text="应用规则", command=apply_budget_rule).pack(side=tk.LEFT, padx=10)

# ============================================================
# Tab 3: 诊断报告
# ============================================================
tab_diag = ttk.Frame(notebook)
notebook.add(tab_diag, text="诊断报告")

diag_text = tk.Text(tab_diag, wrap=tk.WORD, font=("Microsoft YaHei", 10))
diag_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

diag_scroll = ttk.Scrollbar(diag_text, orient=tk.VERTICAL, command=diag_text.yview)
diag_text.configure(yscrollcommand=diag_scroll.set)
diag_scroll.pack(side=tk.RIGHT, fill=tk.Y)

def run_diagnosis_action():
    diag_text.delete("1.0", tk.END)
    months = ctrl.get_months()
    if not months:
        diag_text.insert(tk.END, "(暂无交易数据，请先导入CSV或录入交易)")
        return
    month = current_month_var.get() or months[-1]
    diag_text.insert(tk.END, f"诊断月份: {month}\n")
    diag_text.insert(tk.END, "=" * 60 + "\n")
    try:
        report = ctrl.generate_diagnosis(month)
    except RuntimeError as e:
        diag_text.insert(tk.END, f"诊断失败: {e}\n")
        return

    emoji = {HealthLevel.HEALTHY: "[健康]", HealthLevel.WARNING: "[预警]", HealthLevel.CRITICAL: "[严重]"}
    diag_text.insert(tk.END, f"综合评分: {report.overall_score:.0f}/100  {emoji.get(report.overall_level, '')}\n\n")

    diag_text.insert(tk.END, f"各维度明细 ({len(report.dimensions)}项):\n")
    diag_text.insert(tk.END, "-" * 50 + "\n")
    for dim in report.dimensions:
        mark = emoji.get(dim.level, "")
        diag_text.insert(tk.END, f"  {dim.strategy_name}: {dim.score:.0f}分  {mark}\n")
        if dim.suggestion:
            diag_text.insert(tk.END, f"    -> {dim.suggestion.description}\n")
    diag_text.insert(tk.END, "\n")

    if report.suggestions:
        priority_map = {1: "高优先级", 2: "中优先级", 3: "低优先级"}
        diag_text.insert(tk.END, f"改进建议 ({len(report.suggestions)}条，按影响金额降序):\n")
        diag_text.insert(tk.END, "-" * 50 + "\n")
        for i, s in enumerate(report.suggestions, 1):
            label = priority_map.get(s.priority, "")
            diag_text.insert(tk.END, f"  {i}. [{label}] {s.category}\n")
            diag_text.insert(tk.END, f"     {s.description}\n")
            diag_text.insert(tk.END, f"     预计月改善: ¥{s.impact_amount:.0f}\n")
    else:
        diag_text.insert(tk.END, "无改进建议，财务状况健康！\n")
    diag_text.insert(tk.END, "=" * 60 + "\n")

diag_btn_frame = ttk.Frame(tab_diag)
diag_btn_frame.pack(fill=tk.X, padx=5, pady=3)
ttk.Button(diag_btn_frame, text="生成诊断报告", command=run_diagnosis_action).pack(side=tk.LEFT, padx=2)

# ============================================================
# Tab 4: 储蓄管理
# ============================================================
tab_saving = ttk.Frame(notebook)
notebook.add(tab_saving, text="储蓄管理")

# 储蓄倒推（P0）
save_goal_frame = ttk.LabelFrame(tab_saving, text="储蓄目标倒推（P0）")
save_goal_frame.pack(fill=tk.X, padx=5, pady=5)

goal_row = ttk.Frame(save_goal_frame)
goal_row.pack(fill=tk.X, padx=5, pady=5)

ttk.Label(goal_row, text="目标金额:").pack(side=tk.LEFT)
target_entry = ttk.Entry(goal_row, width=10)
target_entry.insert(0, "12000")
target_entry.pack(side=tk.LEFT, padx=3)

ttk.Label(goal_row, text="  月数:").pack(side=tk.LEFT)
months_entry = ttk.Entry(goal_row, width=6)
months_entry.insert(0, "12")
months_entry.pack(side=tk.LEFT, padx=3)

save_goal_text = tk.Text(save_goal_frame, wrap=tk.WORD, height=10, font=("Microsoft YaHei", 10))
save_goal_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

def run_saving_goal():
    save_goal_text.delete("1.0", tk.END)
    try:
        target = float(target_entry.get().strip())
        months = int(months_entry.get().strip())
    except ValueError:
        save_goal_text.insert(tk.END, "请输入有效数字")
        return
    try:
        plan = ctrl.generate_saving_plan(target, months)
    except Exception as e:
        save_goal_text.insert(tk.END, f"计算失败: {e}\n")
        return

    save_goal_text.insert(tk.END, "=" * 55 + "\n")
    save_goal_text.insert(tk.END, f"  储蓄目标: ¥{target:.0f} / {months} 个月\n")
    save_goal_text.insert(tk.END, f"  每月需存: ¥{plan.required_monthly_saving:.0f}\n")
    save_goal_text.insert(tk.END, f"  当前自然月结余: ¥{plan.current_natural_saving:.0f}\n")
    save_goal_text.insert(tk.END, f"  每月需额外削减: ¥{plan.extra_cut_needed:.0f}\n")
    save_goal_text.insert(tk.END, "-" * 55 + "\n")
    if plan.category_cuts:
        save_goal_text.insert(tk.END, "  建议削减:\n")
        for cat, cut in plan.category_cuts.items():
            save_goal_text.insert(tk.END, f"    {cat}: ¥{cut:.0f}\n")
    else:
        save_goal_text.insert(tk.END, "  无需额外削减\n")
    save_goal_text.insert(tk.END, "-" * 55 + "\n")
    save_goal_text.insert(tk.END, "  建议:\n")
    for s in plan.suggestions:
        save_goal_text.insert(tk.END, f"    [{s.priority}] {s.description}\n")
    save_goal_text.insert(tk.END, "=" * 55 + "\n")

ttk.Button(goal_row, text="计算倒推计划", command=run_saving_goal).pack(side=tk.LEFT, padx=10)

# 储蓄方法（P1）
save_method_frame = ttk.LabelFrame(tab_saving, text="储蓄方法选择（P1）")
save_method_frame.pack(fill=tk.X, padx=5, pady=5)

method_row = ttk.Frame(save_method_frame)
method_row.pack(fill=tk.X, padx=5, pady=5)

ttk.Label(method_row, text="储蓄方法:").pack(side=tk.LEFT)
method_type_var = tk.StringVar(value="fixed")
ttk.Radiobutton(method_row, text="固定金额", variable=method_type_var, value="fixed").pack(side=tk.LEFT, padx=2)
ttk.Radiobutton(method_row, text="52周递增", variable=method_type_var, value="52week").pack(side=tk.LEFT, padx=2)
ttk.Radiobutton(method_row, text="52周递减", variable=method_type_var, value="52week_rev").pack(side=tk.LEFT, padx=2)
ttk.Radiobutton(method_row, text="收入%", variable=method_type_var, value="pct").pack(side=tk.LEFT, padx=2)

ttk.Label(method_row, text="  参数:").pack(side=tk.LEFT)
method_param_entry = ttk.Entry(method_row, width=8)
method_param_entry.insert(0, "500")
method_param_entry.pack(side=tk.LEFT, padx=3)

ttk.Label(method_row, text="  月收入:").pack(side=tk.LEFT)
saving_income_entry = ttk.Entry(method_row, width=8)
saving_income_entry.insert(0, "5000")
saving_income_entry.pack(side=tk.LEFT, padx=3)

save_method_text = tk.Text(save_method_frame, wrap=tk.WORD, height=8, font=("Microsoft YaHei", 10))
save_method_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

def run_savings_method():
    save_method_text.delete("1.0", tk.END)
    try:
        income = float(saving_income_entry.get().strip())
        param = float(method_param_entry.get().strip())
    except ValueError:
        save_method_text.insert(tk.END, "请输入有效数字")
        return

    method_type = method_type_var.get()
    if method_type == "fixed":
        method = FixedAmountMethod(param)
    elif method_type == "52week":
        method = Week52Method(base_amount=param, reversed=False)
    elif method_type == "52week_rev":
        method = Week52Method(base_amount=param, reversed=True)
    elif method_type == "pct":
        method = PercentageMethod(rate=param / 100.0)
    else:
        return

    ctrl.set_savings_method(method)
    try:
        plan = ctrl.get_savings_plan(income)
    except Exception as e:
        save_method_text.insert(tk.END, f"计算失败: {e}\n")
        return

    save_method_text.insert(tk.END, f"方法说明: {plan.description}\n")
    save_method_text.insert(tk.END, f"年储蓄总额: ¥{plan.annual_total:.0f}\n")
    save_method_text.insert(tk.END, "-" * 55 + "\n")
    save_method_text.insert(tk.END, "52周储蓄计划（前12周）:\n")
    for i in range(12):
        save_method_text.insert(tk.END, f"  第{i+1:>2}周: ¥{plan.weekly_amounts[i]:>8.0f}")
        if i % 3 == 2:
            save_method_text.insert(tk.END, "\n")
    save_method_text.insert(tk.END, "\n  ...\n")
    for i in range(48, 52):
        save_method_text.insert(tk.END, f"  第{i+1:>2}周: ¥{plan.weekly_amounts[i]:>8.0f}")
        if i % 3 == 2:
            save_method_text.insert(tk.END, "\n")
    save_method_text.insert(tk.END, "\n")

ttk.Button(method_row, text="计算储蓄计划", command=run_savings_method).pack(side=tk.LEFT, padx=10)

# ============================================================
# Tab 5: 预警消息
# ============================================================
tab_alert = ttk.Frame(notebook)
notebook.add(tab_alert, text="预警消息")

alert_text = tk.Text(tab_alert, wrap=tk.WORD, font=("Microsoft YaHei", 10))
alert_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

alert_scroll = ttk.Scrollbar(alert_text, orient=tk.VERTICAL, command=alert_text.yview)
alert_text.configure(yscrollcommand=alert_scroll.set)
alert_scroll.pack(side=tk.RIGHT, fill=tk.Y)

def refresh_alerts():
    alert_text.delete("1.0", tk.END)
    alerts = ctrl.get_alert_messages()
    if not alerts:
        alert_text.insert(tk.END, "(暂无预警 — 请先设置预算，然后点击「检测预警」或运行诊断)")
    else:
        for a in alerts:
            alert_text.insert(tk.END, a + "\n")

def check_alerts_action():
    """手动触发预警检测"""
    month = current_month_var.get() or None
    ctrl.recalculate_budget_spent(month)
    ctrl.check_budget_alerts()
    refresh_alerts()
    status_var.set("预警检测完成")

def clear_alerts_action():
    ctrl.clear_alerts()
    refresh_alerts()

alert_btn_frame = ttk.Frame(tab_alert)
alert_btn_frame.pack(fill=tk.X, padx=5, pady=3)
ttk.Button(alert_btn_frame, text="刷新", command=refresh_alerts).pack(side=tk.LEFT, padx=2)
ttk.Button(alert_btn_frame, text="检测预警", command=check_alerts_action).pack(side=tk.LEFT, padx=2)
ttk.Button(alert_btn_frame, text="清空预警", command=clear_alerts_action).pack(side=tk.LEFT, padx=2)

# ============================================================
# 底部状态栏
# ============================================================
bottom_bar = ttk.Frame(root)
bottom_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=3)

ttk.Label(bottom_bar, text='提示: 切换月份后点击各页面的「刷新」按钮查看对应数据').pack(side=tk.LEFT)
right_label = ttk.Label(bottom_bar, text="模型: Transaction | Budget | MonthlyPlan | SavingsPlan | DiagnosisReport | Suggestion", foreground="gray")
right_label.pack(side=tk.RIGHT)

# ---------- 初始刷新 ----------
refresh_month_list()
refresh_txn_list()
refresh_budget_list()
refresh_alerts()

# 显示自动导入结果
if _auto_import_log:
    status_var.set(f"自动导入: {'; '.join(_auto_import_log)}")
else:
    status_var.set(f"就绪（未找到CSV文件，可手动导入或添加交易）")

# ---------- 启动 ----------
if __name__ == "__main__":
    root.mainloop()
