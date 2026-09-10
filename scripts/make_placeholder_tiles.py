# -*- coding: utf-8 -*-
"""给还没有实拍图的菜生成品牌占位图卡。

用途：新菜上线时公共图库找不到对得上的照片，与其放一张别的菜的照片误导顾客，
不如放一张干净的品牌字卡。店主拍到实拍图后，直接用同名 .jpg 覆盖即可，
前端无需改动（app.js 只认 recipes.json 里的 image 路径）。

用法：python scripts/make_placeholder_tiles.py            # 生成清单里全部
      python scripts/make_placeholder_tiles.py steamed-crab   # 只生成一张
"""
import io, json, os, sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 900
GREEN_D = (42, 92, 52)      # #2a5c34
GREEN = (58, 140, 80)       # #3a8c50
CREAM = (244, 249, 245)     # #f4f9f5

FONT_BOLD = r'C:\Windows\Fonts\msyhbd.ttc'
FONT_REG = r'C:\Windows\Fonts\msyh.ttc'
FONT_EMOJI = r'C:\Windows\Fonts\seguiemj.ttf'

# 需要占位图的菜：id -> emoji。有成品图的不要留在这里，
# 否则下次跑脚本会把实拍/生成图盖回字卡。
TILES = {
}


def _font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def _center(draw, y, text, font, fill, **kw):
    box = draw.textbbox((0, 0), text, font=font, **kw)
    draw.text(((W - (box[2] - box[0])) // 2 - box[0], y), text, font=font, fill=fill, **kw)
    return box[3] - box[1]


def make_tile(recipe, emoji, out_path):
    img = Image.new('RGB', (W, H), CREAM)
    d = ImageDraw.Draw(img)
    # 斜向浅绿渐变（从左上到右下，很淡，不抢字）
    for y in range(H):
        t = y / float(H - 1)
        c = tuple(int(CREAM[i] + (GREEN[i] - CREAM[i]) * t * 0.22) for i in range(3))
        d.line([(0, y), (W, y)], fill=c)

    # emoji（彩色字形需要 embedded_color）
    try:
        f_e = ImageFont.truetype(FONT_EMOJI, 200)
        box = d.textbbox((0, 0), emoji, font=f_e, embedded_color=True)
        d.text(((W - (box[2] - box[0])) // 2 - box[0], 190), emoji,
               font=f_e, embedded_color=True)
    except Exception:
        pass

    _center(d, 470, recipe['name_cn'], _font(FONT_BOLD, 92), GREEN_D)
    en = recipe.get('name_en') or ''
    if en:
        _center(d, 600, en, _font(FONT_REG, 34), GREEN)

    d.line([(W // 2 - 110, 680), (W // 2 + 110, 680)], fill=GREEN, width=3)
    _center(d, 720, '\u4e1c\u65b9\u8d85\u5e02 \u00b7 \u5bb6\u5e38\u98df\u8c31', _font(FONT_REG, 34), GREEN)

    img.save(out_path, quality=90, optimize=True)
    return os.path.getsize(out_path)


def main(argv):
    recs = {r['id']: r for r in json.load(io.open('data/recipes.json', encoding='utf-8'))['recipes']}
    want = argv[1:] or list(TILES)
    for rid in want:
        if rid not in TILES:
            print('  %s 不在占位清单里，跳过' % rid)
            continue
        if rid not in recs:
            print('  %s 不在 recipes.json 里，跳过' % rid)
            continue
        out = os.path.join('assets', 'images', rid + '.jpg')
        n = make_tile(recs[rid], TILES[rid], out)
        print('  %-24s %s  %dKB' % (rid, recs[rid]['name_cn'], n // 1024))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
