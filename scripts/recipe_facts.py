# -*- coding: utf-8 -*-
"""每道菜的上桌时间、人数、今晚理由，以及成品的真实加热方式。

这些字段写进 data/recipes.json，应用和静态页都读那一份。
改完这里再跑：python scripts/recipe_facts.py
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RECIPES_PATH = os.path.join(ROOT, "data", "recipes.json")

METHODS = ("steam", "boil", "pan", "fry", "microwave", "room")
DECIDE = ("quick", "family", "weekend")

# 成品加热方式 → 给顾客看的说法。不许再把煮、煎、微波一律写成「蒸」。
METHOD_LABEL = {
    "steam": "蒸一蒸",
    "boil": "煮一煮",
    "pan": "煎一煎",
    "fry": "炸或烤",
    "microwave": "热一热",
    "room": "打开就能吃",
}


def _row(minutes, servings, hook, method="", family="", decide="", pairs=()):
    row = {"minutes": minutes, "servings": servings, "hook": hook}
    if method:
        row["method"] = method
    if family:
        row["family"] = family
    if decide:
        row["decide"] = decide
    if pairs:
        row["pairs"] = list(pairs)
    return row


# 键是食谱 id。minutes 是从开始到能吃的大致分钟，含步骤里写明的腌、泡、炖。
FACTS = {
    "hotpot": _row(40, "4人", "羊卷、牛卷、白菜和豆腐，周末围一桌就够。",
                   decide="weekend", pairs=("huaxia-hua", "moyuwan", "veg-enoki-cold")),
    "red-braised-pork": _row(75, "4人", "五花肉小火炖一小时，汁收到发亮就下饭。",
                             pairs=("blanched-choy-sum", "choy-sum-garlic")),
    "braised-beef-brisket": _row(120, "4人", "牛腩要炖到筷子插得进，周末提前上锅。",
                                 pairs=("cant-haoyou-shengcai",)),
    "soy-braised-beef-shank": _row(160, "4人", "牛腱卤好切片，冷藏泡一夜更入味。",
                                   pairs=("veg-celtuce-garlic", "liangban-gandoufu")),
    "white-cut-chicken": _row(45, "4人", "整鸡浸熟，配一碟菜心就是一桌。",
                              pairs=("choy-sum-garlic", "blanched-choy-sum")),
    "twice-cooked-pork": _row(40, "3人", "五花肉回锅，蒜苗和豆瓣酱一起下饭。",
                              pairs=("hot-sour-potato", "veg-shanghai-qing")),
    "cumin-lamb": _row(25, "3人", "羊肩肉快炒，孜然味一出来就能吃。",
                       pairs=("veg-celtuce-garlic",)),
    "tomato-beef-brisket": _row(120, "4人", "番茄把牛腩炖软，汤拌饭就够。",
                                pairs=("gai-lan-oyster-sauce",)),
    "beef-chow-fun": _row(30, "3人", "周四到的河粉，大火快炒才不粘。",
                          pairs=("veg-shanghai-qing", "soy-sauce-cheung-fun")),
    "wet-beef-ho-fun": _row(30, "3人", "河粉垫底，牛肉芥兰连汁浇上去。",
                            pairs=("beef-chow-fun",)),
    "soy-sauce-cheung-fun": _row(15, "2人", "肠粉切段，XO酱和豉油一起炒两分钟。",
                                 pairs=("cheung-fun-ready",)),
    "beef-brisket-noodle-soup": _row(110, "3人", "牛腩汤先炖软，河粉下锅两分钟。",
                                     pairs=("veg-tonghao-garlic",)),
    "cheung-fun-ready": _row(8, "2人", "不用解冻，蒸到软透，蘸生抽就吃。",
                             method="steam", pairs=("soy-sauce-cheung-fun",)),
    "youtiao-ready": _row(10, "2人", "冷冻直接下锅，炸或烤箱都能脆。",
                          method="fry", pairs=("pumpkin-millet-congee",)),
    "nai-huang-bao-ready": _row(15, "2人", "水开再蒸，焖两分钟才不会塌。",
                                method="steam", family="bun",
                                pairs=("huajuan-ready", "pumpkin-millet-congee")),
    "shouzhuabing-ready": _row(8, "2人", "平底锅不用加油，两面煎到起层。",
                               method="pan", pairs=("scallion-egg-pancake",)),
    "huajuan-ready": _row(12, "2人", "冷冻直接蒸，配粥或炒菜都行。",
                          method="steam", family="bun"),
    "hei-jin-liusha-bao-ready": _row(15, "2人", "蒸好焖一分钟再开盖，流沙才烫不到。",
                                     method="steam", family="bun"),
    "cha-shao-bao-ready": _row(15, "2人", "蒸到顶部微微开裂是熟了，不是蒸坏。",
                               method="steam", family="bun"),
    "xian-rou-dabao-ready": _row(18, "2–3人", "一只就顶一顿，蒸好焖两分钟再揭盖。",
                                 method="steam", family="bun"),
    "mapo-tofu": _row(20, "2人", "豆腐焯一下再下锅，豆瓣酱炒出红油。",
                      pairs=("hot-sour-potato", "seaweed-egg-soup")),
    "tomato-egg": _row(15, "2人", "番茄、鸡蛋、葱，店里都有。十五分钟，米饭就有菜。",
                       decide="quick", pairs=("choy-sum-garlic", "seaweed-egg-soup")),
    "pork-green-pepper": _row(20, "2人", "青椒留一点脆，肉末炒散就能拌饭。",
                              pairs=("tomato-egg",)),
    "blanched-choy-sum": _row(12, "2人", "菜心烫到碧绿就捞，热油一淋就上桌。",
                              pairs=("white-cut-chicken", "red-braised-pork")),
    "seaweed-egg-soup": _row(15, "2人", "紫菜蛋花，一锅汤把晚饭补齐。",
                             pairs=("tomato-egg", "guantang-xiaoshuijiao")),
    "xiaolongbao-ready": _row(10, "2人", "垫张油纸蒸，汤汁烫，先咬个小口。",
                              method="steam", pairs=("seaweed-egg-soup",)),
    "shumai-ready": _row(12, "2人", "不用解冻，蒸到糯米透了趁热吃。",
                         method="steam", pairs=("pumpkin-millet-congee",)),
    "purple-rice-floss-bun": _row(1, "2人", "常温就能吃，微波二十秒更松软。",
                                  method="microwave", family="bun"),
    "veg-celtuce-garlic": _row(15, "2人", "莴笋切丝快炒，断生就出锅，还是脆的。",
                               pairs=("soy-braised-beef-shank", "cumin-lamb")),
    "veg-enoki-cold": _row(10, "2人", "金针菇焯三十秒，蒜和生抽拌开胃。",
                           pairs=("hotpot",)),
    "veg-chive-egg": _row(15, "2人", "韭菜和鸡蛋，两样就够一盘。",
                          pairs=("zhurou-jiucaijiao",)),
    "veg-lotus-cold": _row(15, "2人", "藕片凉拌，清甜，适合配重口肉菜。",
                           pairs=("twice-cooked-pork", "osmanthus-lotus-root")),
    "veg-garlic-scape-pork": _row(20, "2人", "蒜苔炒肉，下饭，十分钟出锅。",
                                  pairs=("tomato-egg",)),
    "veg-napa-tofu": _row(25, "3人", "白菜和豆腐一锅炖，汤留着拌饭。",
                          pairs=("napa-pork-vermicelli",)),
    "veg-ayoumai-garlic": _row(12, "2人", "油麦菜蒜蓉快炒，叶子还是绿的就起锅。",
                               pairs=("white-cut-chicken",)),
    "veg-tonghao-garlic": _row(12, "2人", "茼蒿有香气，大火快炒，不要炒老。",
                               pairs=("beef-brisket-noodle-soup",)),
    "veg-wawacai-soup": _row(15, "2人", "娃娃菜上汤，几分钟就软，适合配米饭。",
                             pairs=("minced-pork-steamed-egg",)),
    "veg-eggplant-yuxiang": _row(25, "2人", "茄子烧出汁，鱼香酱拌饭。",
                                 pairs=("yuxiang-doufu",)),
    "veg-wintermelon-pork-soup": _row(50, "3人", "冬瓜和排骨一锅汤，晚饭有菜有汤。",
                                      pairs=("choy-sum-garlic",)),
    "veg-broccoli-oyster": _row(12, "2人", "西兰花焯绿，蚝油淋上就吃。",
                                pairs=("garlic-vermicelli-shrimp",)),
    "veg-shanghai-qing": _row(12, "2人", "上海青清炒，配河粉或红烧肉都行。",
                              pairs=("beef-chow-fun", "twice-cooked-pork")),
    "dujiao-yutou": _row(30, "3人", "鱼头铺剁椒，蒸十分钟，热油一浇。",
                         pairs=("veg-shanghai-qing",)),
    "qingzheng-luyu": _row(25, "2人", "鲈鱼蒸到筷子插得进，豉油和热油分开浇。",
                           pairs=("choy-sum-garlic",)),
    "suancai-yu": _row(30, "3人", "酸菜先煮出味，鱼片最后下一两分钟。",
                       pairs=("napa-vermicelli-pot",)),
    "baochao-youyu": _row(15, "2人", "鱿鱼焯到卷起就捞，大火快炒才不老。",
                          pairs=("veg-broccoli-oyster",)),
    "baizhuoxia": _row(15, "2人", "虾变红弯起来就捞，过久肉会柴。",
                       pairs=("qingzheng-luyu",)),
    "huaxia-hua": _row(10, "2人", "虾滑煮到浮起变白，也可以摊成虾饼。",
                       method="boil", family="hotpot-ball", pairs=("hotpot",)),
    "moyuwan": _row(8, "2人", "墨鱼丸不用解冻，下开水煮到浮起。",
                    method="boil", family="hotpot-ball", pairs=("hotpot",)),
    "shijinyuwan": _row(8, "2人", "什锦鱼丸下火锅或清汤，浮起就能吃。",
                        method="boil", family="hotpot-ball", pairs=("hotpot", "veg-napa-tofu")),
    "jiachang-doufu": _row(25, "3人", "豆腐两面煎黄，豆瓣酱和青椒一起收汁。",
                           pairs=("hot-sour-potato",)),
    "yuxiang-doufu": _row(20, "2人", "没有鱼也是鱼香，汁勾浓了拌饭。",
                          pairs=("veg-eggplant-yuxiang",)),
    "pidan-doufu": _row(10, "2人", "皮蛋和嫩豆腐，淋生抽就是一盘凉菜。",
                        pairs=("white-cut-chicken",)),
    "qincai-xianggan": _row(15, "2人", "香干先炒，芹菜后下，还是脆的。",
                            pairs=("jiachang-doufu",)),
    "liangban-gandoufu": _row(15, "2人", "干豆腐丝焯一下过凉，黄瓜一起拌。",
                              pairs=("soy-braised-beef-shank",)),
    "jidanzheng": _row(15, "2人", "蛋液过筛，小火蒸到表面平、没有流动蛋液。",
                       pairs=("pumpkin-millet-congee",)),
    "fuzhu-charou": _row(40, "2人", "腐竹先泡软，再和五花肉收汁。",
                         pairs=("veg-shanghai-qing",)),
    "guantang-xiaoshuijiao": _row(15, "3人", "水开下锅，点水三次，咬开里面有汤。",
                                  method="boil", family="dumpling",
                                  pairs=("seaweed-egg-soup",)),
    "suancai-roujiiao": _row(15, "3人", "酸菜馅解腻，煮到浮起再多一分钟。",
                             method="boil", family="dumpling",
                             pairs=("veg-napa-tofu",)),
    "bajiaojiao": _row(15, "3人", "鲅鱼馅配姜醋，煮熟就捞，不要久煮。",
                       method="boil", family="dumpling"),
    "yangroujiiao": _row(15, "3人", "羊肉饺蘸蒜醋，水开下锅，浮起再煮一分钟。",
                         method="boil", family="dumpling"),
    "zhurou-jiucaijiao": _row(15, "2人", "韭菜猪肉是家常味，煮熟蘸醋就吃。",
                              method="boil", family="dumpling",
                              pairs=("veg-chive-egg",)),
    "xihongshi-jidan-mian": _row(20, "2人", "番茄炒出汁再下面，一碗就是晚饭。",
                                 pairs=("tomato-egg",)),
    "niurou-lamian": _row(120, "2人", "牛腩先炖软，面另煮，汤浇上去。",
                          pairs=("veg-celtuce-garlic",)),
    "zhajianmian": _row(25, "2人", "甜面酱把肉丁炒香，黄瓜丝拌着吃。",
                        pairs=("liangban-gandoufu",)),
    "cant-douchi-paigu": _row(30, "3人", "排骨腌一刻钟，蒸到熟，葱花收尾。",
                              pairs=("cant-haoyou-jielan",)),
    "cant-suanrong-fensi-shanbei": _row(20, "2人", "扇贝上铺粉丝和蒜蓉，蒸六到八分钟。",
                                        pairs=("choy-sum-garlic",)),
    "cant-haoyou-shengcai": _row(10, "2人", "生菜烫断生，蚝油薄芡淋上。",
                                 pairs=("cant-mizhi-chashao", "white-cut-chicken")),
    "cant-haoyou-jielan": _row(12, "2人", "芥兰焯到翠绿就捞，蚝油只要提鲜。",
                               pairs=("cant-douchi-paigu", "gai-lan-oyster-sauce")),
    "cant-huadan-xiaren": _row(15, "2人", "虾仁先滑熟，蛋液半凝时推在一起。",
                               pairs=("cant-haoyou-shengcai",)),
    "cant-huadan-niurou": _row(15, "2人", "牛肉滑熟再回蛋液，嫩，配米饭。",
                               pairs=("cant-haoyou-jielan",)),
    "cant-lawei-baozaifan": _row(45, "2人", "腊味铺在饭上焖出锅巴，菜心最后放。",
                                 pairs=("choy-sum-garlic",)),
    "cant-mizhi-chashao": _row(150, "3人", "叉烧酱先腌两小时，烤箱半小时刷蜜。",
                               pairs=("cant-haoyou-shengcai", "cha-shao-bao-ready")),
    "cant-tangcu-paigu": _row(40, "3人", "排骨用糖醋料收汁，亮了再撒芝麻。",
                              pairs=("hot-sour-potato",)),
    "steamed-crab": _row(20, "2人", "蟹肚朝上蒸，膏不会流走，配姜醋。",
                         pairs=("pueraria-pork-soup",)),
    "lotus-pork-bone-soup": _row(100, "4人", "藕和筒骨一次把水加够，汤炖到奶白。",
                                 pairs=("choy-sum-garlic", "steamed-kabocha-yam")),
    "osmanthus-lotus-root": _row(180, "4人", "糯米先泡两小时，藕煮软放凉再切。",
                                 pairs=("taro-pork-belly",)),
    "taro-pork-belly": _row(90, "4人", "芋头和带皮五花肉扣蒸一小时，倒扣上桌。",
                            pairs=("gai-lan-oyster-sauce",)),
    "steamed-kabocha-yam": _row(20, "3人", "南瓜不用削皮，和山药一起蒸到能戳透。",
                                pairs=("lotus-pork-bone-soup",)),
    "hot-sour-potato": _row(20, "2–3人", "土豆丝冲掉淀粉再炒，醋最后放才香。",
                            pairs=("twice-cooked-pork", "mapo-tofu")),
    "scallion-braised-tofu": _row(25, "2–3人", "豆腐煎到两面黄，葱段焖出汁拌饭。",
                                  pairs=("tomato-egg",)),
    "tomato-tofu-soup": _row(20, "2–3人", "番茄先炒出红汁，豆腐小火煮，别搅碎。",
                             pairs=("scallion-braised-tofu",)),
    "napa-vermicelli-pot": _row(25, "2–3人", "白菜帮先炒，粉丝后下，留一点汤。",
                                pairs=("suancai-yu",)),
    "shiitake-pork-patty": _row(30, "2–3人", "肉饼蒸到中心熟透，蒸出来的汁留着拌饭。",
                                pairs=("gai-lan-oyster-sauce",)),
    "pumpkin-steamed-ribs": _row(60, "3人", "排骨铺在南瓜上蒸，南瓜吸的是肉汁。",
                                 pairs=("steamed-kabocha-yam",)),
    "garlic-vermicelli-shrimp": _row(30, "2–3人", "虾铺在粉丝上，蒸到虾肉不透明。",
                                     pairs=("veg-broccoli-oyster",)),
    "shrimp-tofu-pot": _row(25, "2–3人", "豆腐先入汤，虾仁最后下，鲜汤拌饭。",
                            pairs=("wintermelon-shrimp-soup",)),
    "lotus-pork-patties": _row(35, "3人", "藕切小粒不要打成泥，小火煎到中心熟。",
                               pairs=("veg-lotus-cold",)),
    "cucumber-beancurd-salad": _row(15, "2–3人", "腐竹泡到没有硬芯，和拍黄瓜现拌。",
                                    pairs=("white-cut-chicken",)),
    "napa-pork-vermicelli": _row(45, "3人", "一锅白菜、五花肉和粉丝，三个人够吃，汤也够拌饭。",
                                 decide="family", pairs=("gai-lan-oyster-sauce", "veg-napa-tofu")),
    "potato-beef-stew": _row(150, "3–4人", "牛腩先炖软再下土豆，土豆才不会煮散。",
                             pairs=("veg-tonghao-garlic",)),
    "wintermelon-shrimp-soup": _row(25, "2–3人", "冬瓜煮到边透明，虾仁最后下。",
                                    pairs=("shrimp-tofu-pot",)),
    "pumpkin-millet-congee": _row(40, "3人", "小米先煮，南瓜后下，粥自己会甜。",
                                  pairs=("youtiao-ready", "jidanzheng")),
    "scallion-egg-pancake": _row(20, "2人", "面糊摊薄，两面金黄、中间没有湿浆。",
                                 pairs=("shouzhuabing-ready", "pumpkin-millet-congee")),
    "shiitake-chicken-soup": _row(75, "3–4人", "香菇和鸡块小火炖，汤清，晚饭喝一碗。",
                                  pairs=("choy-sum-garlic",)),
    "minced-pork-steamed-egg": _row(30, "2–3人", "蛋羹蒸嫩，肉末另炒熟再铺上去。",
                                    pairs=("veg-wawacai-soup", "seaweed-egg-soup")),
    "ants-climbing-tree": _row(25, "2–3人", "肉末先炒熟，粉丝再吸汤，留一点汁。",
                               pairs=("veg-celtuce-garlic",)),
    "eggplant-tofu-braise": _row(30, "2–3人", "茄子先蒸再烧，少吸油，豆腐还是整块的。",
                                 pairs=("yuxiang-doufu",)),
    "pickled-cabbage-pork-pot": _row(70, "3人", "酸菜先尝咸淡，粉丝最后下，热着吃。",
                                     pairs=("napa-pork-vermicelli",)),
    "pueraria-pork-soup": _row(120, "4人", "粉葛是煲汤的根，和沙葛不是同一种。小火煲到粉糯。",
                               pairs=("choy-sum-garlic", "steamed-crab")),
    "gai-lan-oyster-sauce": _row(15, "2–3人", "芥兰茎先焯、叶后下，蚝油只作提鲜。",
                                 pairs=("white-cut-chicken", "napa-pork-vermicelli")),
    "choy-sum-garlic": _row(10, "2–3人", "菜心焯到翠绿就捞，蒜蓉快炒三十秒。",
                            pairs=("white-cut-chicken", "tomato-egg")),
}


_TIME_RE = re.compile(
    r"约\s*(\d+(?:\.\d+)?)\s*(?:[–\-]\s*(\d+(?:\.\d+)?))?\s*(小时|分钟)"
)


def stated_minutes(step):
    """步骤开头写了「约 N 分钟 / 小时」时，返回闭区间。没写就返回 None。

    只认开头那一处总时间。步骤中间的「煮约25分钟」是某一小步，不是整道菜的用时。
    """
    m = _TIME_RE.match((step or "").lstrip())
    if not m:
        return None
    lo = float(m.group(1))
    hi = float(m.group(2) or m.group(1))
    if m.group(3) == "小时":
        lo, hi = lo * 60, hi * 60
    return int(lo), int(round(hi))


def apply_facts(recipes):
    missing = [r.get("id") for r in recipes if r.get("id") not in FACTS]
    extra = sorted(set(FACTS) - {r.get("id") for r in recipes})
    if missing or extra:
        raise SystemExit("食谱事实对不上：缺 %s 多 %s" % (missing, extra))
    optional = ("method", "family", "decide", "pairs")
    for recipe in recipes:
        facts = FACTS[recipe["id"]]
        for key in ("minutes", "servings", "hook"):
            recipe[key] = facts[key]
        for key in optional:
            if key in facts:
                recipe[key] = facts[key]
            else:
                recipe.pop(key, None)
    return recipes


def main():
    with open(RECIPES_PATH, encoding="utf-8") as f:
        data = json.load(f)
    apply_facts(data["recipes"])
    with open(RECIPES_PATH, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("updated %d recipes" % len(data["recipes"]))


if __name__ == "__main__":
    main()
