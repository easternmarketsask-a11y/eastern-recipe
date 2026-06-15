const test = require('node:test');
const assert = require('node:assert');
const RecipeLogic = require('../src/js/lib/recipe-logic.js');
const recipes = require('../data/_fixtures/recipes.sample.json').recipes;

test('matchRecipes: 中文全名命中', () => {
  const r = RecipeLogic.matchRecipes('麻婆豆腐', recipes);
  assert.equal(r.length, 1);
  assert.equal(r[0].id, 'mapo-tofu');
});

test('matchRecipes: 英文别名忽略大小写', () => {
  assert.equal(RecipeLogic.matchRecipes('MAPO', recipes)[0].id, 'mapo-tofu');
});

test('matchRecipes: 拼音别名命中', () => {
  assert.equal(RecipeLogic.matchRecipes('mapodoufu', recipes)[0].id, 'mapo-tofu');
});

test('matchRecipes: 中文部分词命中', () => {
  assert.equal(RecipeLogic.matchRecipes('豆腐', recipes)[0].id, 'mapo-tofu');
});

test('matchRecipes: 无关词返回空', () => {
  assert.deepEqual(RecipeLogic.matchRecipes('披萨', recipes), []);
});

test('matchRecipes: 空查询返回空', () => {
  assert.deepEqual(RecipeLogic.matchRecipes('   ', recipes), []);
});

const products = require('../data/_fixtures/products.sample.json').items;

test('buildProductIndex: 以 code 建索引', () => {
  const idx = RecipeLogic.buildProductIndex(products);
  assert.equal(idx['4011tofu'].name_cn, '嫩豆腐');
});

test('associateRecipe: 行状态与计数正确', () => {
  const idx = RecipeLogic.buildProductIndex(products);
  const res = RecipeLogic.associateRecipe(recipes[0], idx);
  assert.equal(res.totalCount, 4);
  assert.equal(res.haveCount, 2);
  const byLabel = {};
  res.rows.forEach(function (r) { byLabel[r.label] = r; });
  assert.equal(byLabel['嫩豆腐'].available, true);
  assert.equal(byLabel['小葱'].available, false);
  assert.equal(byLabel['牛肉末'].available, false);
  assert.equal(byLabel['牛肉末'].unbound, true);
});

test('associateRecipe: 参考价只含在售 each 项，称重项单列', () => {
  const idx = RecipeLogic.buildProductIndex(products);
  const res = RecipeLogic.associateRecipe(recipes[0], idx);
  assert.equal(res.refPriceEach, 8.48);
  assert.deepEqual(res.weighed, []);
});

test('associateRecipe: 在售称重食材进 weighed 不进总价', () => {
  const idx = RecipeLogic.buildProductIndex(products);
  const idx2 = JSON.parse(JSON.stringify(idx));
  idx2['greenonion'].on_sale = true;
  const res = RecipeLogic.associateRecipe(recipes[0], idx2);
  assert.equal(res.refPriceEach, 8.48);
  assert.equal(res.weighed.length, 1);
  assert.equal(res.weighed[0].label, '小葱');
  assert.equal(res.weighed[0].price, 1.49);
});
