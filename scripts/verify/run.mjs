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
page.on('console', (m) => { if (m.type() === 'error' && !NOISE.test(m.text())) consoleErrors.push(m.text()); });
page.on('pageerror', (e) => pageErrors.push(String(e)));

try {
  // ── 首页 ────────────────────────────────────────────────────────────────
  await page.goto(BASE + '/', { waitUntil: 'networkidle' });
  await page.waitForSelector('#season .card', { timeout: 15000 });

  const seasonVisible = await page.isVisible('#seasonBlock');
  ok('首页出现「中秋 · 应季」板块', seasonVisible);

  // setupLoop 会把卡片复制三份做无缝循环，所以按 data-id 去重才是真实菜数
  const seasonIds = await page.$$eval('#season .card', (els) =>
    [...new Set(els.map((e) => e.dataset.id))]);
  ok('中秋板块有 6 道菜', seasonIds.length === 6, seasonIds.join(', '));

  const firstBlock = await page.$eval('.home .block .block__title', (e) => e.textContent.trim());
  ok('中秋板块排在首页第一位', firstBlock.includes('中秋'), firstBlock);

  const usesWebp = await page.$eval('#season picture source',
    (s) => s.getAttribute('srcset') || '');
  ok('卡片图走 WebP', /\/webp\/.*-400\.webp$/.test(usesWebp), usesWebp);

  // 横滑行里没滚到的图是懒加载，本来就不该加载；要抓的是「加载失败」：
  // complete 且 naturalWidth===0 才是坏图。
  const brokenImgs = await page.$$eval('#season img', (els) =>
    els.filter((i) => i.complete && i.naturalWidth === 0).map((i) => i.currentSrc || i.src));
  ok('中秋板块没有加载失败的图', brokenImgs.length === 0, brokenImgs.slice(0, 2).join(' '));

  // ── 详情页 ──────────────────────────────────────────────────────────────
  await page.click('#season .card[data-id="lotus-pork-bone-soup"]');
  await page.waitForSelector('#detail:not([hidden])', { timeout: 10000 });
  const title = await page.$eval('.detail__title', (e) => e.textContent.trim());
  ok('点卡片能打开详情页', title.includes('莲藕筒骨汤'), title);

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
  await page.waitForSelector('#results .card', { timeout: 10000 });
  const hits = await page.$$eval('#results .card__name', (e) => e.map((x) => x.textContent.trim()));
  ok('搜「月饼」能搜到', hits.some((t) => t.includes('月饼')), hits.slice(0, 3).join('、'));

  await page.fill('#q', '莲藕');
  await page.waitForSelector('#results .card', { timeout: 10000 });
  const byIng = await page.$$eval('#results .card__name', (e) => e.map((x) => x.textContent.trim()));
  ok('搜食材「莲藕」能反查到菜', byIng.length >= 2, byIng.slice(0, 4).join('、'));

  // ── 静态 SEO 页 ─────────────────────────────────────────────────────────
  const p2 = await ctx.newPage();
  const resp = await p2.goto(BASE + '/r/mooncake-ready.html', { waitUntil: 'domcontentloaded' });
  ok('静态菜页返回 200', resp.status() === 200, String(resp.status()));
  const h1 = await p2.$eval('h1', (e) => e.textContent.trim());
  ok('静态菜页有 h1 菜名', h1.includes('月饼'), h1);
  const ld = await p2.$eval('script[type="application/ld+json"]', (e) => JSON.parse(e.textContent));
  ok('静态菜页带 Recipe 结构化数据', ld['@type'] === 'Recipe' && ld.name.includes('月饼'));
  ok('结构化数据含做法步骤', Array.isArray(ld.recipeInstructions) && ld.recipeInstructions.length > 0,
    ld.recipeInstructions.length + ' 步');
  const canon = await p2.$eval('link[rel=canonical]', (e) => e.href);
  ok('静态菜页有 canonical', /\/r\/mooncake-ready\.html$/.test(canon), canon);
  // 真的把 JS 关掉再读一遍 —— 爬虫看到的就是这个
  const noJsCtx = await browser.newContext({ javaScriptEnabled: false });
  const noJs = await noJsCtx.newPage();
  await noJs.goto(BASE + '/r/mooncake-ready.html', { waitUntil: 'domcontentloaded' });
  const stepsText = await noJs.$$eval('.steps li', (e) => e.map((x) => x.textContent.trim()));
  const ingText = await noJs.$$eval('.ing__name', (e) => e.map((x) => x.textContent.trim()));
  ok('关掉 JS 后做法照样在页面上', stepsText.length > 0, stepsText.length + ' 步');
  ok('关掉 JS 后食材照样在页面上', ingText.length > 0, ingText.join('、').slice(0, 30));
  await noJsCtx.close();

  const idx = await p2.goto(BASE + '/r/', { waitUntil: 'domcontentloaded' });
  ok('全部食谱目录页返回 200', idx.status() === 200);
  const links = await p2.$$eval('.pg-seclist a', (e) => e.length);
  ok('目录页链出全部 79 道菜', links === 79, links + ' 条');
  await p2.close();

  ok('浏览器控制台无报错', consoleErrors.length === 0, consoleErrors.slice(0, 2).join(' | '));
  ok('页面无未捕获异常', pageErrors.length === 0, pageErrors.slice(0, 2).join(' | '));
} finally {
  await browser.close();
}

const failed = results.filter((r) => !r.pass);
console.log(`\n${results.length - failed.length}/${results.length} 项通过`);
process.exit(failed.length ? 1 : 0);
