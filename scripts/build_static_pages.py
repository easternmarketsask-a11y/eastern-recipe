# -*- coding: utf-8 -*-
"""build_static_pages.py — 为每道菜生成一个可被搜索引擎收录的静态网页。

产出（都在仓库根目录，直接由 GitHub Pages 提供）：
    r/<id>.html    每道菜一页，无 JS 也能完整阅读，自带 Recipe 结构化数据
    r/index.html   全部食谱目录，给爬虫和顾客一条走得通的路
    sitemap.xml    首页 + 目录页 + 每道菜
    robots.txt     放行抓取并指向 sitemap

为什么需要它：站点本体是 hash 路由（#/r/<id>），对 Google 来说整站只有一个
网址。静态页是搜索入口，页面里的按钮再把人送回单页应用去收藏、凑购物清单。

改完食谱或图片后重新跑一次：
    python scripts/build_static_pages.py
"""
import io
import json
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import static_pages as sp

OUT_DIR = "r"
CSS_V = "18"
ASSET_V = "1"
DELIVERY_URL = "https://easternmarket.ca/group-order"

GRP_ICON = {"新鲜蔬菜": "🥬", "新鲜水果": "🍎", "冷冻食品": "🧊", "豆腐蛋品": "🥚",
            "米面粮油": "🍚", "干货调料": "🧂", "零食饮料": "🥤", "日用杂货": "🧺",
            "中成药品": "🌿"}

PAGE_CSS = """
.pg-crumb{font-size:12px;color:var(--muted);margin:10px 0 4px}
.pg-crumb a{color:var(--green);text-decoration:none}
.pg-h1{margin:6px 0 10px;font-size:23px;color:var(--green-d);line-height:1.3}
.pg-h1 small{display:block;font-size:13px;color:var(--muted);font-weight:400;margin-top:3px}
.pg-h2{font-size:16px;font-weight:600;color:var(--green-d);margin:20px 0 10px}
.pg-lede{font-size:13.5px;color:var(--muted);line-height:1.7;margin:0 0 12px}
.pg-cta{display:flex;gap:8px;flex-wrap:wrap;margin:16px 0 4px}
.pg-cta .mini-btn{flex:1 1 42%}
.pg-cta .mini-btn--go{background:var(--green);color:#fff;border-color:var(--green)}
.pg-more{margin:22px 0 8px}
.pg-allrecipes{display:block;text-align:center;margin:22px 0 4px;color:var(--green);font-size:13px}
.pg-secgrp{margin:22px 0}
.pg-seclist{list-style:none;padding:0;margin:0;display:grid;
  grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:6px 14px}
.pg-seclist a{color:var(--ink);text-decoration:none;font-size:14px;line-height:2}
.pg-seclist a:hover{color:var(--green)}
"""


def head(title, desc, canonical, image, extra=""):
    og_img = sp.absolute(image) if image else "%s/apple-touch-icon.png" % sp.SITE
    return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>%(title)s</title>
<meta name="description" content="%(desc)s">
<link rel="canonical" href="%(canon)s">
<meta property="og:type" content="article">
<meta property="og:title" content="%(title)s">
<meta property="og:description" content="%(desc)s">
<meta property="og:image" content="%(ogimg)s">
<meta property="og:url" content="%(canon)s">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.ico?v=%(av)s" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="/icons/favicon-32.png?v=%(av)s">
<link rel="apple-touch-icon" href="/apple-touch-icon.png?v=%(av)s">
<link rel="stylesheet" href="/css/app.css?v=%(cv)s">
<style>%(css)s</style>
%(extra)s
</head>
<body>
<header class="hdr">
  <div class="hdr__top">
    <a class="hdr__logobtn" href="https://easternmarket.ca" aria-label="东方超市 · 进入主网首页">
      <img class="hdr__logo" src="/assets/logo-horizontal.png?v=%(av)s" alt="东方超市 Eastern Market" width="1080" height="556">
    </a>
    <a class="hdr__name" href="/" style="text-decoration:none">天天新鲜 家常食谱</a>
  </div>
</header>
<main>
""" % {"title": sp.h(title), "desc": sp.h(desc), "canon": sp.h(canonical),
       "ogimg": sp.h(og_img), "cv": CSS_V, "av": ASSET_V,
       "css": PAGE_CSS, "extra": extra}


FOOT = """</main>
<footer class="ftr">
  <strong>Eastern Market 东方超市</strong><br>
  133-412 Willowgrove Square, Saskatoon<br>
  周一至周六 10am–6:30pm<br>
  <a href="https://maps.google.com/?q=Eastern+Market,+412+Willowgrove+Square,+Saskatoon" target="_blank" rel="noopener">📍 地图导航</a>　·　<a href="https://easternmarket.ca">🛒 网上超市</a>　·　<a href="/r/">📖 全部食谱</a><br>
  <span class="ftr__fine">以店内实际供应为准 · 食谱图片仅供参考</span>
</footer>
</body>
</html>
"""


def picture(image, variant, cls, alt):
    """与 app.js 的 picture() 同口径：优先 WebP，浏览器不认回退原 .jpg。"""
    if not image:
        return ""
    img = '<img class="%s" src="%s" alt="%s">' % (sp.h(cls), sp.h("/" + image), sp.h(alt))
    webp = sp.webp_for(image, variant)
    if not webp:
        return img
    return ('<picture><source type="image/webp" srcset="%s">%s</picture>'
            % (sp.h("/" + webp), img))


def card_html(r):
    img = picture(r.get("image"), "card", "card__img", r.get("name_cn") or "")
    en = ('<span class="card__en">%s</span>' % sp.h(r["name_en"])) if r.get("name_en") else ""
    nut = ('<span class="card__nutri">🌿 %s</span>' % sp.h(r["nutrition"])) if r.get("nutrition") else ""
    return ('<a class="card" href="/%s">%s<span class="card__body">'
            '<span class="card__name">%s</span>%s%s</span></a>'
            % (sp.h(sp.recipe_path(r["id"])), img, sp.h(r.get("name_cn") or ""), en, nut))


def recipe_page(r, pidx, all_recipes):
    rid = r["id"]
    name = r.get("name_cn") or ""
    is_ready = r.get("kind") == "ready"
    title = "%s%s · 东方超市家常食谱" % (name, "" if is_ready else "的做法")
    desc = sp.meta_description(r)

    parts = [head(title, desc, sp.recipe_url(rid), r.get("image"),
                  extra=sp.jsonld_script(r, pidx))]

    sec = r.get("section")
    sec_title = sp.SEC_TITLE.get(sec, "")
    parts.append('<nav class="pg-crumb"><a href="/">首页</a> › '
                 '<a href="/#/sec/%s">%s</a> › %s</nav>'
                 % (sp.h(sec), sp.h(sec_title), sp.h(name)))

    parts.append(picture(r.get("image"), "hero", "detail__img", name))
    parts.append('<h1 class="pg-h1">%s%s</h1>'
                 % (sp.h(name),
                    ('<small>%s</small>' % sp.h(r["name_en"])) if r.get("name_en") else ""))
    if r.get("nutrition"):
        parts.append('<div class="detail__nutri">🌿 营养 · %s</div>' % sp.h(r["nutrition"]))
    parts.append('<p class="pg-lede">%s</p>' % sp.h(desc))

    # 食材
    if is_ready:
        parts.append('<div class="ready-tag">🛒 本店有售</div>')
    parts.append('<h2 class="pg-h2">%s</h2>' % ("店里有这些口味" if is_ready else "要买什么"))
    rows = []
    for ing in r.get("ingredients") or []:
        p = pidx.get(ing.get("code")) if ing.get("code") else None
        cat = (p or {}).get("category") or ""
        cat_html = ('<span class="ing__cat">%s %s</span>' % (GRP_ICON.get(cat, "🛒"), sp.h(cat))) if cat else ""
        rows.append('<li class="ing"><span class="ing__name">%s</span>'
                    '<span class="ing__qty">%s</span>%s</li>'
                    % (sp.h(ing.get("label") or ""), sp.h(ing.get("qty") or ""), cat_html))
    parts.append('<ul class="ings">%s</ul>' % "".join(rows))

    parts.append('<div class="pg-cta">'
                 '<a class="mini-btn mini-btn--go" href="%s">♡ 加入想做 · 凑购物清单</a>'
                 '<a class="mini-btn" href="%s" target="_blank" rel="noopener">🚚 网上下单</a>'
                 '</div>' % (sp.h(sp.app_url(rid)), sp.h(DELIVERY_URL)))

    # 做法
    parts.append('<h2 class="pg-h2">%s</h2>' % ("怎么吃" if is_ready else "做法"))
    parts.append('<ol class="steps">%s</ol>'
                 % "".join('<li>%s</li>' % sp.h(s) for s in (r.get("steps") or [])))

    rel = sp.related(r, all_recipes, 6)
    if rel:
        parts.append('<div class="pg-more"><h2 class="pg-h2">换个菜看看</h2>'
                     '<div class="cards">%s</div></div>' % "".join(card_html(x) for x in rel))
    parts.append('<a class="pg-allrecipes" href="/r/">📖 看全部 %d 道食谱 ›</a>' % len(all_recipes))
    parts.append(FOOT)
    return "".join(parts)


def index_page(all_recipes):
    """全部食谱目录：爬虫从这里能一跳走到每一道菜。"""
    n = len(all_recipes)
    title = "全部 %d 道家常食谱 · 东方超市" % n
    desc = ("东方超市家常食谱目录，共 %d 道：中秋应季、今晚吃什么、粤菜、家常蔬菜、"
            "海鲜河鲜、早餐包点、饺子馄饨等。食材在店里都买得到。" % n)[:155]
    parts = [head(title, desc, "%s/r/" % sp.SITE, None)]
    parts.append('<nav class="pg-crumb"><a href="/">首页</a> › 全部食谱</nav>')
    parts.append('<h1 class="pg-h1">全部食谱<small>共 %d 道 · 按板块分组</small></h1>' % n)
    by_sec = {}
    for r in all_recipes:
        by_sec.setdefault(r.get("section"), []).append(r)
    for sec in sp.SEC_ORDER:
        lst = sorted(by_sec.get(sec, []), key=lambda x: -(x.get("priority") or 0))
        if not lst:
            continue
        parts.append('<div class="pg-secgrp"><h2 class="pg-h2">%s（%d）</h2><ul class="pg-seclist">%s</ul></div>'
                     % (sp.h(sp.SEC_TITLE[sec]), len(lst),
                        "".join('<li><a href="/%s">%s</a></li>'
                                % (sp.h(sp.recipe_path(r["id"])), sp.h(r.get("name_cn") or ""))
                                for r in lst)))
    parts.append(FOOT)
    return "".join(parts)


def main():
    recipes = json.load(io.open("data/recipes.json", encoding="utf-8"))["recipes"]
    pidx = {p["code"]: p for p in json.load(io.open("data/products.json", encoding="utf-8"))["items"]}
    if not os.path.isdir(OUT_DIR):
        os.makedirs(OUT_DIR)

    ordered = sorted(recipes,
                     key=lambda r: (sp.SEC_ORDER.index(r["section"])
                                    if r.get("section") in sp.SEC_ORDER else 99,
                                    -(r.get("priority") or 0)))
    for r in ordered:
        with io.open(sp.recipe_path(r["id"]), "w", encoding="utf-8") as f:
            f.write(recipe_page(r, pidx, ordered))
    with io.open(os.path.join(OUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_page(ordered))

    today = date.today().isoformat()
    urls = ["%s/" % sp.SITE, "%s/r/" % sp.SITE] + [sp.recipe_url(r["id"]) for r in ordered]
    with io.open("sitemap.xml", "w", encoding="utf-8") as f:
        f.write(sp.sitemap_xml(urls, today))
    with io.open("robots.txt", "w", encoding="utf-8") as f:
        f.write(sp.robots_txt())

    print("生成 %d 个菜页 + 目录页" % len(ordered))
    print("sitemap.xml: %d 条网址" % len(urls))
    print("robots.txt: 放行抓取")
    return 0


if __name__ == "__main__":
    sys.exit(main())
