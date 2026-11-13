/* Shared favourites and purchase links for static and hash-routed recipe pages. */
(function () {
  'use strict';
  var KEY = 'er_recipe_faves_v1';
  function favorites() {
    try { var value = JSON.parse(localStorage.getItem(KEY)); return Array.isArray(value) ? value : []; }
    catch (error) { return []; }
  }
  function syncFavorites() {
    var saved = favorites();
    document.querySelectorAll('[data-favorite-recipe]').forEach(function (button) {
      var active = saved.indexOf(button.dataset.favoriteRecipe) !== -1;
      button.setAttribute('aria-pressed', String(active));
      button.setAttribute('aria-label', active ? '取消收藏食谱' : '收藏食谱');
      button.title = active ? '取消收藏' : '收藏';
    });
    document.querySelectorAll('[data-buy-recipe]').forEach(preparePurchase);
  }
  function preparePurchase(buy) {
    if (buy.dataset.requestId) return;
    var url = new URL('https://easternmarket.ca/group-order');
    buy.dataset.requestId = crypto.randomUUID();
    url.searchParams.set('recipe', buy.dataset.buyRecipe);
    url.searchParams.set('recipeRequest', buy.dataset.requestId);
    buy.href = url.href;
  }
  document.addEventListener('click', function (event) {
    var button = event.target.closest('[data-favorite-recipe]');
    if (button) {
      var saved = favorites(), id = button.dataset.favoriteRecipe, i = saved.indexOf(id);
      if (i === -1) saved.push(id); else saved.splice(i, 1);
      try { localStorage.setItem(KEY, JSON.stringify(saved)); syncFavorites(); }
      catch (error) { button.setAttribute('aria-label', '收藏未保存，请允许浏览器存储后重试'); }
    }
    var buy = event.target.closest('[data-buy-recipe]');
    if (buy) activatePurchase(buy);
  });
  function activatePurchase(buy) {
    var now = Date.now();
    if (buy.dataset.activatedAt && now - Number(buy.dataset.activatedAt) > 1500) {
      delete buy.dataset.requestId;
    }
    buy.dataset.activatedAt = String(now);
    preparePurchase(buy);
  }
  document.addEventListener('auxclick', function (event) {
    var buy = event.target.closest('[data-buy-recipe]');
    if (buy && event.button === 1) activatePurchase(buy);
  });
  window.addEventListener('pageshow', function (event) {
    if (!event.persisted) return;
    document.querySelectorAll('[data-buy-recipe]').forEach(function (buy) {
      delete buy.dataset.requestId;
      delete buy.dataset.activatedAt;
      preparePurchase(buy);
    });
  });
  window.addEventListener('storage', syncFavorites);
  window.RecipeActions = { syncFavorites: syncFavorites };
  syncFavorites();
})();
