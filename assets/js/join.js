document.addEventListener('DOMContentLoaded', function () {
  var form = document.getElementById('join-form');
  if (!form) return;
  var panels = Array.prototype.slice.call(form.querySelectorAll('.wizard-panel[data-panel]'));
  var dots = Array.prototype.slice.call(document.querySelectorAll('[data-step-dot]'));
  var backBtn = document.querySelector('[data-wizard-back]');
  var nextBtn = document.querySelector('[data-wizard-next]');
  var submitBtn = document.querySelector('[data-wizard-submit]');
  var actions = document.querySelector('[data-wizard-actions]');
  var totalSteps = dots.length; // 0..totalSteps-1 are form steps
  var current = 0;

  function panelFor(index) {
    return panels.filter(function (p) { return p.getAttribute('data-panel') === String(index); })[0];
  }

  function showStep(index) {
    panels.forEach(function (p) { p.classList.remove('is-active'); });
    var panel = panelFor(index);
    if (panel) panel.classList.add('is-active');
    dots.forEach(function (dot, i) {
      dot.classList.toggle('is-active', i === index);
      dot.classList.toggle('is-done', i < index);
    });
    backBtn.disabled = index === 0;
    nextBtn.hidden = index === totalSteps - 1;
    submitBtn.hidden = index !== totalSteps - 1;
    if (index === totalSteps - 1) renderReview();
  }

  function fieldsInStep(index) {
    var panel = panelFor(index);
    return panel ? Array.prototype.slice.call(panel.querySelectorAll('input, textarea')) : [];
  }

  function validateStep(index) {
    var valid = true;
    if (index === 4) {
      var checked = form.querySelectorAll('input[name="participation"]:checked');
      var err = document.getElementById('participation-error');
      if (checked.length === 0) {
        valid = false;
        if (err) err.style.display = 'block';
      } else if (err) {
        err.style.display = 'none';
      }
      return valid;
    }
    fieldsInStep(index).forEach(function (field) {
      var wrapper = field.closest('.field');
      if (field.hasAttribute('required') && !field.value.trim()) {
        valid = false;
        if (wrapper) wrapper.classList.add('has-error');
      } else if (wrapper) {
        wrapper.classList.remove('has-error');
      }
    });
    return valid;
  }

  function renderReview() {
    var summary = document.getElementById('review-summary');
    if (!summary) return;
    var data = collectData();
    var rows = [
      ['Organization', data.org_name],
      ['Website', data.website || '—'],
      ['Contact', data.contact_name + ' (' + data.email + ')'],
      ['Services', data.services],
      ['Population Served', data.population],
      ['Geography', data.geography],
      ['Participation', data.participation.join(', ')],
    ];
    summary.innerHTML = rows.map(function (r) {
      return '<div class="kv-row"><span class="k">' + r[0] + '</span><span class="v">' + escapeHtml(r[1]) + '</span></div>';
    }).join('');
  }

  function escapeHtml(str) {
    var div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  function collectData() {
    var fd = new FormData(form);
    return {
      org_name: fd.get('org_name') || '',
      website: fd.get('website') || '',
      contact_name: fd.get('contact_name') || '',
      email: fd.get('email') || '',
      phone: fd.get('phone') || '',
      services: fd.get('services') || '',
      population: fd.get('population') || '',
      geography: fd.get('geography') || '',
      participation: fd.getAll('participation'),
    };
  }

  nextBtn.addEventListener('click', function () {
    if (!validateStep(current)) return;
    current = Math.min(current + 1, totalSteps - 1);
    showStep(current);
  });
  backBtn.addEventListener('click', function () {
    current = Math.max(current - 1, 0);
    showStep(current);
  });

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    if (!validateStep(current)) return;
    var data = collectData();
    var appId = 'CPI-APP-' + new Date().getFullYear() + '-' + Math.floor(1000 + Math.random() * 9000);
    var idEl = document.getElementById('application-id');
    if (idEl) idEl.textContent = appId;

    var bodyLines = [
      'New CPI Partner Application (' + appId + ')',
      '',
      'Organization: ' + data.org_name,
      'Website: ' + data.website,
      'Contact: ' + data.contact_name,
      'Email: ' + data.email,
      'Phone: ' + data.phone,
      'Services: ' + data.services,
      'Population Served: ' + data.population,
      'Geography: ' + data.geography,
      'Participation: ' + data.participation.join(', '),
    ];
    var mailto = 'mailto:partners@cpinitiatives.org?subject=' +
      encodeURIComponent('CPI Partner Application - ' + data.org_name) +
      '&body=' + encodeURIComponent(bodyLines.join('\n'));
    var emailBtn = document.getElementById('email-application-btn');
    if (emailBtn) emailBtn.setAttribute('href', mailto);

    panels.forEach(function (p) { p.classList.remove('is-active'); });
    panelFor('confirmation').classList.add('is-active');
    if (actions) actions.hidden = true;
    window.scrollTo({ top: 0, behavior: 'smooth' });
    window.location.href = mailto;
  });

  showStep(0);
});