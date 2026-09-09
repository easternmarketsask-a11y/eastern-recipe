# -*- coding: utf-8 -*-
"""static_pages.py 的纯函数测试。跑法：python -m pytest scripts/ -v"""
import json
import re

import pytest

import static_pages as sp

DISH = {
    "id": "mapo-tofu",
    "name_cn": "麻婆豆腐",
    "name_en": "Mapo Tofu",
    "section": "other",
    "kind": "dish",
    "image": "assets/images/mapo-tofu.jpg",
    "nutrition": "高蛋白·下饭",
    "tags": ["川菜", "豆腐"],
    "steps": ["豆腐切块焯水。", "下豆瓣酱炒香。", "勾芡出锅。"],
    "ingredients": [
        {"label": "嫩豆腐", "qty": "1盒", "code": "T1", "required": True},
        {"label": "牛肉碎", "qty": "150g", "code": "T2", "required": True},
        {"label": "花椒粉", "qty": "适量", "code": None, "required": False},
    ],
}
READY = {
    "id": "mooncake-ready",
    "name_cn": "月饼",
    "name_en": "Mooncakes",
    "section": "season",
    "kind": "ready",
    "image": "assets/images/mooncake-ready.jpg",
    "steps": ["切小块分食。"],
    "ingredients": [{"label": "五仁月饼", "qty": "1盒", "code": "T3", "required": True}],
}
PIDX = {
    "T1": {"code": "T1", "name_cn": "嫩豆腐", "category": "豆腐蛋品"},
    "T2": {"code": "T2", "name_cn": "牛肉碎", "category": "冷冻食品"},
    "T3": {"code": "T3", "name_cn": "五仁月饼", "category": "零食饮料"},
}


# ── URL ──────────────────────────────────────────────────────────────────────

def test_recipe_url_is_absolute_https_canonical():
    assert sp.recipe_url("mapo-tofu") == "https://recipe.easternmarket.ca/r/mapo-tofu.html"


def test_recipe_path_is_relative_for_writing_to_disk():
    assert sp.recipe_path("mapo-tofu") == "r/mapo-tofu.html"


def test_app_url_points_back_into_the_hash_app():
    assert sp.app_url("mapo-tofu") == "https://recipe.easternmarket.ca/#/r/mapo-tofu"


def test_absolute_turns_site_relative_asset_into_full_url():
    assert sp.absolute("assets/images/x.jpg") == "https://recipe.easternmarket.ca/assets/images/x.jpg"
    # 已经是绝对地址的原样返回
    assert sp.absolute("https://e.ca/a.jpg") == "https://e.ca/a.jpg"


# ── WebP 派生 ────────────────────────────────────────────────────────────────

def test_webp_for_card_and_hero():
    assert sp.webp_for("assets/images/x.jpg", "card") == "assets/images/webp/x-400.webp"
    assert sp.webp_for("assets/images/x.jpg", "hero") == "assets/images/webp/x.webp"


def test_webp_for_returns_none_when_not_a_jpeg():
    assert sp.webp_for("assets/images/x.png", "hero") is None
    assert sp.webp_for("", "hero") is None
    assert sp.webp_for(None, "hero") is None


# ── 摘要 ─────────────────────────────────────────────────────────────────────

def test_meta_description_mentions_dish_and_store_and_fits_serp():
    d = sp.meta_description(DISH)
    assert "麻婆豆腐" in d
    assert "东方超市" in d
    assert 0 < len(d) <= 155      # 超过约 155 字 Google 会截断
    assert "\n" not in d


def test_meta_description_for_ready_says_in_store():
    assert "本店有售" in sp.meta_description(READY)


# ── JSON-LD ──────────────────────────────────────────────────────────────────

def test_jsonld_is_a_valid_recipe_object():
    d = sp.recipe_jsonld(DISH, PIDX)
    assert d["@context"] == "https://schema.org"
    assert d["@type"] == "Recipe"
    assert d["name"] == "麻婆豆腐"
    assert d["inLanguage"] == "zh-CN"
    assert d["image"] == ["https://recipe.easternmarket.ca/assets/images/mapo-tofu.jpg"]


def test_jsonld_ingredients_carry_quantity():
    d = sp.recipe_jsonld(DISH, PIDX)
    assert d["recipeIngredient"] == ["嫩豆腐 1盒", "牛肉碎 150g", "花椒粉 适量"]


def test_jsonld_instructions_are_howtostep_in_order():
    d = sp.recipe_jsonld(DISH, PIDX)
    steps = d["recipeInstructions"]
    assert [s["@type"] for s in steps] == ["HowToStep"] * 3
    assert steps[0]["text"] == "豆腐切块焯水。"
    assert steps[-1]["text"] == "勾芡出锅。"
    assert [s["position"] for s in steps] == [1, 2, 3]


def test_jsonld_publisher_is_the_store():
    d = sp.recipe_jsonld(DISH, PIDX)
    assert d["publisher"]["@type"] == "Grocery Store" or d["publisher"]["name"] == "Eastern Market 东方超市"


def test_jsonld_serialises_to_json_without_escaping_chinese():
    s = sp.jsonld_script(DISH, PIDX)
    assert "麻婆豆腐" in s          # 不要输出 \u9ebb 这种，可读性 + 体积
    json.loads(re.sub(r'^<script[^>]*>|</script>$', '', s).strip())


def test_jsonld_script_neutralises_closing_script_tag():
    """菜名/步骤里若混进 </script> 会截断页面 —— 必须转义。"""
    evil = dict(DISH, name_cn="坏菜</script><script>alert(1)</script>")
    s = sp.jsonld_script(evil, PIDX)
    body = s[s.index('>') + 1:s.rindex('</script>')]
    assert "</script" not in body          # 正文里不许有未转义的收尾标签
    assert r'\u003c/script' in body      # 内容本身留着，只是被转义


# ── 相关推荐（站内互链，给爬虫爬行路径）────────────────────────────────────────

def test_related_prefers_same_section_and_excludes_self():
    all_r = [DISH,
             dict(DISH, id="a", name_cn="A"),
             dict(DISH, id="b", name_cn="B"),
             dict(READY, id="z", name_cn="Z")]
    rel = sp.related(DISH, all_r, 2)
    ids = [r["id"] for r in rel]
    assert DISH["id"] not in ids
    assert ids == ["a", "b"]


def test_related_falls_back_to_other_sections_when_section_is_thin():
    all_r = [DISH, dict(READY, id="z")]
    rel = sp.related(DISH, all_r, 3)
    assert [r["id"] for r in rel] == ["z"]


# ── sitemap / robots ─────────────────────────────────────────────────────────

def test_sitemap_lists_every_url_once_and_is_wellformed():
    import xml.etree.ElementTree as ET
    urls = ["https://recipe.easternmarket.ca/",
            "https://recipe.easternmarket.ca/r/mapo-tofu.html"]
    xml = sp.sitemap_xml(urls, "2026-09-09")
    root = ET.fromstring(xml.encode("utf-8"))
    got = [e.text for e in root.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
    assert got == urls


def test_sitemap_escapes_ampersands():
    import xml.etree.ElementTree as ET
    xml = sp.sitemap_xml(["https://recipe.easternmarket.ca/r/a&b.html"], "2026-09-09")
    ET.fromstring(xml.encode("utf-8"))     # 未转义的 & 会让解析直接报错


def test_robots_allows_crawling_and_points_at_sitemap():
    r = sp.robots_txt()
    assert "User-agent: *" in r
    assert "Disallow:" in r and "Disallow: /\n" not in r     # 不能整站禁爬
    assert "https://recipe.easternmarket.ca/sitemap.xml" in r


# ── HTML 转义 ────────────────────────────────────────────────────────────────

def test_html_escape_covers_quotes_and_angles():
    assert sp.h('<a href="x">&') == "&lt;a href=&quot;x&quot;&gt;&amp;"
