# -*- coding: utf-8 -*-
"""Attach common alternative names (alt) to recipe ingredients so customers
can search a dish by any colloquial / regional ingredient name."""
import json

# canonical substring (appears in ingredient label) -> alternative search terms
SYN = {
    # 肉类
    "牛腩":   ["牛肋条", "安格斯牛腩", "坑腩"],
    "牛肉卷": ["肥牛", "肥牛卷", "涮牛肉"],
    "牛肉":   ["牛柳", "牛里脊"],
    "五花肉": ["三层肉", "腩肉", "猪腩肉"],
    "排骨":   ["肋排", "子排", "猪小排"],
    "叉烧":   ["叉燒", "蜜汁叉烧"],
    "腊味":   ["腊肠", "腊肉", "广式腊味", "腊鸭"],
    "腊肠":   ["香肠", "广式香肠", "膶肠"],
    "鸡":     ["光鸡", "三黄鸡", "土鸡"],
    # 海鲜
    "鱿鱼":   ["枪乌贼", "柔鱼", "鲜鱿"],
    "虾仁":   ["虾肉", "基围虾仁", "虾球"],
    "虾":     ["基围虾", "明虾", "海虾"],
    "扇贝":   ["带子", "元贝", "瑶柱"],
    "鲈鱼":   ["花鲈", "七星鲈", "海鲈"],
    "鱼丸":   ["鱼蛋", "鱼圆"],
    # 蔬菜
    "香菜":   ["芫荽", "芫茜", "胡荽"],
    "生菜":   ["唛仔菜", "西生菜", "玻璃生菜"],
    "油麦菜": ["莜麦菜", "苦菜"],
    "土豆":   ["马铃薯", "洋芋", "薯仔"],
    "番茄":   ["西红柿", "洋柿子"],
    "青椒":   ["灯笼椒", "柿子椒", "菜椒"],
    "芥兰":   ["芥蓝", "盖兰菜"],
    "菜心":   ["菜薹", "广东菜心", "心菜"],
    "茄子":   ["矮瓜", "吊菜子"],
    "苦瓜":   ["凉瓜"],
    "冬瓜":   ["白瓜"],
    "玉米":   ["苞米", "粟米", "包谷"],
    "茼蒿":   ["蒿子杆", "皇帝菜", "蓬蒿"],
    "空心菜": ["通菜", "蕹菜"],
    "韭菜":   ["扁菜", "起阳草"],
    "包菜":   ["卷心菜", "圆白菜", "椰菜", "莲花白"],
    "白菜":   ["大白菜", "黄芽白", "绍菜"],
    "萝卜":   ["白萝卜", "莱菔"],
    "蒜苗":   ["青蒜", "蒜青"],
    "蒜苔":   ["蒜薹", "蒜毫"],
    "豆芽":   ["银芽", "芽菜", "黄豆芽", "绿豆芽"],
    "木耳":   ["黑木耳", "云耳"],
    "香菇":   ["冬菇", "花菇", "香蕈"],
    # 主食 / 粉面 / 豆制品
    "河粉":   ["沙河粉", "粿条", "贵刁", "粄条"],
    "肠粉":   ["猪肠粉", "拉肠", "布拉肠"],
    "粉丝":   ["冬粉", "龙口粉丝", "细粉"],
    "粉条":   ["宽粉", "红薯粉"],
    "豆腐":   ["水豆腐", "嫩豆腐", "老豆腐"],
    "腐竹":   ["支竹", "豆筋"],
    "鸡蛋":   ["鸡子", "土鸡蛋"],
    # 葱蒜姜（注意 洋葱 单独处理，避免被 葱 误匹配）
    "洋葱":   ["圆葱", "球葱"],
    "葱":     ["大葱", "香葱", "青葱"],
    "蒜":     ["大蒜", "蒜头", "蒜瓣"],
    "姜":     ["生姜", "老姜"],
}

# keys sorted longest-first so the most specific match wins per label
KEYS = sorted(SYN.keys(), key=len, reverse=True)

rj = r"D:\easternmarket.ca\eastern-recipe\data\recipes.json"
data = json.load(open(rj, encoding="utf-8"))

touched = 0
for r in data["recipes"]:
    for ing in r.get("ingredients", []):
        # 勾芡/腌肉的"土豆淀粉"在菜谱里就叫"淀粉"，避免搜"土豆"误中一堆勾芡菜
        if "土豆淀粉" in ing["label"]:
            ing["label"] = ing["label"].replace("土豆淀粉", "淀粉")
        label = ing["label"]
        # pick the single longest canonical key contained in this label
        chosen = None
        for k in KEYS:
            if k in label:
                # 土豆淀粉/生粉是芡粉，不是土豆这味菜料，别挂"马铃薯"别名
                if k == "土豆" and ("淀粉" in label or "生粉" in label or "粉" in label):
                    continue
                chosen = k
                break
        if not chosen:
            ing.pop("alt", None)
            continue
        alts = SYN[chosen]
        # don't duplicate terms already present in the label itself
        alts = [a for a in alts if a not in label]
        if alts:
            ing["alt"] = alts
            touched += 1
        else:
            ing.pop("alt", None)

json.dump(data, open(rj, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("ingredients tagged with alt:", touched)
