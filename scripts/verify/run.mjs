/* verify-browser.mjs — 真浏览器跑一遍关键路径。
   单元测试抓不到「按钮在、点了没反应、也不报错」这类失败，只有真跑才看得见。

   用法（先在仓库根起个静态服务器，例如 python -m http.server 8099）：
     node scripts/verify/run.mjs
     EM_BASE=https://recipe.easternmarket.ca node scripts/verify/run.mjs   # 打生产

   浏览器用系统自带的 Edge / Chrome，不下载浏览器二进制。 */
import { chromium } from 'playwright-core';
import { existsSync } from 'node:fs';

const BASE = process.env.EM_BASE || 'http://localhost:8099';
const CANDIDATES = [
  process.env.EM_BROWSER,
  'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
  'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe',
  '/usr/bin/google-chrome',
  '/usr/bin/chromium-browser',
].filter(Boolean);
const exe = CANDIDATES.find((p) => existsSync(p));
if (!exe) {
  console.error('找不到可用的 Edge/Chrome，设 EM_BROWSER 指定路径');
  process.exit(2);
}

const results = [];
const ok = (name, pass, detail = '') => {
  results.push({ name, pass, detail });
  console.log(`${pass ? '  OK  ' : '  FAIL'} ${name}${detail ? '  — ' + detail : ''}`);
};

// 从 localhost 打生产后端会被 CORS 挡，浏览器把它记成 console error —— 是环境噪声，不是缺陷
const NOISE = /blocked by CORS policy|Failed to load resource|ERR_INTERNET_DISCONNECTED/i;

const browser = await chromium.launch({ executablePath: exe, headless: true });
const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } });
const page = await ctx.newPage();
const consoleErrors = [];
const pageErrors = [];
const requested = [];
page.on('console', (m) => { if (m.type() === 'error' && !NOISE.test(m.text())) consoleErrors.push(m.text()); });
page.on('pageerror', (e) => pageErrors.push(String(e)));
page.on('request', (r) => requested.push(r.url()));

try {
  // ── 首页 ────────────────────────────────────────────────────────────────
  await page.goto(BASE + '/', { waitUntil: 'networkidle' });
  await page.waitForSelector('#season .card', { timeout: 15000 });

  const seasonVisible = await page.isVisible('#seasonBlock');
  ok('首页出现「应季」板块', seasonVisible);

  // setupLoop 会把卡片复制三份做无缝循环，所以按 data-id 去重才是真实菜数
  const seasonIds = await page.$$eval('#season .card', (els) =>
    [...new Set(els.map((e) => e.dataset.id))]);
  ok('应季板块有 10 道菜，含粉葛汤且不含月饼', seasonIds.length === 10 && seasonIds.includes('pueraria-pork-soup') && !seasonIds.includes('mooncake-ready'), seasonIds.join(', '));

  const usesCatalog = requested.some((u) => u.includes('/data/catalog.json'));
  const usesFullCatalog = requested.some((u) => u.includes('/data/products.json'));
  ok('首页下载精简目录，不下载全库商品', usesCatalog && !usesFullCatalog);

  const jumpText = await page.$eval('#jump', (e) => e.textContent);
  ok('首页有板块快捷条', jumpText.includes('应季') && jumpText.includes('粤菜') && jumpText.includes('饺子') && !jumpText.includes('中秋'), jumpText);

  const desk = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  const dp = await desk.newPage();
  await dp.goto(BASE + '/', { waitUntil: 'networkidle' });
  await dp.waitForSelector('#veg .card', { timeout: 15000 });
  const vegNums = await dp.$$eval('#veg .card', (els) => {
    const ids = els.map((e) => e.dataset.id);
    return { n: ids.length, u: new Set(ids).size };
  });
  ok('宽屏把菜铺开，不复制三份', vegNums.n === vegNums.u && vegNums.u >= 10,
    vegNums.n + ' 张卡片 / ' + vegNums.u + ' 道菜');
  const decideCols = await dp.$eval('#decide', (el) => getComputedStyle(el).gridTemplateColumns);
  ok('宽屏三种吃法并排', decideCols.split(' ').filter(Boolean).length === 3, decideCols);
  await desk.close();

  const firstBlock = await page.$eval('.home .block .block__title', (e) => e.textContent.trim());
  ok('今晚吃什么排在首页第一位', firstBlock.includes('今晚吃什么'), firstBlock);

  const decide = await page.$$eval('#decide .decide__card', (els) => els.map((e) => ({
    id: e.dataset.id,
    role: (e.querySelector('.decide__role') || {}).textContent || '',
  })));
  ok('首页三种吃法各一道',
    decide.length === 3
      && decide[0].id === 'tomato-egg' && decide[0].role.includes('快手上桌')
      && decide[1].id === 'napa-pork-vermicelli' && decide[1].role.includes('一家三口')
      && decide[2].id === 'hotpot' && decide[2].role.includes('周末多做一点'),
    decide.map((d) => d.role + ':' + d.id).join(' / '));
  await page.click('#decide .decide__card[data-id="tomato-egg"]');
  await page.waitForSelector('#detail:not([hidden]) .detail__title', { timeout: 10000 });
  const quickTitle = await page.$eval('.detail__title', (e) => e.textContent.trim());
  ok('点快手上桌打开番茄炒蛋', quickTitle.includes('番茄炒蛋'), quickTitle);
  await page.goBack();
  await page.waitForSelector('#season .card', { timeout: 10000 });

  const usesWebp = await page.$eval('#season picture source',
    (s) => s.getAttribute('srcset') || '');
  ok('卡片图走 WebP', /\/webp\/.*-400\.webp$/.test(usesWebp), usesWebp);

  // 横滑行里没滚到的图是懒加载，本来就不该加载；要抓的是「加载失败」：
  // complete 且 naturalWidth===0 才是坏图。
  const brokenImgs = await page.$$eval('#season img', (els) =>
    els.filter((i) => i.complete && i.naturalWidth === 0).map((i) => i.currentSrc || i.src));
  ok('应季板块没有加载失败的图', brokenImgs.length === 0, brokenImgs.slice(0, 2).join(' '));

  // 把所有横滑行滚到底，逼出全部懒加载图，再查全站有没有裂图。
  // WebP 文件缺失时 <picture> 不会回退 JPEG（回退看的是浏览器支不支持，
  // 不是文件在不在），图片会直接裂开且没有任何报错 —— 只有这样才抓得到。
  await page.evaluate(() => {
    document.querySelectorAll('.cards--row').forEach((el) => { el.scrollLeft = el.scrollWidth; });
    window.scrollTo(0, document.body.scrollHeight);
  });
  await page.waitForTimeout(4000);
  const brokenAll = await page.$$eval('img', (els) =>
    els.filter((i) => i.complete && i.naturalWidth === 0).map((i) => i.currentSrc || i.src));
  ok('首页全部图片都能加载（无裂图）', brokenAll.length === 0,
    brokenAll.length ? brokenAll.slice(0, 3).join(' ') : '已滚完全部横滑行');
  await page.evaluate(() => window.scrollTo(0, 0));

  // ── 详情页 ──────────────────────────────────────────────────────────────
  await page.click('#season .card[data-id="lotus-pork-bone-soup"]');
  await page.waitForSelector('#detail:not([hidden])', { timeout: 10000 });
  const title = await page.$eval('.detail__title', (e) => e.textContent.trim());
  ok('点卡片能打开详情页', title.includes('莲藕筒骨汤'), title);

  const facts = await page.$eval('.detail__facts', (e) => e.textContent.trim());
  const hook = await page.$eval('.detail__hook', (e) => e.textContent.trim());
  ok('详情页写时间和一句为什么今晚做', /约\d+分钟/.test(facts) && hook.length > 8, facts + ' / ' + hook);
  const stockBadge = await page.$$eval('#detail .ing', (els) =>
    els.filter((e) => e.textContent.includes('有货')).length);
  ok('详情页不再无条件印有货', stockBadge === 0);

  const ings = await page.$$eval('#detail .ing__name', (e) => e.map((x) => x.textContent.trim()));
  ok('详情页列出食材', ings.length >= 5, ings.slice(0, 3).join('、') + ' …');

  const cats = await page.$$eval('#detail .ing__cat', (e) => e.map((x) => x.textContent.trim()));
  ok('食材带超市分区（说明条码绑定有效）', cats.length >= 4, [...new Set(cats)].join(' '));

  const deliver = await page.$('#detail a.mini-btn[href*="group-order"]');
  ok('详情页出现「网上下单」按钮', !!deliver);

  // 复制链接：要复制静态页网址，不是 hash 地址
  await ctx.grantPermissions(['clipboard-read', 'clipboard-write']);
  await page.click('#copylink');
  await page.waitForTimeout(300);
  const copied = await page.evaluate(() => navigator.clipboard.readText());
  ok('复制链接复制的是静态菜页网址',
    /\/r\/lotus-pork-bone-soup\.html$/.test(copied), copied);

  // 加入想做 → 购物清单
  await page.click('#fave');
  await page.waitForSelector('#tolist', { timeout: 5000 });
  await page.click('#tolist');
  await page.waitForSelector('.shopgrp', { timeout: 10000 });
  const grpNames = await page.$$eval('.shopgrp__hd', (e) => e.map((x) => x.textContent.trim()));
  ok('购物清单按超市分区分组', grpNames.length >= 2, grpNames.join(' / '));
  // 「其他」= 没绑条码的调味料（盐、八角这类），是有意的；主料掉进去才是绑定坏了
  const otherItems = await page.$$eval('.shopgrp', (grps) => {
    const g = grps.find((x) => x.querySelector('.shopgrp__hd').textContent.includes('其他'));
    return g ? [...g.querySelectorAll('.shopitem__name')].map((x) => x.textContent.trim()) : [];
  });
  const mains = ['猪筒骨', '莲藕'];
  ok('主料没掉进「其他」组（说明条码绑定有效）',
    mains.every((m) => !otherItems.includes(m)), '其他组：' + (otherItems.join('、') || '空'));

  // ── 搜索 ────────────────────────────────────────────────────────────────
  await page.fill('#q', '月饼');
  await page.waitForSelector('#results .empty', { timeout: 10000 });
  const moonMiss = await page.$eval('#results .empty', (e) => e.textContent.trim());
  ok('搜「月饼」已经下架', moonMiss.includes('没找到'), moonMiss);

  await page.fill('#q', '莲藕');
  await page.waitForSelector('#results .card', { timeout: 10000 });
  const byIng = await page.$$eval('#results .card__name', (e) => e.map((x) => x.textContent.trim()));
  ok('搜食材「莲藕」能反查到菜', byIng.length >= 2, byIng.slice(0, 4).join('、'));

  // ── 静态 SEO 页 ─────────────────────────────────────────────────────────
  const p2 = await ctx.newPage();
  const resp = await p2.goto(BASE + '/r/hotpot.html', { waitUntil: 'domcontentloaded' });
  ok('静态菜页返回 200', resp.status() === 200, String(resp.status()));
  const h1 = await p2.$eval('h1', (e) => e.textContent.trim());
  ok('静态菜页有 h1 菜名', h1.includes('火锅'), h1);
  const ld = await p2.$eval('script[type="application/ld+json"]', (e) => JSON.parse(e.textContent));
  ok('静态菜页带 Recipe 结构化数据', ld['@type'] === 'Recipe' && ld.name.includes('火锅'));
  ok('结构化数据含做法步骤', Array.isArray(ld.recipeInstructions) && ld.recipeInstructions.length > 0,
    ld.recipeInstructions.length + ' 步');
  const canon = await p2.$eval('link[rel=canonical]', (e) => e.href);
  ok('静态菜页有 canonical', /\/r\/hotpot\.html$/.test(canon), canon);
  const dump = await p2.goto(BASE + '/r/guantang-xiaoshuijiao.html', { waitUntil: 'domcontentloaded' });
  const dumpFacts = await p2.$eval('.pg-facts', (e) => e.textContent);
  const dumpMeta = await p2.$eval('meta[name=description]', (e) => e.content);
  const dumpTag = await p2.$eval('.ready-tag', (e) => e.textContent);
  ok('水饺按煮来写，不说蒸一蒸',
    dump.status() === 200 && dumpFacts.includes('煮一煮') && dumpMeta.includes('煮一煮')
      && dumpTag.includes('煮一煮') && !dumpMeta.includes('蒸') && !dumpFacts.includes('蒸'),
    dumpFacts + ' / ' + dumpMeta.slice(0, 40));
  // 真的把 JS 关掉再读一遍 —— 爬虫看到的就是这个
  const noJsCtx = await browser.newContext({ javaScriptEnabled: false });
  const noJs = await noJsCtx.newPage();
  await noJs.goto(BASE + '/r/hotpot.html', { waitUntil: 'domcontentloaded' });
  const stepsText = await noJs.$$eval('.steps li', (e) => e.map((x) => x.textContent.trim()));
  const ingText = await noJs.$$eval('.ing__name', (e) => e.map((x) => x.textContent.trim()));
  ok('关掉 JS 后做法照样在页面上', stepsText.length > 0, stepsText.length + ' 步');
  ok('关掉 JS 后食材照样在页面上', ingText.length > 0, ingText.join('、').slice(0, 30));
  await noJsCtx.close();

  const idx = await p2.goto(BASE + '/r/', { waitUntil: 'domcontentloaded' });
  ok('全部食谱目录页返回 200', idx.status() === 200);
  const links = await p2.$$eval('.pg-seclist a', (e) => e.length);
  ok('目录页链出全部 101 道菜', links === 101, links + ' 条');
  for (const [id, name] of [
    ['pueraria-pork-soup', '粉葛猪骨汤'],
    ['gai-lan-oyster-sauce', '蚝油芥兰'],
    ['choy-sum-garlic', '蒜蓉菜心'],
    ['minced-pork-steamed-egg', '肉末蒸蛋'],
  ]) {
    const response = await p2.goto(BASE + '/r/' + id + '.html', { waitUntil: 'networkidle' });
    const title = await p2.locator('h1').innerText();
    const hero = await p2.locator('.detail__img').evaluate((img) => ({ loaded: img.complete && img.naturalWidth > 0, src: img.currentSrc }));
    ok(name + '线上可读且配图完整', response.status() === 200 && title.includes(name) && hero.loaded && hero.src.includes(id + '-ai-202609'), hero.src);
  }
  await p2.close();

  ok('浏览器控制台无报错', consoleErrors.length === 0, consoleErrors.slice(0, 2).join(' | '));
  ok('页面无未捕获异常', pageErrors.length === 0, pageErrors.slice(0, 2).join(' | '));
} finally {
  await browser.close();
}

const failed = results.filter((r) => !r.pass);
console.log(`\n${results.length - failed.length}/${results.length} 项通过`);
process.exit(failed.length ? 1 : 0);
