# services — 业务服务模块
from .category_normalizer import (
    normalize_category,         # 通用简单查表
    normalize_alipay_category,  # 支付宝专用：交易分类→标准类别
    infer_category_wechat,      # 微信专用：商户名+商品→推断类别
    CATEGORY_MAP,               # 简单映射表（兼容旧代码）
)
from .csv_importer import import_csv  # -> tuple[list[Transaction], int]
from .finance_controller import FinanceController
