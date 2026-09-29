# 东方超市食谱搜索引擎

纯静态站（GitHub Pages）。顾客搜一道菜（或点食材看能做什么），看到食谱 + 每样食材在东方超市的分类/是否有货（不显示价格）。应用直接从站点根目录提供（`index.html` + `css/` `js/` `assets/`），网址即 `recipe.easternmarket.ca`，不再带 `/src/` 路径。

## 两套页面，各管一头

| | 单页应用（`index.html`） | 静态菜页（`r/*.html`） |
|---|---|---|
| 网址 | `#/r/<id>` 井号路由 | `r/<id>.html` 真实网址 |
| 谁在用 | 顾客逛、搜、收藏、凑购物清单 | 搜索引擎收录 + 微信分享落地 |
| 内容来源 | 前端 JS 读 `data/*.json` | `build_static_pages.py` 生成好写进文件 |
| 有没有 JS | 有 | **没有**，关掉 JS 照样能读完 |

Google 爬不到井号后面的东西，所以每道菜额外生成一个真网址；菜页上的按钮再把人送回应用里去收藏、凑清单。详情页「🔗 复制链接」复制的就是静态菜页地址（有自己的大图预览）。

## 页面路由（hash，可分享）
- `#/r/<id>` 单道菜详情（发会员群直达这道菜）
- `#/sec/<section>` 某板块全部
- `#/list` 到店购物清单（收藏的菜 → 食材按超市分区汇总，可勾选）
- 返回键走浏览器历史（微信里按返回不再直接退出网站）

## 配送入口
`js/app.js` 顶部 `DELIVERY = { enabled: true, url: 'https://easternmarket.ca/group-order' }`，
详情页和购物清单页有「🚚 网上下单」。主网那个页面需要登录，未登录会落到登录页，是主网既有行为。
要关掉就把 `enabled` 改 `false`（记得 bump `index.html` 里 `app.js?v=N`）。

## 数据流
```
StockWise API (Firestore products) --export_products.py--> data/products.json
手工精选 + bind_ingredients.py                          --> data/recipes.json
              ├── build_static_pages.py 读全库，生成静态菜页 + sitemap
              └── 同时抽出食谱用到的商品 → data/catalog.json
                    └── 前端 js/ 只读 recipes.json + catalog.json
```

`products.json` 是全库快照（约 2700 条，含图片地址），只给绑定脚本和静态页生成用。
顾客打开网站下载的是 `catalog.json`（只有食谱引用到的那一百多条，没有图片地址）。

匿名商品接口现在最多返回 200 条。**不要**再跑 `export_products.py` 去覆盖
`data/products.json`：脚本发现新结果不到现有条数的一半会直接拒绝，避免把快照缩成 200 条、食材绑定全部断开。

## 图片
- 原图 `assets/images/<id>.jpg`，WebP 由 `optimize_images.py` 生成到 `assets/images/webp/`
  （`<id>-400.webp` 卡片用、`<id>.webp` 大图用）
- 前端用 `<picture>`：优先 WebP，浏览器不认回退原 JPEG。**原 JPEG 别删** —— iOS 13
  及更早的 iPhone 不认 WebP，店里客群有这种机器
- 换图流程：把新 JPEG 覆盖 `assets/images/<id>.jpg` → 跑 `optimize_images.py` → 跑
  `build_static_pages.py`。文件名不变，`recipes.json` 不用动

### 占位图卡
公共图库（维基共享资源）对不少中式家常菜没有能用的照片，搜出来常是别的菜。
**宁可放品牌字卡，也不要放错的菜的照片。** `make_placeholder_tiles.py` 生成这种字卡，
清单在脚本顶部的 `TILES`。拍到实拍图后按上面的换图流程覆盖即可，脚本清单里删掉那一条。

当前没有菜在用占位卡。

### 2026-09 内容与配图约定

食谱图片可以使用高质量 AI 示意图，`image_credit` 必须记录来源；页脚说明图片含 AI 示意图。
新图使用独立文件名（如 `-ai-202609.jpg`），保留原照片，避免缓存与回退问题。
配图必须与实际食材、做法一致。粉葛不可误配沙葛，芥兰和菜心不可用生菜图替代。
新增食谱的主要食材先核对 StockWise 商品记录；核查证据见
`docs/content-ingredients-2026-09-29.json`。在售商品记录不等于实时物理库存保证。
内容批次脚本只有在主要食材通过核验后才允许生成；不要用硬编码名单绕过核验。

## 本地跑
```bash
npm install                      # 只装 playwright-core，不下载浏览器
npm run serve                    # http://localhost:8099
npm test                         # JS 单元测试（node --test）
python -m pytest scripts/ -v     # Python 单元测试
npm run verify                   # 真浏览器跑一遍关键路径（需先 npm run serve）
```

`npm run verify` 用系统自带的 Edge/Chrome，`EM_BROWSER` 可指定路径，
`EM_BASE=https://recipe.easternmarket.ca npm run verify` 可以直接打生产。
它覆盖单元测试抓不到的失败态：按钮在、点了没反应、也不报错。

## 改了食谱或图片之后
```bash
python scripts/optimize_images.py        # 有新图才需要
python scripts/build_static_pages.py     # 重新生成 r/*.html + sitemap，并重写 catalog.json
```
两个脚本都是幂等的，重复跑没有副作用。**加了新菜一定要跑 build_static_pages.py**，
否则那道菜没有可被搜索收录的网址。

## 换季
首页板块 `season` 现在是「🍂 应季」。月饼只在中秋档期上，过节后从 `data/recipes.json` 拿掉。
换季不用删代码：改菜，再改三处标题（`index.html` 的板块标题、`js/app.js` 的
`SEC_TITLE`、`scripts/static_pages.py` 的 `SEC_TITLE`）。板块内没有菜时会自动隐藏。

## 部署
push 到 GitHub（easternmarketsask-a11y/eastern-recipe）→ GitHub Pages 自动发布。CNAME=recipe.easternmarket.ca。
`r/`、`sitemap.xml`、`robots.txt` 都是生成产物但**要提交进仓库**（GitHub Pages 不跑构建）。
（push 由 Chris 执行。）
