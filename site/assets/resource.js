(function () {
  'use strict';

  var grid = document.getElementById('grid');
  var countEl = document.getElementById('count');
  var emptyEl = document.getElementById('empty');
  var searchEl = document.getElementById('search');
  var chipsEl = document.getElementById('chips');
  var DATA = [];
  var activeCat = '全部';

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c];
    });
  }

  function tagClass(text) {
    if (/免费|全免费|公益/.test(text) && !/付费|部分|学币/.test(text)) return 'tag free';
    if (/付费|部分|学币|商用|授权/.test(text)) return 'tag warn';
    return 'tag';
  }

  function shortUrl(url) {
    try {
      var u = new URL(url);
      return u.hostname.replace(/^www\./, '') + (u.pathname !== '/' ? u.pathname : '');
    } catch (e) { return url; }
  }

  function render() {
    var q = (searchEl.value || '').trim().toLowerCase();
    var rows = DATA.filter(function (d) {
      var catOK = activeCat === '全部' || d.cat === activeCat;
      var hay = [d.name, d.scope, d.desc, d.note, d.sub, d.access].join(' ').toLowerCase();
      return catOK && (!q || hay.indexOf(q) !== -1);
    });
    countEl.textContent = '显示 ' + rows.length + ' / ' + DATA.length + ' 项';
    emptyEl.hidden = rows.length > 0;
    grid.innerHTML = rows.map(function (d) {
      return '<article class="card">' +
        '<div class="tags">' +
          '<span class="tag">' + esc(d.cat) + (d.sub ? ' · ' + esc(d.sub) : '') + '</span>' +
          '<span class="' + tagClass(d.access) + '">' + esc(d.access) + '</span>' +
        '</div>' +
        '<h3>' + esc(d.name) + '</h3>' +
        '<p class="scope">' + esc(d.scope) + '</p>' +
        '<p class="desc">' + esc(d.desc) + '</p>' +
        '<div class="note">' + esc(d.note) + '</div>' +
        '<a class="card-link" href="' + esc(d.link) + '" target="_blank" rel="noopener noreferrer">打开 ' + esc(shortUrl(d.link)) + ' ↗</a>' +
      '</article>';
    }).join('');
  }

  chipsEl.addEventListener('click', function (e) {
    var btn = e.target.closest('.chip');
    if (!btn) return;
    activeCat = btn.dataset.cat;
    Array.prototype.forEach.call(chipsEl.querySelectorAll('.chip'), function (c) {
      c.classList.toggle('active', c === btn);
    });
    render();
  });
  searchEl.addEventListener('input', render);

  fetch('./data/resources.json')
    .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
    .then(function (data) {
      DATA = data;
      render();
    })
    .catch(function (err) {
      countEl.textContent = '目录载入失败：' + err.message;
      emptyEl.hidden = false;
      emptyEl.textContent = '请检查 data/resources.json 是否已生成。';
    });
})();
