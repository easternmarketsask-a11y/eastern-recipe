# 东方超市菜谱搜索引擎

纯静态站（GitHub Pages）。顾客搜一道菜，看到菜谱 + 食材在东方超市的价格/分类/是否在售。

## 数据流
StockWise API (Firestore products) --export_products.py--> data/products.json
手工精选 + bind_ingredients.py --> data/recipes.json
前端关联渲染（src/js）。

## 本地跑
- 前端：任意静态服务器，如 `python -m http.server 8080`，开 http://localhost:8080
- 导出商品：`python scripts/export_products.py --api <STOCKWISE_URL> --out data/products.json`
- JS 测试：`node --test test/`
- Python 测试：`python -m pytest scripts/ -v`

## 部署
push 到 GitHub（easternmarketsask-a11y/eastern-recipe）→ GitHub Pages 自动发布。CNAME=recipe.easternmarket.ca。
（push 由 Chris 执行。）
