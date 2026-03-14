import { MixVisit } from '/static/js/mixvisit.js';

// ── Theme toggle ──
let dark = true;
document.getElementById('themeBtn').addEventListener('click', () => {
  dark = !dark;
  document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light');
  document.getElementById('themeBtn').textContent = dark ? '🌙' : '☀️';
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

function setNotice(ok, text = '') {
  const n = document.getElementById('notice');
  if (ok) {
    n.className = 'notice ok';
    n.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg> Saved to database — ID: ${text}`;
  } else {
    n.className = 'notice err';
    n.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg> Could not save to database.`;
  }
}

async function run() {
  try {
    const payload = await collectData();
    renderUI(payload);

    // const result = await persist(payload);
    // setNotice(true, result.id);
  } catch (err) {
    console.error('Core error:', err);
    setNotice(false);
  }
}

window.addEventListener('load', run);
