# category_normalizer — 类别标准化
# 输入：CSV中的原始类别名/商户名/商品描述
# 输出：6个标准类别之一（餐饮/交通/娱乐/学习/日用/其他）
# 映射规则存储在 category_rules.json，方便组员协作扩充
import json
from pathlib import Path
from typing import Optional


# ============================================================
# 模块加载时读入规则文件
# ============================================================
_rules_path = Path(__file__).parent / "category_rules.json"
with open(_rules_path, "r", encoding="utf-8") as _f:
    _rules = json.load(_f)

# 支付宝交易分类映射
ALIPAY_CATEGORY_MAP: dict[str, str] = _rules["alipay_category_map"]
# 支付宝跳过列表
ALIPAY_SKIP_CATEGORIES: set[str] = set(_rules["alipay_skip_categories"]["列表"])
# 通用字符串映射
SIMPLE_CATEGORY_MAP: dict[str, str] = _rules["simple_category_map"]
# 微信关键词规则：(商户名列表, 商品列表, 目标类别)
WECHAT_KEYWORD_RULES: list[tuple[list[str], list[str], str]] = [
    (r["商户名关键词"], r["商品关键词"], r["类别"])
    for r in _rules["wechat_keyword_rules"]["规则列表"]
]


# ============================================================
# 对外函数
# ============================================================

def normalize_alipay_category(raw_category: str) -> Optional[str]:
    """支付宝专用：将交易分类映射为标准类别。返回None表示应跳过"""
    c = raw_category.strip()
    if c in ALIPAY_SKIP_CATEGORIES:
        return None  # 投资理财/退款/账户存取 → 跳过
    return ALIPAY_CATEGORY_MAP.get(c, "其他")


def normalize_simple(raw: str) -> str:
    """简单映射：查表匹配，未匹配返回去除空白后的原值"""
    cleaned = raw.strip()
    return SIMPLE_CATEGORY_MAP.get(cleaned, cleaned)


def infer_category_wechat(merchant: str, product: str) -> str:
    """微信专用：根据商户名和商品描述推断类别"""
    m = merchant.strip()
    p = product.strip()

    for merchants, products, category in WECHAT_KEYWORD_RULES:
        # 检查商户名是否含任一关键词
        if any(kw in m for kw in merchants):
            return category
        # 检查商品描述是否含任一关键词
        if any(kw in p for kw in products):
            return category

    # 全部未匹配 → 其他
    return "其他"


# 兼容旧接口
def normalize_category(raw: str) -> str:
    """通用类别标准化（简单查表）。用于非微信/支付宝来源"""
    return normalize_simple(raw)


# 对外暴露的映射表（兼容旧代码引用）
CATEGORY_MAP = SIMPLE_CATEGORY_MAP
