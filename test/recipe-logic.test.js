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

test('dishesForIngredient: 按食材 label 命中菜', () => {
  const idx = RecipeLogic.buildProductIndex(products);
  const r = RecipeLogic.dishesForIngredient('豆腐', recipes, idx);
  assert.equal(r.length, 1);
  assert.equal(r[0].id, 'mapo-tofu');
});

test('dishesForIngredient: 按绑定商品英文名命中', () => {
  const idx = RecipeLogic.buildProductIndex(products);
  const r = RecipeLogic.dishesForIngredient('bean paste', recipes, idx);
  assert.equal(r[0].id, 'mapo-tofu');
});

test('dishesForIngredient: 无关食材返回空', () => {
  const idx = RecipeLogic.buildProductIndex(products);
  assert.deepEqual(RecipeLogic.dishesForIngredient('三文鱼', recipes, idx), []);
});

test('todaysPicks: 同 seed 确定、数量受限', () => {
  const a = RecipeLogic.todaysPicks(recipes, '2026-06-14', 1);
  const b = RecipeLogic.todaysPicks(recipes, '2026-06-14', 1);
  assert.deepEqual(a.map(x => x.id), b.map(x => x.id));
  assert.equal(a.length, 1);
});

test('todaysPicks: n 超过总数时返回全部、不重复', () => {
  const a = RecipeLogic.todaysPicks(recipes, 'seed-x', 99);
  assert.equal(a.length, recipes.length);
  assert.equal(new Set(a.map(x => x.id)).size, recipes.length);
});

test('todaysPicks: 不同 seed 轮换（多菜时子集不同）', () => {
  const many = ['a','b','c','d','e'].map(id => ({ id: id, name_cn: id, ingredients: [] }));
  const s1 = RecipeLogic.todaysPicks(many, 'day-1', 2).map(x => x.id).join(',');
  const s2 = RecipeLogic.todaysPicks(many, 'day-2', 2).map(x => x.id).join(',');
  assert.notEqual(s1, s2);
});
