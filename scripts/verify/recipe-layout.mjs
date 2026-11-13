import { chromium } from 'playwright-core';
import { readFile, mkdir } from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
const root = process.cwd();
const output = path.join(root, '_incoming', 'recipe-ui-check');
await mkdir(output, { recursive: true });
const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
try {
  const context = await browser.newContext();
  await context.route('https://recipe-preview.test/**', async route => {
    const pathname = decodeURIComponent(new URL(route.request().url()).pathname);
    const file = path.join(root, pathname === '/' ? 'index.html' : pathname);
    const ext = path.extname(file);
    const mime = { '.html': 'text/html', '.js': 'application/javascript', '.json': 'application/json', '.css': 'text/css', '.webp': 'image/webp', '.jpg': 'image/jpeg', '.png': 'image/png', '.ico': 'image/x-icon' };
    try { await route.fulfill({ body: await readFile(file), contentType: mime[ext] || 'application/octet-stream' }); }
    catch { await route.fulfill({ status: 404, body: '' }); }
  });
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', error => errors.push(String(error)));
  for (const width of [390, 1280]) {
    await page.setViewportSize({ width, height: 900 });
    for (const suffix of ['/r/mapo-tofu.html', '/#/r/mapo-tofu']) {
      await page.goto('https://recipe-preview.test' + suffix);
      const heart = page.locator('[data-favorite-recipe="mapo-tofu"]');
      await heart.waitFor();
      const share = page.locator('summary.share-icon-btn');
      const h = await heart.boundingBox(), s = await share.boundingBox();
      assert(h.x + h.width <= s.x && Math.abs(h.y - s.y) < 2);
      assert(h.width <= 44 && h.height <= 44);
      const before = await heart.getAttribute('aria-pressed');
      await heart.click();
      assert.notEqual(await heart.getAttribute('aria-pressed'), before);
      await page.reload();
      await heart.waitFor();
      assert.notEqual(await heart.getAttribute('aria-pressed'), before);
      assert.equal(await page.locator('.fave-btn').count(), 0);
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
      const buy = page.locator('[data-buy-recipe="mapo-tofu"]');
      assert.equal(await buy.innerText(), '一键购买全部食材');
      // Suppress navigation only; the real delegated click handler still builds the purchase URL.
      await page.evaluate(() => document.addEventListener('click', event => { if (event.target.closest('[data-buy-recipe]')) event.preventDefault(); }));
      await buy.click();
      const url = new URL(await buy.getAttribute('href'));
      assert.equal(url.origin, 'https://easternmarket.ca');
      assert.equal(url.searchParams.get('recipe'), 'mapo-tofu');
      assert.match(url.searchParams.get('recipeRequest'), /^[a-f0-9-]{36}$/);
      await buy.click();
      assert.equal(await buy.getAttribute('href'), url.href);
      await buy.evaluate(el => { el.dataset.activatedAt = '0'; });
      await buy.click();
      assert.notEqual(await buy.getAttribute('href'), url.href, 'a later intentional purchase must get a fresh request');
      await page.screenshot({ path: path.join(output, `${width}-${suffix.includes('#') ? 'spa' : 'static'}.png`), fullPage: true });
      console.log(`PASS ${width}px ${suffix}: heart order, toggle/persistence, layout, purchase request`);
    }
  }
  assert.deepEqual(errors, []);
} finally { await browser.close(); }
