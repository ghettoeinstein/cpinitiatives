document.addEventListener('DOMContentLoaded', function () {
  var catSelect = document.getElementById('filter-category');
  var statusSelect = document.getElementById('filter-status');
  var locSelect = document.getElementById('filter-location');
  var needSelect = document.getElementById('filter-need');
  var cards = Array.prototype.slice.call(document.querySelectorAll('#initiative-results .initiative-card'));
  var countEl = document.getElementById('results-count');
  var emptyEl = document.getElementById('empty-state');

  function apply() {
    var cat = catSelect ? catSelect.value : 'all';
    var status = statusSelect ? statusSelect.value : 'all';
    var loc = locSelect ? locSelect.value : 'all';
    var need = needSelect ? needSelect.value : 'all';
    var visible = 0;
    cards.forEach(function (card) {
      var locs = (card.getAttribute('data-locations') || '').split(',');
      var needs = (card.getAttribute('data-needs') || '').split('|');
      var matchesCat = cat === 'all' || card.getAttribute('data-category') === cat;
      var matchesStatus = status === 'all' || card.getAttribute('data-status') === status;
      var matchesLoc = loc === 'all' || locs.indexOf(loc) !== -1;
      var matchesNeed = need === 'all' || needs.indexOf(need) !== -1;
      var show = matchesCat && matchesStatus && matchesLoc && matchesNeed;
      card.hidden = !show;
      if (show) visible++;
    });
    if (countEl) countEl.textContent = visible + (visible === 1 ? ' initiative found' : ' initiatives found');
    if (emptyEl) emptyEl.hidden = visible !== 0;
  }

  [catSelect, statusSelect, locSelect, needSelect].forEach(function (el) {
    if (el) el.addEventListener('change', apply);
  });
  apply();
});