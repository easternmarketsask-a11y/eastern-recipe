document.addEventListener('click', async function (event) {
  var button = event.target.closest('[data-copy-recipe]');
  if (!button) return;
  var url = button.dataset.copyRecipe;
  var status = button.parentElement.querySelector('[role="status"]');
  try {
    await navigator.clipboard.writeText(url);
    status.textContent = '已复制链接';
  } catch (error) {
    var input = document.createElement('input');
    input.type = 'url';
    input.readOnly = true;
    input.value = url;
    input.setAttribute('aria-label', '食谱链接');
    status.textContent = '请选择并复制链接';
    status.appendChild(input);
    input.focus();
    input.select();
  }
});
