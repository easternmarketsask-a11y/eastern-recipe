"""bind_ingredients.py — 半自动绑定：读 recipes.json 里未绑定(code=null)的食材，
对 products.json 打分，输出候选供人工确认。
用法: python scripts/bind_ingredients.py --products data/products.json --recipes data/recipes.json --topn 3
"""
import argparse, json
import recipe_lib as rl

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--products", default="data/products.json")
    ap.add_argument("--recipes", default="data/recipes.json")
    ap.add_argument("--topn", type=int, default=3)
    args = ap.parse_args()

    products = json.load(open(args.products, encoding="utf-8"))["items"]
    recipes = json.load(open(args.recipes, encoding="utf-8"))["recipes"]

    for r in recipes:
        for ing in r.get("ingredients", []):
            if ing.get("code"):
                continue
            ranked = [x for x in rl.score_match(ing["label"], products) if x[1] > 0][: args.topn]
            print("\n[%s] 食材「%s」候选：" % (r["id"], ing["label"]))
            if not ranked:
                print("  （无候选，建议标 code=null 暂缺）")
            for p, s in ranked:
                print("  %.1f  %s  %s / %s  $%s" %
                      (s, p["code"], p.get("name_cn"), p.get("name_en"), p.get("price")))

if __name__ == "__main__":
    main()
