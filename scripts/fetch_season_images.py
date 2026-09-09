# -*- coding: utf-8 -*-
"""抓「中秋·应季」6 道新菜的配图：维基词条首图优先 + Commons 兜底。
沿用 fetch_images.py 的来源与校验口径（<30KB 视为坏图，换下一个候选）。
用法：python scripts/fetch_season_images.py   （在仓库根目录跑）
"""
import json, re, sys, time, urllib.parse, os, io

import requests

S = requests.Session()
S.headers['User-Agent'] = 'EasternMarketRecipe/1.0 (easternmarketsask@gmail.com; recipe site)'

CAND = {
    'mooncake-ready':       ['en:Mooncake', 'commons:月餅', 'commons:Mooncake'],
    'steamed-crab':         ['commons:清蒸螃蟹', 'commons:蒸蟹', 'commons:Steamed crab', 'en:Chinese mitten crab'],
    'lotus-pork-bone-soup': ['commons:蓮藕湯', 'commons:排骨蓮藕湯', 'commons:Lotus root soup'],
    'osmanthus-lotus-root': ['commons:糯米藕', 'commons:桂花糖藕', 'commons:Lotus root stuffed with glutinous rice'],
    'taro-pork-belly':      ['commons:芋頭扣肉', 'commons:荔浦芋扣肉', 'commons:Taro pork belly'],
    'steamed-kabocha-yam':  ['commons:蒸南瓜', 'commons:Kabocha', 'commons:Steamed pumpkin'],
}

OUT_DIR = os.path.join('assets', 'images')
CRED_PATH = os.path.join(OUT_DIR, '_credits.json')


def wiki_img(lang, title):
    u = 'https://%s.wikipedia.org/api/rest_v1/page/summary/%s' % (
        lang, urllib.parse.quote(title.replace(' ', '_')))
    try:
        d = S.get(u, timeout=20).json()
        img = (d.get('originalimage') or d.get('thumbnail') or {}).get('source', '')
        if re.search(r'\.(jpg|jpeg|png)(\?|$)', img, re.I):
            return {'url': img, 'page': u}
    except Exception:
        pass
    return None


def commons_imgs(q):
    p = {'action': 'query', 'format': 'json', 'generator': 'search', 'gsrnamespace': 6,
         'gsrlimit': 10, 'gsrsearch': q, 'prop': 'imageinfo', 'iiprop': 'url', 'iiurlwidth': 1400}
    out = []
    try:
        d = S.get('https://commons.wikimedia.org/w/api.php', params=p, timeout=20).json()
    except Exception:
        return out
    pages = ((d.get('query') or {}).get('pages') or {}).values()
    for pg in sorted(pages, key=lambda x: x.get('index', 99)):
        ii = (pg.get('imageinfo') or [{}])[0]
        url = ii.get('thumburl') or ii.get('url') or ''
        if re.search(r'\.(jpg|jpeg|png)(\?|$)', url, re.I):
            out.append({'url': url, 'page': ii.get('descriptionurl', '')})
    return out


def try_download(hit, path):
    try:
        img = S.get(hit['url'], timeout=35).content
        if len(img) < 30000:
            return 0
        with open(path, 'wb') as f:
            f.write(img)
        return len(img)
    except Exception:
        return 0


def main():
    creds = {}
    if os.path.exists(CRED_PATH):
        creds = json.load(io.open(CRED_PATH, encoding='utf-8'))
    recs = {r['id']: r for r in json.load(io.open('data/recipes.json', encoding='utf-8'))['recipes']}
    ok = 0
    for rid, cands in CAND.items():
        name = recs.get(rid, {}).get('name_cn', rid)
        path = os.path.join(OUT_DIR, rid + '.jpg')
        done = False
        for cand in cands:
            if cand[:3] in ('en:', 'zh:'):
                h = wiki_img(cand[:2], cand[3:])
                hits = [h] if h else []
            else:
                hits = commons_imgs(cand.split(':', 1)[1])
            for h in hits:
                n = try_download(h, path)
                if n:
                    creds[rid] = {'source': h['page'], 'via': cand}
                    print('  %-24s OK %4dKB  via %s' % (rid, n // 1024, cand))
                    done = True
                    ok += 1
                    break
            if done:
                break
            time.sleep(0.2)
        if not done:
            print('  %-24s MISS  (%s)' % (rid, name))
    with io.open(CRED_PATH, 'w', encoding='utf-8') as f:
        f.write(json.dumps(creds, ensure_ascii=False, indent=2))
    print('抓到 %d/%d' % (ok, len(CAND)))
    return 0 if ok == len(CAND) else 1


if __name__ == '__main__':
    sys.exit(main())
