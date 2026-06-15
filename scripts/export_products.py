#!/usr/bin/env python3
"""export_products.py — Pull products + categories from StockWise API and write data/products.json.

Usage:
    python export_products.py \
        --api https://stockwise-app-873982544406.us-central1.run.app \
        --out ../data/products.json

Both endpoints are public (no-auth GET), verified in stockwise_final/auth.py is_public_path():
  GET /api/firebase/categories  → {"categories": [<name>, ...], ...}
  GET /api/firebase/products    → {"products": [{doc fields}, ...], ...}
"""
import argparse
import json
import sys
from datetime import datetime, timezone

import requests

from recipe_lib import build_product_record

# ── CLI ──────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description="Export StockWise products to products.json")
    p.add_argument(
        "--api",
        default="https://stockwise-app-873982544406.us-central1.run.app",
        help="StockWise API base URL (no trailing slash)",
    )
    p.add_argument(
        "--out",
        default="../data/products.json",
        help="Output path for products.json",
    )
    return p.parse_args()

# ── Data fetchers ─────────────────────────────────────────────────────────────

def load_valid_categories(api_base: str) -> set:
    """GET /api/firebase/categories → set of active category name strings."""
    url = f"{api_base.rstrip('/')}/api/firebase/categories"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    cats = data.get("categories", [])
    if not cats:
        print("WARNING: categories endpoint returned empty list", file=sys.stderr)
    return set(cats)


def load_products(api_base: str) -> list:
    """GET /api/firebase/products?limit=5000 → list of raw product dicts."""
    url = f"{api_base.rstrip('/')}/api/firebase/products"
    params = {"limit": 5000}
    resp = requests.get(url, params=params, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    products = data.get("products", [])
    return products


def load_sold_90d(api_base: str) -> dict:
    """Return per-product 90-day sales keyed by clover_item_id.

    No public endpoint exists for sales data in v1 — returns empty dict so
    build_product_record() defaults sold_90d to 0.
    """
    # Sourcing/sales endpoints require admin auth; skip for public export.
    return {}

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    args = parse_args()
    api = args.api.rstrip("/")
    out_path = args.out

    print(f"Fetching categories from {api} …")
    valid_categories = load_valid_categories(api)
    print(f"  {len(valid_categories)} categories: {sorted(valid_categories)}")

    print(f"Fetching products from {api} …")
    raw_products = load_products(api)
    print(f"  {len(raw_products)} products fetched (before filtering)")

    sold_map = load_sold_90d(api)  # empty dict in v1

    items = []
    skipped_deleted = 0
    skipped_no_code = 0
    warned_category = 0

    for doc in raw_products:
        # Skip deleted products
        if doc.get("deleted"):
            skipped_deleted += 1
            continue

        record = build_product_record(doc, valid_categories, sold_90d=sold_map.get(doc.get("clover_item_id", ""), 0))

        # Skip records with empty code
        if not record.get("code"):
            skipped_no_code += 1
            continue

        # Warn on non-standard category
        if record["category"] and record["category"] not in valid_categories:
            print(
                f"WARN: non-standard category '{record['category']}' on product {record['code']} — {record['name_cn'] or record['name_en']}",
                file=sys.stderr,
            )
            warned_category += 1

        items.append(record)

    # Deduplicate by code (keep last seen — API shouldn't have dupes but be safe)
    seen = {}
    for item in items:
        seen[item["code"]] = item
    items = list(seen.values())

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "items": items,
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(
        f"\nWrote {len(items)} products to {out_path}\n"
        f"  Skipped deleted: {skipped_deleted}\n"
        f"  Skipped no-code: {skipped_no_code}\n"
        f"  Category warnings: {warned_category}\n"
        f"  sold_90d: defaulted to 0 (no public sales endpoint in v1)"
    )


if __name__ == "__main__":
    main()
