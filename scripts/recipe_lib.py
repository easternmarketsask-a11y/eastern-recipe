"""recipe_lib.py — 导出器/绑定器共用的纯函数。无网络、无副作用，便于 TDD。"""
import re

_WEIGHT_RE = re.compile(r'\b(lb|lbs|kg|/lb|per\s*lb)\b', re.I)

def split_name(name):
    """把 Clover 混排名拆成 (中文, 英文)。中文=含 CJK 的连续片段，英文=其余拉丁片段。
    一旦遇到含 CJK 的 token，其后所有 token（含规格如 500g）都归中文侧。"""
    s = (name or "").strip()
    tokens = s.split()
    # 找到第一个含 CJK 字符的 token 位置
    first_cn = next((i for i, t in enumerate(tokens) if re.search(r'[一-鿿]', t)), None)
    if first_cn is None:
        return ("", s)
    en_parts = tokens[:first_cn]
    cn_parts = tokens[first_cn:]
    return (" ".join(cn_parts).strip(), " ".join(en_parts).strip())

def detect_price_unit(name, clover_unit):
    """称重→'lb'，否则'each'。优先看 Clover 单位，其次商品名里的重量标记。"""
    if (clover_unit or "").strip().lower() in ("lb", "kg"):
        return "lb"
    if _WEIGHT_RE.search(name or ""):
        return "lb"
    return "each"

def normalize_category(raw, valid):
    """命中 9 类规范则原样返回；否则保留原值（导出器会另行告警，不静默丢弃）。"""
    raw = (raw or "").strip()
    return raw if raw in valid else raw

def build_product_record(doc, valid_categories, sold_90d=0):
    """Firestore product doc → 公开站 products.json 的一条记录。"""
    cn, en = split_name(doc.get("name"))
    on_sale = bool(doc.get("available", True)) and not bool(doc.get("deleted", False))
    return {
        "code": doc.get("code", ""),
        "name_cn": cn,
        "name_en": en,
        "price": doc.get("price"),
        "price_unit": detect_price_unit(doc.get("name"), doc.get("clover_unit")),
        "category": normalize_category(doc.get("category"), valid_categories),
        "image_url": doc.get("imageUrl", "") or "",
        "on_sale": on_sale,
        "sold_90d": sold_90d,
    }
