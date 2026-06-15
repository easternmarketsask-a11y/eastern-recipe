import recipe_lib as rl

def test_split_name_mixed():
    cn, en = rl.split_name("LH Mushroom Seasoning 香菇调味料 500g")
    assert cn == "香菇调味料 500g"
    assert en == "LH Mushroom Seasoning"

def test_split_name_cn_only():
    cn, en = rl.split_name("嫩豆腐")
    assert cn == "嫩豆腐"
    assert en == ""

def test_detect_price_unit_weight():
    assert rl.detect_price_unit("Tong Ho Crown Daisy 茼蒿", "lb") == "lb"
    assert rl.detect_price_unit("Cilantro 芫荽", "") == "each"

def test_normalize_category_known():
    valid = {"新鲜蔬菜", "干货调料"}
    assert rl.normalize_category("新鲜蔬菜", valid) == "新鲜蔬菜"

def test_normalize_category_unknown_falls_back():
    valid = {"新鲜蔬菜"}
    assert rl.normalize_category("未知类", valid) == "未知类"  # 保留原值，导出器另行告警

def test_build_product_record():
    doc = {"code": "10588", "name": "Cilantro 芫荽", "price": 0.99,
           "category": "新鲜蔬菜", "imageUrl": "http://x/c.jpg",
           "clover_unit": "lb", "available": True, "deleted": False}
    rec = rl.build_product_record(doc, valid_categories={"新鲜蔬菜"}, sold_90d=142)
    assert rec == {
        "code": "10588", "name_cn": "芫荽", "name_en": "Cilantro",
        "price": 0.99, "price_unit": "lb", "category": "新鲜蔬菜",
        "image_url": "http://x/c.jpg", "on_sale": True, "sold_90d": 142,
    }

def test_score_match_exact_substring_wins():
    prods = [
        {"code": "a", "name_cn": "嫩豆腐", "name_en": "Soft Tofu"},
        {"code": "b", "name_cn": "豆腐干", "name_en": "Dried Tofu"},
        {"code": "c", "name_cn": "白萝卜", "name_en": "Daikon"},
    ]
    ranked = rl.score_match("豆腐", prods)
    assert ranked[0][0]["code"] in ("a", "b")   # 含"豆腐"的排前
    assert ranked[-1][0]["code"] == "c"          # 不相关排末
    assert ranked[0][1] >= ranked[-1][1]         # 分数降序

def test_score_match_english_token():
    prods = [{"code": "a", "name_cn": "丹丹豆瓣酱", "name_en": "Dan Dan Bean Paste"}]
    ranked = rl.score_match("bean paste", prods)
    assert ranked[0][1] > 0
