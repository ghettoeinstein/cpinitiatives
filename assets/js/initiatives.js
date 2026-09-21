document.addEventListener('DOMContentLoaded', function () {
  var catSelect = document.getElementById('filter-category');
  var statusSelect = document.getElementById('filter-status');
  var cards = Array.prototype.slice.call(document.querySelectorAll('#initiative-results .initiative-card'));
  var countEl = document.getElementById('results-count');
  var emptyEl = document.getElementById('empty-state');

  function apply() {
    var cat = catSelect ? catSelect.value : 'all';
    var status = statusSelect ? statusSelect.value : 'all';
    var visible = 0;
    cards.forEach(function (card) {
      var matchesCat = cat === 'all' || card.getAttribute('data-category') === cat;
      var matchesStatus = status === 'all' || card.getAttribute('data-status') === status;
      var show = matchesCat && matchesStatus;
      card.hidden = !show;
      if (show) visible++;
    });
    if (countEl) countEl.textContent = visible + (visible === 1 ? ' initiative found' : ' initiatives found');
    if (emptyEl) emptyEl.hidden = visible !== 0;
  }

  [catSelect, statusSelect].forEach(function (el) {
    if (el) el.addEventListener('change', apply);
  });
  apply();
});