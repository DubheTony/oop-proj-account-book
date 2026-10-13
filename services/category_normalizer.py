# category_normalizer — 类别标准化
# 输入：CSV中的原始类别名/商户名/商品描述
# 输出：标准类别（13个）
# 映射规则存储在 category_rules.json，方便组员协作扩充
import json
from pathlib import Path
from typing import Optional


# ============================================================
# 模块加载时读入规则文件
# ============================================================
_rules_path = Path(__file__).parent / "category_rules.json"

def _load_rules():
    """加载类别映射规则。文件缺失或损坏时返回空规则并打印提示。"""
    try:
        with open(_rules_path, "r", encoding="utf-8") as _f:
            return json.load(_f)
    except FileNotFoundError:
        print(f"[警告] 类别规则文件未找到: {_rules_path}")
        print(f"  请确保 category_rules.json 与本模块在同一目录下。")
        print(f"  当前将使用空规则运行，CSV导入的类别匹配会受到影响。")
        return {}
    except json.JSONDecodeError as e:
        print(f"[警告] 类别规则文件格式错误: {e}")
        print(f"  请检查 {_rules_path} 是否为合法JSON。")
        return {}

_rules = _load_rules()

# 支付宝交易分类映射
ALIPAY_CATEGORY_MAP: dict[str, str] = _rules.get("alipay_category_map", {})
# 支付宝跳过列表（投资理财/退款等不纳入记账）
_skip_cfg = _rules.get("alipay_skip_categories", {})
ALIPAY_SKIP_CATEGORIES: set[str] = set(_skip_cfg.get("列表", []))
# 通用字符串映射
SIMPLE_CATEGORY_MAP: dict[str, str] = _rules.get("simple_category_map", {})
# 微信关键词规则：(商户名关键词列表, 商品关键词列表, 目标类别)
_wechat_cfg = _rules.get("wechat_keyword_rules", {})
WECHAT_KEYWORD_RULES: list[tuple[list[str], list[str], str]] = [
    (r["商户名关键词"], r["商品关键词"], r["类别"])
    for r in _wechat_cfg.get("规则列表", [])
]
# 拼多多商户直查表
_pdd_cfg = _rules.get("pinduoduo_store_rules", {})
PINDUODUO_STORE_MAP: dict[str, str] = _pdd_cfg.get("店铺映射", {})

# ============================================================
# 从规则文件中提取所有有效标准类别（供其他模块引用）
# ============================================================
STANDARD_CATEGORIES: list[str] = sorted(set(
    v for k, v in SIMPLE_CATEGORY_MAP.items() if not k.startswith("_")
)) if SIMPLE_CATEGORY_MAP else [
    # 规则文件缺失时的硬编码回退列表
    "餐饮", "交通", "娱乐", "学习", "家居日用",
    "数码电子", "个人护理", "运动户外", "服饰配饰",
    "医疗健康", "其他",
]

# 向后兼容：旧类别名 → 新类别名（用于已有交易记录的平滑迁移）
LEGACY_CATEGORY_MAP: dict[str, str] = {"日用": "家居日用"}

# 类别父子关系：子类别支出计入父类别预算
# 例如"餐饮食品"的支出自动算在"餐饮"预算里
CATEGORY_PARENTS: dict[str, str] = {
    "餐饮食品": "餐饮",
    "娱乐玩具": "娱乐",
}


# ============================================================
# 对外函数
# ============================================================

def normalize_alipay_category(raw_category: str) -> Optional[str]:
    """支付宝专用：将交易分类映射为标准类别。返回None表示应跳过。"""
    c = raw_category.strip()
    if c in ALIPAY_SKIP_CATEGORIES:
        return None
    return ALIPAY_CATEGORY_MAP.get(c, "其他")


def normalize_simple(raw: str) -> str:
    """简单查表映射，未匹配返回原值"""
    cleaned = raw.strip()
    return SIMPLE_CATEGORY_MAP.get(cleaned, cleaned)


def infer_category_wechat(merchant: str, product: str) -> str:
    """微信专用：根据商户名和商品描述推断类别。"""
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
    """带向后兼容的类别标准化。旧类别名自动转为新类别名。"""
    cleaned = raw.strip()
    result = SIMPLE_CATEGORY_MAP.get(cleaned, cleaned)
    return LEGACY_CATEGORY_MAP.get(result, result)


# 兼容旧接口
normalize_category = normalize_simple
CATEGORY_MAP = SIMPLE_CATEGORY_MAP
