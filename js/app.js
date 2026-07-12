/* app.js — 逛发现首页(今晚吃什么/食材chips/想做清单) + 统一搜索(菜名/以货找菜) + 食谱详情
   + 到店购物清单 + hash 路由(每道菜可分享链接、返回键可用)。
   渲染薄层，计算全调 RecipeLogic；收藏/勾选存 localStorage。 */
(function () {
  'use strict';
  var RL = window.RecipeLogic;
  var FAVE_KEY = 'er_recipe_faves_v1';
  var DONE_KEY = 'er_shoplist_done_v1';
  // 配送业务正式上线后把 enabled 改 true 即可（入口出现在详情页和购物清单页）
  var DELIVERY = { enabled: false, url: 'https://easternmarket.ca' };
  var state = { recipes: [], productIndex: {}, byId: {} };
  var didNav = 0;   // 本次会话内的站内跳转数；0 = 直接落地某深链，返回按钮回首页而非退出

  function $(id) { return document.getElementById(id); }
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }

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
  // ---- 购物清单勾选状态（localStorage）----
  function getDone() {
    try { return JSON.parse(localStorage.getItem(DONE_KEY)) || {}; } catch (e) { return {}; }
  }
  function setDone(map) {
    try { localStorage.setItem(DONE_KEY, JSON.stringify(map)); } catch (e) {}
  }

  // ---- hash 路由 ----
  // ''            → 首页（搜索框有词则显示搜索结果）
  // #/r/<id>      → 食谱详情（可直接分享这条链接）
  // #/sec/<sec>   → 某板块全部
  // #/list        → 到店购物清单
  function parseHash() {
    var h = location.hash || '', m;
    if ((m = h.match(/^#\/r\/(.+)$/))) return { view: 'detail', id: decodeURIComponent(m[1]) };
    if ((m = h.match(/^#\/sec\/([a-z]+)$/))) return { view: 'section', sec: m[1] };
    if (h === '#/list') return { view: 'list' };
    return { view: 'home' };
  }
  function nav(hash) {
    if (location.hash === hash) route();
    else location.hash = hash;   // 触发 hashchange → route()
  }
  function goBack() {
    if (didNav > 0) history.back();
    else location.hash = '';     // 直接落地深链：返回=去首页
  }
  function route() {
    var r = parseHash();
    if (r.view === 'detail') {
      var rec = state.byId[r.id];
      if (rec) { renderDetail(rec); return; }
      // 未知 id（菜被下架/链接打错）→ 落回首页
    }
    if (r.view === 'section' && SEC_TITLE[r.sec]) { showSection(r.sec); return; }
    if (r.view === 'list') { renderShoppingList(); return; }
    var q = $('q').value;
    if (q && q.trim()) { renderResults(q); }
    else { show('home'); renderHome(); }
  }

  // ---- 复制链接（微信/浏览器都可用；clipboard 不可用时走隐藏输入框兜底）----
  function copyText(t, onOk) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(t).then(onOk, function () { legacyCopy(t, onOk); });
    } else { legacyCopy(t, onOk); }
  }
  function legacyCopy(t, onOk) {
    var ta = document.createElement('textarea');
    ta.value = t; ta.style.position = 'fixed'; ta.style.opacity = '0';
    document.body.appendChild(ta); ta.select();
    try { if (document.execCommand('copy')) onOk(); } catch (e) {}
    document.body.removeChild(ta);
  }

  // ---- 菜卡 ----
  function recipeCard(r) {
    var img = r.image ? '<img class="card__img" src="' + esc(r.image) + '" alt="' + esc(r.name_cn) + '" loading="lazy">' : '';
    var en = r.name_en ? '<span class="card__en">' + esc(r.name_en) + '</span>' : '';
    var nutri = r.nutrition ? '<span class="card__nutri">🌿 ' + esc(r.nutrition) + '</span>' : '';
    return '<button class="card" data-id="' + esc(r.id) + '">' + img +
      '<span class="card__body">' +
        '<span class="card__name">' + esc(r.name_cn) + '</span>' + en + nutri +
      '</span></button>';
  }
  function wireCards(container) {
    Array.prototype.forEach.call(container.querySelectorAll('.card'), function (btn) {
      btn.onclick = function () {
        if (state.byId[btn.dataset.id]) nav('#/r/' + encodeURIComponent(btn.dataset.id));
      };
    });
  }

  // ---- 食材行（不显示价格、不显示缺货；默认都有货，客人到店购买）----
  function ingredientRow(r) {
    var cat = r.category ? '<span class="ing__cat">' + esc(r.category) + '</span>' : '';
    return '<li class="ing"><span class="ing__name">' + esc(r.label) +
      '</span><span class="ing__qty">' + esc(r.qty) + '</span>' +
      '<span class="ing__tag ing__tag--ok">有货</span>' + cat + '</li>';
  }

  function show(section) {
    $('home').hidden = section !== 'home';
    $('results').hidden = section !== 'results';
    $('detail').hidden = section !== 'detail';
  }

  function renderDetail(recipe) {
    var d = $('detail');
    var faved = isFave(recipe.id);
    // 成品(ready)：本店有售，不拿商品表卡它；普通食谱(dish)：列食材 有货/暂缺
    var bodyHtml;
    if (recipe.kind === 'ready') {
      bodyHtml = '<div class="ready-tag">🛒 本店有售</div>';
    } else {
      var a = RL.associateRecipe(recipe, state.productIndex);
      bodyHtml = '<ul class="ings">' + a.rows.map(ingredientRow).join('') + '</ul>';
    }
    var stepsTitle = recipe.kind === 'ready' ? '怎么吃' : '做法';
    var hero = recipe.image ? '<img class="detail__img" src="' + esc(recipe.image) + '" alt="' + esc(recipe.name_cn) + '">' : '';
    var actions = '<div class="detail__actions">' +
      '<button class="mini-btn" id="copylink">🔗 复制链接</button>' +
      (faved ? '<button class="mini-btn" id="tolist">🧾 看购物清单</button>' : '') +
      (DELIVERY.enabled ? '<a class="mini-btn" href="' + esc(DELIVERY.url) + '" target="_blank" rel="noopener">🚚 网上下单</a>' : '') +
      '</div>';
    d.innerHTML =
      '<button class="back" id="back">← 返回</button>' +
      hero +
      '<h2 class="detail__title">' + esc(recipe.name_cn) +
        ' <small>' + esc(recipe.name_en || '') + '</small></h2>' +
      (recipe.nutrition ? '<div class="detail__nutri">🌿 营养 · ' + esc(recipe.nutrition) + '</div>' : '') +
      bodyHtml +
      '<button class="fave-btn' + (faved ? ' is-on' : '') + '" id="fave">' +
        (faved ? '♥ 已加入想做' : '♡ 加入想做') + '</button>' +
      actions +
      '<h3 class="detail__h3">' + stepsTitle + '</h3>' +
      '<ol class="steps">' + (recipe.steps || []).map(function (s) {
        return '<li>' + esc(s) + '</li>';
      }).join('') + '</ol>';
    $('back').onclick = goBack;
    $('fave').onclick = function () { toggleFave(recipe.id); renderDetail(recipe); };
    $('copylink').onclick = function () {
      copyText(location.href, function () { $('copylink').textContent = '✅ 已复制，发给家人吧'; });
    };
    if ($('tolist')) $('tolist').onclick = function () { nav('#/list'); };
    show('detail');
    $('back').focus();   // 无障碍：详情打开后把焦点移到返回按钮
    window.scrollTo(0, 0);
  }

  // ---- 到店购物清单：收藏的菜 → 食材汇总，按超市分区分组，可勾选划掉 ----
  function renderShoppingList() {
    var faves = getFaves().map(function (id) { return state.byId[id]; }).filter(Boolean);
    var el = $('results');
    var html = '<button class="back" id="listback">← 返回首页</button>' +
      '<h2 class="block__title">🧾 到店购物清单</h2>';
    if (!faves.length) {
      el.innerHTML = html + '<p class="empty">还没有收藏的菜～<br>看到想做的菜点「♡ 加入想做」，这里就会帮你把食材汇总好。</p>';
      $('listback').onclick = goBack;
      show('results'); window.scrollTo(0, 0); return;
    }
    var list = RL.buildShoppingList(faves, state.productIndex);
    var done = getDone();
    // 只保留当前清单里还存在的勾选记录
    var pruned = {};
    list.groups.forEach(function (g) {
      g.items.forEach(function (it) { if (done[it.key]) pruned[it.key] = 1; });
    });
    setDone(pruned); done = pruned;

    html += '<p class="block__note">来自你收藏的 ' + faves.length + ' 道菜 · 按超市分区排好，到店照着拿</p>';
    html += '<div class="shop-srcs">' + faves.map(function (r) {
      return '<span class="src-chip">' + esc(r.name_cn) +
        '<button data-rm="' + esc(r.id) + '" aria-label="从清单移除' + esc(r.name_cn) + '">✕</button></span>';
    }).join('') + '</div>';
    if (list.ready.length) {
      html += '<div class="ready-tag">🛒 成品直接拿：' +
        list.ready.map(function (r) { return esc(r.name_cn); }).join('、') + '（本店有售）</div>';
    }
    var GRP_ICON = { '新鲜蔬菜': '🥬', '新鲜水果': '🍎', '冷冻食品': '🧊', '豆腐蛋品': '🥚',
      '米面粮油': '🍚', '干货调料': '🧂', '零食饮料': '🥤', '日用杂货': '🧺', '中成药品': '🌿' };
    html += list.groups.map(function (g) {
      return '<div class="shopgrp"><div class="shopgrp__hd">' +
        (GRP_ICON[g.category] || '🛒') + ' ' + esc(g.category) + '</div><ul>' +
        g.items.map(function (it) {
          var uses = it.uses.map(function (u) {
            return esc(u.recipe_cn) + (u.qty ? ' ' + esc(u.qty) : '');
          }).join(' · ');
          return '<li class="shopitem' + (done[it.key] ? ' is-done' : '') + '" data-key="' + esc(it.key) + '">' +
            '<label><input type="checkbox"' + (done[it.key] ? ' checked' : '') + '>' +
            '<span class="shopitem__name">' + esc(it.label) + '</span>' +
            '<span class="shopitem__uses">' + uses + '</span></label></li>';
        }).join('') + '</ul></div>';
    }).join('');
    html += '<div class="shoplist__actions">' +
      '<button class="mini-btn" id="listcopy">🔗 复制清单文字</button>' +
      '<button class="mini-btn" id="listclear">↺ 清除勾选</button>' +
      (DELIVERY.enabled ? '<a class="mini-btn" href="' + esc(DELIVERY.url) + '" target="_blank" rel="noopener">🚚 网上下单</a>' : '') +
      '</div>';
    el.innerHTML = html;

    $('listback').onclick = goBack;
    Array.prototype.forEach.call(el.querySelectorAll('.src-chip button'), function (btn) {
      btn.onclick = function () { toggleFave(btn.dataset.rm); renderShoppingList(); };
    });
    Array.prototype.forEach.call(el.querySelectorAll('.shopitem input'), function (cb) {
      cb.onchange = function () {
        var li = cb.closest('.shopitem'), map = getDone();
        if (cb.checked) map[li.dataset.key] = 1; else delete map[li.dataset.key];
        setDone(map);
        li.classList.toggle('is-done', cb.checked);
      };
    });
    $('listclear').onclick = function () { setDone({}); renderShoppingList(); };
    $('listcopy').onclick = function () {
      var lines = ['🧾 东方超市购物清单（' + faves.map(function (r) { return r.name_cn; }).join('、') + '）'];
      list.groups.forEach(function (g) {
        lines.push('【' + g.category + '】' + g.items.map(function (it) { return it.label; }).join('、'));
      });
      if (list.ready.length) lines.push('【成品】' + list.ready.map(function (r) { return r.name_cn; }).join('、'));
      lines.push('食谱都在 → ' + location.origin + location.pathname);
      copyText(lines.join('\n'), function () { $('listcopy').textContent = '✅ 已复制'; });
    };
    show('results');
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
      html += '<h2 class="block__title">食谱</h2><div class="cards">' +
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

  // 「查看全部」：把某分类全部食谱铺在结果区（网格），带返回首页
  var SEC_TITLE = {
    tonight: '🔥 今晚吃什么', cantonese: '🥢 粤菜 · 广式', seafood: '🐟 海鲜河鲜', staple: '🍚 主食 · 面饭',
    dumpling: '🥟 饺子 · 馄饨', fresh: '🍜 鲜河粉 · 鲜肠粉', breakfast: '🌅 早餐包点', veg: '🥗 家常蔬菜',
    other: '🍳 家常菜'
  };
  function showSection(sec) {
    var list = bySection(sec);
    var el = $('results');
    el.innerHTML =
      '<button class="back" id="secback">← 返回首页</button>' +
      '<h2 class="block__title">' + esc(SEC_TITLE[sec] || '') + '（' + list.length + '）</h2>' +
      '<div class="cards">' + list.map(recipeCard).join('') + '</div>';
    $('secback').onclick = goBack;
    wireCards(el);
    show('results');
    window.scrollTo(0, 0);
  }

  function onSearch() {
    // 在详情/板块/清单页开始搜索：静默清掉 hash（不产生历史记录），视图跟着搜索走
    if (location.hash) history.replaceState(null, '', location.pathname + location.search);
    var q = $('q').value;
    if (!q || !q.trim()) { show('home'); renderHome(); return; }
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
  // 无限循环横滑：把一份卡片复制成三份，滚动到边界时无缝跳回中间份
  function setupLoop(el) {
    if (el._onScroll) { el.removeEventListener('scroll', el._onScroll); el._onScroll = null; }
    if (el.scrollWidth <= el.clientWidth + 16) return; // 不溢出就不循环
    var one = el.innerHTML;
    el.innerHTML = one + one + one;
    wireCards(el);                 // 克隆卡片靠 data-id 共用点击
    var setW = el.scrollWidth / 3;
    el.scrollLeft = setW;          // 起点落在中间那份
    el._onScroll = function () {
      if (el.scrollLeft < setW * 0.5) el.scrollLeft += setW;
      else if (el.scrollLeft > setW * 1.5) el.scrollLeft -= setW;
    };
    el.addEventListener('scroll', el._onScroll, { passive: true });
  }
  function fillCards(id, list) {
    var el = $(id);
    el.innerHTML = list.map(recipeCard).join('');
    wireCards(el);
    setupLoop(el);
  }

  function renderHome() {
    // 🔥 今晚吃什么：tonight 全部上，按热卖度排序
    fillCards('picks', bySection('tonight'));

    // 🥢 粤菜
    var cantonese = bySection('cantonese');
    $('cantoneseBlock').hidden = !cantonese.length;
    fillCards('cantonese', cantonese);
    // 🐟 海鲜 / 🍚 主食 / 🥟 饺子馄饨
    var seafood = bySection('seafood');
    $('seafoodBlock').hidden = !seafood.length;
    fillCards('seafood', seafood);
    var staple = bySection('staple');
    $('stapleBlock').hidden = !staple.length;
    fillCards('staple', staple);
    // 🍳 家常菜（section:"other"，原先无首页入口）
    var other = bySection('other');
    $('otherBlock').hidden = !other.length;
    fillCards('other', other);
    var dumpling = bySection('dumpling');
    $('dumplingBlock').hidden = !dumpling.length;
    fillCards('dumpling', dumpling);
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
      fetch('data/recipes.json').then(function (r) { return r.json(); }),
      fetch('data/products.json').then(function (r) { return r.json(); })
    ]).then(function (out) {
      state.recipes = out[0].recipes || [];
      state.productIndex = RL.buildProductIndex((out[1].items) || []);
      state.recipes.forEach(function (r) { state.byId[r.id] = r; });
      $('q').addEventListener('input', onSearch);
      Array.prototype.forEach.call(document.querySelectorAll('.seeall'), function (btn) {
        btn.onclick = function () { nav('#/sec/' + btn.dataset.sec); };
      });
      $('openShoplist').onclick = function () { nav('#/list'); };
      window.addEventListener('hashchange', function () { didNav += 1; route(); });
      show('home');     // 先显示(可见)再渲染，循环行才能量到宽度
      renderHome();
      if (location.hash) route();   // 直接落地的深链（#/r/xxx 分享链接）
    }).catch(function () {
      $('home').innerHTML = '<p class="empty">数据加载失败，请检查网络后<button class="link-btn" type="button" onclick="location.reload()">重试</button></p>';
    });
  }
  document.addEventListener('DOMContentLoaded', boot);
})();
