# 菜谱搜索引擎 Phase 1：地基 + 搜菜引流（A）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 上线一个能用的"搜菜找货"静态站——顾客搜一道菜，看到菜谱 + 每样食材在东方超市的价格/分类/是否在售，并能生成到店购物清单。

**Architecture:** 纯静态 GitHub Pages 站（无 build、经典 `<script>`，对齐 eastern-farm）。一个 Python 导出器经 StockWise API 把 Firestore 商品写成 `data/products.json`；手工精选菜谱 + 半自动绑定脚本产出 `data/recipes.json`；前端把两者关联渲染。可独立测的纯逻辑（搜索匹配、食材关联、价格计算）抽成 `RecipeLogic` 模块，用 `node --test` 做 TDD；商品名拆分/分类归一/绑定打分等 Python 纯函数用 `pytest` TDD。

**Tech Stack:** Vanilla JS（经典 script，UMD-lite 双导出便于 Node 测试）、Node 内置 test runner、Python 3 + `requests` + `pytest`、StockWise FastAPI API、GitHub Pages。

**范围边界（本计划只做）：** 仓库地基 + `products.json` 导出器 + 绑定脚本 + 前端 A（搜菜→食材→价格→购物清单）+ 6 道真实种子菜谱 + 移动端视觉与版权/微信验收。**不做**（留给 Plan 2/3）：B「今天做什么菜」、`featured.json`、促销海报复用、每日自动导出定时、搜索词回收到 Firestore。

**参考资料（实施前必读）：**
- 设计 spec：`docs/superpowers/specs/2026-06-14-recipe-search-engine-design.md`
- 同构参考工程：`D:\easternmarket.ca\eastern-farm`（结构/脚本/CNAME 约定）
- 商品数据源/字段/9 大分类/API：`D:\easternmarket.ca\CLAUDE.md`（StockWise API、`/api/firebase/categories`、`products` 字段）
- 品牌色：主绿 `#3a8c50`、深绿 `#2a5c34`、强调橙红 `#E8522A`（仅 logo/徽章）、背景白 + `#f4f9f5`

**全局约定：**
- 所有 commit **本地进行，不 push**（push 由 Chris 亲手做——见 memory `feedback_no_cross_repo_commits`）。
- 仅在本仓库 `D:\easternmarket.ca\eastern-recipe` 内操作，不碰别的 repo。
- 金额一律加元 `$`，不用 `¥`。

---

## 文件结构

| 文件 | 职责 |
|------|------|
| `index.html` | 根重定向到 `src/index.html`（对齐 eastern-farm）|
| `src/index.html` | A 页面骨架：搜索框 + 结果容器 + 菜谱详情容器 |
| `src/css/app.css` | 移动优先样式，品牌色，菜谱卡 + 食材行 |
| `src/js/lib/recipe-logic.js` | **纯逻辑**（无 DOM）：`normalizeQuery` / `matchRecipes` / `associateRecipe` / `buildProductIndex` / `dishesForIngredient`（以货找菜倒排）/ `todaysPicks`（今晚吃什么每日轮换）。UMD-lite 双导出（browser global `RecipeLogic` + Node `require`）|
| `src/js/app.js` | 入口：fetch 两个 JSON → 建索引 → 渲染逛发现首页（今晚吃什么/食材 chips/统一搜索/想做清单）→ 菜谱详情。薄 DOM 层，逻辑全调 `RecipeLogic`；收藏用 localStorage |
| `data/products.json` | 导出器产物（机器生成）|
| `data/recipes.json` | 菜谱 + 绑定（人审）|
| `data/_fixtures/products.sample.json` | 测试夹具：小批商品 |
| `data/_fixtures/recipes.sample.json` | 测试夹具：含已绑定/未绑定/称重食材 |
| `scripts/export_products.py` | 经 StockWise API 拉商品 → 写 `data/products.json` |
| `scripts/recipe_lib.py` | **纯函数**：`split_name` / `detect_price_unit` / `normalize_category` / `build_product_record` / `score_match` |
| `scripts/bind_ingredients.py` | 半自动绑定 CLI：食材词 → 候选 `code` + 置信度 |
| `scripts/requirements.txt` | `requests`、`pytest` |
| `test/recipe-logic.test.js` | `RecipeLogic` 的 Node 测试 |
| `scripts/test_recipe_lib.py` | `recipe_lib.py` 的 pytest |
| `CNAME` | `recipe.easternmarket.ca` |
| `README.md` | 跑法、数据流、部署说明 |

---

## Task 0: 仓库地基与目录骨架

**Files:**
- Create: `index.html`, `CNAME`, `README.md`, `.gitignore`（已存在，校验）
- Create 空目录占位：`src/css/`, `src/js/lib/`, `data/_fixtures/`, `scripts/`, `test/`

- [ ] **Step 1: 建目录与根重定向页**

`index.html`（对齐 eastern-farm 根重定向）：
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta http-equiv="refresh" content="0; url=src/index.html">
<title>东方超市 · 菜谱搜索</title>
<link rel="canonical" href="src/index.html">
</head>
<body>
<p>跳转到 <a href="src/index.html">东方超市菜谱</a>…</p>
<script>location.replace('src/index.html');</script>
</body>
</html>
```

- [ ] **Step 2: 写 CNAME**

`CNAME` 内容（单行，无换行尾随空格）：
```
recipe.easternmarket.ca
```

- [ ] **Step 3: 写 README**

`README.md`：
```markdown
# 东方超市菜谱搜索引擎

纯静态站（GitHub Pages）。顾客搜一道菜，看到菜谱 + 食材在东方超市的价格/分类/是否在售。

## 数据流
StockWise API (Firestore products) --export_products.py--> data/products.json
手工精选 + bind_ingredients.py --> data/recipes.json
前端关联渲染（src/js）。

## 本地跑
- 前端：任意静态服务器，如 `python -m http.server 8080`，开 http://localhost:8080
- 导出商品：`python scripts/export_products.py --api <STOCKWISE_URL> --out data/products.json`
- JS 测试：`node --test`
- Python 测试：`python -m pytest scripts/ -v`

## 部署
push 到 GitHub（easternmarketsask-a11y/eastern-recipe）→ GitHub Pages 自动发布。CNAME=recipe.easternmarket.ca。
（push 由 Chris 执行。）
```

- [ ] **Step 4: 校验 .gitignore 含 _incoming 与 venv**

确认 `.gitignore` 至少包含（已在前序创建，缺则补）：
```
node_modules/
.venv/
_incoming/
*.local
__pycache__/
```

- [ ] **Step 5: Commit**

```bash
cd /d/easternmarket.ca/eastern-recipe
git add index.html CNAME README.md .gitignore
git -c user.name="Claude" -c user.email="noreply@anthropic.com" commit -m "chore: scaffold eastern-recipe static site"
```

---

## Task 1: 测试夹具（products + recipes 样例）

**Files:**
- Create: `data/_fixtures/products.sample.json`
- Create: `data/_fixtures/recipes.sample.json`

这些夹具是后续所有 TDD 的输入，必须覆盖：在售 `each`、在售 `lb`（称重）、不在售、未绑定。

- [ ] **Step 1: 写 products 夹具**

`data/_fixtures/products.sample.json`：
```json
{
  "generated_at": "2026-06-14T21:00:00-06:00",
  "items": [
    { "code": "4011tofu", "name_cn": "嫩豆腐", "name_en": "Soft Tofu", "price": 2.49, "price_unit": "each", "category": "豆腐蛋品", "image_url": "", "on_sale": true, "sold_90d": 88 },
    { "code": "ddbanjiang", "name_cn": "丹丹郫县豆瓣酱", "name_en": "Dan Dan Pixian Bean Paste", "price": 5.99, "price_unit": "each", "category": "干货调料", "image_url": "", "on_sale": true, "sold_90d": 31 },
    { "code": "10588", "name_cn": "芫荽", "name_en": "Cilantro", "price": 0.99, "price_unit": "lb", "category": "新鲜蔬菜", "image_url": "", "on_sale": true, "sold_90d": 142 },
    { "code": "greenonion", "name_cn": "小葱", "name_en": "Green Onion", "price": 1.49, "price_unit": "lb", "category": "新鲜蔬菜", "image_url": "", "on_sale": false, "sold_90d": 60 }
  ]
}
```

- [ ] **Step 2: 写 recipes 夹具**

`data/_fixtures/recipes.sample.json`（麻婆豆腐：豆腐+豆瓣已绑且在售；牛肉末未绑定 `code:null`；小葱已绑但不在售）：
```json
{
  "recipes": [
    {
      "id": "mapo-tofu",
      "name_cn": "麻婆豆腐",
      "name_en": "Mapo Tofu",
      "aliases": ["麻婆豆腐", "mapo", "麻辣豆腐", "mapodoufu"],
      "image": "images/mapo-tofu.jpg",
      "image_credit": "self",
      "tags": ["川菜", "下饭", "快手"],
      "steps": ["豆腐切块焯水", "下豆瓣酱炒香", "加豆腐烧入味", "撒葱花出锅"],
      "ingredients": [
        { "label": "嫩豆腐", "qty": "1 盒", "code": "4011tofu", "required": true },
        { "label": "郫县豆瓣酱", "qty": "2 勺", "code": "ddbanjiang", "required": true },
        { "label": "小葱", "qty": "2 根", "code": "greenonion", "required": false },
        { "label": "牛肉末", "qty": "200g", "code": null, "required": false }
      ]
    }
  ]
}
```

- [ ] **Step 3: Commit**

```bash
git add data/_fixtures/
git -c user.name="Claude" -c user.email="noreply@anthropic.com" commit -m "test: add product/recipe fixtures for TDD"
```

---

## Task 2: `RecipeLogic.matchRecipes`（搜索匹配，TDD）

**Files:**
- Create: `src/js/lib/recipe-logic.js`
- Test: `test/recipe-logic.test.js`

- [ ] **Step 1: 写失败测试**

`test/recipe-logic.test.js`：
```js
const test = require('node:test');
const assert = require('node:assert');
const RecipeLogic = require('../src/js/lib/recipe-logic.js');
const recipes = require('../data/_fixtures/recipes.sample.json').recipes;

test('matchRecipes: 中文全名命中', () => {
  const r = RecipeLogic.matchRecipes('麻婆豆腐', recipes);
  assert.equal(r.length, 1);
  assert.equal(r[0].id, 'mapo-tofu');
});

test('matchRecipes: 英文别名忽略大小写', () => {
  assert.equal(RecipeLogic.matchRecipes('MAPO', recipes)[0].id, 'mapo-tofu');
});

test('matchRecipes: 拼音别名命中', () => {
  assert.equal(RecipeLogic.matchRecipes('mapodoufu', recipes)[0].id, 'mapo-tofu');
});

test('matchRecipes: 中文部分词命中', () => {
  assert.equal(RecipeLogic.matchRecipes('豆腐', recipes)[0].id, 'mapo-tofu');
});

test('matchRecipes: 无关词返回空', () => {
  assert.deepEqual(RecipeLogic.matchRecipes('披萨', recipes), []);
});

test('matchRecipes: 空查询返回空', () => {
  assert.deepEqual(RecipeLogic.matchRecipes('   ', recipes), []);
});
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd /d/easternmarket.ca/eastern-recipe && node --test`
Expected: FAIL（`Cannot find module '../src/js/lib/recipe-logic.js'`）

- [ ] **Step 3: 写最小实现**

`src/js/lib/recipe-logic.js`：
```js
/**
 * recipe-logic.js — 纯逻辑（无 DOM），可在浏览器(全局 RecipeLogic)与 Node(require) 复用。
 */
(function (global, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else global.RecipeLogic = api;
})(typeof window !== 'undefined' ? window : this, function () {
  'use strict';

  // 归一：小写 + 去空白。中文不变，英文/拼音可大小写无关匹配。
  function normalizeQuery(s) {
    return String(s == null ? '' : s).toLowerCase().replace(/\s+/g, '');
  }

  // 在 name_cn / name_en / aliases 里做子串匹配
  function matchRecipes(query, recipes) {
    const q = normalizeQuery(query);
    if (!q) return [];
    return (recipes || []).filter(function (r) {
      const hay = [r.name_cn, r.name_en].concat(r.aliases || []).map(normalizeQuery);
      return hay.some(function (h) { return h.indexOf(q) !== -1; });
    });
  }

  return { normalizeQuery: normalizeQuery, matchRecipes: matchRecipes };
});
```

- [ ] **Step 4: 跑测试确认通过**

Run: `node --test`
Expected: PASS（6 个 matchRecipes 测试通过）

- [ ] **Step 5: Commit**

```bash
git add src/js/lib/recipe-logic.js test/recipe-logic.test.js
git -c user.name="Claude" -c user.email="noreply@anthropic.com" commit -m "feat: RecipeLogic.matchRecipes with cn/en/pinyin matching"
```

---

## Task 3: `RecipeLogic.buildProductIndex` + `associateRecipe`（食材关联与参考价，TDD）

**Files:**
- Modify: `src/js/lib/recipe-logic.js`
- Modify: `test/recipe-logic.test.js`

关键业务规则（来自 spec §5）：
- 每个食材按 `code` 查商品；`code:null` 或商品 `on_sale:false` → 标"暂缺"。
- `haveCount` = 全部食材里"在售"的数量；`totalCount` = 食材总数。
- 参考价 `refPriceEach` 只累加**在售且 `price_unit==='each'`** 的食材单价；称重(`lb`)在售食材进 `weighed` 数组单列（每磅价），**不进总价**。

- [ ] **Step 1: 追加失败测试**

在 `test/recipe-logic.test.js` 末尾追加：
```js
const products = require('../data/_fixtures/products.sample.json').items;

test('buildProductIndex: 以 code 建索引', () => {
  const idx = RecipeLogic.buildProductIndex(products);
  assert.equal(idx['4011tofu'].name_cn, '嫩豆腐');
});

test('associateRecipe: 行状态与计数正确', () => {
  const idx = RecipeLogic.buildProductIndex(products);
  const res = RecipeLogic.associateRecipe(recipes[0], idx);
  // 4 样食材：豆腐(each在售) 豆瓣(each在售) 小葱(lb不在售→暂缺) 牛肉末(null→暂缺)
  assert.equal(res.totalCount, 4);
  assert.equal(res.haveCount, 2);
  const byLabel = {};
  res.rows.forEach(function (r) { byLabel[r.label] = r; });
  assert.equal(byLabel['嫩豆腐'].available, true);
  assert.equal(byLabel['小葱'].available, false);   // 不在售
  assert.equal(byLabel['牛肉末'].available, false);  // 未绑定
  assert.equal(byLabel['牛肉末'].unbound, true);
});

test('associateRecipe: 参考价只含在售 each 项，称重项单列', () => {
  const idx = RecipeLogic.buildProductIndex(products);
  const res = RecipeLogic.associateRecipe(recipes[0], idx);
  // 在售 each：豆腐 2.49 + 豆瓣 5.99 = 8.48；小葱虽是 lb 但不在售，不计入 weighed
  assert.equal(res.refPriceEach, 8.48);
  assert.deepEqual(res.weighed, []); // 唯一的 lb 食材(小葱)不在售
});

test('associateRecipe: 在售称重食材进 weighed 不进总价', () => {
  const idx = RecipeLogic.buildProductIndex(products);
  // 构造：把小葱改成在售
  const idx2 = JSON.parse(JSON.stringify(idx));
  idx2['greenonion'].on_sale = true;
  const res = RecipeLogic.associateRecipe(recipes[0], idx2);
  assert.equal(res.refPriceEach, 8.48);          // 总价不变
  assert.equal(res.weighed.length, 1);
  assert.equal(res.weighed[0].label, '小葱');
  assert.equal(res.weighed[0].price, 1.49);
});
```

- [ ] **Step 2: 跑测试确认失败**

Run: `node --test`
Expected: FAIL（`buildProductIndex is not a function`）

- [ ] **Step 3: 实现 buildProductIndex + associateRecipe**

在 `recipe-logic.js` 的 `return` 之前插入：
```js
  function buildProductIndex(items) {
    const idx = {};
    (items || []).forEach(function (p) { idx[p.code] = p; });
    return idx;
  }

  function round2(n) { return Math.round(n * 100) / 100; }

  function associateRecipe(recipe, productIndex) {
    const rows = [];
    const weighed = [];
    let refPriceEach = 0;
    let haveCount = 0;
    (recipe.ingredients || []).forEach(function (ing) {
      const p = ing.code ? productIndex[ing.code] : null;
      const available = !!(p && p.on_sale);
      const row = {
        label: ing.label,
        qty: ing.qty,
        required: !!ing.required,
        unbound: !ing.code || !p,
        available: available,
        price: p ? p.price : null,
        price_unit: p ? p.price_unit : null,
        category: p ? p.category : null,
        image_url: p ? p.image_url : ''
      };
      rows.push(row);
      if (available) {
        haveCount += 1;
        if (p.price_unit === 'each') refPriceEach += p.price;
        else if (p.price_unit === 'lb') weighed.push({ label: ing.label, price: p.price });
      }
    });
    return {
      rows: rows,
      totalCount: (recipe.ingredients || []).length,
      haveCount: haveCount,
      refPriceEach: round2(refPriceEach),
      weighed: weighed
    };
  }
```
并把 `return { ... }` 改为：
```js
  return {
    normalizeQuery: normalizeQuery,
    matchRecipes: matchRecipes,
    buildProductIndex: buildProductIndex,
    associateRecipe: associateRecipe
  };
```

- [ ] **Step 4: 跑测试确认通过**

Run: `node --test`
Expected: PASS（全部 10 个测试通过）

- [ ] **Step 5: Commit**

```bash
git add src/js/lib/recipe-logic.js test/recipe-logic.test.js
git -c user.name="Claude" -c user.email="noreply@anthropic.com" commit -m "feat: associateRecipe with reference-price (weighed items excluded)"
```

---

## Task 3B: `RecipeLogic.dishesForIngredient` + `todaysPicks`（以货找菜 + 今晚吃什么，TDD）

**Files:**
- Modify: `src/js/lib/recipe-logic.js`
- Modify: `test/recipe-logic.test.js`

业务规则（spec §5 A2 + 首页）：
- `dishesForIngredient(query, recipes, productIndex)`：找出所有"用到该食材"的菜——匹配口径 = 食材 `label` 含 query，或该食材绑定商品的 `name_cn`/`name_en` 含 query。结果按"齐全度（在售食材数）降序，食材总数升序"排，让顾客先看到买齐成本低、好做的菜。
- `todaysPicks(recipes, seed, n)`：按 `seed`（日期串，或日期+「换一批」计数）确定性轮换返回 n 道菜——同 seed 结果稳定，不同 seed 轮换出不同子集。

- [ ] **Step 1: 追加失败测试**

在 `test/recipe-logic.test.js` 末尾追加：
```js
test('dishesForIngredient: 按食材 label 命中菜', () => {
  const idx = RecipeLogic.buildProductIndex(products);
  const r = RecipeLogic.dishesForIngredient('豆腐', recipes, idx);
  assert.equal(r.length, 1);
  assert.equal(r[0].id, 'mapo-tofu');
});

test('dishesForIngredient: 按绑定商品英文名命中', () => {
  const idx = RecipeLogic.buildProductIndex(products);
  // 豆瓣酱绑定商品 name_en = "Dan Dan Pixian Bean Paste"
  const r = RecipeLogic.dishesForIngredient('bean paste', recipes, idx);
  assert.equal(r[0].id, 'mapo-tofu');
});

test('dishesForIngredient: 无关食材返回空', () => {
  const idx = RecipeLogic.buildProductIndex(products);
  assert.deepEqual(RecipeLogic.dishesForIngredient('三文鱼', recipes, idx), []);
});

test('todaysPicks: 同 seed 确定、数量受限', () => {
  const a = RecipeLogic.todaysPicks(recipes, '2026-06-14', 1);
  const b = RecipeLogic.todaysPicks(recipes, '2026-06-14', 1);
  assert.deepEqual(a.map(x => x.id), b.map(x => x.id));
  assert.equal(a.length, 1);
});

test('todaysPicks: n 超过总数时返回全部、不重复', () => {
  const a = RecipeLogic.todaysPicks(recipes, 'seed-x', 99);
  assert.equal(a.length, recipes.length);
  assert.equal(new Set(a.map(x => x.id)).size, recipes.length);
});

test('todaysPicks: 不同 seed 轮换（多菜时子集不同）', () => {
  const many = ['a','b','c','d','e'].map(id => ({ id: id, name_cn: id, ingredients: [] }));
  const s1 = RecipeLogic.todaysPicks(many, 'day-1', 2).map(x => x.id).join(',');
  const s2 = RecipeLogic.todaysPicks(many, 'day-2', 2).map(x => x.id).join(',');
  assert.notEqual(s1, s2);
});
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd /d/easternmarket.ca/eastern-recipe && node --test`
Expected: FAIL（`dishesForIngredient is not a function`）

- [ ] **Step 3: 实现**

在 `recipe-logic.js` 的 `return { ... }` 之前插入：
```js
  // 以货找菜：哪些菜用到了这个食材（按食材 label 或其绑定商品名）
  function dishesForIngredient(query, recipes, productIndex) {
    const q = normalizeQuery(query);
    if (!q) return [];
    const hit = (recipes || []).filter(function (r) {
      return (r.ingredients || []).some(function (ing) {
        if (normalizeQuery(ing.label).indexOf(q) !== -1) return true;
        const p = ing.code ? productIndex[ing.code] : null;
        if (!p) return false;
        return normalizeQuery(p.name_cn).indexOf(q) !== -1 ||
               normalizeQuery(p.name_en).indexOf(q) !== -1;
      });
    });
    // 齐全度降序、食材总数升序
    return hit.slice().sort(function (a, b) {
      const av = associateRecipe(a, productIndex);
      const bv = associateRecipe(b, productIndex);
      if (bv.haveCount !== av.haveCount) return bv.haveCount - av.haveCount;
      return av.totalCount - bv.totalCount;
    });
  }

  // 字符串 → 32bit 无符号 hash（确定性，不依赖随机数）
  function hashStr(s) {
    let h = 2166136261;
    for (let i = 0; i < s.length; i++) {
      h ^= s.charCodeAt(i);
      h = (h * 16777619) >>> 0;
    }
    return h >>> 0;
  }

  // 今晚吃什么：按 seed 确定性轮换取 n 道
  function todaysPicks(recipes, seed, n) {
    const list = (recipes || []).slice();
    if (!list.length) return [];
    const offset = hashStr(String(seed)) % list.length;
    const out = [];
    const take = Math.min(n, list.length);
    for (let i = 0; i < take; i++) out.push(list[(offset + i) % list.length]);
    return out;
  }
```
并把 `return { ... }` 扩展为包含新函数：
```js
  return {
    normalizeQuery: normalizeQuery,
    matchRecipes: matchRecipes,
    buildProductIndex: buildProductIndex,
    associateRecipe: associateRecipe,
    dishesForIngredient: dishesForIngredient,
    todaysPicks: todaysPicks
  };
```

- [ ] **Step 4: 跑测试确认通过**

Run: `node --test`
Expected: PASS（全部 16 个测试通过）

- [ ] **Step 5: Commit**

```bash
git add src/js/lib/recipe-logic.js test/recipe-logic.test.js
git -c user.name="Claude" -c user.email="noreply@anthropic.com" commit -m "feat: dishesForIngredient (reverse lookup) + todaysPicks rotation"
```

---

## Task 4: 前端「逛着发现」首页 + 菜谱详情（骨架 + 渲染接线）

**Files:**
- Create: `src/index.html`
- Create: `src/js/app.js`

首页落地即"逛着发现"：今晚吃什么轮换 + 食材快捷 chips + 统一搜索（菜名/食材双向）+ 想做清单。渲染层薄，计算全调 `RecipeLogic`；收藏用 localStorage。无法纯 TDD（DOM），用"启动无报错 + 视觉验收"把关（Task 10）。

- [ ] **Step 1: 写页面骨架**

`src/index.html`：
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>东方超市 · 今晚吃什么</title>
<meta name="description" content="今晚吃什么？东方超市帮你想——看看店里的菜能做成什么、怎么做、买齐多少钱。">
<link rel="stylesheet" href="css/app.css?v=1">
</head>
<body>
<header class="hdr">
  <h1 class="hdr__title">东方超市 · 今晚吃什么</h1>
  <p class="hdr__sub">搜菜名找食材，或点食材看能做什么</p>
  <div class="search">
    <input id="q" class="search__input" type="search" inputmode="search"
           placeholder="试试：麻婆豆腐 · mapo · 豆腐 · 鸡翅" autocomplete="off">
  </div>
</header>
<main>
  <section id="home" class="home">
    <div class="block">
      <div class="block__hd">
        <h2 class="block__title">今晚吃什么</h2>
        <button id="reshuffle" class="link-btn">换一批</button>
      </div>
      <div id="picks" class="cards"></div>
    </div>
    <div class="block">
      <h2 class="block__title">家里有这些？看看能做什么</h2>
      <div id="chips" class="chips"></div>
    </div>
    <div class="block" id="favesBlock" hidden>
      <h2 class="block__title">♥ 我想做的</h2>
      <div id="faves" class="cards"></div>
    </div>
  </section>
  <section id="results" class="results" hidden aria-live="polite"></section>
  <section id="detail" class="detail" hidden></section>
</main>
<footer class="ftr">价格仅供参考，以店内标价为准 · Eastern Market 东方超市</footer>

<script src="js/lib/recipe-logic.js"></script>
<script src="js/app.js"></script>
</body>
</html>
```

- [ ] **Step 2: 写入口与渲染**

`src/js/app.js`：
```js
/* app.js — 逛发现首页(今晚吃什么/食材chips/想做清单) + 统一搜索(菜名/以货找菜) + 菜谱详情。
   渲染薄层，计算全调 RecipeLogic；收藏存 localStorage。 */
(function () {
  'use strict';
  var RL = window.RecipeLogic;
  var FAVE_KEY = 'er_recipe_faves_v1';
  var state = { recipes: [], productIndex: {}, byId: {}, reshuffle: 0 };

  function $(id) { return document.getElementById(id); }
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }
  function todayStr() { return new Date().toISOString().slice(0, 10); }

  // ---- 收藏（localStorage）----
  function getFaves() {
    try { return JSON.parse(localStorage.getItem(FAVE_KEY)) || []; } catch (e) { return []; }
  }
  function isFave(id) { return getFaves().indexOf(id) !== -1; }
  function toggleFave(id) {
    var f = getFaves(), i = f.indexOf(id);
    if (i === -1) f.push(id); else f.splice(i, 1);
    try { localStorage.setItem(FAVE_KEY, JSON.stringify(f)); } catch (e) {}
  }

  // ---- 菜卡 ----
  function recipeCard(r) {
    return '<button class="card" data-id="' + esc(r.id) + '">' +
      '<span class="card__name">' + esc(r.name_cn) + '</span>' +
      '<span class="card__tags">' + esc((r.tags || []).join(' · ')) + '</span></button>';
  }
  function wireCards(container) {
    Array.prototype.forEach.call(container.querySelectorAll('.card'), function (btn) {
      btn.onclick = function () { var r = state.byId[btn.dataset.id]; if (r) renderDetail(r); };
    });
  }

  // ---- 食材行 ----
  function ingredientRow(r) {
    if (!r.available) {
      return '<li class="ing ing--out"><span class="ing__name">' + esc(r.label) +
        '</span><span class="ing__qty">' + esc(r.qty) + '</span>' +
        '<span class="ing__tag">暂缺</span></li>';
    }
    var price = r.price_unit === 'lb'
      ? '$' + r.price.toFixed(2) + '/lb · 按需称重'
      : '$' + r.price.toFixed(2);
    return '<li class="ing"><span class="ing__name">' + esc(r.label) +
      '</span><span class="ing__qty">' + esc(r.qty) + '</span>' +
      '<span class="ing__price">' + esc(price) + '</span>' +
      '<span class="ing__cat">' + esc(r.category || '') + '</span></li>';
  }

  function show(section) {
    $('home').hidden = section !== 'home';
    $('results').hidden = section !== 'results';
    $('detail').hidden = section !== 'detail';
  }

  function renderDetail(recipe) {
    var a = RL.associateRecipe(recipe, state.productIndex);
    var d = $('detail');
    var weighedNote = a.weighed.length
      ? '<p class="detail__weighed">另含按重量计价：' +
        a.weighed.map(function (w) { return esc(w.label) + ' $' + w.price.toFixed(2) + '/lb'; }).join('、') +
        '</p>'
      : '';
    var faved = isFave(recipe.id);
    d.innerHTML =
      '<button class="back" id="back">← 返回</button>' +
      '<h2 class="detail__title">' + esc(recipe.name_cn) +
        ' <small>' + esc(recipe.name_en || '') + '</small></h2>' +
      '<ul class="ings">' + a.rows.map(ingredientRow).join('') + '</ul>' +
      '<div class="summary">这道菜共 ' + a.totalCount + ' 样食材，我们有 ' +
        a.haveCount + ' 样　·　定量食材约 $' + a.refPriceEach.toFixed(2) + ' 起</div>' +
      weighedNote +
      '<button class="fave-btn' + (faved ? ' is-on' : '') + '" id="fave">' +
        (faved ? '♥ 已加入想做' : '♡ 加入想做') + '</button>' +
      '<h3 class="detail__h3">做法</h3>' +
      '<ol class="steps">' + (recipe.steps || []).map(function (s) {
        return '<li>' + esc(s) + '</li>';
      }).join('') + '</ol>';
    $('back').onclick = function () { renderHome(); show('home'); };
    $('fave').onclick = function () { toggleFave(recipe.id); renderDetail(recipe); };
    show('detail');
    window.scrollTo(0, 0);
  }

  // ---- 统一搜索：菜名 + 以货找菜 ----
  function renderResults(query) {
    var dishes = RL.matchRecipes(query, state.recipes);
    var dishIds = {}; dishes.forEach(function (r) { dishIds[r.id] = 1; });
    var byIng = RL.dishesForIngredient(query, state.recipes, state.productIndex)
      .filter(function (r) { return !dishIds[r.id]; });
    var el = $('results');
    if (!dishes.length && !byIng.length) {
      el.innerHTML = '<p class="empty">没找到～换个菜名或食材试试。</p>';
      show('results'); return;
    }
    var html = '';
    if (dishes.length) {
      html += '<h2 class="block__title">菜谱</h2><div class="cards">' +
        dishes.map(recipeCard).join('') + '</div>';
    }
    if (byIng.length) {
      html += '<h2 class="block__title">用「' + esc(query.trim()) + '」还能做</h2><div class="cards">' +
        byIng.map(recipeCard).join('') + '</div>';
    }
    el.innerHTML = html;
    wireCards(el);
    show('results');
  }

  function onSearch() {
    var q = $('q').value;
    if (!q || !q.trim()) { renderHome(); show('home'); return; }
    renderResults(q);
  }

  // ---- 首页 ----
  // 在售食材按其绑定商品 sold_90d 取热门，做快捷 chips
  function popularIngredientChips(max) {
    var seen = {}, arr = [];
    state.recipes.forEach(function (r) {
      (r.ingredients || []).forEach(function (ing) {
        var p = ing.code ? state.productIndex[ing.code] : null;
        if (!p || !p.on_sale) return;
        var sold = p.sold_90d || 0;
        if (seen[ing.label]) { if (sold > seen[ing.label].sold) seen[ing.label].sold = sold; return; }
        seen[ing.label] = { label: ing.label, sold: sold };
        arr.push(seen[ing.label]);
      });
    });
    arr.sort(function (a, b) { return b.sold - a.sold; });
    return arr.slice(0, max).map(function (x) { return x.label; });
  }

  function renderHome() {
    var seed = todayStr() + (state.reshuffle ? '#' + state.reshuffle : '');
    var picks = RL.todaysPicks(state.recipes, seed, 4);
    $('picks').innerHTML = picks.map(recipeCard).join('');
    wireCards($('picks'));

    var chips = popularIngredientChips(8);
    $('chips').innerHTML = chips.map(function (c) {
      return '<button class="chip" data-ing="' + esc(c) + '">' + esc(c) + '</button>';
    }).join('');
    Array.prototype.forEach.call($('chips').querySelectorAll('.chip'), function (btn) {
      btn.onclick = function () { $('q').value = btn.dataset.ing; renderResults(btn.dataset.ing); };
    });

    var faves = getFaves().map(function (id) { return state.byId[id]; }).filter(Boolean);
    if (faves.length) {
      $('favesBlock').hidden = false;
      $('faves').innerHTML = faves.map(recipeCard).join('');
      wireCards($('faves'));
    } else {
      $('favesBlock').hidden = true;
    }
  }

  function boot() {
    Promise.all([
      fetch('../data/recipes.json').then(function (r) { return r.json(); }),
      fetch('../data/products.json').then(function (r) { return r.json(); })
    ]).then(function (out) {
      state.recipes = out[0].recipes || [];
      state.productIndex = RL.buildProductIndex((out[1].items) || []);
      state.recipes.forEach(function (r) { state.byId[r.id] = r; });
      $('q').addEventListener('input', onSearch);
      $('reshuffle').onclick = function () { state.reshuffle += 1; renderHome(); };
      renderHome();
      show('home');
    }).catch(function () {
      $('home').innerHTML = '<p class="empty">数据加载失败，请稍后再试。</p>';
    });
  }
  document.addEventListener('DOMContentLoaded', boot);
})();
```

- [ ] **Step 3: 用样例数据本地起站冒烟**

把夹具临时拷成正式数据以便本地预览：
```bash
cp data/_fixtures/products.sample.json data/products.json
cp data/_fixtures/recipes.sample.json data/recipes.json
python -m http.server 8080
```
浏览器开 `http://localhost:8080` 验证：
- 首页直接显示「今晚吃什么」卡片 + 食材 chips（豆腐/豆瓣酱等在售食材）；「换一批」可点。
- 搜索框输"麻婆豆腐"→「菜谱」区出现卡片；点开→ 4 行食材（豆腐/豆瓣有价、小葱/牛肉末"暂缺"）、汇总"4 样食材我们有 2 样 · 约 $8.48 起"、可点「♡ 加入想做」。
- 搜索框输"豆腐"→「用「豆腐」还能做」区出现麻婆豆腐（以货找菜）。
- 加入想做后返回首页→「♥ 我想做的」区出现该菜；刷新页面仍在（localStorage）。
Expected: 控制台 F12 无红色报错。

- [ ] **Step 4: Commit**

```bash
git add src/index.html src/js/app.js data/products.json data/recipes.json
git -c user.name="Claude" -c user.email="noreply@anthropic.com" commit -m "feat: browse-first home (today's picks/chips/faves) + unified search + detail"
```

---

## Task 5: 移动优先样式（品牌色，高标准视觉）

**Files:**
- Create: `src/css/app.css`

- [ ] **Step 1: 写样式**

`src/css/app.css`（品牌色变量 + 卡片/食材行/汇总；极细阴影、轻压力风格，对齐 EM 品牌规范）：
```css
:root{
  --green:#3a8c50; --green-d:#2a5c34; --accent:#E8522A;
  --bg:#f4f9f5; --card:#fff; --ink:#1f2a22; --muted:#6b7a6f; --line:#e6efe8;
  --radius:14px; --shadow:0 1px 3px rgba(30,42,34,.08);
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;line-height:1.5}
.hdr{padding:20px 16px 12px;background:var(--card);border-bottom:1px solid var(--line)}
.hdr__title{margin:0;font-size:20px;font-weight:600;color:var(--green-d)}
.hdr__sub{margin:4px 0 12px;color:var(--muted);font-size:14px}
.search__input{width:100%;height:46px;border:1px solid var(--line);border-radius:23px;
  padding:0 18px;font-size:16px;outline:none;background:#fbfdfb}
.search__input:focus{border-color:var(--green)}
main{max-width:560px;margin:0 auto;padding:12px 16px 40px}
.card{display:flex;flex-direction:column;align-items:flex-start;gap:4px;width:100%;
  text-align:left;background:var(--card);border:1px solid var(--line);border-radius:var(--radius);
  box-shadow:var(--shadow);padding:14px 16px;margin-bottom:10px;cursor:pointer}
.card__name{font-size:17px;font-weight:600}
.card__tags{font-size:12px;color:var(--muted)}
.empty{color:var(--muted);text-align:center;padding:32px 0}
/* 逛发现首页 */
.block{margin:18px 0}
.block__hd{display:flex;align-items:baseline;justify-content:space-between}
.block__title{font-size:16px;font-weight:600;color:var(--green-d);margin:0 0 10px}
.link-btn{background:none;border:none;color:var(--green);font-size:13px;cursor:pointer;padding:0}
.cards{display:grid;grid-template-columns:1fr 1fr;gap:10px}
@media (max-width:380px){.cards{grid-template-columns:1fr}}
.cards .card{margin-bottom:0}
.chips{display:flex;flex-wrap:wrap;gap:8px}
.chip{background:var(--card);border:1px solid var(--line);border-radius:18px;
  padding:8px 14px;font-size:14px;color:var(--ink);cursor:pointer;min-height:36px}
.chip:active{background:#eef6f0;border-color:var(--green)}
.fave-btn{display:block;width:100%;margin:14px 0 4px;height:44px;border-radius:var(--radius);
  border:1px solid var(--green);background:var(--card);color:var(--green-d);font-size:15px;cursor:pointer}
.fave-btn.is-on{background:#eef6f0}
.back{background:none;border:none;color:var(--green);font-size:15px;padding:8px 0;cursor:pointer}
.detail__title{margin:4px 0 12px;font-size:22px;color:var(--green-d)}
.detail__title small{font-size:14px;color:var(--muted);font-weight:400}
.ings{list-style:none;margin:0 0 12px;padding:0;background:var(--card);
  border:1px solid var(--line);border-radius:var(--radius);overflow:hidden}
.ing{display:flex;align-items:center;gap:8px;padding:11px 14px;border-bottom:1px solid var(--line)}
.ing:last-child{border-bottom:none}
.ing__name{flex:1;font-weight:500}
.ing__qty{color:var(--muted);font-size:13px}
.ing__price{color:var(--green-d);font-weight:600}
.ing__cat{font-size:11px;color:var(--muted);background:var(--bg);border-radius:8px;padding:2px 8px}
.ing--out{opacity:.6}
.ing__tag{font-size:11px;color:#a23;background:#fdecec;border-radius:8px;padding:2px 8px}
.summary{background:#eef6f0;border:1px solid var(--line);border-radius:var(--radius);
  padding:12px 14px;font-size:14px;color:var(--green-d);font-weight:500}
.detail__weighed{font-size:12px;color:var(--muted);margin:8px 2px}
.steps{padding-left:20px}.steps li{margin-bottom:6px}
.ftr{text-align:center;color:var(--muted);font-size:12px;padding:20px}
```

- [ ] **Step 2: 视觉冒烟（移动视口）**

`python -m http.server 8080`，Chrome DevTools 切 iPhone 视口：
- 首页「今晚吃什么」卡片 2 列网格、食材 chips 自动换行、触摸目标 ≥36–44px。
- 搜"麻婆豆腐"看详情：标题深绿、食材行对齐、"暂缺"红字淡底、汇总绿底卡片、「♡ 加入想做」按钮满宽。
Expected: 移动端无横向滚动、触摸目标足够大、控制台无报错。

- [ ] **Step 3: Commit**

```bash
git add src/css/app.css
git -c user.name="Claude" -c user.email="noreply@anthropic.com" commit -m "style: mobile-first brand styling for search page"
```

---

## Task 6: 导出器纯函数（`recipe_lib.py`，TDD）

**Files:**
- Create: `scripts/recipe_lib.py`
- Create: `scripts/test_recipe_lib.py`
- Create: `scripts/requirements.txt`

- [ ] **Step 1: 写 requirements 并装依赖**

`scripts/requirements.txt`：
```
requests>=2.31
pytest>=8.0
```
Run: `cd /d/easternmarket.ca/eastern-recipe && python -m pip install -r scripts/requirements.txt`

- [ ] **Step 2: 写失败测试**

`scripts/test_recipe_lib.py`：
```python
import recipe_lib as rl

def test_split_name_mixed():
    cn, en = rl.split_name("LH Mushroom Seasoning 香菇调味料 500g")
    assert cn == "香菇调味料 500g"
    assert en == "LH Mushroom Seasoning"

def test_split_name_cn_only():
    cn, en = rl.split_name("嫩豆腐")
    assert cn == "嫩豆腐"
    assert en == ""

def test_detect_price_unit_weight():
    assert rl.detect_price_unit("Tong Ho Crown Daisy 茼蒿", "lb") == "lb"
    assert rl.detect_price_unit("Cilantro 芫荽", "") == "each"

def test_normalize_category_known():
    valid = {"新鲜蔬菜", "干货调料"}
    assert rl.normalize_category("新鲜蔬菜", valid) == "新鲜蔬菜"

def test_normalize_category_unknown_falls_back():
    valid = {"新鲜蔬菜"}
    assert rl.normalize_category("未知类", valid) == "未知类"  # 保留原值，导出器另行告警

def test_build_product_record():
    doc = {"code": "10588", "name": "Cilantro 芫荽", "price": 0.99,
           "category": "新鲜蔬菜", "imageUrl": "http://x/c.jpg",
           "clover_unit": "lb", "available": True, "deleted": False}
    rec = rl.build_product_record(doc, valid_categories={"新鲜蔬菜"}, sold_90d=142)
    assert rec == {
        "code": "10588", "name_cn": "芫荽", "name_en": "Cilantro",
        "price": 0.99, "price_unit": "lb", "category": "新鲜蔬菜",
        "image_url": "http://x/c.jpg", "on_sale": True, "sold_90d": 142,
    }
```

- [ ] **Step 3: 跑测试确认失败**

Run: `cd /d/easternmarket.ca/eastern-recipe/scripts && python -m pytest test_recipe_lib.py -v`
Expected: FAIL（`ModuleNotFoundError: No module named 'recipe_lib'`）

- [ ] **Step 4: 写实现**

`scripts/recipe_lib.py`：
```python
"""recipe_lib.py — 导出器/绑定器共用的纯函数。无网络、无副作用，便于 TDD。"""
import re

_WEIGHT_RE = re.compile(r'\b(lb|lbs|kg|/lb|per\s*lb)\b', re.I)

def split_name(name):
    """把 Clover 混排名拆成 (中文, 英文)。英文=第一个 CJK token 之前的拉丁前缀，
    中文=从第一个含 CJK 的 token 起到末尾（含规格如 500g）。"""
    s = (name or "").strip()
    tokens = s.split()
    first_cn = next((i for i, t in enumerate(tokens) if re.search(r'[一-鿿]', t)), None)
    if first_cn is None:
        return ("", s)
    en_parts = tokens[:first_cn]
    cn_parts = tokens[first_cn:]
    return (" ".join(cn_parts).strip(), " ".join(en_parts).strip())

def detect_price_unit(name, clover_unit):
    """称重→'lb'，否则'each'。优先看 Clover 单位，其次商品名里的重量标记。"""
    if (clover_unit or "").strip().lower() in ("lb", "kg"):
        return "lb"
    if _WEIGHT_RE.search(name or ""):
        return "lb"
    return "each"

def normalize_category(raw, valid):
    """命中 9 类规范则原样返回；否则保留原值（导出器会另行告警，不静默丢弃）。"""
    raw = (raw or "").strip()
    return raw if raw in valid else raw

def build_product_record(doc, valid_categories, sold_90d=0):
    """Firestore product doc → 公开站 products.json 的一条记录。"""
    cn, en = split_name(doc.get("name"))
    on_sale = bool(doc.get("available", True)) and not bool(doc.get("deleted", False))
    return {
        "code": doc.get("code", ""),
        "name_cn": cn,
        "name_en": en,
        "price": doc.get("price"),
        "price_unit": detect_price_unit(doc.get("name"), doc.get("clover_unit")),
        "category": normalize_category(doc.get("category"), valid_categories),
        "image_url": doc.get("imageUrl", "") or "",
        "on_sale": on_sale,
        "sold_90d": sold_90d,
    }
```

- [ ] **Step 5: 跑测试确认通过**

Run: `python -m pytest test_recipe_lib.py -v`
Expected: PASS（6 个测试通过）

- [ ] **Step 6: Commit**

```bash
cd /d/easternmarket.ca/eastern-recipe
git add scripts/recipe_lib.py scripts/test_recipe_lib.py scripts/requirements.txt
git -c user.name="Claude" -c user.email="noreply@anthropic.com" commit -m "feat: export pure functions (split_name/price_unit/category/record)"
```

---

## Task 7: 导出器 CLI（`export_products.py`，HTTP 接线）

**Files:**
- Create: `scripts/export_products.py`

调 StockWise API 取商品 + 分类 + 近 90 天动销，组装 `products.json`。HTTP 部分用真实 API 手测；逻辑已在 Task 6 测过。

> ⚠️ 实施者**先读** `D:\easternmarket.ca\CLAUDE.md` 确认实际端点与字段名（`GET /api/firebase/categories` 返回 `name`；商品读取端点见 `firebase_api_endpoints.py`；动销 join 用 `clover_item_id`，`sales.product_doc_id` 多为空）。下方端点路径若与实际不符，以 CLAUDE.md / 后端代码为准。

- [ ] **Step 1: 写导出器**

`scripts/export_products.py`：
```python
"""export_products.py — 经 StockWise API 拉商品 → data/products.json。
用法: python scripts/export_products.py --api https://<stockwise-url> --out data/products.json
"""
import argparse, json, sys
from datetime import datetime, timezone, timedelta
import requests
import recipe_lib as rl

def fetch_json(url, params=None):
    r = requests.get(url, params=params, timeout=60)
    r.raise_for_status()
    return r.json()

def load_valid_categories(api):
    data = fetch_json(api.rstrip("/") + "/api/firebase/categories")
    items = data.get("full") or data.get("categories") or data
    return {c["name"] for c in items if c.get("name")}

def load_products(api):
    # ⚠️ 端点以后端实际为准；CLAUDE.md 指向 firebase_api_endpoints.py
    data = fetch_json(api.rstrip("/") + "/api/firebase/products")
    return data.get("products") or data.get("items") or data

def load_sold_90d(api):
    """返回 {clover_item_id: 件数}。端点/字段以后端为准；取不到则返回 {}。"""
    try:
        data = fetch_json(api.rstrip("/") + "/api/analytics/sold-90d")
        return {k: int(v) for k, v in (data.get("counts") or {}).items()}
    except Exception:
        return {}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--api", required=True)
    ap.add_argument("--out", default="data/products.json")
    args = ap.parse_args()

    valid = load_valid_categories(args.api)
    products = load_products(args.api)
    sold = load_sold_90d(args.api)

    items, dropped = [], []
    for doc in products:
        if doc.get("deleted"):
            continue
        rec = rl.build_product_record(
            doc, valid_categories=valid,
            sold_90d=sold.get(doc.get("clover_item_id"), 0),
        )
        if not rec["code"]:
            dropped.append(doc.get("name"))
            continue
        if rec["category"] not in valid:
            print("WARN 非标准分类: %r (%s)" % (rec["category"], rec["name_cn"]), file=sys.stderr)
        items.append(rec)

    now = datetime.now(timezone(timedelta(hours=-6))).isoformat(timespec="seconds")
    out = {"generated_at": now, "items": items}
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("导出 %d 条商品 → %s（跳过无 code %d 条）" % (len(items), args.out, len(dropped)))

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 对真实 API 手测**

Run（用真实 StockWise URL，见 CLAUDE.md）：
```bash
cd /d/easternmarket.ca/eastern-recipe/scripts
python export_products.py --api https://stockwise-app-873982544406.us-central1.run.app --out ../data/products.json
```
Expected: 打印"导出 N 条商品"，`data/products.json` 有真实商品；抽查几条 `price_unit`/`category`/双语名正确。若端点 404，按后端实际端点修正 `load_products`/`load_sold_90d` 后重试。

- [ ] **Step 3: Commit（脚本，不提交真实 products.json）**

> `data/products.json` 是机器生成、随时可重建，**不进 git**（避免把商品数据/价格历史塞进版本库）。在 `.gitignore` 增加 `data/products.json`。
```bash
cd /d/easternmarket.ca/eastern-recipe
printf "data/products.json\n" >> .gitignore
git add scripts/export_products.py .gitignore
git -c user.name="Claude" -c user.email="noreply@anthropic.com" commit -m "feat: export_products CLI hitting StockWise API"
```

---

## Task 8: 绑定脚本（`bind_ingredients.py`，打分 TDD + CLI）

**Files:**
- Modify: `scripts/recipe_lib.py`（加 `score_match`）
- Modify: `scripts/test_recipe_lib.py`（加打分测试）
- Create: `scripts/bind_ingredients.py`

- [ ] **Step 1: 追加打分失败测试**

在 `scripts/test_recipe_lib.py` 末尾追加：
```python
def test_score_match_exact_substring_wins():
    prods = [
        {"code": "a", "name_cn": "嫩豆腐", "name_en": "Soft Tofu"},
        {"code": "b", "name_cn": "豆腐干", "name_en": "Dried Tofu"},
        {"code": "c", "name_cn": "白萝卜", "name_en": "Daikon"},
    ]
    ranked = rl.score_match("豆腐", prods)
    assert ranked[0][0]["code"] in ("a", "b")   # 含"豆腐"的排前
    assert ranked[-1][0]["code"] == "c"          # 不相关排末
    assert ranked[0][1] >= ranked[-1][1]         # 分数降序

def test_score_match_english_token():
    prods = [{"code": "a", "name_cn": "丹丹豆瓣酱", "name_en": "Dan Dan Bean Paste"}]
    ranked = rl.score_match("bean paste", prods)
    assert ranked[0][1] > 0
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd /d/easternmarket.ca/eastern-recipe/scripts && python -m pytest test_recipe_lib.py -v`
Expected: FAIL（`score_match` 不存在）

- [ ] **Step 3: 实现 score_match**

在 `scripts/recipe_lib.py` 末尾追加：
```python
def score_match(ingredient, products):
    """给食材在商品列表里的候选打分，返回 [(product, score), ...] 按分降序。
    打分：中文子串命中 +2；英文 token 命中 +1/词；归一后完全相等 +1。"""
    ing = (ingredient or "").strip().lower()
    ing_cn = ing
    ing_tokens = [t for t in re.split(r'\s+', ing) if t]
    ranked = []
    for p in products:
        cn = (p.get("name_cn") or "").lower()
        en = (p.get("name_en") or "").lower()
        score = 0.0
        if ing_cn and ing_cn in cn:
            score += 2.0
        for tok in ing_tokens:
            if tok and (tok in en or tok in cn):
                score += 1.0
        if ing_cn and (ing_cn == cn or ing_cn == en):
            score += 1.0
        ranked.append((p, score))
    ranked.sort(key=lambda x: x[1], reverse=True)
    return ranked
```

- [ ] **Step 4: 跑测试确认通过**

Run: `python -m pytest test_recipe_lib.py -v`
Expected: PASS（8 个测试通过）

- [ ] **Step 5: 写绑定 CLI**

`scripts/bind_ingredients.py`：
```python
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
```

- [ ] **Step 6: 用样例冒烟**

Run:
```bash
cd /d/easternmarket.ca/eastern-recipe
python scripts/bind_ingredients.py --products data/_fixtures/products.sample.json --recipes data/_fixtures/recipes.sample.json
```
Expected: 对"牛肉末"打印候选（样例里无肉类→提示无候选），不报错。

- [ ] **Step 7: Commit**

```bash
git add scripts/recipe_lib.py scripts/test_recipe_lib.py scripts/bind_ingredients.py
git -c user.name="Claude" -c user.email="noreply@anthropic.com" commit -m "feat: ingredient binding scorer + bind CLI"
```

---

## Task 9: 6 道真实种子菜谱（内容 + 绑定）

**Files:**
- Modify: `data/recipes.json`
- Create: `src/assets/images/`（菜品图，自拍/AI/授权）

- [ ] **Step 1: 用真实导出选菜**

先确保 `data/products.json` 是 Task 7 的真实导出。选 6 道"顾客常做 + 本店食材最齐"的家常菜（优先 `sold_90d` 高的食材覆盖的菜，如麻婆豆腐、番茄炒蛋、青椒肉丝、白灼菜心、紫菜蛋花汤、可乐鸡翅）。

- [ ] **Step 2: 逐道绑定**

对每道菜先写 `ingredients`（`code:null` 占位），再跑：
```bash
python scripts/bind_ingredients.py --products data/products.json --recipes data/recipes.json
```
按输出把高置信候选的 `code` 填回 `data/recipes.json`；无候选的食材保留 `code:null`（前端会显示"暂缺"）。每道补 `aliases`（含拼音）、`tags`、`steps`、`image_credit`。

- [ ] **Step 3: 配图（版权合规）**

每道菜放一张成品图到 `src/assets/images/<id>.jpg`，并在菜谱 `image` 指向它、`image_credit` 标 `self`/`ai`/`licensed`。**禁止**直接下载网图。先没有合规图的菜，`image` 留空，前端用占位（不阻断上线）。

- [ ] **Step 4: 关联自检**

```bash
python -m http.server 8080
```
逐道搜索→点开→确认：已绑食材显示真实价格/分类、未绑显示"暂缺"、汇总数字正确、无控制台报错。

- [ ] **Step 5: Commit**

```bash
git add data/recipes.json src/assets/images/
git -c user.name="Claude" -c user.email="noreply@anthropic.com" commit -m "content: 6 seed recipes bound to real SKUs"
```

---

## Task 10: 高标准验收（移动/微信/版权/端到端）

**Files:** 无（验收 + 修复）

- [ ] **Step 1: 自动化逻辑回归**

```bash
cd /d/easternmarket.ca/eastern-recipe
node --test && python -m pytest scripts/ -v
```
Expected: 全绿。任一失败先修再继续。

- [ ] **Step 2: 移动端视觉验收（按 Chris「最高标准」）**

DevTools iPhone + Android 视口逐项确认：
- 无横向滚动、触摸目标 ≥44px、品牌色正确（深绿标题、绿底汇总、红字"暂缺"）
- 长英文商品名/长菜名不溢出、食材行不串行
- 列出每条不达标项，修 `app.css` 后复验
Expected: 截图存档，逐项 ✅。

- [ ] **Step 3: 微信内置浏览器实测**

把本地站经 Tailscale/局域网在手机微信里打开（参考 eastern-farm `docs/WECHAT-SHARE.md`）。确认搜索、点开、渲染正常（经典 `<script>` 已规避 ESM 兼容问题）。
Expected: 微信内可用，无白屏。

- [ ] **Step 4: 版权合规检查**

逐张 `src/assets/images/*` 核对 `image_credit`，确认无来源不明网图。任何存疑的图删除并改占位。
Expected: 每张图来源 = self/ai/licensed，可追溯。

- [ ] **Step 5: 价格准确性抽查（引流生死线）**

随机抽 3 道菜的已绑食材，拿 `code` 去 StockWise 后台核对：价格、是否真在售、分类一致。任一错绑立刻改 `recipes.json`（错绑会把顾客引到没货商品，零容忍）。
Expected: 抽查 100% 一致。

- [ ] **Step 6: 部署就绪自检（不 push）**

确认：`CNAME`=recipe.easternmarket.ca、根 `index.html` 重定向正常、`data/products.json` 在 `.gitignore`（但**部署需要它**——见下注）、`git status` 干净。
> ⚠️ 部署注意：GitHub Pages 需要 `data/products.json` 实际存在于发布分支。两种做法（Plan 3 定）：① 取消忽略、把导出产物纳入发布；② 用 GitHub Actions 在部署时跑导出。本计划阶段先**临时取消忽略并提交一份真实导出**以便 Chris 首次手动 push 上线。
```bash
git rm --cached -q --ignore-unmatch data/products.json 2>/dev/null; true
# 若选择随库发布：从 .gitignore 移除 data/products.json 并提交真实导出
```

- [ ] **Step 7: 交付说明（给 Chris 的 push 清单）**

在对话里给出：仓库路径、`git log` 摘要、待 Chris 执行的步骤（建 GitHub repo `eastern-recipe`、`git remote add`、`git push`、GitHub Pages 设 Pages source + 自定义域 recipe.easternmarket.ca、DNS CNAME）。**不代替 Chris push。**

---

## 后续计划（不在本计划内）

- **Plan 2 — B「今天做什么菜」+ 促销**：`featured.json` 主推食材、库存反推菜谱、复用 promo-poster 管线导出海报。
- **Plan 3 — 自动化 + 回收**：每日导出定时（复用 `D:\easternmarket.ca\routines` 计划任务或 GitHub Actions）、搜索词回收到 Firestore `recipe_search_misses`、products.json 发布策略定稿。

---

## 自检记录（写完计划后对照 spec）

- **spec §1 A 搜菜找货**：Task 2、4、5、9 覆盖（搜菜→食材→价格→暂缺→汇总→想做收藏）。✅
- **spec §1 A2 以货找菜（货→菜）**：Task 3B（`dishesForIngredient` 倒排）+ Task 4（统一搜索的"还能做"区 + 食材 chips）。✅
- **spec §1 粘性首页**：Task 3B（`todaysPicks` 每日轮换）+ Task 4（今晚吃什么/换一批/chips/想做清单 localStorage）+ Task 5（首页样式）。✅
- **spec §2 数据源/分类/币种/称重**：Task 6（build_product_record/价格单位/分类归一）、Task 3（称重不入总价）、全局加元。✅
- **spec §4 数据模型**：Task 1 夹具 + Task 6 记录结构一致（字段名 `code`/`price_unit`/`sold_90d` 全程一致）。✅
- **spec §6 半自动绑定**：Task 8 打分 + CLI、Task 9 实操。✅
- **spec §7 版权/缓存/暂缺/价格时效**：Task 9 配图合规、Task 4 fetch 失败兜底、Task 3 暂缺、页脚"以店内标价为准"。✅
- **spec §8 测试策略**：Task 2/3/3B/6/8 的 node/pytest 用例对应（含倒排 + 轮换确定性）。✅
- **未覆盖（有意延后）**：B/featured.json、海报复用、每日自动化、搜索词回收、深度粘性(推送/个性化) → Plan 2/3（spec §10 开放项一并在那里定）。
- **类型一致性核对**：`code`/`price_unit`/`on_sale`/`sold_90d`/`refPriceEach`/`haveCount`/`weighed` 在 JS 与 Python 两侧命名一致；`dishesForIngredient`/`todaysPicks`/`buildProductIndex`/`associateRecipe`/`matchRecipes` 五个导出名在 Task 3B 实现与 Task 4 调用处一致；前端渲染读取字段与 `associateRecipe` 返回结构一致。✅
