document.addEventListener('DOMContentLoaded', function () {
  var supportSelect = document.getElementById('filter-support');
  var cards = Array.prototype.slice.call(document.querySelectorAll('#need-results .need-card'));
  var countEl = document.getElementById('results-count');
  var emptyEl = document.getElementById('empty-state');

  function apply() {
    var support = supportSelect ? supportSelect.value : 'all';
    var visible = 0;
    cards.forEach(function (card) {
      var show = support === 'all' || card.getAttribute('data-support') === support;
      card.hidden = !show;
      if (show) visible++;
    });
    if (countEl) countEl.textContent = visible + (visible === 1 ? ' open need' : ' open needs');
    if (emptyEl) emptyEl.hidden = visible !== 0;
  }

  if (supportSelect) supportSelect.addEventListener('change', apply);
  apply();
});