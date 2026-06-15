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
      // 价格为 0 / 空 = 市价商品（多为按重量的生鲜，系统里录成 0），不报具体价
      const hasPrice = available && typeof p.price === 'number' && p.price > 0;
      const row = {
        label: ing.label,
        qty: ing.qty,
        required: !!ing.required,
        unbound: !ing.code || !p,
        available: available,
        market_price: available && !hasPrice,
        price: p ? p.price : null,
        price_unit: p ? p.price_unit : null,
        category: p ? p.category : null,
        image_url: p ? p.image_url : ''
      };
      rows.push(row);
      if (available) {
        haveCount += 1;
        if (hasPrice) {
          if (p.price_unit === 'each') refPriceEach += p.price;
          else if (p.price_unit === 'lb') weighed.push({ label: ing.label, price: p.price });
        }
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
    // 先算一次每道菜的齐全度，避免在 sort 比较器里反复调用 associateRecipe
    const scored = hit.map(function (r) {
      const v = associateRecipe(r, productIndex);
      return { recipe: r, haveCount: v.haveCount, totalCount: v.totalCount };
    });
    scored.sort(function (a, b) {
      if (b.haveCount !== a.haveCount) return b.haveCount - a.haveCount;
      return a.totalCount - b.totalCount;
    });
    return scored.map(function (s) { return s.recipe; });
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

  return {
    normalizeQuery: normalizeQuery,
    matchRecipes: matchRecipes,
    buildProductIndex: buildProductIndex,
    associateRecipe: associateRecipe,
    dishesForIngredient: dishesForIngredient,
    todaysPicks: todaysPicks
  };
});
