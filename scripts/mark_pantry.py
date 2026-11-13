# -*- coding: utf-8 -*-
"""Mark home-staple ingredients explicitly so audits stop flagging them.

pantry=True means: deliberately NOT bound to a store product (water, salt,
cooking oil, small-quantity honey). Every other code-less row is a real gap.
Safe for readers: app.js / recipe-logic.js / static_pages.py only read
label/qty/required/code/alt and ignore unknown keys.
"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, 'data', 'recipes.json')

PANTRY_LABELS = {'水', '温水', '盐', '食用油', '蜂蜜'}

# 已知待办：不算新缺口，--check 只对 KNOWN 之外的行报错
KNOWN_GAPS = {('purple-rice-floss-bun', '肉松紫米包'):
              '成品本身，店内暂无此商品（2026-11-13 直连库核过），待确认是否上架'}

with io.open(PATH, encoding='utf-8') as f:
    raw = f.read()
doc = json.loads(raw)

# 1) round-trip must be byte-identical before we touch anything
probe = json.dumps(doc, ensure_ascii=False, indent=2)
if probe != raw:
    sys.exit('ABORT: round-trip drift, refusing to rewrite (check dump settings)')

changed = 0
pantry_rows = 0
gap_rows = []
for r in doc['recipes']:
    for ig in (r.get('ingredients') or []):
        if (ig.get('code') or '').strip():
            continue
        label = ig.get('label') or ''
        if label in PANTRY_LABELS:
            if not ig.get('pantry'):
                ig['pantry'] = True
                changed += 1
            pantry_rows += 1
        else:
            gap_rows.append((r.get('id'), label, ig.get('qty')))

if '--check' in sys.argv:
    new_gaps = [g for g in gap_rows if (g[0], g[1]) not in KNOWN_GAPS]
    print('pantry_rows=%d known=%d new_gaps=%d' % (
        pantry_rows, len(gap_rows) - len(new_gaps), len(new_gaps)))
    for rid, label, qty in gap_rows:
        tag = 'KNOWN' if (rid, label) in KNOWN_GAPS else 'GAP'
        print('%s %s | %s | %s' % (tag, rid, label, qty))
    sys.exit(0 if not new_gaps else 1)

with io.open(PATH, 'w', encoding='utf-8', newline='') as f:
    f.write(json.dumps(doc, ensure_ascii=False, indent=2))
print('marked=%d pantry_rows=%d gaps=%d' % (changed, pantry_rows, len(gap_rows)))
for g in gap_rows:
    print('GAP %s | %s | %s' % g)
