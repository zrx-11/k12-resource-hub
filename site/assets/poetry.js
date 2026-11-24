(function () {
  'use strict';

  var listEl = document.getElementById('poem-list');
  var readerEl = document.getElementById('poem-reader');
  var searchEl = document.getElementById('poem-search');
  var catListEl = document.getElementById('cat-list');
  var countEl = document.getElementById('poem-count');

  var POEMS = [];
  var activeCat = '全部';
  var currentId = null;

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c];
    });
  }

  function filtered() {
    var q = (searchEl.value || '').trim().toLowerCase();
    return POEMS.filter(function (p) {
      if (activeCat !== '全部' && p.cat !== activeCat) return false;
      if (!q) return true;
      var hay = [p.title, p.author, p.dynasty].concat(p.paragraphs || []).join(' ').toLowerCase();
      return hay.indexOf(q) !== -1;
    });
  }

  function renderList() {
    var rows = filtered();
    if (!rows.length) {
      listEl.innerHTML = '<div class="empty">没有匹配的诗文。</div>';
      return;
    }
    listEl.innerHTML = rows.map(function (p) {
      return '<button class="poem-item' + (p.id === currentId ? ' active' : '') + '" data-id="' + esc(p.id) + '">' +
        '<strong>' + esc(p.title) + '</strong>' +
        '<span>' + esc([p.dynasty, p.author].filter(Boolean).join(' · ')) + '</span>' +
      '</button>';
    }).join('');
  }

  function renderReader(p) {
    if (!p) {
      readerEl.innerHTML = '<p class="poem-by">没有可显示的内容。</p>';
      return;
    }
    var body = (p.paragraphs || []).map(function (line) { return '<p>' + esc(line) + '</p>'; }).join('');
    readerEl.innerHTML =
      '<h2 class="poem-title">' + esc(p.title) + '</h2>' +
      '<p class="poem-by">' + esc([p.dynasty, p.author].filter(Boolean).join(' · ') || '佚名') + '</p>' +
      '<div class="poem-body">' + body + '</div>' +
      (p.note ? '<p class="poem-note">' + esc(p.note) + '</p>' : '') +
      '<div class="poem-actions">' +
        '<button class="ghost-btn" id="copy-poem">复制全文</button>' +
        '<button class="ghost-btn" id="random-poem">随机一篇</button>' +
        '<button class="ghost-btn" id="prev-poem">上一篇</button>' +
        '<button class="ghost-btn" id="next-poem">下一篇</button>' +
      '</div>';

    document.getElementById('copy-poem').addEventListener('click', function () {
      var text = p.title + '\n' + ([p.dynasty, p.author].filter(Boolean).join('·')) + '\n\n' + (p.paragraphs || []).join('\n');
      copyText(text);
    });
    document.getElementById('random-poem').addEventListener('click', function () {
      var rows = filtered();
      if (!rows.length) return;
      select(rows[Math.floor(Math.random() * rows.length)].id, true);
    });
    document.getElementById('prev-poem').addEventListener('click', function () { step(-1); });
    document.getElementById('next-poem').addEventListener('click', function () { step(1); });
  }

  function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () { toast('已复制'); }).catch(function () { fallbackCopy(text); });
    } else { fallbackCopy(text); }
  }

  function fallbackCopy(text) {
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand('copy'); toast('已复制'); } catch (e) { toast('复制失败，请手动选择'); }
    document.body.removeChild(ta);
  }

  function toast(msg) {
    var t = document.createElement('div');
    t.textContent = msg;
    t.style.cssText = 'position:fixed;left:50%;bottom:28px;transform:translateX(-50%);background:#1d211e;color:#fff;padding:8px 14px;border-radius:999px;font-size:13px;z-index:99;opacity:.95';
    document.body.appendChild(t);
    setTimeout(function () { t.remove(); }, 1600);
  }

  function select(id, scroll) {
    var p = POEMS.find(function (x) { return x.id === id; });
    if (!p) return;
    currentId = id;
    if (history.replaceState) history.replaceState(null, '', '#p-' + encodeURIComponent(id));
    renderReader(p);
    renderList();
    if (scroll) {
      readerEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  function step(delta) {
    var rows = filtered();
    if (!rows.length) return;
    var idx = rows.findIndex(function (x) { return x.id === currentId; });
    if (idx === -1) idx = 0;
    var next = rows[(idx + delta + rows.length) % rows.length];
    select(next.id, true);
  }

  listEl.addEventListener('click', function (e) {
    var btn = e.target.closest('.poem-item');
    if (!btn) return;
    select(btn.dataset.id, false);
  });

  searchEl.addEventListener('input', function () {
    renderList();
    var rows = filtered();
    if (rows.length && !rows.some(function (x) { return x.id === currentId; })) {
      select(rows[0].id, false);
    }
  });

  catListEl.addEventListener('click', function (e) {
    var btn = e.target.closest('.cat-btn');
    if (!btn) return;
    activeCat = btn.dataset.cat;
    Array.prototype.forEach.call(catListEl.querySelectorAll('.cat-btn'), function (b) {
      b.classList.toggle('active', b === btn);
    });
    var rows = filtered();
    renderList();
    if (rows.length) select(rows[0].id, false);
  });

  fetch('../data/poetry.json')
    .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
    .then(function (data) {
      POEMS = data.poems || [];
      countEl.textContent = String(POEMS.length);
      var id = null;
      if (location.hash.indexOf('#p-') === 0) {
        try { id = decodeURIComponent(location.hash.slice(3)); } catch (e) { id = null; }
      }
      var first = POEMS.find(function (x) { return x.id === id; }) || POEMS[0];
      if (first) select(first.id, false);
      renderList();
    })
    .catch(function (err) {
      readerEl.innerHTML = '<p class="poem-by">诗词数据载入失败：' + esc(err.message) + '</p>';
    });
})();
