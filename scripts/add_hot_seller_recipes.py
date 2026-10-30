"""2026-10 热卖且单价不低、食谱站还没有的货。幂等，不联网。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

NEW_PRODUCTS = [
    {
        "code": "92294",
        "name_cn": "新鲜松茸 盒340G",
        "name_en": "Matsutake",
        "category": "新鲜蔬菜",
        "image_url": "",
        "on_sale": True,
        "sold_90d": 0,
    },
    {
        "code": "LXLX",
        "name_cn": "蓝蟹 LB",
        "name_en": "Blue Crab",
        "category": "新鲜蔬菜",
        "image_url": "",
        "on_sale": True,
        "sold_90d": 0,
    },
]

# 商品库里 code 为空，货号在 sku。食谱站只用 code 对货架名，所以快照里用 LXLX。
CONTENT = [
    {
        "id": "steamed-blue-crab",
        "name_cn": "清蒸蓝蟹",
        "name_en": "Steamed Blue Crab",
        "aliases": ["清蒸蓝蟹", "蓝蟹", "Steamed Blue Crab", "blue crab"],
        "section": "seafood",
        "tags": ["蓝蟹", "海鲜", "清蒸"],
        "ingredients": [
            {"label": "蓝蟹", "qty": "约2磅", "code": "LXLX", "required": True},
            {"label": "生姜", "qty": "1大块", "code": "1037", "required": True},
            {"label": "小葱", "qty": "2根", "code": "HFCXCXC", "required": False},
            {"label": "香醋", "qty": "2汤匙", "code": None, "required": False},
            {"label": "生抽", "qty": "1茶匙，可省略", "code": "078895128789", "required": False},
        ],
        "steps": [
            "约25分钟，2人份。蓝蟹要鲜活的；已经死了的不要蒸。刷净壳，揭开盖，去掉鳃，腹部的脐也去掉。",
            "姜切丝。一半垫在盘底，蟹肚朝上码好。蒸锅水开后再上锅，中火蒸15–18分钟。",
            "壳全红、肉不透明、腿节一掰就离，就是熟了。蟹大就再蒸两三分钟，不要凭感觉提前揭盖。",
            "剩下的姜丝配香醋做蘸汁，喜欢咸一点加一茶匙生抽，撒一点葱花。趁热吃，放凉了肉会柴。",
        ],
    },
    {
        "id": "matsutake-silkie-soup",
        "name_cn": "松茸竹丝鸡汤",
        "name_en": "Matsutake and Silkie Chicken Soup",
        "aliases": ["松茸竹丝鸡汤", "松茸汤", "竹丝鸡汤", "Matsutake and Silkie Chicken Soup"],
        "section": "season",
        "tags": ["松茸", "竹丝鸡", "汤"],
        "ingredients": [
            {"label": "竹丝鸡", "qty": "约600g（1只小的）", "code": "778621732791", "required": True},
            {"label": "新鲜松茸", "qty": "1盒（340g）", "code": "92294", "required": True},
            {"label": "生姜", "qty": "4片", "code": "1037", "required": True},
            {"label": "盐", "qty": "约1/2茶匙，最后按口味", "code": None, "required": False},
        ],
        "steps": [
            "约80分钟，另计解冻，3–4人份。竹丝鸡冷藏解冻后切块，不要用流水冲洗生鸡。松茸用湿布擦净，不要久泡，切厚片；根太硬就削掉。",
            "鸡块冷水下锅，煮开后撇沫，再煮约2分钟捞出。接触生鸡的盆和板洗干净。",
            "鸡块、姜片和约1.5升热水下锅，煮开转小火，盖盖炖约40分钟。最厚处避开骨头测到74°C，肉也软了，再下松茸。",
            "松茸只煮8–10分钟，香气还在就加盐。煮太久香气散掉，汤也会浑。",
        ],
    },
    {
        "id": "scallion-sea-cucumber",
        "name_cn": "葱烧红刺参",
        "name_en": "Scallion Braised Sea Cucumber",
        "aliases": ["葱烧红刺参", "葱烧海参", "冰海参", "Scallion Braised Sea Cucumber"],
        "section": "seafood",
        "tags": ["海参", "红刺参", "海鲜"],
        "ingredients": [
            {"label": "冰海参（加拿大红刺参）", "qty": "1磅", "code": "0729", "required": True},
            {"label": "小葱", "qty": "4根", "code": "HFCXCXC", "required": True},
            {"label": "生姜", "qty": "3片", "code": "1037", "required": False},
            {"label": "生抽", "qty": "1汤匙", "code": "078895128789", "required": True},
            {"label": "食用油", "qty": "1汤匙", "code": None, "required": False},
        ],
        "steps": [
            "约25分钟，另计解冻，2–3人份。冰海参提前冷藏解冻，冲洗干净。这是冻过的刺参，不要大火久煮，一煮散就没有口感。",
            "小葱切段，葱白和葱绿分开。锅里少放油，小火把葱白和姜片炒香。",
            "下海参、生抽和两汤匙水，小火加热3–4分钟，到海参热透、捏上去还有弹性。",
            "撒葱绿，马上出锅。汁留一点，拌饭刚好。",
        ],
    },
    {
        "id": "snow-beef-pepper",
        "name_cn": "雪花肥牛卷炒青椒",
        "name_en": "Snow Beef Rolls with Tiger Peppers",
        "aliases": ["雪花肥牛卷炒青椒", "肥牛卷青椒", "雪花牛五花卷", "Snow Beef Rolls with Tiger Peppers"],
        "section": "tonight",
        "tags": ["肥牛卷", "青椒", "快炒"],
        "ingredients": [
            {"label": "雪花牛五花卷", "qty": "半袋，约1磅", "code": "6292644004467", "required": True},
            {"label": "虎皮青椒", "qty": "3个，约200g", "code": "Lsj", "required": True},
            {"label": "蒜", "qty": "2瓣", "code": "0178", "required": False},
            {"label": "生抽", "qty": "1汤匙", "code": "078895128789", "required": False},
            {"label": "食用油", "qty": "1汤匙", "code": None, "required": False},
        ],
        "steps": [
            "约15分钟，2–3人份。肥牛卷半冻时一片片揭开。全化了再撕容易烂。虎皮青椒去籽切块，蒜切片。",
            "锅烧热，加油，中大火下牛肉，散开快炒到没有粉红色，先盛出来。薄片很快熟，多炒就老。",
            "原锅下青椒和蒜，炒到断生、还脆，大约2分钟。",
            "牛肉回锅，加生抽翻匀即可。一袋是2磅，这一碟用半袋，剩下的留着涮火锅。",
        ],
    },
    {
        "id": "garlic-crayfish",
        "name_cn": "蒜蓉小龙虾尾",
        "name_en": "Garlic Crayfish Tails",
        "aliases": ["蒜蓉小龙虾尾", "龙虾尾", "Garlic Crayfish Tails"],
        "section": "seafood",
        "tags": ["龙虾", "蒜蓉", "海鲜"],
        "ingredients": [
            {"label": "小龙虾尾", "qty": "1袋（680g）", "code": "841624002847", "required": True},
            {"label": "蒜", "qty": "6瓣", "code": "0178", "required": True},
            {"label": "生姜", "qty": "3片", "code": "1037", "required": False},
            {"label": "小葱", "qty": "1根", "code": "HFCXCXC", "required": False},
            {"label": "生抽", "qty": "1汤匙", "code": "078895128789", "required": False},
            {"label": "食用油", "qty": "1汤匙", "code": None, "required": False},
        ],
        "steps": [
            "约20分钟，另计解冻，2–3人份。龙虾尾冷藏解冻后冲洗。蒜切末，一半用油小火炒到浅金色，关火拌进另一半生蒜末。",
            "下龙虾尾和姜片，中火翻炒4–6分钟，加生抽和两汤匙水。",
            "虾肉完全不透明、最厚处没有透明的心，再出锅。炒过头肉会缩、会柴。",
            "撒葱花。蒜分两次下，留一半生的，味道才冲。",
        ],
    },
    {
        "id": "arctic-surf-clam",
        "name_cn": "北极贝",
        "name_en": "Arctic Surf Clams",
        "aliases": ["北极贝", "Arctic Surf Clams"],
        "section": "seafood",
        "tags": ["北极贝", "海鲜", "凉菜"],
        "ingredients": [
            {"label": "北极贝", "qty": "半袋，约500g", "code": "BJB", "required": True},
            {"label": "生抽", "qty": "1汤匙", "code": "078895128789", "required": False},
            {"label": "小葱", "qty": "1根", "code": "HFCXCXC", "required": False},
        ],
        "steps": [
            "约15分钟，另计解冻，2–3人份。整袋是1公斤，这一碟用半袋。放冰箱冷藏化开，不要泡热水，也不要化了再冻。",
            "冲洗后斜刀切薄片。当天吃完。",
            "生抽做蘸汁，有芥末就加一点，葱切细撒上。",
            "不想生吃：水烧开，贝片焯20–30秒就捞。再久就老了。",
        ],
    },
]


def main():
    products = json.loads((ROOT / "data" / "products.json").read_text(encoding="utf-8-sig"))
    codes = {p.get("code") for p in products["items"]}

    need = set()
    for recipe in CONTENT:
        for ing in recipe["ingredients"]:
            if ing.get("code"):
                need.add(ing["code"])
    missing = sorted(need - codes)
    if missing:
        raise SystemExit("商品库没有这些编号：" + ", ".join(missing))

    path = ROOT / "data" / "recipes.json"
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    existing = {r["id"] for r in data["recipes"]}
    added = 0
    for recipe in CONTENT:
        if recipe["id"] in existing:
            continue
        data["recipes"].append({
            "id": recipe["id"],
            "name_cn": recipe["name_cn"],
            "name_en": recipe["name_en"],
            "aliases": recipe["aliases"],
            "section": recipe["section"],
            "kind": "dish",
            "priority": 96,
            "image": "assets/images/%s.jpg" % recipe["id"],
            "image_credit": "品牌字卡，还没有成品照片",
            "tags": recipe["tags"],
            "ingredients": recipe["ingredients"],
            "steps": recipe["steps"],
        })
        added += 1
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("added", added, "total", len(data["recipes"]))


if __name__ == "__main__":
    main()
