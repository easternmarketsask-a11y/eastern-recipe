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

def detect_price_unit(doc):
    """称重→'lb'，否则'each'。优先 Firestore 的 is_weighed / price_unit 信号，
    再退到商品名里的重量标记。兼容传入裸商品名字符串（仅按名字判断）。"""
    if isinstance(doc, dict):
        if doc.get("is_weighed") is True:
            return "lb"
        pu = (doc.get("price_unit") or "").strip().lower()
        if pu in ("lb", "kg"):
            return "lb"
        name = doc.get("name") or ""
    else:
        name = doc or ""
    if _WEIGHT_RE.search(name):
        return "lb"
    return "each"

def normalize_category(raw, valid):
    """命中 9 类规范则原样返回；否则保留原值（导出器会另行告警，不静默丢弃）。"""
    raw = (raw or "").strip()
    return raw if raw in valid else raw

def build_product_record(doc, valid_categories, sold_90d=0):
    """Firestore product doc → 公开站 products.json 的一条记录。"""
    cn, en = split_name(doc.get("name"))
    # 真实 Firestore 字段是 isActive（无 available 字段）；缺失或 None 视为在售（未知≠下架）
    raw_active = doc.get("isActive", doc.get("available"))
    active = True if raw_active is None else bool(raw_active)
    on_sale = active and not bool(doc.get("deleted", False))
    return {
        "code": doc.get("code", ""),
        "name_cn": cn,
        "name_en": en,
        "price": doc.get("price"),
        "price_unit": detect_price_unit(doc),
        "category": normalize_category(doc.get("category"), valid_categories),
        "image_url": doc.get("imageUrl", "") or "",
        "on_sale": on_sale,
        "sold_90d": sold_90d,
    }

def score_match(ingredient, products):
    """给食材在商品列表里的候选打分，返回 [(product, score), ...] 按分降序。
    打分：中文子串命中 +2；英文 token 命中 +1/词；归一后完全相等 +1。"""
    ing = (ingredient or "").strip().lower()
    ing_cn = ing
    ing_tokens = [t for t in re.split(r'\s+', ing) if t]
    ranked = []
    for p in products:
        cn = (p.get("name_cn") or "").lower()
        en = (p.get("name_en") or "").lower()
        score = 0.0
        if ing_cn and ing_cn in cn:
            score += 2.0
        for tok in ing_tokens:
            if tok and (tok in en or tok in cn):
                score += 1.0
        if ing_cn and (ing_cn == cn or ing_cn == en):
            score += 1.0
        ranked.append((p, score))
    ranked.sort(key=lambda x: x[1], reverse=True)
    return ranked
