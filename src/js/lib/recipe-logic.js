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
