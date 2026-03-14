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
async function collectData() {
  const mv = new MixVisit();
  await mv.load();
  return {
    hash:     mv.fingerprintHash,
    platform: mv.get('platform'),
    loadTime: mv.loadTime,
    signals:  mv.get(),
  };
}

function renderUI(payload) {
  rawData = JSON.stringify(payload, null, 2);
  document.getElementById('loader').style.display    = 'none';
  document.getElementById('fpSection').style.display = 'block';
  document.getElementById('fpBody').innerHTML        = highlight(payload);
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
