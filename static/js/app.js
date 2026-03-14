import { MixVisit } from '/static/js/mixvisit.js';

// ── Theme toggle ──
let dark = document.documentElement.getAttribute('data-theme') !== 'light';
const savedTheme = localStorage.getItem('theme');
if (savedTheme) {
  dark = savedTheme === 'dark';
  document.documentElement.setAttribute('data-theme', savedTheme);
}
const themeBtn = document.getElementById('themeBtn');
themeBtn.textContent = dark ? '🌙' : '☀️';
themeBtn.addEventListener('click', () => {
  dark = !dark;
  const t = dark ? 'dark' : 'light';
  document.documentElement.setAttribute('data-theme', t);
  localStorage.setItem('theme', t);
  themeBtn.textContent = dark ? '🌙' : '☀️';
});

// ── Syntax highlight ──
function highlight(obj) {
  return JSON.stringify(obj, null, 2).replace(
    /("(?:\\.|[^"\\])*"(?=\s*:)|"(?:\\.|[^"\\])*"|\b(true|false|null)\b|-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)/g,
    m => {
      if (/^".*":\s*$/.test(m + ' ')) return `<span class="jk">${m}</span>`;
      if (/".*":/.test(m))            return `<span class="jk">${m}</span>`;
      if (/^"/.test(m))               return `<span class="js">${m}</span>`;
      if (/true|false/.test(m))       return `<span class="jb">${m}</span>`;
      return `<span class="jn">${m}</span>`;
    }
  );
}

// ── Copy button ──
let rawData = '';
const copyBtn = document.getElementById('copyBtn');
const COPY_HTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg> Copy`;
const CHECK_HTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg> Copied!`;

copyBtn.addEventListener('click', async () => {
  await navigator.clipboard.writeText(rawData);
  copyBtn.classList.add('copied');
  copyBtn.innerHTML = CHECK_HTML;
  setTimeout(() => { copyBtn.classList.remove('copied'); copyBtn.innerHTML = COPY_HTML; }, 2000);
});

// ── Logic: Collect, Render, Persist ──
const CATEGORIES = {
  'Identity':   ['hash', 'platform', 'loadTime'],
  'Browser':    ['userAgent', 'language', 'languages', 'vendor', 'product', 'productSub', 'appCodeName', 'appName', 'appVersion'],
  'Hardware':   ['deviceMemory', 'hardwareConcurrency', 'maxTouchPoints', 'oscpu', 'cpuClass'],
  'Display':    ['screen', 'innerWidth', 'innerHeight', 'outerWidth', 'outerHeight', 'devicePixelRatio', 'colorDepth', 'pixelDepth'],
  'Environment':['timezone', 'timezoneOffset', 'cookieEnabled', 'doNotTrack', 'webdriver', 'pdfViewerEnabled'],
  'Graphics':   ['canvas', 'webgl', 'webglInfo', 'gpu'],
  'Audio':      ['audio'],
  'Network':    ['ip', 'downlink', 'effectiveType', 'rtt', 'saveData']
};

async function collectData() {
  const mv = new MixVisit();
  await mv.load();
  const signals = mv.get();
  return {
    hash:     mv.fingerprintHash,
    platform: mv.get('platform'),
    loadTime: mv.loadTime,
    signals:  signals,
  };
}

function renderUI(payload) {
  rawData = JSON.stringify(payload, null, 2);
  const body = document.getElementById('fpBody');
  const loader = document.getElementById('loader');
  const section = document.getElementById('fpSection');

  loader.style.display = 'none';
  section.style.display = 'block';
  body.innerHTML = '';

  const { signals, ...core } = payload;
  const flat = { ...core, ...signals };
  const usedKeys = new Set();

  Object.entries(CATEGORIES).forEach(([name, keys]) => {
    const chunk = {};
    keys.forEach(k => {
      if (flat[k] !== undefined) {
        chunk[k] = flat[k];
        usedKeys.add(k);
      }
    });

    if (Object.keys(chunk).length > 0) {
      appendSegment(body, name, chunk);
    }
  });

  // Remaining keys in 'Other'
  const other = {};
  Object.keys(flat).forEach(k => {
    if (!usedKeys.has(k)) other[k] = flat[k];
  });
  if (Object.keys(other).length > 0) {
    appendSegment(body, 'Other Signals', other);
  }
}

function appendSegment(parent, name, data) {
  const keys = Object.keys(data).length;
  const html = `
    <div class="fp-segment">
      <div class="fps-head">
        <span class="fps-title">${name}</span>
        <span class="fps-count">${keys} key${keys === 1 ? '' : 's'}</span>
      </div>
      <div class="fps-content">${highlight(data)}</div>
    </div>
  `;
  parent.insertAdjacentHTML('beforeend', html);
}

async function persist(payload) {
  const res = await fetch('/save', {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('Save failed');
  return res.json();
}


async function run() {
  try {
    const payload = await collectData();
    renderUI(payload);

    // Silently persist data to backend
    persist(payload).catch();
  } catch (err) {
    console.error('Core error:', err);
  }
}

window.addEventListener('load', run);
