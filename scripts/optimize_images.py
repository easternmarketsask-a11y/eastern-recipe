# -*- coding: utf-8 -*-
"""把 assets/images/*.jpg 转成 WebP 两档，供前端 <picture> 使用。

  assets/images/webp/<name>-400.webp   卡片用（首页横滑行、搜索结果网格）
  assets/images/webp/<name>.webp       大图用（详情页 hero、静态菜页、分享预览）

原图 .jpg 保留不动，作为不支持 WebP 时的兜底。只有超过 --max-src-kb 的原图
会被就地缩到 --max-src-w 宽并重存，避免个别几 MB 的图白白躺在仓库里。

用法：python scripts/optimize_images.py            # 只处理有变动的
      python scripts/optimize_images.py --force    # 全部重做
"""
import argparse
import os
import sys

from PIL import Image

SRC_DIR = os.path.join('assets', 'images')
OUT_DIR = os.path.join(SRC_DIR, 'webp')
CARD_W = 400
HERO_W = 900
QUALITY = 80


def _resized(im, target_w):
    if im.width <= target_w:
        return im.copy()
    h = max(1, round(im.height * target_w / float(im.width)))
    return im.resize((target_w, h), Image.LANCZOS)


def _stale(src, dst, force):
    if force or not os.path.exists(dst):
        return True
    return os.path.getmtime(src) > os.path.getmtime(dst)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--force', action='store_true', help='忽略时间戳，全部重做')
    ap.add_argument('--max-src-kb', type=int, default=600, help='超过这个大小的原图就地缩小')
    ap.add_argument('--max-src-w', type=int, default=1600, help='原图缩小后的最大宽度')
    args = ap.parse_args(argv)

    if not os.path.isdir(SRC_DIR):
        sys.exit('找不到 %s，请在仓库根目录运行' % SRC_DIR)
    if not os.path.isdir(OUT_DIR):
        os.makedirs(OUT_DIR)

    names = sorted(n for n in os.listdir(SRC_DIR) if n.lower().endswith(('.jpg', '.jpeg')))
    src_before = src_after = webp_total = 0
    shrunk = made = 0

    for n in names:
        src = os.path.join(SRC_DIR, n)
        stem = os.path.splitext(n)[0]
        size = os.path.getsize(src)
        src_before += size

        # 个别几 MB 的原图就地缩小（新抓的图常常是 4000px 的原始尺寸）
        if size > args.max_src_kb * 1024:
            with Image.open(src) as im:
                im = im.convert('RGB')
                _resized(im, args.max_src_w).save(src, 'JPEG', quality=85, optimize=True,
                                                  progressive=True)
            print('  缩原图 %-28s %5dKB -> %5dKB' % (n, size // 1024,
                                                  os.path.getsize(src) // 1024))
            shrunk += 1
        src_after += os.path.getsize(src)

        card = os.path.join(OUT_DIR, '%s-%d.webp' % (stem, CARD_W))
        hero = os.path.join(OUT_DIR, '%s.webp' % stem)
        if _stale(src, card, args.force) or _stale(src, hero, args.force):
            with Image.open(src) as im:
                im = im.convert('RGB')
                _resized(im, CARD_W).save(card, 'WEBP', quality=QUALITY, method=6)
                _resized(im, HERO_W).save(hero, 'WEBP', quality=QUALITY, method=6)
            made += 1
        webp_total += os.path.getsize(card) + os.path.getsize(hero)

    print('原图 %d 张：%.1fMB -> %.1fMB（就地缩小 %d 张）'
          % (len(names), src_before / 1048576.0, src_after / 1048576.0, shrunk))
    print('WebP 两档共 %d 个文件，合计 %.1fMB（本次新生成 %d 组）'
          % (len(names) * 2, webp_total / 1048576.0, made))
    print('卡片实际下载的是 -%d.webp 那一档：%.1fMB'
          % (CARD_W, sum(os.path.getsize(os.path.join(OUT_DIR, f))
                         for f in os.listdir(OUT_DIR)
                         if f.endswith('-%d.webp' % CARD_W)) / 1048576.0))
    return 0


if __name__ == '__main__':
    sys.exit(main())
