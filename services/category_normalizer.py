# category_normalizer — 类别标准化
# 输入：CSV中的原始类别名/商户名/商品描述
# 输出：标准类别（13个：餐饮/餐饮食品/交通/学习/数码电子/个人护理/
#       家居日用/运动户外/服饰配饰/医疗健康/娱乐/娱乐玩具/其他）
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
# 从规则文件中提取所有有效标准类别（供其他模块引用）
# ============================================================
STANDARD_CATEGORIES: list[str] = sorted(set(
    v for k, v in SIMPLE_CATEGORY_MAP.items()
    if not k.startswith("_")
))

# 向后兼容：旧类别名 → 新类别名（用于已有交易记录的平滑迁移）
LEGACY_CATEGORY_MAP: dict[str, str] = {
    "日用": "家居日用",     # 旧"日用"映射到"家居日用"
}

# 类别父子关系：子类别支出计入父类别预算
# 例如"餐饮食品"的支出自动算在"餐饮"预算里，"娱乐玩具"算在"娱乐"预算里
CATEGORY_PARENTS: dict[str, str] = {
    "餐饮食品": "餐饮",
    "娱乐玩具": "娱乐",
}


# ============================================================
# Pinduoduo store direct mapping
# ============================================================
PINDUODUO_STORE_MAP: dict[str, str] = _rules.get("pinduoduo_store_rules", {}).get("店铺映射", {})


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
    """微信专用：根据商户名和商品描述推断类别。支持拼多多商户直查。"""
    m = merchant.strip()
    p = product.strip()

    # 0. 先查拼多多商户直查表（精确商户名匹配）
    if m in PINDUODUO_STORE_MAP:
        return PINDUODUO_STORE_MAP[m]

    # 1. 关键词规则匹配
    for merchants, products, category in WECHAT_KEYWORD_RULES:
        if any(kw in m for kw in merchants):
            return category
        if any(kw in p for kw in products):
            return category

    # 2. 全部未匹配 → 其他
    return "其他"


def normalize_category_legacy(raw: str) -> str:
    """带向后兼容的类别标准化。如果匹配到旧类别名，自动转为新类别名。"""
    cleaned = raw.strip()
    result = SIMPLE_CATEGORY_MAP.get(cleaned, cleaned)
    # 如果是旧类别名，映射到新类别名
    return LEGACY_CATEGORY_MAP.get(result, result)


# 兼容旧接口
def normalize_category(raw: str) -> str:
    """通用类别标准化（简单查表）。用于非微信/支付宝来源"""
    return normalize_simple(raw)


# 对外暴露的映射表（兼容旧代码引用）
CATEGORY_MAP = SIMPLE_CATEGORY_MAP
