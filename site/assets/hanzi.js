(function () {
  'use strict';

  var input = document.getElementById('char-input');
  var loadBtn = document.getElementById('load-char');
  var target = document.getElementById('character-target');
  var titleEl = document.getElementById('char-title');
  var pinyinEl = document.getElementById('char-pinyin');
  var strokeEl = document.getElementById('stroke-count');
  var radicalEl = document.getElementById('radical-strokes');
  var fileEl = document.getElementById('data-file');
  var statusEl = document.getElementById('char-status');
  var quickEl = document.getElementById('quick-chars');

  var writer = null;
  var outlineVisible = true;
  var currentChar = '';

  var QUICK = ('永 人 口 手 水 火 木 金 土 日 月 山 川 田 目 耳 心 大 小 上 下 中 天 地 雨 云 风 花 草 鸟 鱼 马 牛 羊 犬 刀 尺 弓 车 舟 门 户 书 文 字 学 生 老 师 父 母 子 女 春 夏 秋 冬 东 南 西 北 红 黄 蓝 白 黑 一 二 三 四 五 六 七 八 九 十').split(' ');

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c];
    });
  }

  function setStatus(msg, isError) {
    statusEl.textContent = msg;
    statusEl.style.color = isError ? 'var(--ochre)' : 'var(--muted)';
  }

  function dataUrl(ch) {
    return '../data/hanzi/' + encodeURIComponent(ch) + '.json';
  }

  function loadChar(ch) {
    ch = Array.from(String(ch || '').trim())[0] || '';
    if (!ch) return;
    currentChar = ch;
    input.value = ch;
    titleEl.textContent = ch;
    pinyinEl.textContent = '';
    strokeEl.textContent = '—';
    radicalEl.textContent = '—';
    fileEl.textContent = dataUrl(ch);
    setStatus('正在载入 ' + ch + ' 的笔顺数据……', false);

    if (writer && writer.cancelQuiz) {
      try { writer.cancelQuiz(); } catch (e) { /* ignore */ }
    }
    target.innerHTML = '';

    fetch(dataUrl(ch))
      .then(function (r) {
        if (!r.ok) throw new Error('没有这个字的数据');
        return r.json();
      })
      .then(function (data) {
        strokeEl.textContent = String((data.strokes || []).length);
        radicalEl.textContent = String((data.radStrokes || []).length) + ' 笔';
        try {
          pinyinEl.textContent = window.pinyinPro ? window.pinyinPro.pinyin(ch, { toneType: 'symbol' }) : '';
        } catch (e) { pinyinEl.textContent = ''; }
        setStatus('已载入。点“播放笔顺”看动画，或点“描红练习”跟着写。', false);

        writer = HanziWriter.create('character-target', ch, {
          width: 340,
          height: 340,
          padding: 18,
          showOutline: true,
          strokeColor: '#1d211e',
          radicalColor: '#0f6e62',
          highlightColor: '#a2582a',
          strokeAnimationSpeed: 1.1,
          delayBetweenStrokes: 90,
          charDataLoader: function (c, onComplete, onError) {
            fetch(dataUrl(c)).then(function (r) {
              if (!r.ok) throw new Error('missing');
              return r.json();
            }).then(onComplete).catch(onError);
          }
        });
        outlineVisible = true;
        writer.animateCharacter();
      })
      .catch(function (err) {
        setStatus('查不到“' + ch + '”的笔顺数据：' + err.message + '。可以换一个常用字试试。', true);
        strokeEl.textContent = '—';
        radicalEl.textContent = '—';
      });

    if (history.replaceState) history.replaceState(null, '', '#' + encodeURIComponent(ch));
  }

  document.getElementById('play').addEventListener('click', function () {
    if (writer) writer.animateCharacter();
  });

  document.getElementById('quiz').addEventListener('click', function () {
    if (!writer) return;
    writer.cancelQuiz();
    writer.quiz({
      onMistake: function (strokeData) {
        setStatus('这一笔写错了，正确起笔在第 ' + (strokeData.strokeNum + 1) + ' 笔。', true);
      },
      onComplete: function () {
        setStatus('写完了，笔顺正确。', false);
      }
    });
  });

  document.getElementById('outline').addEventListener('click', function () {
    if (!writer) return;
    outlineVisible = !outlineVisible;
    if (outlineVisible) writer.showOutline(); else writer.hideOutline();
  });

  document.getElementById('reset').addEventListener('click', function () {
    if (!writer) return;
    writer.cancelQuiz();
    writer.showCharacter();
    writer.showOutline();
    outlineVisible = true;
  });

  loadBtn.addEventListener('click', function () { loadChar(input.value); });
  input.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') { e.preventDefault(); loadChar(input.value); }
  });
  input.addEventListener('input', function () {
    var chars = Array.from(input.value.trim());
    if (chars.length > 1) input.value = chars[0];
  });

  quickEl.innerHTML = QUICK.map(function (c) {
    return '<button class="quick-char" data-char="' + esc(c) + '" title="' + esc(c) + '">' + esc(c) + '</button>';
  }).join('');
  quickEl.addEventListener('click', function (e) {
    var btn = e.target.closest('.quick-char');
    if (btn) loadChar(btn.dataset.char);
  });

  var hash = '';
  try { hash = decodeURIComponent(location.hash.slice(1)); } catch (e) { hash = ''; }
  loadChar(hash || '永');
})();
