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
    var img = r.image ? '<img class="card__img" src="' + esc(r.image) + '" alt="" loading="lazy">' : '';
    return '<button class="card" data-id="' + esc(r.id) + '">' + img +
      '<span class="card__body">' +
        '<span class="card__name">' + esc(r.name_cn) + '</span>' +
        '<span class="card__tags">' + esc((r.tags || []).join(' · ')) + '</span>' +
      '</span></button>';
  }
  function wireCards(container) {
    Array.prototype.forEach.call(container.querySelectorAll('.card'), function (btn) {
      btn.onclick = function () { var r = state.byId[btn.dataset.id]; if (r) renderDetail(r); };
    });
  }

  // ---- 食材行（不显示价格；只标用量/分类/是否有货）----
  function ingredientRow(r) {
    if (!r.available) {
      return '<li class="ing ing--out"><span class="ing__name">' + esc(r.label) +
        '</span><span class="ing__qty">' + esc(r.qty) + '</span>' +
        '<span class="ing__tag">暂缺</span></li>';
    }
    return '<li class="ing"><span class="ing__name">' + esc(r.label) +
      '</span><span class="ing__qty">' + esc(r.qty) + '</span>' +
      '<span class="ing__tag ing__tag--ok">有货</span>' +
      '<span class="ing__cat">' + esc(r.category || '') + '</span></li>';
  }

  function show(section) {
    $('home').hidden = section !== 'home';
    $('results').hidden = section !== 'results';
    $('detail').hidden = section !== 'detail';
  }

  function renderDetail(recipe) {
    var cameFrom = $('results').hidden ? 'home' : 'results';
    var d = $('detail');
    var faved = isFave(recipe.id);
    // 成品(ready)：本店有售，不拿商品表卡它；普通菜谱(dish)：列食材 有货/暂缺
    var bodyHtml;
    if (recipe.kind === 'ready') {
      bodyHtml = '<div class="ready-tag">🛒 本店有售</div>';
    } else {
      var a = RL.associateRecipe(recipe, state.productIndex);
      bodyHtml = '<ul class="ings">' + a.rows.map(ingredientRow).join('') + '</ul>';
    }
    var stepsTitle = recipe.kind === 'ready' ? '怎么吃' : '做法';
    var hero = recipe.image ? '<img class="detail__img" src="' + esc(recipe.image) + '" alt="">' : '';
    d.innerHTML =
      '<button class="back" id="back">← 返回</button>' +
      hero +
      '<h2 class="detail__title">' + esc(recipe.name_cn) +
        ' <small>' + esc(recipe.name_en || '') + '</small></h2>' +
      bodyHtml +
      '<button class="fave-btn' + (faved ? ' is-on' : '') + '" id="fave">' +
        (faved ? '♥ 已加入想做' : '♡ 加入想做') + '</button>' +
      '<h3 class="detail__h3">' + stepsTitle + '</h3>' +
      '<ol class="steps">' + (recipe.steps || []).map(function (s) {
        return '<li>' + esc(s) + '</li>';
      }).join('') + '</ol>';
    $('back').onclick = function () {
      if (cameFrom === 'results') { show('results'); }      // 从搜索来 → 回到搜索结果，保留查询
      else { $('q').value = ''; renderHome(); show('home'); } // 从首页来 → 回首页并清空搜索框
    };
    $('fave').onclick = function () { toggleFave(recipe.id); renderDetail(recipe); };
    show('detail');
    $('back').focus();   // 无障碍：详情打开后把焦点移到返回按钮
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
  // 某板块的菜，按 priority 高→低（priority 即按你 90 天销量定的热卖度）
  function bySection(sec) {
    return state.recipes.filter(function (r) { return r.section === sec; })
      .sort(function (a, b) { return (b.priority || 0) - (a.priority || 0); });
  }
  // 快捷 chips：取"今晚吃什么 + 鲜河粉肠粉"里每道菜的主料（第一个必需且在售的食材），引导到高营业额菜
  function featuredIngredientChips(max) {
    var seen = {}, arr = [];
    bySection('tonight').concat(bySection('fresh')).forEach(function (r) {
      var ings = (r.ingredients || []).filter(function (ing) {
        var p = ing.code ? state.productIndex[ing.code] : null;
        return p && p.on_sale;
      });
      if (!ings.length) return;
      var lbl = ings[0].label;             // 主料
      if (seen[lbl]) return;
      seen[lbl] = 1; arr.push(lbl);
    });
    return arr.slice(0, max);
  }
  function fillCards(id, list) {
    $(id).innerHTML = list.map(recipeCard).join('');
    wireCards($(id));
  }

  function renderHome() {
    // 🔥 今晚吃什么：tonight 按热卖度排序，显示一个 4 道的窗口，「换一批」往后翻
    var tonight = bySection('tonight');
    if (tonight.length) {
      var n = 4, start = (state.reshuffle * n) % tonight.length;
      var win = [];
      for (var i = 0; i < Math.min(n, tonight.length); i++) win.push(tonight[(start + i) % tonight.length]);
      fillCards('picks', win);
    } else {
      fillCards('picks', RL.todaysPicks(state.recipes, todayStr(), 4)); // 兜底
    }

    // 🍜 鲜河粉鲜肠粉 / 🌅 早餐包点
    var fresh = bySection('fresh');
    $('freshBlock').hidden = !fresh.length;
    fillCards('fresh', fresh);
    var breakfast = bySection('breakfast');
    $('breakfastBlock').hidden = !breakfast.length;
    fillCards('breakfast', breakfast);
    var veg = bySection('veg');
    $('vegBlock').hidden = !veg.length;
    fillCards('veg', veg);

    // 🥬 chips（主料 → 以货找菜）
    var chips = featuredIngredientChips(10);
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
      $('home').innerHTML = '<p class="empty">数据加载失败，请检查网络后<button class="link-btn" type="button" onclick="location.reload()">重试</button></p>';
    });
  }
  document.addEventListener('DOMContentLoaded', boot);
})();
