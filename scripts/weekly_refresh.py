# -*- coding: utf-8 -*-
"""weekly_refresh.py — 每周在售核验（安全版）：只认肯定证据，不确定的只报不改。

为什么不用全量导出：公开 products?limit=5000 已被匿名 200 上限截断
（见 recipe_lib.catalog_shrink_error），全量覆盖会拆掉绑定；且按文档计费，
巡检不扫全表。本脚本沿用 check_content_ingredients.ps1 的定向 search 模式，
一次只查一个条码。

规则（逐条码）：
  精确命中（code/sku 相等）且在售 → 刷新快照里的 name_cn/name_en（分类只跟
    规范值），on_sale 记 True；
  精确命中但 isActive==False 或 deleted → on_sale 记 False（下架的肯定证据）；
  无精确命中 / 同码多档且不在 PINNED_IDS → 不动文件，只进报告；
    若不在 KNOWN 允许表里，退出码 1（要人工看）。

之后照常跑：python scripts/build_static_pages.py（重写 catalog.json +
r/*.html + sitemap.xml），再跑 pytest 与 node --test，都绿才提 PR。
"""
import io
import json
import os
import sys
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import recipe_lib as rl

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RECIPES = os.path.join(ROOT, 'data', 'recipes.json')
PRODUCTS = os.path.join(ROOT, 'data', 'products.json')
API = 'https://stockwise-app-873982544406.us-central1.run.app'
STANDARD_CATS = {'新鲜蔬菜', '新鲜水果', '冷冻食品', '豆腐蛋品', '米面粮油',
                 '干货调料', '零食饮料', '日用杂货', '健康中草药', '中成药品'}

# 同码多档时认准哪一件（Firestore doc id，2026-11-13 直连核过）
PINNED_IDS = {
    '0030': 'IkzltGAFYOg74oXtkrXP',
    '0033': 'r1X4SN4hsXvzO4m1PnRF',
    '0050': 'IneulVaQPBUpSpYrO7mI',
    '4061scsc': 'aaw9W6CzwV8IK7mc1gJA',
    '628719295106': 'GwUHGmSsYKuK90RShiSz',
}
# 已知待办：不动文件，只是不让周任务变红
KNOWN_UNRESOLVED = {
    '9735': '条码已不在库（2026-11-13），niurou-lamian/potato-beef-stew 待改绑',
    'LXLX': '蓝蟹有货但无条码，补码后绑定',
}
KNOWN_AMBIGUOUS = {
    'Hhlo': '洪湖粉藕一码两档（EA600G/box），待确认卖哪种',
}


def api_get(path, params):
    url = API + path + '?' + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=30) as resp:
        return json.load(resp)


def main():
    recipes = json.load(io.open(RECIPES, encoding='utf-8'))['recipes']
    pdoc = json.load(io.open(PRODUCTS, encoding='utf-8'))
    idx = {p.get('code'): p for p in pdoc['items']}
    codes = sorted({(ig.get('code') or '').strip() for r in recipes
                    for ig in (r.get('ingredients') or []) if (ig.get('code') or '').strip()})
    try:
        valid_cats = set(api_get('/api/firebase/categories', {}).get('categories', []))
    except Exception as e:  # noqa: BLE001
        sys.exit('ERROR: categories 接口不可达: %s' % e)

    updated, offed, unres, ambig = [], [], [], []
    for code in codes:
        try:
            hits = api_get('/api/firebase/products', {'limit': 5, 'search': code}).get('products', [])
        except Exception as e:  # noqa: BLE001
            print('QUERY-FAIL %s %s' % (code, e))
            unres.append(code)
            continue
        exact = [h for h in hits if h.get('code') == code or h.get('sku') == code]
        if code in PINNED_IDS:
            exact = [h for h in exact if h.get('id') == PINNED_IDS[code]] or exact
        if not exact:
            if code not in KNOWN_UNRESOLVED:
                print('UNRESOLVED %s' % code)
            unres.append(code)
            continue
        if len(exact) > 1 and code not in PINNED_IDS:
            if code not in KNOWN_AMBIGUOUS:
                print('AMBIGUOUS %s' % code)
            ambig.append(code)
            continue
        doc = exact[0]
        row = idx.get(code)
        if row is None:
            print('UNRESOLVED %s（快照缺行）' % code)
            unres.append(code)
            continue
        live_on = doc.get('isActive', True) is not False and not doc.get('deleted', False)
        if not live_on:
            if row.get('on_sale'):
                row['on_sale'] = False
                offed.append(code)
            continue
        cn, en = rl.split_name(doc.get('name') or '')
        if cn and (cn, en) != (row.get('name_cn'), row.get('name_en')):
            row['name_cn'], row['name_en'] = cn, en
            updated.append(code)
        cat = (doc.get('category') or '').strip()
        if cat and cat in STANDARD_CATS and cat in valid_cats and cat != row.get('category'):
            row['category'] = cat
            updated.append(code)
        row['on_sale'] = True

    with io.open(PRODUCTS, 'w', encoding='utf-8', newline='') as f:
        f.write(json.dumps(pdoc, ensure_ascii=False, indent=2))
    new_unres = [c for c in unres if c not in KNOWN_UNRESOLVED]
    new_ambig = [a for a in ambig if a not in KNOWN_AMBIGUOUS]
    print('checked=%d updated=%d off_sale=%d unresolved=%d ambiguous=%d' % (
        len(codes), len(updated), len(offed), len(unres), len(ambig)))
    for c in offed:
        print('OFF_SALE %s' % c)
    sys.exit(1 if (new_unres or new_ambig) else 0)


if __name__ == '__main__':
    main()
