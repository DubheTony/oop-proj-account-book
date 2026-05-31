# csv_importer — 从微信/支付宝导出的CSV文件导入交易记录
#
# 支持的格式：
#   - 微信支付账单导出（UTF-8-BOM, 11列）
#   - 支付宝交易明细导出（GBK, 12列）
#
# 容错设计：一行坏数据不中断整个导入
import csv
from datetime import date, datetime
from models.transaction import Transaction, AccountType
from services.category_normalizer import (
    normalize_alipay_category,
    infer_category_wechat,
)


# ============================================================
# 格式检测
# ============================================================

def _detect_format(path: str) -> str:
    """检测CSV文件来源，返回 'wechat' 或 'alipay'。

    先尝试 UTF-8-BOM 编码，扫描前几行找特征字符串；
    UTF-8 失败则尝试 GBK。
    """
    # 先试 UTF-8-BOM（微信）
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            head = "".join(f.readline() for _ in range(6))
        if "微信支付账单明细" in head:
            return "wechat"
        if "支付宝交易明细" in head or "支付宝" in head:
            return "alipay"
    except UnicodeDecodeError:
        pass

    # 再试 GBK（支付宝）
    try:
        with open(path, "r", encoding="gbk") as f:
            head = "".join(f.readline() for _ in range(6))
        if "支付宝" in head:
            return "alipay"
    except UnicodeDecodeError:
        pass

    # 两种编码都失败 → 最后尝试 UTF-8
    try:
        with open(path, "r", encoding="utf-8") as f:
            head = "".join(f.readline() for _ in range(6))
        if "微信支付账单明细" in head or "微信" in head:
            return "wechat"
        if "支付宝" in head:
            return "alipay"
    except UnicodeDecodeError:
        raise ValueError("无法解码文件，支持的编码: UTF-8, GBK")

    raise ValueError("无法识别的CSV格式，支持的格式: 微信支付账单导出、支付宝交易明细导出")


# ============================================================
# 表头定位
# ============================================================

def _find_header_row(reader) -> int:
    """在reader中定位表头行（第0列为'交易时间'）。
    返回表头所在行号(0-based)。找不到返回 -1。
    """
    for i, row in enumerate(reader):
        if row and row[0].strip() == "交易时间":
            return i
    return -1


# ============================================================
# 金额解析
# ============================================================

def _parse_amount(raw: str) -> float:
    """解析金额字符串，支持 ¥29.24 和 ¥2,000.00 格式"""
    s = raw.strip()
    s = s.lstrip("¥").lstrip("￥")  # 去掉 ¥ 前缀
    s = s.replace(",", "")          # 去掉千位逗号
    return float(s)


# ============================================================
# 日期解析
# ============================================================

def _parse_date(raw: str) -> date:
    """解析日期，支持 YYYY-MM-DD 和 YYYY-MM-DD HH:mm:ss"""
    s = raw.strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"无法解析日期: {raw}")


# ============================================================
# 主入口
# ============================================================

def import_csv(path: str) -> tuple[list[Transaction], int]:
    """自动检测CSV格式（微信/支付宝），解析并返回交易列表。

    返回:
        (transactions, skipped_count)
        - transactions: 成功解析的Transaction列表
        - skipped_count: 跳过的行数（格式错误 + 中性交易过滤）

    异常:
        ValueError: 无法识别的CSV格式
    """
    fmt = _detect_format(path)

    if fmt == "wechat":
        return _import_wechat(path)
    else:
        return _import_alipay(path)


# ============================================================
# 微信解析
# ============================================================

def _import_wechat(path: str) -> tuple[list[Transaction], int]:
    """解析微信支付账单CSV"""
    transactions = []
    skipped = 0

    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header_row = _find_header_row(reader)
        if header_row < 0:
            print("[CSV] 警告: 未找到表头行，返回空列表")
            return [], 0

        # 从表头下一行开始读数据
        for i, row in enumerate(reader):
            # header_row=表头行号, +1跳表头, +i跳过已读数据行, +1转人类行号(从1开始)
            actual_row = header_row + i + 2

            # 跳过空行
            if not row or all(c.strip() == "" for c in row):
                continue
            # 跳过分隔线
            if row[0].startswith("-"):
                continue

            try:
                if len(row) < 6:
                    raise ValueError("列数不足")

                # 微信列布局（11列）:
                # 0:交易时间  1:交易类型  2:交易对方  3:商品
                # 4:收/支     5:金额(元)  6:支付方式  7:当前状态
                # 8:交易单号  9:商户单号  10:备注

                raw_date = row[0].strip()
                raw_type = row[4].strip()
                raw_amount = row[5].strip()
                merchant = row[2].strip()      # 用于推断类别
                product = row[3].strip()        # 用于推断类别 + note
                raw_note = row[10].strip() if len(row) > 10 else ""

                # 过滤中性交易（收/支="/"）
                if raw_type == "/":
                    continue  # 静默跳过，不计入 skipped

                # 解析各字段
                t_date = _parse_date(raw_date)
                amount = _parse_amount(raw_amount)
                t_type = "支出" if raw_type == "支出" else "收入"
                # 微信没有类别字段，从商户名推断
                category = infer_category_wechat(merchant, product)
                # 微信来源，账户固定为 WECHAT
                account = AccountType.WECHAT
                # 备注：优先用备注列，为空则用商品描述
                note = raw_note if raw_note and raw_note != "/" else product

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
                print(f"[CSV] 微信第{actual_row}行跳过: {e}")

    # 统计"其他"类别占比，提醒人工复查
    other_count = sum(1 for t in transactions if t.category == "其他")
    if other_count > 0:
        pct = other_count / len(transactions) * 100 if transactions else 0
        print(f"[CSV] 微信: {other_count} 条归入\"其他\"({pct:.0f}%)，建议复查")

    print(f"[CSV] 微信导入完成: {len(transactions)} 条成功, {skipped} 条跳过")
    return transactions, skipped


# ============================================================
# 支付宝解析
# ============================================================

def _import_alipay(path: str) -> tuple[list[Transaction], int]:
    """解析支付宝交易明细CSV"""
    transactions = []
    skipped = 0

    # 支付宝官方导出为GBK，但用户可能用记事本改存为UTF-8
    try:
        f = open(path, "r", encoding="gbk")
    except UnicodeDecodeError:
        f = open(path, "r", encoding="utf-8-sig")

    with f:
        reader = csv.reader(f)
        header_row = _find_header_row(reader)
        if header_row < 0:
            print("[CSV] 警告: 未找到表头行，返回空列表")
            return [], 0

        for i, row in enumerate(reader):
            actual_row = header_row + i + 2

            if not row or all(c.strip() == "" for c in row):
                continue
            if row[0].startswith("-"):
                continue

            try:
                if len(row) < 7:
                    raise ValueError("列数不足")

                # 支付宝列布局（12-13列）:
                # 0:交易时间  1:交易分类  2:交易对方  3:对方账号
                # 4:商品说明  5:收/支     6:金额     7:收/付款方式
                # 8:交易状态  9:交易订单号 10:商家订单号 11:备注 12:(空)

                raw_date = row[0].strip()
                raw_category = row[1].strip()   # 支付宝有交易分类！
                raw_type = row[5].strip()
                raw_amount = row[6].strip()
                raw_note = row[4].strip() if len(row) > 4 else ""  # 商品说明

                # 过滤中性交易
                if raw_type == "不计收支":
                    continue  # 静默跳过

                # 类别映射：支付宝交易分类 → 标准类别
                category = normalize_alipay_category(raw_category)
                if category is None:
                    # 投资理财/退款/账户存取 → 跳过
                    continue

                t_date = _parse_date(raw_date)
                amount = _parse_amount(raw_amount)  # 兼容纯数字和含逗号金额
                t_type = "支出" if raw_type == "支出" else "收入"
                account = AccountType.ALIPAY
                note = raw_note if raw_note else ""

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
                print(f"[CSV] 支付宝第{actual_row}行跳过: {e}")

    # 统计"其他"类别占比，提醒人工复查
    other_count = sum(1 for t in transactions if t.category == "其他")
    if other_count > 0:
        pct = other_count / len(transactions) * 100 if transactions else 0
        print(f"[CSV] 支付宝: {other_count} 条归入\"其他\"({pct:.0f}%)，建议复查")

    print(f"[CSV] 支付宝导入完成: {len(transactions)} 条成功, {skipped} 条跳过")
    return transactions, skipped
