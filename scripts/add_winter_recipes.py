"""Curated 2026-11 winter batch; idempotent, no network or product writes.

Mains picked from 2026-10-15~10-29 14-day EM-POS revenue (see
docs/content-ingredients-2026-11-01.json): every dish maps to a high-sales
item, supporting ingredients stay supporting. Run, then recipe_facts.py
(minutes/servings/hook), add_ingredient_aliases.py, optimize_images.py,
build_static_pages.py — same order as every batch.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CREDIT = "AI-generated illustration; Muse Image, 2026-10-31"

P = {
    "安格斯牛肋条": "NknIRL292NLT", "白萝卜": "1028blb",
    "虎皮青椒": "Lsj", "猪肉碎": "627735189635",
    "牛筋": "2034njnj", "牛金钱肚": "20591",
    "潮州牛肉丸": "00330", "上海苗": "10251",
    "冷冻野生带鱼": "990488000039",
    "蝦餃皇": "827510006212", "广式烧鸭": "800794308487",
    "姜": "1037", "小葱": "HFCXCXC",
    "生抽": "078895128789", "老抽": "722337817020",
    "料酒": "6907592001245", "八角": "6954769010128",
    "白砂糖": "063111103541", "淀粉": "6941837101024",
    "蒜": "0178", "干辣椒": "6971005993144",
    "香醋": "6901055000011", "辣椒油": "213466668855",
    "白胡椒粉": "698921021831", "芝麻油": "742812710905",
}

# id, name, English, section, kind, priority, tags, ingredients(label, qty, main), steps
CONTENT = [
    ("radish-beef-brisket", "萝卜炖牛腩", "White Radish and Beef Brisket Stew",
     "season", "dish", 97, ["牛肉", "白萝卜", "炖肉", "下饭", "暖身"],
     [("安格斯牛肋条", "800g", 1), ("白萝卜", "1根，约600g", 1),
      ("姜", "4片", 1), ("小葱", "2根", 0),
      ("生抽", "2汤匙", 1), ("老抽", "1汤匙", 1), ("料酒", "2汤匙", 1),
      ("八角", "2颗", 0), ("白砂糖", "1茶匙", 0),
      ("盐", "适量", 0), ("水", "约1.5升", 0)],
     ["约2.5小时，4人份。牛肋条冷藏解冻后切4cm块；冷水下锅煮开，撇沫再煮3分钟，捞出用温水冲净。",
      "白萝卜削皮切滚刀块；姜切片，葱切段。",
      "炖锅加少许油炒香姜片，下牛肋条翻炒，加生抽、老抽、白砂糖和料酒，倒入约1.5升热水没过肉。",
      "煮开转小火，盖盖炖约2小时，筷子能插入肉块；中途缺水补热水。",
      "下白萝卜再炖25–30分钟至透明软糯，加盐调味，撒葱花。萝卜后放，吸足肉汤又不煮散。"]),
    ("tiger-pepper-stuffed-pork", "虎皮青椒酿肉", "Tiger Peppers Stuffed with Pork",
     "season", "dish", 96, ["猪肉", "虎皮青椒", "下饭", "家常菜"],
     [("虎皮青椒", "6根，约400g", 1), ("猪肉碎", "250g", 1),
      ("生抽", "1汤匙", 1), ("淀粉", "1茶匙", 1),
      ("蒜", "2瓣", 0), ("白砂糖", "1/2茶匙", 0),
      ("盐", "1/4茶匙", 0), ("食用油", "2汤匙", 0), ("水", "100ml", 0)],
     ["约40分钟，3人份。青椒洗净，从一侧划开去籽；肉碎加生抽、淀粉、盐和少许水，顺一个方向搅上劲。",
      "把肉馅酿进青椒，填满压实。",
      "平底锅加油，中小火放青椒，有肉的一面朝下先煎3分钟定型，再翻面煎出虎皮斑。",
      "加100ml水、白砂糖和蒜末，盖盖小火焖8分钟；肉馅中心达到71°C。",
      "开盖大火略收汁，酱汁浓了就出锅。馅料饱满、青椒软而不烂。"]),
    ("braised-beef-tendon", "红烧牛筋", "Red-Braised Beef Tendon",
     "season", "dish", 95, ["牛筋", "红烧", "炖肉", "下饭"],
     [("牛筋", "600g", 1),
      ("生抽", "2汤匙", 1), ("老抽", "1汤匙", 1), ("料酒", "2汤匙", 1),
      ("姜", "4片", 1), ("小葱", "2根", 0),
      ("八角", "2颗", 0), ("白砂糖", "1茶匙", 0),
      ("食用油", "1汤匙", 0), ("水", "约1升", 0), ("盐", "少许", 0)],
     ["约2.5小时，3人份。牛筋冷藏解冻，冷水下锅煮开撇沫，再煮5分钟捞出，温水冲净切段。",
      "锅中加油炒香姜片，下牛筋翻炒，加生抽、老抽、白砂糖、料酒和八角。",
      "倒入约1升热水没过牛筋，煮开转小火，盖盖炖约2小时。",
      "牛筋炖到透明、筷子能轻松夹断，开盖大火收汁到浓稠，加盐调味撒葱花。",
      "牛筋久炖才起胶，不要心急开大火；收汁时盯着锅，别收干。"]),
    ("marinated-beef-tripe", "卤水牛金钱肚", "Marinated Beef Money-Tripe",
     "season", "dish", 96, ["牛肚", "卤味", "凉拌", "下酒菜"],
     [("牛金钱肚", "500g", 1),
      ("生抽", "3汤匙", 1), ("老抽", "1汤匙", 1), ("料酒", "2汤匙", 1),
      ("姜", "5片", 1), ("小葱", "3根", 1),
      ("八角", "2颗", 0), ("干辣椒", "3个", 0),
      ("香醋", "1汤匙", 0), ("辣椒油", "1茶匙", 0),
      ("盐", "适量", 0), ("水", "约1.5升", 0)],
     ["约90分钟，另计浸泡，3人份。金钱肚冷藏解冻，冷水下锅煮开撇沫，煮5分钟捞出冲净。",
      "锅中加约1.5升水，放金钱肚、姜片、葱段、生抽、老抽、料酒和八角，大火烧开撇沫。",
      "转小火加盖卤约1小时，筷子能穿透、口感爽脆不柴。",
      "关火在卤汁里继续泡30分钟以上（冷藏泡一夜更入味），取出切片。",
      "香醋、辣椒油和少许卤汁调成蘸汁，浇在肚丝上，撒干辣椒段点缀。切薄片才爽口。"]),
    ("beef-ball-greens-soup", "牛肉丸青菜汤", "Beef Ball and Greens Soup",
     "season", "dish", 95, ["牛肉丸", "青菜", "喝汤", "暖胃", "快手菜"],
     [("潮州牛肉丸", "300g", 1), ("上海苗", "250g", 1),
      ("姜", "3片", 1), ("白胡椒粉", "少许", 0),
      ("盐", "约1/2茶匙", 0), ("水", "约1升", 0), ("芝麻油", "数滴", 0)],
     ["约20分钟，3人份。牛肉丸提前冷藏解冻；上海苗洗净，姜切片。",
      "锅中加约1升水和姜片，大火烧开，下牛肉丸煮至全部浮起。",
      "转中小火再煮3分钟，丸子熟透Q弹。",
      "下上海苗烫1–2分钟至软，加盐、白胡椒粉，滴芝麻油出锅。青菜最后下，颜色才翠绿。"]),
    ("pan-fried-hairtail", "干煎带鱼", "Pan-Fried Hairtail",
     "seafood", "dish", 94, ["带鱼", "海鲜", "香煎", "下饭"],
     [("冷冻野生带鱼", "500g", 1),
      ("姜", "3片", 1), ("小葱", "2根", 0),
      ("料酒", "1汤匙", 1), ("盐", "1/2茶匙", 0), ("食用油", "3汤匙", 0)],
     ["约25分钟，3人份。带鱼冷藏解冻，去内脏洗净，剪成约6cm段，两面斜划几刀。",
      "用厨房纸吸干水分，抹盐和料酒，加姜片腌15分钟。",
      "平底锅烧热加油，中火放带鱼段，每面煎约4分钟至金黄。",
      "鱼肉雪白、能轻松离骨就是熟了，撒葱花出锅。擦干是关键，带水下锅必粘。"]),
    ("shrimp-dumpling-ready", "虾饺皇", "Shrimp Dumplings (Ready to Steam)",
     "breakfast", "ready", 93, ["早餐", "速食", "蒸食", "粤式点心"],
     [("蝦餃皇", "1袋，400g", 1)],
     ["约12分钟，2人份。从冷冻取出，无需解冻，蒸笼垫纸或刷薄油。",
      "水开后放虾饺，大火蒸约8–10分钟。",
      "蒸到皮透出虾仁的红就可以吃，蘸生抽或辣酱。别蒸太久，皮破了就不漂亮了。"]),
    ("roast-duck-ready", "广式烧鸭", "Cantonese Roast Duck (Ready to Eat)",
     "tonight", "ready", 91, ["烧味", "熟食", "粤菜", "即食"],
     [("广式烧鸭", "1只，450g", 1)],
     ["约15分钟，3人份。烧鸭室温回温10分钟，斩件摆盘就能吃。",
      "想吃脆皮：烤箱预热180°C，烧鸭放烤架烤8分钟，皮会重新变脆。",
      "配白饭、一碟菜心就是一桌。斩件时顺着骨缝下刀，肉才整齐。"]),
]


def main():
    path = ROOT / "data" / "recipes.json"
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    existing = {r["id"] for r in data["recipes"]}
    products = {p["code"] for p in json.loads((ROOT / "data" / "products.json").read_text(encoding="utf-8-sig"))["items"]}
    checked = {p["code"] for p in json.loads((ROOT / "docs" / "content-ingredients-2026-11-01.json").read_text(encoding="utf-8-sig"))["products"]}
    for rid, cn, en, section, kind, prio, tags, ingredients, steps in CONTENT:
        assert all(P.get(label) in checked for label, _, main in ingredients if main), rid
        rows = [{"label": label, "qty": qty, "code": P.get(label) if P.get(label) in products else None, "required": bool(main)} for label, qty, main in ingredients]
        if rid not in existing:
            data["recipes"].append({"id": rid, "name_cn": cn, "name_en": en, "aliases": [cn, en],
                                    "section": section, "kind": kind, "priority": prio,
                                    "image": f"assets/images/{rid}-ai-202611.jpg", "image_credit": CREDIT,
                                    "tags": tags, "ingredients": rows, "steps": steps})
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Recipes: {len(data['recipes'])}; batch: {len(CONTENT)}")


if __name__ == "__main__":
    main()
