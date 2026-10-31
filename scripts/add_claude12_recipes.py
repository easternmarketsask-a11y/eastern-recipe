"""Claude-12 batch (2026-11): 12 dishes incl. soup section; idempotent, no network.

Mains picked from 2026-10-15~10-29 14-day EM-POS revenue (see
docs/content-ingredients-2026-11-01.json): noodle/rice staples anchor the
staple section, water-boiled dishes ride the hot pot wave, pepper pork-tripe
chicken soup leads the new soup board. Run, then recipe_facts.py,
add_ingredient_aliases.py, optimize_images.py, build_static_pages.py.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CREDIT = "AI-generated illustration; Muse Image, 2026-10-31"

P = {
    "牛肉卷": "0723nrj", "酸汤肥牛": "6920143506808",
    "金针菇": "6931787400001", "娃娃菜": "WWC",
    "黄灯笼辣酱": "6921464025887",
    "羊肩肉": "6944", "京葱": "10636jcjcjc",
    "梅头猪肉卷": "700953767868", "郫县豆瓣": "6909003200193",
    "豆芽": "1024", "生菜": "Yscysc", "花椒粉": "6948691110063",
    "蚝油": "6922824007468",
    "香米": "628774325817", "鸡蛋": "2008",
    "大虾": "209145dxdx827510004140", "腊肠": "074545300215",
    "皮蛋": "6920775217509", "猪肉碎": "627735189635",
    "拉面": "800794206004", "新竹米粉": "4712862612074",
    "韭菜": "1015", "洋葱": "1087ycyc", "咖喱粉": "HCLF",
    "白萝卜": "1028blb", "三黄鸡": "4889shj",
    "猪肚鸡汤料": "6976760276723", "干香菇": "871392001636",
    "红枣": "6941837101611", "枸杞": "698921027979",
    "安格斯牛肋条": "NknIRL292NLT", "馄饨皮": "066279008116",
    "蒜": "0178", "姜": "1037", "小葱": "HFCXCXC",
    "生抽": "078895128789", "老抽": "722337817020",
    "料酒": "6907592001245", "白砂糖": "063111103541",
    "淀粉": "6941837101024", "白胡椒粉": "698921021831",
    "芝麻油": "742812710905", "香醋": "6901055000011",
    "辣椒油": "213466668855", "干辣椒": "6971005993144",
}

# Kitchen basics with no snapshot code: exempt from the evidence assert.
CODELESS = {"盐", "水", "食用油"}

# Search aliases: full name + short name + pinyin + short English.
ALIASES = {
    "suantang-feiniu": ["酸汤肥牛", "酸汤牛肉", "suantang feiniu", "sour soup beef"],
    "congbao-yangrou": ["葱爆羊肉", "葱爆羊肩肉", "congbao yangrou", "scallion lamb"],
    "shuizhu-roupian": ["水煮肉片", "水煮猪肉", "shuizhu roupian", "boiled pork slices"],
    "jinzhen-feiniu-juan": ["金针菇肥牛卷", "肥牛金针菇卷", "feiniu juan", "beef enoki rolls"],
    "yangzhou-chaofan": ["扬州炒饭", "什锦炒饭", "chaofan", "yangzhou fried rice"],
    "pidan-shourou-zhou": ["皮蛋瘦肉粥", "皮蛋粥", "zhou", "congee"],
    "congyou-banmian": ["葱油拌面", "葱油面", "banmian", "scallion oil noodles"],
    "xingzhou-chaomifen": ["星洲炒米粉", "星洲米粉", "chaomifen", "singapore noodles"],
    "lamb-daikon-soup": ["白萝卜羊肉汤", "羊肉萝卜汤", "yangrou tang", "lamb daikon soup"],
    "pepper-pork-tripe-chicken-soup": ["胡椒猪肚鸡汤", "猪肚鸡汤", "zhuduji", "pepper chicken soup"],
    "shuizhu-niurou": ["水煮牛肉", "水煮牛肋条", "shuizhu niurou", "boiled beef"],
    "hongyou-chaoshou": ["红油抄手", "抄手", "馄饨", "hongyou chaoshou", "chili wontons"],
}

# id, name, English, section, kind, priority, tags, ingredients(label, qty, main), steps
CONTENT = [
    ("suantang-feiniu", "酸汤肥牛", "Beef Slices in Sour Soup",
     "tonight", "dish", 94, ["牛肉", "快手菜", "下饭", "开胃"],
     [("牛肉卷", "1盒，635g", 1), ("酸汤肥牛", "1袋，100g", 1),
      ("金针菇", "200g", 1), ("娃娃菜", "1棵", 1),
      ("蒜", "3瓣", 1), ("姜", "3片", 1),
      ("黄灯笼辣酱", "1汤匙（加辣用）", 0), ("小葱", "2根", 0)],
     ["约25分钟，3人份。牛肉卷回温10分钟，不要全解冻，微冻才好分片；金针菇去根撕开，娃娃菜切块。",
      "金针菇、娃娃菜焯1分钟铺碗底。",
      "锅中加油爆香蒜姜，加酸汤料和约800ml水煮沸；先尝咸淡，调料已有咸酸味，一般不用加盐，要辣加1汤匙黄灯笼。",
      "牛肉一片片下锅，变色30–60秒立刻关火，久煮必老。",
      "连汤浇在配菜上，撒葱花。汤拌饭比肉还抢手。"]),
    ("congbao-yangrou", "葱爆羊肉", "Scallion Lamb Stir-Fry",
     "tonight", "dish", 91, ["羊肉", "快手菜", "下饭"],
     [("羊肩肉", "500g，切薄片", 1), ("京葱", "2根", 1),
      ("生抽", "1汤匙", 1), ("料酒", "1汤匙", 1), ("淀粉", "1茶匙", 1),
      ("姜", "3片", 1), ("蒜", "2瓣", 0), ("芝麻油", "数滴", 0)],
     ["约20分钟，3人份。羊肩肉逆纹切薄片，加生抽、淀粉抓浆腌10分钟；京葱斜切段。",
      "锅烧到冒烟加油，羊肉滑炒变色立刻盛出。",
      "留底油爆京葱到边缘微焦，下姜蒜炒香。",
      "羊肉回锅，沿锅边淋料酒，大火翻匀，滴芝麻油出锅。"]),
    ("shuizhu-roupian", "水煮肉片", "Sichuan Boiled Pork Slices",
     "tonight", "dish", 92, ["猪肉", "川菜", "下饭", "香辣"],
     [("梅头猪肉卷", "约400g", 1), ("郫县豆瓣", "2汤匙", 1),
      ("豆芽", "300g", 1), ("生菜", "1颗", 1),
      ("干辣椒", "8个", 1), ("花椒粉", "1茶匙", 1),
      ("蒜", "4瓣", 1), ("姜", "3片", 1),
      ("生抽", "1汤匙", 1), ("料酒", "1汤匙", 1), ("淀粉", "1汤匙", 1),
      ("小葱", "2根", 0)],
     ["约30分钟，3–4人份。肉片加生抽、料酒、淀粉上浆腌15分钟；豆芽生菜焯水铺碗底。",
      "锅中加油炒郫县豆瓣出红油，加约800ml水煮沸，加盐调味。",
      "转小火保持微沸，肉片一片片下锅，变白浮起就连汤倒进碗里。",
      "面上撒蒜末、干辣椒段和花椒粉，烧3汤匙热油浇香，撒葱花。"]),
    ("jinzhen-feiniu-juan", "金针菇肥牛卷", "Enoki Beef Rolls",
     "tonight", "dish", 93, ["牛肉", "快手菜", "下饭"],
     [("牛肉卷", "1盒，635g", 1), ("金针菇", "2包", 1),
      ("生抽", "2汤匙", 1), ("蚝油", "1汤匙", 1),
      ("蒜", "2瓣", 0), ("小葱", "1根", 0), ("白砂糖", "1茶匙", 0)],
     ["约20分钟，2–3人份。金针菇去根分成12束，每片牛肉卷一束，收口朝下。",
      "生抽2汤匙、蚝油1汤匙、白砂糖和半碗水调成汁。",
      "平底锅加少许油，肉卷收口朝下煎定型再翻面。",
      "倒汁加盖焖3分钟，开盖收浓，撒葱花蒜末。"]),
    ("yangzhou-chaofan", "扬州炒饭", "Yangzhou Fried Rice",
     "staple", "dish", 92, ["主食", "米饭", "快手菜"],
     [("香米", "约600g隔夜冷饭", 1), ("鸡蛋", "3个", 1),
      ("大虾", "8–10只，去壳", 1), ("腊肠", "2根，切丁", 1),
      ("小葱", "3根", 1), ("生菜", "2片，切丝", 0),
      ("白胡椒粉", "少许", 0)],
     ["约20分钟，3–4人份。大虾去壳去线抓少许淀粉；鸡蛋打散；腊肠切丁；冷饭压散。",
      "先炒虾仁变色盛出，再炒鸡蛋凝固盛出。",
      "腊肠丁炒出油，下冷饭大火压散，炒到粒粒分明。",
      "蛋虾回锅，加盐和白胡椒粉，下生菜丝和葱花翻匀出锅。"]),
    ("pidan-shourou-zhou", "皮蛋瘦肉粥", "Century Egg and Pork Congee",
     "staple", "dish", 90, ["主食", "粥", "早餐"],
     [("皮蛋", "2个", 1), ("猪肉碎", "150g", 1), ("香米", "150g", 1),
      ("姜", "1小块，切丝", 1), ("小葱", "2根", 0),
      ("白胡椒粉", "少许", 0), ("芝麻油", "数滴", 0),
      ("料酒", "1茶匙", 0), ("淀粉", "1茶匙", 0)],
     ["约50分钟，4人份。香米洗净拌少许油和盐腌20分钟；皮蛋切块；肉碎加料酒淀粉抓匀。",
      "水开下米，大火10分钟转小火熬35–40分钟，熬到开花绵滑，中途多搅防糊底。",
      "一半皮蛋先下锅煮出味，肉碎拨散下锅煮3分钟。",
      "剩下皮蛋最后下锅保形状，加盐、白胡椒粉，撒葱花姜丝，滴芝麻油。"]),
    ("congyou-banmian", "上海葱油拌面", "Shanghai Scallion Oil Noodles",
     "staple", "dish", 91, ["主食", "面条", "快手菜"],
     [("拉面", "2份", 1), ("小葱", "1大把，约150g", 1),
      ("生抽", "3汤匙", 1), ("老抽", "1汤匙", 1),
      ("白砂糖", "1汤匙", 1), ("食用油", "80ml", 1)],
     ["约25分钟，2人份。小葱洗净擦干，有水下锅会溅；葱白葱绿分开切段。",
      "冷油下葱白小火熬5分钟，再下葱绿熬到焦黄酥脆，捞出葱酥。",
      "葱油加生抽、老抽和白砂糖搅匀成酱汁，多余的装瓶冷藏一周。",
      "面煮熟捞出，每碗浇2汤匙酱汁拌匀，铺葱酥。"]),
    ("xingzhou-chaomifen", "星洲炒米粉", "Singapore Chow Mei Fun",
     "staple", "dish", 90, ["主食", "米粉", "快手菜"],
     [("新竹米粉", "300g", 1), ("大虾", "8只，去壳", 1),
      ("腊肠", "2根，切片", 1), ("鸡蛋", "2个", 1),
      ("豆芽", "150g", 1), ("韭菜", "1小把", 1),
      ("洋葱", "半个", 1), ("咖喱粉", "1大匙", 1)],
     ["约25分钟，3–4人份。新竹米粉温水泡15分钟，捞出剪两刀；鸡蛋虾仁腊肠分别炒好盛出。",
      "锅中加油爆香洋葱，下米粉，沿锅边淋少许水防干。",
      "撒咖喱粉1大匙炒匀，炒到米粉金黄干爽。",
      "全部回锅，豆芽韭菜最后下锅翻匀，加盐调味。"]),
    ("lamb-daikon-soup", "白萝卜羊肉汤", "Lamb and Daikon Soup",
     "soup", "dish", 94, ["羊肉", "白萝卜", "喝汤", "暖身"],
     [("羊肩肉", "约800g", 1), ("白萝卜", "1根，约600g", 1),
      ("姜", "1大块", 1), ("枸杞", "1小把", 0),
      ("料酒", "2汤匙", 1), ("白胡椒粉", "1茶匙", 1),
      ("小葱", "2根", 0)],
     ["约90分钟，4人份。羊肩肉切块冷水下锅，焯5分钟洗净；姜拍松。",
      "约2升热水下羊肉和姜，小火炖60分钟，撇净浮沫。",
      "白萝卜切滚刀块下锅，再炖25分钟到能戳透。",
      "加盐和白胡椒粉，枸杞最后2分钟下锅，撒葱花。"]),
    ("pepper-pork-tripe-chicken-soup", "胡椒猪肚鸡汤", "White Pepper Chicken Soup",
     "soup", "dish", 93, ["鸡", "喝汤", "暖身", "胡椒"],
     [("三黄鸡", "半只，约600g", 1), ("猪肚鸡汤料", "1袋，190g", 1),
      ("白胡椒粉", "1茶匙", 1), ("干香菇", "6朵", 1),
      ("红枣", "6颗", 0), ("枸杞", "1小把", 0),
      ("姜", "1大块", 1), ("料酒", "1汤匙", 1)],
     ["约100分钟，4人份。三黄鸡斩块焯水；干香菇泡发；这是汤料简版，肉柜若有新鲜猪肚，切条在炖鸡时一同下锅即升级正版。",
      "鸡块加姜和约2升水，小火炖50分钟。",
      "下猪肚鸡汤料、香菇、红枣和枸杞，再炖15分钟。",
      "白胡椒先加1茶匙尝着加，加盐调味，胡椒味够正才出锅。"]),
    ("shuizhu-niurou", "水煮牛肉", "Sichuan Boiled Beef Slices",
     "tonight", "dish", 95, ["牛肉", "川菜", "下饭", "香辣"],
     [("安格斯牛肋条", "500g，逆纹薄片", 1), ("郫县豆瓣", "2汤匙", 1),
      ("豆芽", "300g", 1), ("生菜", "1颗", 1),
      ("干辣椒", "8个", 1), ("花椒粉", "1茶匙", 1),
      ("蒜", "4瓣", 1), ("姜", "3片", 1),
      ("生抽", "1汤匙", 1), ("料酒", "1汤匙", 1), ("淀粉", "1汤匙", 1),
      ("小葱", "2根", 0)],
     ["约30分钟，3–4人份。牛肋条逆纹切薄片，加生抽、料酒、淀粉上浆腌15分钟，图省事可用牛肉卷；豆芽生菜焯水铺碗底。",
      "锅中加油炒郫县豆瓣出红油，加约800ml水煮沸。",
      "小火微沸下牛肉片，变色连汤倒碗。",
      "面上撒蒜末辣椒花椒，热油浇香，撒葱花。和水煮肉片同一套，学会一个等于会两个。"]),
    ("hongyou-chaoshou", "红油抄手", "Wontons in Chili Oil",
     "dumpling", "dish", 92, ["馄饨", "川菜", "现包", "香辣"],
     [("馄饨皮", "1袋，454g", 1), ("猪肉碎", "250g", 1),
      ("姜", "1小块", 1), ("小葱", "3根", 1),
      ("生抽", "1汤匙", 1), ("花椒粉", "1/2茶匙", 1),
      ("蒜", "3瓣", 1), ("辣椒油", "2汤匙", 1), ("香醋", "1汤匙", 1),
      ("芝麻油", "1茶匙", 0), ("料酒", "1茶匙", 0),
      ("白胡椒粉", "少许", 0)],
     ["约35分钟，约30个，3人份。肉碎加生抽、料酒、白胡椒粉和葱姜水，朝一个方向搅上胶。",
      "1茶匙馅包一个元宝形；多包的平铺冷冻，随吃随煮。",
      "碗底先调红油汁：辣椒油、香醋、蒜末、花椒粉和少许煮馄饨的原汤。",
      "水开下锅，浮起再煮1分钟，连汤舀进碗化开酱汁拌匀。"]),
]


def main():
    path = ROOT / "data" / "recipes.json"
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    existing = {r["id"] for r in data["recipes"]}
    products = {p["code"] for p in json.loads((ROOT / "data" / "products.json").read_text(encoding="utf-8-sig"))["items"]}
    checked = {p["code"] for p in json.loads((ROOT / "docs" / "content-ingredients-2026-11-01.json").read_text(encoding="utf-8-sig"))["products"]}
    for rid, cn, en, section, kind, prio, tags, ingredients, steps in CONTENT:
        assert all(P.get(label) in checked for label, _, main in ingredients if main and label not in CODELESS), rid
        rows = [{"label": label, "qty": qty, "code": P.get(label) if P.get(label) in products else None, "required": bool(main)} for label, qty, main in ingredients]
        if rid not in existing:
            data["recipes"].append({"id": rid, "name_cn": cn, "name_en": en, "aliases": ALIASES[rid],
                                    "section": section, "kind": kind, "priority": prio,
                                    "image": f"assets/images/{rid}-ai-202611.jpg", "image_credit": CREDIT,
                                    "tags": tags, "ingredients": rows, "steps": steps})
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Recipes: {len(data['recipes'])}; batch: {len(CONTENT)}")


if __name__ == "__main__":
    main()
