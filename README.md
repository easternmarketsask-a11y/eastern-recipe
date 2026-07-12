# 东方超市食谱搜索引擎

纯静态站（GitHub Pages）。顾客搜一道菜（或点食材看能做什么），看到食谱 + 每样食材在东方超市的分类/是否有货（不显示价格）。应用直接从站点根目录提供（`index.html` + `css/` `js/` `assets/`），网址即 `recipe.easternmarket.ca`，不再带 `/src/` 路径。

## 页面路由（hash，可分享）
- `#/r/<id>` 单道菜详情（发会员群直达这道菜）
- `#/sec/<section>` 某板块全部
- `#/list` 到店购物清单（收藏的菜 → 食材按超市分区汇总，可勾选）
- 返回键走浏览器历史（微信里按返回不再直接退出网站）

## 配送入口开关
`js/app.js` 顶部 `DELIVERY = { enabled: false, url: ... }`。配送业务正式上线后改
`enabled: true`（记得 bump `index.html` 里 `app.js?v=N`），详情页和购物清单页会出现「🚚 网上下单」按钮。

## 数据流
StockWise API (Firestore products) --export_products.py--> data/products.json
手工精选 + bind_ingredients.py --> data/recipes.json
前端关联渲染（js/）。

## 本地跑
- 前端：任意静态服务器，如 `python -m http.server 8080`，开 http://localhost:8080
- 导出商品：`python scripts/export_products.py --api <STOCKWISE_URL> --out data/products.json`
- JS 测试：`node --test`（在仓库根目录跑）
- Python 测试：`python -m pytest scripts/ -v`

## 部署
push 到 GitHub（easternmarketsask-a11y/eastern-recipe）→ GitHub Pages 自动发布。CNAME=recipe.easternmarket.ca。
（push 由 Chris 执行。）
