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

  return {
    normalizeQuery: normalizeQuery,
    matchRecipes: matchRecipes,
    buildProductIndex: buildProductIndex,
    associateRecipe: associateRecipe
  };
});
