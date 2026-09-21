document.addEventListener('DOMContentLoaded', function () {
  var pills = Array.prototype.slice.call(document.querySelectorAll('#resource-categories .category-pill'));
  var cards = Array.prototype.slice.call(document.querySelectorAll('#resource-results .resource-card'));
  var emptyEl = document.getElementById('empty-state');

  function apply(cat) {
    var visible = 0;
    cards.forEach(function (card) {
      var show = cat === 'all' || card.getAttribute('data-category') === cat;
      card.hidden = !show;
      if (show) visible++;
    });
    if (emptyEl) emptyEl.hidden = visible !== 0;
  }

  pills.forEach(function (pill) {
    pill.addEventListener('click', function () {
      pills.forEach(function (p) { p.classList.remove('is-active'); });
      pill.classList.add('is-active');
      apply(pill.getAttribute('data-cat'));
    });
  });
  apply('all');
});