"""Audit recipe bindings against the shelf snapshot or the public storefront API."""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import sys
from urllib.parse import urlencode
from urllib.request import urlopen

from recipe_lib import score_match

ROOT = Path(__file__).resolve().parents[1]


def public_matches(api, code):
    query = urlencode({"search": code, "limit": 20})
    with urlopen(f"{api.rstrip('/')}/api/firebase/products?{query}", timeout=12) as response:
        rows = json.load(response)["products"]
    return {row["id"]: row for row in rows if any(
        str(value or "").strip().lower() == code.lower()
        for value in [row.get("code"), row.get("sku"), row.get("alt_code"), *(row.get("alt_codes") or [])]
    )}


def live_status(rows):
    if not rows:
        return "missing_public"
    if len(rows) > 1:
        return "ambiguous_public"
    row = next(iter(rows.values()))
    if row.get("available_for_delivery") is False:
        return "delivery_disabled"
    if row.get("want_only"):
        return "want_only"
    price = row.get("price")
    if not isinstance(price, (int, float)) or not 0 < price < float("inf"):
        return "invalid_price"
    return "buyable"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api", help="StockWise base URL for live, read-only checks")
    parser.add_argument("--recipe", help="Limit the audit to one recipe ID")
    args = parser.parse_args()
    recipes = json.loads((ROOT / "data/recipes.json").read_text(encoding="utf-8"))["recipes"]
    if args.recipe:
        recipes = [recipe for recipe in recipes if recipe["id"] == args.recipe]
        if not recipes:
            parser.error("Unknown recipe ID")
    products = json.loads((ROOT / "data/products.json").read_text(encoding="utf-8"))["items"]
    by_code = defaultdict(list)
    for product in products:
        by_code[product["code"]].append(product)

    cache = {}
    counts = Counter()
    issues = []
    for recipe in recipes:
        for ingredient in recipe["ingredients"]:
            code = (ingredient.get("code") or "").strip()
            label = ingredient["label"]
            required = bool(ingredient.get("required"))
            if not code:
                status = "unbound"
            elif args.api:
                if code not in cache:
                    cache[code] = live_status(public_matches(args.api, code))
                status = cache[code]
            else:
                matches = len(by_code[code])
                status = {0: "missing_snapshot", 1: "matched_snapshot"}.get(matches, "ambiguous_snapshot")
            counts[("required" if required else "optional", status)] += 1
            if status not in {"buyable", "matched_snapshot"}:
                row = {"recipe": recipe["id"], "label": label, "code": code, "required": required, "status": status}
                if not code:
                    row["candidates"] = [
                        {"code": product["code"], "name": product.get("name_cn")}
                        for product, score in score_match(label, products)[:3] if score > 0
                    ]
                issues.append(row)
    report = {
        "source": "public_api" if args.api else "shelf_snapshot",
        "recipes": len(recipes),
        "counts": {f"{group}.{status}": count for (group, status), count in sorted(counts.items())},
        "issues": issues,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    try:
        main()
    except OSError as exc:
        sys.exit(f"Audit incomplete: {exc}")
