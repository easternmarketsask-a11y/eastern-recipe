import assert from 'node:assert/strict';
import { chromium } from 'playwright-core';
import { existsSync } from 'node:fs';

const base = process.env.EM_BASE || 'http://127.0.0.1:8099';
const executablePath = [process.env.EM_BROWSER, 'C:/Program Files/Google/Chrome/Application/chrome.exe', 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe', '/usr/bin/google-chrome', '/usr/bin/chromium'].find(p => p && existsSync(p));
if (!executablePath) throw new Error('Set EM_BROWSER to a Chrome or Edge executable');
const browser = await chromium.launch({ executablePath, headless: true });
try {
  for (const width of [390, 1280]) {
    const page = await browser.newPage({ viewport: { width, height: 844 } });
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.goto(base);
    await page.locator('#soup .card').first().waitFor();
    const outside = await page.locator('main .block').evaluateAll(blocks => blocks.filter(block => !block.closest('#home') && !block.closest('#detail') && !block.closest('#results')).map(block => block.id));
    assert.deepEqual(outside, [], 'home blocks must hide together when opening a recipe');
    for (const id of ['lotus-pork-bone-soup', 'gai-lan-oyster-sauce', 'hotpot']) {
      await page.locator(`#home [data-id="${id}"]`).first().click();
      await page.locator('#detail:not([hidden]) .detail__title').waitFor();
      assert.equal(await page.locator('#soupBlock').isVisible(), false, 'homepage must not cover the recipe');
      assert.ok(await page.locator('#detail').evaluate(el => el.getBoundingClientRect().top) < 200, 'recipe must open near the top, not below the homepage');
      await page.locator('#back').click();
      await page.locator('#soupBlock').waitFor();
    }
    await page.locator('#soupBlock .seeall').click();
    await page.locator('#results:not([hidden]) .card').first().waitFor();
    assert.equal(await page.locator('#soupBlock').isVisible(), false, 'category hides homepage');
    await page.locator('#secback').click();
    await page.locator('#soupBlock').waitFor();
    await page.locator('#q').fill('麻婆豆腐');
    await page.locator('#results:not([hidden]) .card').first().waitFor();
    assert.equal(await page.locator('#soupBlock').isVisible(), false, 'search hides homepage');
    await page.locator('#results .card').first().click();
    await page.locator('#detail:not([hidden]) .detail__title').waitFor();
    assert.deepEqual(errors, []);
    await page.close();
    console.log(`Recipe navigation passed at ${width}px: homepage, three recipes, back, category, search and detail position.`);
  }
} finally {
  await browser.close();
}
