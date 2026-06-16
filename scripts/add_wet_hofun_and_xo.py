# -*- coding: utf-8 -*-
import json
rj = r"D:\easternmarket.ca\eastern-recipe\data\recipes.json"
data = json.load(open(rj, encoding="utf-8"))
recs = data["recipes"]

# --- 1) New recipe: 湿炒牛河 (wet-fried beef ho fun) ---
wet = {
    "id": "wet-beef-ho-fun",
    "name_cn": "湿炒牛河",
    "name_en": "Saucy Beef Ho Fun",
    "aliases": ["湿炒河粉", "牛肉河", "滑炒牛河", "shichao niuhe",
                "牛河（湿炒）", "saucy beef ho fun", "beef ho fun gravy"],
    "section": "fresh",
    "kind": "dish",
    "fresh": True,
    "priority": 98,
    "image": "",
    "image_credit": "",
    "tags": ["牛河", "河粉", "牛肉", "滑嫩", "浓汁", "周末菜"],
    "steps": [
        "牛肉卷半解冻后切片，加生抽1茶匙、土豆淀粉、少许油抓匀，腌15分钟。",
        "鲜河粉室温回软，用手轻轻拨散成条不粘连；芥兰洗净斜切段，蒜切末，葱切段。",
        "调味汁：生抽2汤匙、老抽1茶匙、蚝油1汤匙、糖少许、清水约150ml、土豆淀粉1茶匙，调匀备用。",
        "热锅多油，下河粉中火煎散、煎到边缘微焦，盛起平铺在盘中。",
        "锅留底油爆香蒜末，下牛肉片大火快炒至变色盛起；下芥兰段炒至翠绿。",
        "倒回牛肉，淋入调好的味汁煮滚、勾成薄芡，连汁一起淋在河粉上即可（喜欢可点几滴芝麻油）。"
    ],
    "ingredients": [
        {"label": "鲜河粉", "qty": "908g（1包）", "code": "058398101014", "required": True},
        {"label": "牛肉卷", "qty": "约300g", "code": "6292644004009", "required": True},
        {"label": "芥兰", "qty": "约200g", "code": "1006jljl", "required": True},
        {"label": "蒜", "qty": "2瓣", "code": "0178", "required": True},
        {"label": "小葱", "qty": "2根（切段）", "code": "HFCXCXC", "required": False},
        {"label": "生抽", "qty": "适量", "code": "078895128789", "required": True},
        {"label": "老抽", "qty": "少许", "code": "722337817020", "required": False},
        {"label": "蚝油", "qty": "1汤匙", "code": "6922824007468", "required": True},
        {"label": "土豆淀粉（腌肉+勾芡）", "qty": "适量", "code": "6941837101024", "required": True},
        {"label": "芝麻油", "qty": "几滴", "code": "742812710905", "required": False},
        {"label": "食用油", "qty": "适量", "code": None, "required": False}
    ],
    "nutrition": "牛肉河粉·浓汁裹粉更下饭"
}

# insert right after 干炒牛河 (beef-chow-fun)
idx = next(i for i, r in enumerate(recs) if r["id"] == "beef-chow-fun")
if not any(r["id"] == "wet-beef-ho-fun" for r in recs):
    recs.insert(idx + 1, wet)

# --- 2) Rename 豉油皇炒肠粉 -> 豉油皇XO酱炒肠粉, add 李锦记XO酱 ---
for r in recs:
    if r["id"] == "soy-sauce-cheung-fun":
        r["name_cn"] = "豉油皇XO酱炒肠粉"
        r["name_en"] = "XO & Soy Sauce Stir-Fried Rice Rolls"
        for a in ["豉油皇XO炒肠粉", "XO酱炒肠粉", "xo chang fen"]:
            if a not in r["aliases"]:
                r["aliases"].append(a)
        if "XO酱" not in r["tags"]:
            r["tags"].append("XO酱")
        # add ingredient if not present
        if not any(i.get("code") == "78895144413" for i in r["ingredients"]):
            # insert XO sauce right after the rice-rolls (first ingredient)
            r["ingredients"].insert(1, {
                "label": "李锦记海皇XO酱", "qty": "1汤匙",
                "code": "78895144413", "required": True})
        # add a step about XO sauce before the final plating step
        xo_step = "加入1汤匙李锦记海皇XO酱，与肠粉一起翻炒出香（XO酱咸鲜，豉油可酌量减少）。"
        if not any("XO" in s for s in r["steps"]):
            r["steps"].insert(len(r["steps"]) - 1, xo_step)
        break

json.dump(data, open(rj, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("done. total recipes:", len(recs))
