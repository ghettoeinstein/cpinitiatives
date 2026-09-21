document.addEventListener('DOMContentLoaded', function () {
  var searchInput = document.getElementById('partner-search');
  var catSelect = document.getElementById('filter-category');
  var locSelect = document.getElementById('filter-location');
  var cards = Array.prototype.slice.call(document.querySelectorAll('#partner-results .partner-card'));
  var countEl = document.getElementById('results-count');
  var emptyEl = document.getElementById('empty-state');

  function apply() {
    var q = (searchInput && searchInput.value || '').toLowerCase().trim();
    var cat = catSelect ? catSelect.value : 'all';
    var loc = locSelect ? locSelect.value : 'all';
    var visible = 0;
    cards.forEach(function (card) {
      var name = card.getAttribute('data-name') || '';
      var cats = (card.getAttribute('data-categories') || '').split(',');
      var locs = (card.getAttribute('data-locations') || '').split(',');
      var matchesQ = !q || name.indexOf(q) !== -1;
      var matchesCat = cat === 'all' || cats.indexOf(cat) !== -1;
      var matchesLoc = loc === 'all' || locs.indexOf(loc) !== -1;
      var show = matchesQ && matchesCat && matchesLoc;
      card.hidden = !show;
      if (show) visible++;
    });
    if (countEl) countEl.textContent = visible + (visible === 1 ? ' organization found' : ' organizations found');
    if (emptyEl) emptyEl.hidden = visible !== 0;
  }

  [searchInput, catSelect, locSelect].forEach(function (el) {
    if (el) el.addEventListener('input', apply);
  });

  var params = new URLSearchParams(window.location.search);
  if (params.get('category') && catSelect) catSelect.value = params.get('category');
  apply();
});