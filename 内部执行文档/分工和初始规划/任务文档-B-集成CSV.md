# 任务文档 — B（集成 + CSV 导入 + CLI 原型）

> 本文档只包含你需要关心的内容。全局设计见 `设计文档.md`，接口契约见 `接口文档.md`。

---

## 你的职责（三个阶段）

1. **第 1 周：最小 CLI 原型** — 验证 Controller API 设计是否合理
2. **第 2 周：CSV 导入模块 + 类别标准化** — 解析约五个月真实数据
3. **第 3-4 周：集成测试 + 演示数据 + 机动支援**

---

## 你需要交付的文件

```
services/
├── csv_importer.py           # CSV 解析
└── category_normalizer.py    # 类别标准化映射

main_cli.py                   # 最小 CLI 原型（第 1 周，可作为 main.py 的参考）
```

---

## 阶段一：最小 CLI 原型（第 1 周）

### 目的
在 D 和 E 还在写策略代码时，你用 C 的实体类 + 假数据，跑通 Controller 的调用链，提前发现 API 设计问题。

### 功能要求
```python
# main_cli.py 交互示例

=== 个人财务管理系统（CLI 原型） ===

1. 查看交易列表
2. 添加交易
3. 查看预算
4. 设置预算
5. 生成诊断报告（需 D 的 Strategy）
6. 生成储蓄计划（需 E 的 SavingGoalCalculator）
7. 导入 CSV
0. 退出

请选择:
```

- 选项 1-4 第一周即可完成（只依赖 C 的实体类 + Controller 骨架）
- 选项 5 需要 D 提供一个策略实例后对接
- 选项 6 需要 E 提供 SavingGoalCalculator 后对接
- 选项 7 等你的 CSV 模块完成后对接

### 代码结构
```python
# main_cli.py
from models.transaction import Transaction, AccountType
from models.budget import Budget
from services.finance_controller import FinanceController
from datetime import date


def main():
    ctrl = FinanceController()

    # 预置假数据
    ctrl.add_transaction(Transaction(35.5, "支出", "餐饮", AccountType.WECHAT, date(2025,3,15), "食堂午饭"))
    ctrl.add_transaction(Transaction(2000, "收入", "其他", AccountType.BANK_CARD, date(2025,3,15), "三月生活费"))
    ctrl.set_budget(Budget("餐饮", 1500))
    ctrl.set_budget(Budget("娱乐", 300))

    # 设置策略（第 2 周对接后才生效）
    # ctrl.set_diagnosis_strategy(CompositeDiagnosis([...]))

    # 主循环
    while True:
        print_menu()
        choice = input("请选择: ")
        if choice == "1":
            for t in ctrl.get_transactions():
                print(f"  {t.date} | {t.type} | {t.category} | ¥{t.amount:.2f} | {t.account.value} | {t.note}")
        elif choice == "2":
            # 交互式录入
            ...
        elif choice == "3":
            for b in ctrl.get_budgets():
                print(f"  {b.category}: 限额 ¥{b.monthly_limit:.0f} | 已支出 ¥{b.current_spent:.0f} | 剩余 ¥{b.get_remaining():.0f}")
        elif choice == "5":
            try:
                report = ctrl.generate_diagnosis()
                print_report(report)
            except RuntimeError as e:
                print(f"错误: {e}")
        # ...
```

---

## 阶段二：CSV 导入模块（第 2 周）

### 文件 1：`services/category_normalizer.py`

把 CSV 中不统一的类别名标准化为 `Transaction.category` 可用的值：

```python
CATEGORY_MAP: dict[str, str] = {
    # 餐饮
    "三餐": "餐饮", "食堂": "餐饮", "吃饭": "餐饮",
    "外卖": "餐饮", "聚餐": "餐饮", "零食": "餐饮",
    "早餐": "餐饮", "午餐": "餐饮", "晚餐": "餐饮",
    # 交通
    "公交": "交通", "地铁": "交通", "打车": "交通",
    "滴滴": "交通", "高铁": "交通", "火车": "交通",
    # 娱乐
    "电影": "娱乐", "游戏": "娱乐", "KTV": "娱乐",
    "旅游": "娱乐", "演出": "娱乐", "运动": "娱乐",
    # 学习
    "书籍": "学习", "文具": "学习", "课程": "学习",
    "培训": "学习", "考试": "学习",
    # 日用
    "超市": "日用", "日用品": "日用", "话费": "日用",
    "衣服": "日用", "网购": "日用", "美妆": "日用",
    # 其他
    "医疗": "其他", "礼物": "其他", "红包": "其他",
    "转账": "其他", "还款": "其他",
}


def normalize_category(raw: str) -> str:
    """标准化类别名。无法匹配时返回原值（去除首尾空白）。"""
    cleaned = raw.strip()
    return CATEGORY_MAP.get(cleaned, cleaned)
```

> 实际映射表可以根据 CSV 数据中的实际类别名扩充。你和组员一起看一遍 CSV 后补充。

### 文件 2：`services/csv_importer.py`

```python
import csv
from datetime import date, datetime
from models.transaction import Transaction, AccountType
from services.category_normalizer import normalize_category


def import_csv(path: str) -> list[Transaction]:
    """
    解析 CSV 文件，返回交易列表。
    CSV 列：date, amount, type, category, account, note

    容错：
    - 空行跳过
    - 日期格式错误跳过并 print 警告
    - amount 非数字跳过并 print 警告
    - account 无法匹配 AccountType 时跳过并 print 警告
    - 第一行为表头时自动跳过（检测 'date' 关键字）
    """
    transactions = []
    skipped = 0

    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            # 跳过空行
            if not row or all(cell.strip() == "" for cell in row):
                continue
            # 跳过表头行
            if i == 0 and "date" in row[0].lower():
                continue

            try:
                if len(row) < 5:
                    raise ValueError("列数不足")

                raw_date, raw_amount, raw_type, raw_category, raw_account = row[0:5]
                raw_note = row[5] if len(row) > 5 else ""

                t_date = _parse_date(raw_date.strip())
                amount = float(raw_amount.strip())
                t_type = raw_type.strip()
                category = normalize_category(raw_category.strip())
                account = _parse_account(raw_account.strip())
                note = raw_note.strip()

                transactions.append(Transaction(
                    amount=amount,
                    type=t_type,
                    category=category,
                    account=account,
                    date=t_date,
                    note=note,
                ))
            except (ValueError, KeyError) as e:
                skipped += 1
                print(f"[CSV] 第{i+1}行跳过: {e} — {row}")

    print(f"[CSV] 导入完成: {len(transactions)} 条成功, {skipped} 条跳过")
    return transactions


def _parse_date(raw: str) -> date:
    """支持 YYYY-MM-DD 和 YYYY/MM/DD"""
    for fmt in ("%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"无法解析日期: {raw}")


def _parse_account(raw: str) -> AccountType:
    """支持 微信/支付宝/现金/银行卡 或 WECHAT/ALIPAY/CASH/BANK_CARD 或英文值"""
    mapping = {
        "微信": AccountType.WECHAT, "wechat": AccountType.WECHAT, "WECHAT": AccountType.WECHAT,
        "支付宝": AccountType.ALIPAY, "alipay": AccountType.ALIPAY, "ALIPAY": AccountType.ALIPAY,
        "现金": AccountType.CASH, "cash": AccountType.CASH, "CASH": AccountType.CASH,
        "银行卡": AccountType.BANK_CARD, "bank": AccountType.BANK_CARD, "BANK_CARD": AccountType.BANK_CARD,
    }
    key = raw.strip()
    if key in mapping:
        return mapping[key]
    raise KeyError(f"未知账户类型: {raw}")
```

**注意**：
- 编码用 `utf-8-sig` 以兼容带 BOM 的 CSV（Excel 导出常见）
- 每行错误单独捕获，不因一行坏数据中断整个导入
- 最终 CSV 列名以实际数据为准，可能需要调整列序

---

## 阶段三：集成测试 + 演示数据（第 3-4 周）

### 集成测试要点
1. CSV 导入 → 确认交易列表正确
2. 设置预算 → 添加多笔支出 → 确认预警触发
3. 设置诊断策略 → generate_diagnosis() → 确认报告合理
4. 设置预算规则 → apply_budget_rule() → 确认分配结果
5. 储蓄倒推 → 确认不同目标输出不同 MonthlyPlan
6. 切换储蓄方法 → 确认不同方法输出不同 SavingsPlan
7. 以上全部从 CLI 和 GUI 各跑一遍

### 演示数据
从 CSV 中选取"健康月"和"不健康月"各一段：
- **健康月**：各项支出在预算内、储蓄率 ≥20%
- **不健康月**：餐饮或娱乐严重超支、储蓄率 <0

打印对比诊断报告，作为答辩演示素材。

---

## 时间线

| 周 | 任务 |
|---|---|
| 第 1 周 | CLI 原型：用 C 的实体类 + 硬编码假数据，实现菜单 1-4、7。把 API 问题反馈给 C |
| 第 2 周 | CSV 导入模块 + CategoryNormalizer 完成并测试。CSV 导入成功后，所有交易在 CLI 和 GUI 中可见 |
| 第 3 周 | D 和 E 的策略接入 CLI，跑集成测试，记录所有 bug 反馈 |
| 第 4 周 | 演示数据准备 + 答辩文档辅助 |

---

## 注意事项

- CSV 解析要容错：一行坏数据不应该中断整个导入
- `CategoryNormalizer` 的映射表是一个起点，需要根据实际 CSV 数据扩充
- CLI 原型的目的不是做出一个完整的命令行程序，而是**验证 Controller API**——发现签名不合理、返回值不对的地方，第 1 周就改
- 集成测试时关注边界情况：空列表（无交易时诊断会不会崩？）、数据不足 1 个月时储蓄倒推的行为
