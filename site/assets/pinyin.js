(function () {
  'use strict';

  var input = document.getElementById('pinyin-input');
  var output = document.getElementById('pinyin-output');
  var tableBody = document.querySelector('#pinyin-table tbody');
  var multipleEl = document.getElementById('multiple');
  var examplesEl = document.getElementById('examples');

  var INITIALS = ['zh', 'ch', 'sh', 'b', 'p', 'm', 'f', 'd', 't', 'n', 'l', 'g', 'k', 'h', 'j', 'q', 'x', 'r', 'z', 'c', 's', 'y', 'w'];

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c];
    });
  }

  function toneType() {
    var checked = document.querySelector('input[name="tone"]:checked');
    return checked ? checked.value : 'symbol';
  }

  function isHan(ch) {
    return /[\u3400-\u9fff\uf900-\ufaff]/.test(ch);
  }

  function splitInitial(py) {
    if (!py) return { initial: '', final: '' };
    for (var i = 0; i < INITIALS.length; i++) {
      var ini = INITIALS[i];
      if (py.indexOf(ini) === 0) {
        return { initial: ini, final: py.slice(ini.length) };
      }
    }
    return { initial: '', final: py };
  }

  function convert() {
    var text = input.value || '';
    if (!window.pinyinPro) {
      output.textContent = '拼音库未载入。';
      return;
    }
    var opts = { toneType: toneType(), multiple: multipleEl.checked };
    var arr = window.pinyinPro.pinyin(text, Object.assign({ type: 'array' }, opts));
    output.textContent = arr.join(' ');

    var chars = Array.from(text);
    var aligned = arr.length === chars.length ? arr : null;
    var rows = [];
    for (var i = 0; i < chars.length; i++) {
      var ch = chars[i];
      if (!isHan(ch)) continue;
      var py = (aligned && aligned[i]) || window.pinyinPro.pinyin(ch, Object.assign({ type: 'array', multiple: true }, opts))[0] || '';
      var parts = splitInitial(py);
      rows.push('<tr><td>' + esc(ch) + '</td><td>' + esc(py) + '</td><td>' + esc(parts.initial || '—') + '</td><td>' + esc(parts.final || '—') + '</td></tr>');
    }
    tableBody.innerHTML = rows.length ? rows.join('') : '<tr><td colspan="4" style="color:var(--muted)">没有可标注的汉字</td></tr>';
  }

  document.getElementById('convert').addEventListener('click', convert);
  document.getElementById('copy-pinyin').addEventListener('click', function () {
    var text = output.textContent || '';
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () {
        document.getElementById('copy-pinyin').textContent = '已复制';
        setTimeout(function () { document.getElementById('copy-pinyin').textContent = '复制结果'; }, 1400);
      });
    }
  });

  Array.prototype.forEach.call(document.querySelectorAll('input[name="tone"]'), function (r) {
    r.addEventListener('change', convert);
  });
  multipleEl.addEventListener('change', convert);
  input.addEventListener('input', convert);

  examplesEl.addEventListener('click', function (e) {
    var btn = e.target.closest('button[data-text]');
    if (!btn) return;
    input.value = btn.dataset.text;
    convert();
  });

  convert();
})();
