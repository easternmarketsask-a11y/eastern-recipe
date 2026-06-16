# -*- coding: utf-8 -*-
"""Process 8 owner-provided Cantonese dish photos into recipe images."""
import json, os
from PIL import Image, ImageOps

SRC = r"C:\Users\yue00\Downloads"
ROOT = r"D:\easternmarket.ca\eastern-recipe"
OUT = os.path.join(ROOT, "src", "assets", "images")

# filename -> recipe id
MAP = {
    "蒜蓉粉丝蒸扇贝.jpg": "cant-suanrong-fensi-shanbei",
    "腊味煲仔饭.jpg":     "cant-lawei-baozaifan",
    "滑蛋虾仁.jpg":       "cant-huadan-xiaren",
    "滑蛋牛肉.jpg":       "cant-huadan-niurou",
    "蚝油生菜.jpeg":      "cant-haoyou-shengcai",
    "蚝油芥兰.jpg":       "cant-haoyou-jielan",
    "糖醋排骨.jpg":       "cant-tangcu-paigu",
    "豉汁蒸排骨.jpg":     "cant-douchi-paigu",
}

MAXW = 880
done = {}
for fn, rid in MAP.items():
    p = os.path.join(SRC, fn)
    im = Image.open(p)
    im = ImageOps.exif_transpose(im).convert("RGB")
    if im.width > MAXW:
        h = round(im.height * MAXW / im.width)
        im = im.resize((MAXW, h), Image.LANCZOS)
    outp = os.path.join(OUT, rid + ".jpg")
    im.save(outp, "JPEG", quality=85, optimize=True)
    done[rid] = "assets/images/%s.jpg" % rid
    print("saved", rid, im.size, os.path.getsize(outp), "bytes")

# update recipes.json
rj = os.path.join(ROOT, "data", "recipes.json")
data = json.load(open(rj, encoding="utf-8"))
for r in data["recipes"]:
    if r["id"] in done:
        r["image"] = done[r["id"]]
        r["image_credit"] = "self"
json.dump(data, open(rj, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("recipes.json updated")

# update _credits.json if present
cj = os.path.join(ROOT, "data", "_credits.json")
if os.path.exists(cj):
    cr = json.load(open(cj, encoding="utf-8"))
    for rid in done:
        cr[rid] = {"source": "self", "credit": "本店实拍"}
    json.dump(cr, open(cj, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("_credits.json updated")
else:
    print("(no _credits.json)")
