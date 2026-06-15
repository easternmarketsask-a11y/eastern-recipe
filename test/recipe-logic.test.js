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
