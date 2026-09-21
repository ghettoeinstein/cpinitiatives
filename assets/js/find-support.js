document.addEventListener('DOMContentLoaded', function () {
  var searchInput = document.getElementById('partner-search');
  var chips = Array.prototype.slice.call(document.querySelectorAll('#category-chips .chip'));
  var cards = Array.prototype.slice.call(document.querySelectorAll('#partner-results .partner-card'));
  var countEl = document.getElementById('results-count');
  var emptyEl = document.getElementById('empty-state');
  var activeCat = 'all';

  function apply() {
    var q = (searchInput && searchInput.value || '').toLowerCase().trim();
    var visible = 0;
    cards.forEach(function (card) {
      var name = card.getAttribute('data-name') || '';
      var cats = (card.getAttribute('data-categories') || '').split(',');
      var matchesQ = !q || name.indexOf(q) !== -1;
      var matchesCat = activeCat === 'all' || cats.indexOf(activeCat) !== -1;
      var show = matchesQ && matchesCat;
      card.hidden = !show;
      if (show) visible++;
    });
    if (countEl) countEl.textContent = visible + (visible === 1 ? ' organization found' : ' organizations found');
    if (emptyEl) emptyEl.hidden = visible !== 0;
  }

  chips.forEach(function (chip) {
    chip.addEventListener('click', function () {
      chips.forEach(function (c) { c.setAttribute('aria-pressed', 'false'); });
      chip.setAttribute('aria-pressed', 'true');
      activeCat = chip.getAttribute('data-cat');
      apply();
    });
  });
  if (searchInput) searchInput.addEventListener('input', apply);

  var params = new URLSearchParams(window.location.search);
  if (params.get('q') && searchInput) searchInput.value = params.get('q');
  var wantedCat = params.get('category');
  if (wantedCat) {
    var match = chips.filter(function (c) { return c.getAttribute('data-cat') === wantedCat; })[0];
    if (match) match.click();
  }
  apply();
});