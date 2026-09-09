# -*- coding: utf-8 -*-
"""static_pages.py — 生成可被搜索引擎收录的静态菜页所需的纯函数。

背景：站点本体是 hash 路由的单页应用（#/r/<id>），对 Google 来说整站只有
一个网址，73 道菜藏在井号后面爬不到。这里为每道菜产出一个真实网址
/r/<id>.html，页面自带完整食材与做法（不依赖 JS）、Recipe 结构化数据、
以及自己的分享大图，让「XX 怎么做」这类搜索能落到我们站上。

本模块无 IO、无网络，便于 TDD；读写文件的部分在 build_static_pages.py。
"""
import json
import re

SITE = "https://recipe.easternmarket.ca"
STORE_NAME = "Eastern Market 东方超市"
STORE_ADDR = "133-412 Willowgrove Square, Saskatoon, Saskatchewan"

# 与 index.html / app.js 的 SEC_TITLE 保持一致
SEC_TITLE = {
    "season": "🥮 中秋 · 应季",
    "tonight": "🔥 今晚吃什么",
    "cantonese": "🥢 粤菜 · 广式",
    "veg": "🥗 家常蔬菜",
    "seafood": "🐟 海鲜河鲜",
    "fresh": "🍜 鲜河粉 · 鲜肠粉",
    "breakfast": "🌅 早餐包点",
    "staple": "🍚 主食 · 面饭",
    "other": "🍳 家常菜",
    "dumpling": "🥟 饺子 · 馄饨",
}
SEC_ORDER = list(SEC_TITLE)


# ── HTML / URL ───────────────────────────────────────────────────────────────

def h(s):
    """HTML 转义。属性值也用它，所以引号必须一起转。"""
    return (str("" if s is None else s)
            .replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def recipe_path(rid):
    """写盘用的相对路径。"""
    return "r/%s.html" % rid


def recipe_url(rid):
    """canonical 用的绝对网址 —— 这才是给 Google 收录的地址。"""
    return "%s/%s" % (SITE, recipe_path(rid))


def app_url(rid):
    """回到单页应用里这道菜（收藏、购物清单等交互都在那边）。"""
    return "%s/#/r/%s" % (SITE, rid)


def absolute(path):
    """站内相对路径 → 绝对网址；已是绝对地址的原样返回（og:image 必须绝对）。"""
    if not path:
        return ""
    if re.match(r'^https?://', path):
        return path
    return "%s/%s" % (SITE, path.lstrip("/"))


def webp_for(image, variant):
    """assets/images/x.jpg → assets/images/webp/x-400.webp（card）/ x.webp（hero）。

    非 jpg 一律返回 None，让调用方退回原图，不要凭空拼一个不存在的地址。
    """
    m = re.match(r'^(.*/)([^/]+)\.jpe?g$', image or '', re.I)
    if not m:
        return None
    suffix = "-400" if variant == "card" else ""
    return "%swebp/%s%s.webp" % (m.group(1), m.group(2), suffix)


# ── 摘要 ─────────────────────────────────────────────────────────────────────

_MAX_DESC = 155


def meta_description(recipe):
    """搜索结果里那两行字。控制在 155 字内，超出会被 Google 截断。"""
    name = recipe.get("name_cn") or ""
    if recipe.get("kind") == "ready":
        base = "%s——东方超市本店有售，买回家蒸一蒸就能吃。" % name
    else:
        mains = [i.get("label") for i in (recipe.get("ingredients") or [])
                 if i.get("required") and i.get("label")][:3]
        food = "、".join(mains)
        base = "%s的家常做法：%s，一步步跟着做。食材在东方超市都买得到。" % (name, food) \
            if food else "%s的家常做法，一步步跟着做。食材在东方超市都买得到。" % name
    base = re.sub(r'\s+', ' ', base).strip()
    return base[:_MAX_DESC]


# ── 结构化数据 ───────────────────────────────────────────────────────────────

def recipe_jsonld(recipe, product_index):
    """schema.org/Recipe。Google 的食谱富媒体结果认这个。"""
    steps = []
    for i, text in enumerate(recipe.get("steps") or []):
        steps.append({"@type": "HowToStep", "position": i + 1, "text": text})

    ings = []
    for ing in recipe.get("ingredients") or []:
        label = ing.get("label") or ""
        qty = ing.get("qty") or ""
        ings.append(("%s %s" % (label, qty)).strip())

    doc = {
        "@context": "https://schema.org",
        "@type": "Recipe",
        "name": recipe.get("name_cn") or "",
        "inLanguage": "zh-CN",
        "url": recipe_url(recipe.get("id")),
        "description": meta_description(recipe),
        "recipeIngredient": ings,
        "recipeInstructions": steps,
        "author": {"@type": "Organization", "name": STORE_NAME},
        "publisher": {
            "@type": "GroceryStore",
            "name": STORE_NAME,
            "address": STORE_ADDR,
            "url": "https://easternmarket.ca",
        },
    }
    if recipe.get("image"):
        doc["image"] = [absolute(recipe["image"])]
    if recipe.get("name_en"):
        doc["alternateName"] = recipe["name_en"]
    if recipe.get("tags"):
        doc["keywords"] = "，".join(recipe["tags"])
    if recipe.get("nutrition"):
        doc["nutrition"] = {"@type": "NutritionInformation",
                            "description": recipe["nutrition"]}
    cat = SEC_TITLE.get(recipe.get("section"))
    if cat:
        doc["recipeCategory"] = re.sub(r'^[^\w一-鿿]+', '', cat).strip()
    return doc


def jsonld_script(recipe, product_index):
    """把 JSON-LD 包成 <script>。

    ensure_ascii=False 保留中文（可读且省体积）；`<` 一律转成 \\u003c，
    否则菜名或步骤里一旦出现 </script> 就会把页面截断。
    """
    body = json.dumps(recipe_jsonld(recipe, product_index),
                      ensure_ascii=False, indent=2)
    body = body.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    return '<script type="application/ld+json">\n%s\n</script>' % body


# ── 站内互链 ─────────────────────────────────────────────────────────────────

def related(recipe, all_recipes, n):
    """同板块优先，不够再拿别的板块补。给爬虫留爬行路径，也方便顾客继续逛。"""
    rid = recipe.get("id")
    same, other = [], []
    for r in all_recipes:
        if r.get("id") == rid:
            continue
        (same if r.get("section") == recipe.get("section") else other).append(r)
    return (same + other)[:n]


# ── sitemap / robots ─────────────────────────────────────────────────────────

def sitemap_xml(urls, lastmod):
    rows = []
    for u in urls:
        rows.append("  <url><loc>%s</loc><lastmod>%s</lastmod></url>" % (h(u), h(lastmod)))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "\n".join(rows) + "\n</urlset>\n")


def robots_txt():
    return ("User-agent: *\n"
            "Disallow:\n"
            "\n"
            "Sitemap: %s/sitemap.xml\n" % SITE)
