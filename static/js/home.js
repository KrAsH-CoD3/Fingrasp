import { MixVisit } from '/static/js/mixvisit.js';

const PAGE_LOAD_TIME = Date.now();
let validatedCode = null;

function setLoaderMessage(message) {
  const loaderMsg = document.getElementById('loaderMessage');
  if (loaderMsg) loaderMsg.innerHTML = message;
}

function showToast(message, type = 'error') {
  const container = document.getElementById('toastContainer');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  container.appendChild(toast);

  setTimeout(() => {
    toast.classList.add('hiding');
    setTimeout(() => toast.remove(), 300);
  }, 5000);
}

function formatKey(key) {
  return key
    .replace(/([a-z])([A-Z])/g, '$1 $2')
    .replace(/([A-Z]+)([A-Z][a-z])/g, '$1 $2')
    .replace(/^./, s => s.toUpperCase());
}

/**
 * Detect the user's platform using a priority-based signal hierarchy:
 * 1. navigator.userAgentData.getHighEntropyValues() — most reliable (async, Chromium-only)
 * 2. navigator.userAgentData.platform — modern sync fallback
 * 3. navigator.platform + maxTouchPoints — legacy fallback for Safari/Firefox
 *
 * For iOS, uses screen dimensions to distinguish iPhone from iPad.
 * Returns: 'iphone' | 'ipad' | 'mac' | 'android' | 'windows' | 'linux' | null
 */
async function detectPlatform() {
  let platform = null;
  
  // ── Priority 1: High Entropy Values (Chromium browsers) ──
  if (navigator.userAgentData && typeof navigator.userAgentData.getHighEntropyValues === 'function') {
    try {
      const hints = await navigator.userAgentData.getHighEntropyValues(['platform', 'model', 'mobile']);
      const p = (hints.platform || '').toLowerCase();
      const model = (hints.model || '').toLowerCase();

      if (p === 'android') platform = 'android';
      else if (p === 'windows') platform = 'windows';
      else if (p === 'linux') platform = 'linux';
      else if (p === 'ios') {
        if (model.startsWith('ipad')) platform = 'ipad';
        else if (model.startsWith('iphone')) platform = 'iphone';
        else platform = _iosScreenHeuristic();
      }
      else if (p === 'macos' || p === 'mac os x') {
        platform = navigator.maxTouchPoints > 0 ? 'ipad' : 'mac';
      }
    } catch (e) {
      console.warn('High entropy values failed:', e);
    }
  }

  // ── Priority 2: navigator.userAgentData.platform (sync, Chromium) ──
  if (!platform && navigator.userAgentData && navigator.userAgentData.platform) {
    const p = navigator.userAgentData.platform.toLowerCase();
    if (p === 'android') platform = 'android';
    else if (p === 'windows') platform = 'windows';
    else if (p === 'linux') platform = 'linux';
    else if (p === 'ios') platform = _iosScreenHeuristic();
    else if (p === 'macos') platform = navigator.maxTouchPoints > 0 ? 'ipad' : 'mac';
  }

  // ── Priority 3: navigator.platform + maxTouchPoints (Safari, Firefox) ──
  if (!platform) {
    const navPlatform = (navigator.platform || '').toLowerCase();
    const touchPoints = navigator.maxTouchPoints || 0;

    if (navPlatform === 'iphone') platform = 'iphone';
    else if (navPlatform === 'ipad') platform = 'ipad';
    else if (navPlatform === 'macintel' || navPlatform === 'macarm') {
      platform = touchPoints > 0 ? 'ipad' : 'mac';
    }
    else if (navPlatform.startsWith('win')) platform = 'windows';
    else if (navPlatform === 'linux' || navPlatform === 'x11') {
      platform = (touchPoints > 0 && /android/i.test(navigator.userAgent)) ? 'android' : 'linux';
    }
  }

  // ── Priority 4: User-Agent string (last resort) ──
  if (!platform) {
    const ua = (navigator.userAgent || '').toLowerCase();
    const touchPoints = navigator.maxTouchPoints || 0;
    if (ua.includes('android')) platform = 'android';
    else if (ua.includes('iphone')) platform = 'iphone';
    else if (ua.includes('ipad')) platform = 'ipad';
    else if (ua.includes('macintosh')) platform = touchPoints > 0 ? 'ipad' : 'mac';
    else if (ua.includes('windows')) platform = 'windows';
    else if (ua.includes('linux')) platform = 'linux';
  }

  if (!platform) return null;

  // ── Calculate screen key for iOS model filtering ──
  let screenKey = null;
  if (platform === 'iphone' || platform === 'ipad') {
    const w = Math.min(window.screen.width, window.screen.height);
    const h = Math.max(window.screen.width, window.screen.height);
    const scale = window.devicePixelRatio ? Math.round(window.devicePixelRatio) : 0;
    screenKey = `${w}x${h}x${scale}`;
    console.log(`[Fingrasp] Screen key: ${screenKey}`);
  }
  
  console.log(`[Fingrasp] Platform: ${platform}, Screen Key: ${screenKey || 'N/A'}`);

  return { platform, screenKey };
}

/**
 * Distinguish iPhone from iPad using screen dimensions.
 * iPads have a minimum dimension > 700px (logical pixels).
 */
function _iosScreenHeuristic() {
  const minDim = Math.min(screen.width, screen.height);
  return minDim > 700 ? 'ipad' : 'iphone';
}

function getDeviceList(platform) {
  const el = document.getElementById('deviceLists');
  if (!el) return [];
  try {
    const lists = JSON.parse(el.textContent);
    return lists[platform] || [];
  } catch (err) {
    console.error('Failed to parse device lists:', err);
    return [];
  }
}

function populateModelDropdown(devices, selectEl, platformName) {
  const placeholderText = platformName ? `Select your ${platformName} model` : 'Select your device model';
  selectEl.innerHTML = `<option value="" disabled selected>${placeholderText}</option>`;
  devices.forEach(device => {
    const option = document.createElement('option');
    option.value = device;
    option.textContent = device;
    selectEl.appendChild(option);
  });
  // Add "Not Sure" option at the end
  const notSureOption = document.createElement('option');
  notSureOption.value = 'not_sure';
  notSureOption.textContent = 'Not Sure';
  selectEl.appendChild(notSureOption);
}

function escHtml(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function renderValue(val, depth = 0, noTruncate = false) {
  if (val === null || val === undefined)
    return '<span class="val-null">null</span>';

  if (typeof val === 'boolean')
    return val
      ? '<span class="val-bool val-true">✓ true</span>'
      : '<span class="val-bool val-false">✗ false</span>';

  if (typeof val === 'number')
    return `<span class="val-num">${val}</span>`;

  if (typeof val === 'string') {
    if (!noTruncate && val.length > 120) {
      const id = 'exp-' + Math.random().toString(36).slice(2, 8);
      return `<span class="val-str val-long">
<span class="val-preview" id="${id}-p">${escHtml(val.slice(0, 80))}…</span>
<span class="val-full hidden" id="${id}-f">${escHtml(val)}</span>
<button class="val-expand" data-target="${id}">show more</button>
</span>`;
    }
    return `<span class="val-str">${escHtml(val)}</span>`;
  }

  if (Array.isArray(val)) {
    if (val.length === 0) return '<span class="val-null">[ ]</span>';

    if (val.length <= 5 && val.every(v => typeof v !== 'object')) {
      const preview = `[${val.map(v => typeof v === 'string' ? `"${escHtml(v)}"` : v).join(', ')}]`;
      if (preview.length < 60) {
        return `<span class="val-arr">${preview}</span>`;
      }
    }

    const id = 'nest-' + Math.random().toString(36).slice(2, 8);
    const rows = val.map((item, i) =>
      `<tr class="kv-row"><td class="kv-key">[${i}]</td><td class="kv-val">${renderValue(item, depth + 1)}</td></tr>`
    ).join('');
    return `<div class="val-nested">
<button class="val-toggle" data-target="${id}"><span>▶</span> Array (${val.length} items)</button>
<table class="kv-table kv-sub hidden" id="${id}">${rows}</table>
</div>`;
  }

  if (typeof val === 'object') {
    const entries = Object.entries(val);
    if (entries.length === 0) return '<span class="val-null">{ }</span>';
    if (val.error && typeof val.error === 'object' && val.error.code)
      return `<span class="val-err">⚠ ${escHtml(val.error.message || 'Error')}</span>`;
    if ('value' in val && 'duration' in val)
      return renderValue(val.value, depth);

    if (entries.length <= 3 && entries.every(([k, v]) => typeof v !== 'object')) {
      const preview = `{ ${entries.map(([k, v]) => `${k}: ${typeof v === 'string' ? `"${escHtml(v)}"` : v}`).join(', ')} }`;
      if (preview.length < 50) {
        return `<span class="val-arr">${preview}</span>`;
      }
    }

    const id = 'nest-' + Math.random().toString(36).slice(2, 8);
    const rows = entries.map(([k, v]) => {
      const lowK = k.toLowerCase();
      const noTrunc = ['useragent', 'ua', 'appversion', 'version', 'navigator'].includes(lowK);
      const rendered = renderValue(v, depth + 1, noTrunc);
      const shouldWrap = ['useragent', 'ua', 'appversion', 'version'].includes(lowK) || rendered.length > 60;
      const wrap = shouldWrap ? ' wrap' : '';
      return `<tr class="kv-row"><td class="kv-key">${formatKey(k)}</td><td class="kv-val${wrap}">${rendered}</td></tr>`;
    }).join('');
    if (depth === 0)
      return `<table class="kv-table">${rows}</table>`;
    return `<div class="val-nested">
<button class="val-toggle" data-target="${id}"><span>▶</span> Object (${entries.length} keys)</button>
<table class="kv-table kv-sub hidden" id="${id}">${rows}</table>
</div>`;
  }

  return `<span class="val-str">${escHtml(String(val))}</span>`;
}

window.toggleExpand = (id) => {
  const p = document.getElementById(id + '-p');
  const f = document.getElementById(id + '-f');
  const btn = p.parentElement.querySelector('.val-expand');
  if (f.classList.contains('hidden')) {
    p.classList.add('hidden'); f.classList.remove('hidden'); btn.textContent = 'show less';
  } else {
    p.classList.remove('hidden'); f.classList.add('hidden'); btn.textContent = 'show more';
  }
};

window.toggleNested = (btn, id) => {
  const el = document.getElementById(id);
  const icon = btn.querySelector('span');
  if (el.classList.contains('hidden')) {
    el.classList.remove('hidden');
    if (icon) icon.textContent = '▼';
  } else {
    el.classList.add('hidden');
    if (icon) icon.textContent = '▶';
  }
};

function setupNestedToggles() {
  document.addEventListener('click', (e) => {
    if (e.target.matches('.val-toggle')) {
      const btn = e.target;
      const id = btn.dataset.target;
      const el = document.getElementById(id);
      const icon = btn.querySelector('span');
      if (el.classList.contains('hidden')) {
        el.classList.remove('hidden');
        if (icon) icon.textContent = '▼';
      } else {
        el.classList.add('hidden');
        if (icon) icon.textContent = '▶';
      }
    }

    if (e.target.matches('.val-expand')) {
      const btn = e.target;
      const id = btn.dataset.target;
      const p = document.getElementById(id + '-p');
      const f = document.getElementById(id + '-f');
      if (f.classList.contains('hidden')) {
        p.classList.add('hidden');
        f.classList.remove('hidden');
        btn.textContent = 'show less';
      } else {
        p.classList.remove('hidden');
        f.classList.add('hidden');
        btn.textContent = 'show more';
      }
    }
  });
}

let rawData = '';
const copyBtn = document.getElementById('copyBtn');
if (copyBtn) {
  const COPY_HTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg> Copy All`;
  const CHECK_HTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg> Copied!`;

  copyBtn.addEventListener('click', async () => {
    await navigator.clipboard.writeText(rawData);
    copyBtn.classList.add('copied');
    copyBtn.innerHTML = CHECK_HTML;
    setTimeout(() => { copyBtn.classList.remove('copied'); copyBtn.innerHTML = COPY_HTML; }, 2000);
  });
}

const toggleAllBtn = document.getElementById('toggleAllBtn');
if (toggleAllBtn) {
  let allCollapsed = false;

  toggleAllBtn.addEventListener('click', () => {
    allCollapsed = !allCollapsed;
    const segments = document.querySelectorAll('.fp-segment');
    segments.forEach(seg => {
      if (allCollapsed) {
        seg.classList.add('collapsed');
      } else {
        seg.classList.remove('collapsed');
      }
    });

    toggleAllBtn.classList.toggle('active', allCollapsed);
    toggleAllBtn.querySelector('span').textContent = allCollapsed ? 'Expand All' : 'Collapse All';
  });
}

function renderUI(payload) {
  const { hash, loadTime, fingerprint } = payload;

  const desktopLayout = document.getElementById('desktopLayout');
  if (desktopLayout) desktopLayout.classList.remove('show-code-entry');

  document.getElementById('valHash').textContent = hash;
  document.getElementById('valTime').textContent = `${loadTime}ms`;
  rawData = JSON.stringify(payload, null, 2);

  const body = document.getElementById('fpBody');
  const loader = document.getElementById('loader');
  const section = document.getElementById('fpSection');
  const outerHe = document.getElementById('fpOuterHeader');
  const codeEntry = document.getElementById('codeEntrySection');
  const heroWaiting = document.getElementById('heroWaiting');
  const heroCollected = document.getElementById('heroCollected');

  if (loader) loader.classList.add('hidden');
  if (codeEntry) codeEntry.classList.add('hidden');
  if (section) {
    section.classList.remove('hidden');
    section.classList.add('visible');
  }
  if (outerHe) {
    outerHe.classList.remove('hidden');
    outerHe.classList.add('visible');
  }
  if (heroWaiting) heroWaiting.classList.add('hidden');
  if (heroCollected) heroCollected.classList.remove('hidden');
  if (body) body.innerHTML = '';

  const flat = { ...fingerprint };
  const usedKeys = new Set();

  const CATEGORIES = {
    'Browser': ['navigator', 'navigatorProperties', 'vendorFlavors', 'cookiesEnabled', 'sessionStorage', 'localStorage', 'openDatabase', 'indexedDB'],
    'Display': ['screen', 'screenResolution', 'screenFrame', 'devicePixelRatio', 'colorDepth', 'colorGamut', 'colorSpaceSupport', 'hdr', 'hdcp', 'invertedColors', 'forcedColors', 'monochromeDepth', 'contrastPreference', 'reducedMotion', 'reducedTransparency'],
    'Hardware': ['architecture', 'touchSupport', 'memory', 'systemInfo', 'scheduling', 'baseLatency'],
    'Graphics': ['canvas', 'webgl', 'webgpu', 'clientRects', 'fontRendering'],
    'Audio': ['audio', 'speechSynthesisVoices', 'mediaCapabilities', 'mediaDecodingCapabilities'],
    'Network': ['networkAPI', 'networkInfo', 'location', 'geolocation', 'webrtc'],
    'Fonts & Intl': ['fonts', 'fontPreferences', 'intl', 'math'],
    'Environment': ['timezone', 'globalPrivacyControl', 'performance', 'devToolsOpen', 'batteryAPI', 'batteryInfo', 'bluetoothAPI'],
    'APIs & Engine': ['activeX', 'silverlight', 'flash', 'java', 'drmSupport', 'fileAPIs', 'storageQuota', 'symbolProperties', 'webkitAPIs', 'builtInObjects', 'cssSupport', 'computedStyleProperties', 'globalObjests']
  };

  Object.entries(CATEGORIES).forEach(([name, keys]) => {
    const chunk = {};
    keys.forEach(k => {
      if (flat[k] !== undefined) { chunk[k] = flat[k]; usedKeys.add(k); }
    });
    if (Object.keys(chunk).length > 0 && body) appendSegment(body, name, chunk);
  });

  const other = {};
  Object.keys(flat).forEach(k => { if (!usedKeys.has(k)) other[k] = flat[k]; });
  if (Object.keys(other).length > 0 && body) appendSegment(body, 'Other Signals', other);
}

function appendSegment(parent, name, data) {
  const count = Object.keys(data).length;
  const sectionId = `sec-${name.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`;
  const json = JSON.stringify(data, null, 2);

  const rows = Object.entries(data).map(([key, val]) => {
    const display = (val && typeof val === 'object' && 'value' in val && 'duration' in val) ? val.value : val;
    const lowKey = key.toLowerCase();
    const noTrunc = ['useragent', 'ua', 'appversion', 'version', 'navigator'].includes(lowKey);
    const rendered = renderValue(display, 0, noTrunc);
    const shouldWrap = ['useragent', 'ua', 'appversion', 'version'].includes(lowKey) || rendered.length > 60;
    const wrap = shouldWrap ? ' wrap' : '';
    return `<tr class="kv-row">
<td class="kv-key">${formatKey(key)}</td>
<td class="kv-val${wrap}">${rendered}</td>
</tr>`;
  }).join('');

  const segmentDiv = document.createElement('div');
  segmentDiv.className = 'fp-segment';
  segmentDiv.id = sectionId;
  segmentDiv.dataset.json = json;

  segmentDiv.innerHTML = `
<div class="fps-head">
<div class="fps-head-left">
<div class="fps-chevron">
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg>
</div>
<span class="fps-title">${name}</span>
<span class="fps-count">${count} signal${count === 1 ? '' : 's'}</span>
</div>
<button class="fps-copy">
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg>
Copy
</button>
</div>
<div class="fps-content-wrapper">
<div class="fps-content"><table class="kv-table">${rows}</table></div>
</div>
`;

  segmentDiv.querySelector('.fps-head').addEventListener('click', () => {
    segmentDiv.classList.toggle('collapsed');
  });

  segmentDiv.querySelector('.fps-copy').addEventListener('click', (e) => {
    e.stopPropagation();
    copySection(sectionId);
  });

  parent.appendChild(segmentDiv);
}

function copySection(id) {
  const sec = document.getElementById(id);
  const raw = sec.dataset.json;
  const btn = sec.querySelector('.fps-copy');

  navigator.clipboard.writeText(raw).then(() => {
    const original = btn.innerHTML;
    btn.classList.add('copied');
    btn.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg> Copied!`;

    setTimeout(() => {
      btn.classList.remove('copied');
      btn.innerHTML = original;
    }, 2000);
  });
}

async function validateTurnstile(turnstileToken, honeypotEmail, timeToSolve) {
  try {
    const csrfMatch = document.cookie.match(/(?:^|; )csrf_token=([^;]+)/);
    const csrfToken = csrfMatch ? csrfMatch[1] : '';
    const payload = {
        cf_turnstile_response: turnstileToken,
        honeypot_email: honeypotEmail,
        time_to_solve: timeToSolve
    };
    const res = await fetch('/api/validate-turnstile', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': csrfToken },
      body: JSON.stringify(payload)
    });
    
    if (res.ok) {
        const body = await res.json();
        return body.session_token;
    }
    return null;
  } catch (err) {
    console.error('Validation fetch error:', err);
    return null;
  }
}

async function collectAndSubmit(deviceModel, turnstileToken, honeypotEmail, timeToSolve) {
  const loader = document.getElementById('loader');
  const codeEntry = document.getElementById('codeEntrySection');

  try {
    if (loader) loader.classList.remove('hidden');
    if (codeEntry) codeEntry.classList.add('hidden');

    setLoaderMessage('Verifying security check<span class="dot-anim"></span>');
    const sessionToken = await validateTurnstile(turnstileToken, honeypotEmail, timeToSolve);

    if (!sessionToken) {
      showToast('Security verification failed. Please try again.', 'error');
      if (loader) loader.classList.add('hidden');
      if (codeEntry) codeEntry.classList.remove('hidden');
      return;
    }

    setLoaderMessage('Obtaining fingerprint<span class="dot-anim"></span>');
    const mv = new MixVisit();
    await mv.load();

    const payload = {
      session_token: sessionToken,
      hash: mv.fingerprintHash,
      loadTime: mv.loadTime,
      fingerprint: mv.get(),
      device_model: deviceModel?.trim()
    };

    const csrfMatch = document.cookie.match(/(?:^|; )csrf_token=([^;]+)/);
    const csrfToken = csrfMatch ? csrfMatch[1] : '';
    const res = await fetch('/api/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': csrfToken },
      body: JSON.stringify(payload)
    });

    if (res.ok) {
      renderUI({ hash: payload.hash, loadTime: payload.loadTime, fingerprint: payload.fingerprint });
    } else {
      const data = await res.json().catch(() => ({}));
      showToast(data.message || 'Submission failed.', 'error');
      if (loader) loader.classList.add('hidden');
      if (codeEntry) codeEntry.classList.remove('hidden');
    }
  } catch (err) {
    console.error('Collection error:', err);
    showToast('An error occurred during submission.', 'error');
    if (loader) loader.classList.add('hidden');
    if (codeEntry) codeEntry.classList.remove('hidden');
  }
}

function showCodeEntryUI(urlCode = null) {
  const desktopLayout = document.getElementById('desktopLayout');
  const detectSection = document.getElementById('platformDetectSection');
  const errorSection = document.getElementById('platformErrorSection');
  const codeEntry = document.getElementById('codeEntrySection');

  // Hide detection/error states
  if (detectSection) detectSection.classList.add('hidden');
  if (errorSection) errorSection.classList.add('hidden');

  // Show code entry
  if (codeEntry) codeEntry.classList.remove('hidden');
  if (desktopLayout) {
    desktopLayout.classList.remove('hidden');
    desktopLayout.classList.add('show-code-entry');
  }

  const codeInput = document.getElementById('codeInput');

  if (urlCode && codeInput) {
    codeInput.value = urlCode;
    const btn = codeInput.closest('.input-wrapper')?.querySelector('.clear-input-btn');
    if (btn) btn.classList.remove('hidden');
  }
}

function showPlatformError() {
  const desktopLayout = document.getElementById('desktopLayout');
  const detectSection = document.getElementById('platformDetectSection');
  const errorSection = document.getElementById('platformErrorSection');

  if (detectSection) detectSection.classList.add('hidden');
  if (errorSection) errorSection.classList.remove('hidden');
  
  if (desktopLayout) {
    desktopLayout.classList.remove('hidden');
    desktopLayout.classList.add('show-code-entry');
  }
}

async function initFormLogic(detectedPlatform, screenKey = null) {
  const form = document.getElementById('codeForm');
  const platformSelect = document.getElementById('platformSelect');
  const modelFieldContainer = document.getElementById('modelFieldContainer');
  const deviceModelSelect = document.getElementById('deviceModelSelect');
  const deviceModelInput = document.getElementById('deviceModelInput');
  const honeypotEmailInput = document.getElementById('honeypotEmail');
  const modelNote = document.getElementById('modelNote');
  const noteHelpTrigger = document.getElementById('noteHelpTrigger');
  const modelHelpModal = document.getElementById('modelHelpModal');
  const modalCloseBtn = document.getElementById('modalCloseBtn');

  if (noteHelpTrigger && modelHelpModal) {
    noteHelpTrigger.addEventListener('click', () => {
      modelHelpModal.classList.remove('hidden');
    });

    modalCloseBtn?.addEventListener('click', () => {
      modelHelpModal.classList.add('hidden');
    });
  }

  if (!form) return;

  const platformNames = {
    'iphone': 'iPhone',
    'ipad': 'iPad',
    'mac': 'Mac',
    'android': 'Android',
    'windows': 'Windows',
    'linux': 'Linux'
  };

  // Lock the platform select to the detected value
  if (platformSelect) {
    platformSelect.value = detectedPlatform;
    platformSelect.disabled = true;
    platformSelect.classList.add('locked');
  }

  // Configure the model field for the detected platform
  _configureModelField(detectedPlatform, {
    modelFieldContainer, deviceModelSelect, deviceModelInput, modelNote, platformNames
  }, screenKey);
  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const platform = platformSelect ? platformSelect.value : '';
    if (!platform) {
      showToast('Please select your device platform.', 'error');
      return;
    }

    let deviceModel = '';
    const dropdownPlatforms = ['iphone', 'ipad', 'mac'];
    if (dropdownPlatforms.includes(platform)) {
      deviceModel = deviceModelSelect ? deviceModelSelect.value : '';
    } else {
      deviceModel = deviceModelInput ? deviceModelInput.value.trim() : '';
    }

    if (!deviceModel) {
      showToast(dropdownPlatforms.includes(platform) ? 'Please select model.' : 'Please enter model.', 'error');
      return;
    }

    // Get Turnstile token
    let turnstileToken = '';
    const turnstileResponseInput = document.querySelector('input[name="cf-turnstile-response"]');
    if (turnstileResponseInput) {
        turnstileToken = turnstileResponseInput.value;
    }
    
    if (!turnstileToken) {
      showToast('Please complete the Cloudflare Turnstile challenge.', 'error');
      return;
    }

    const honeypotEmail = honeypotEmailInput ? honeypotEmailInput.value : '';
    const timeToSolve = Date.now() - PAGE_LOAD_TIME;

    const loader = document.getElementById('loader');
    const codeEntry = document.getElementById('codeEntrySection');
    try {
      await collectAndSubmit(deviceModel, turnstileToken, honeypotEmail, timeToSolve);
    } catch (err) {
      console.error('Submit error:', err);
      loader?.classList.add('hidden');
      codeEntry?.classList.remove('hidden');
      showToast('An unexpected error occurred.', 'error');
    }
  });
}

/**
 * Configure the model field (dropdown vs text input) based on the selected platform.
 */
function _configureModelField(platform, els, screenKey = null) {
  const { modelFieldContainer, deviceModelSelect, deviceModelInput, modelNote, platformNames } = els;
  const displayName = platformNames[platform] || 'device';

  if (modelFieldContainer) modelFieldContainer.classList.remove('hidden');

  const dropdownPlatforms = ['iphone', 'ipad', 'mac'];
  if (dropdownPlatforms.includes(platform)) {
    // Show model dropdown (Apple devices have a known, finite set of models)
    if (deviceModelSelect) deviceModelSelect.classList.remove('hidden');
    if (deviceModelInput) {
      const wrapper = deviceModelInput.closest('.input-wrapper');
      if (wrapper) wrapper.classList.add('hidden');
      deviceModelInput.value = '';
    }
    if (modelNote) modelNote.classList.add('hidden');
    
    let devices = getDeviceList(platform);
    
    // For iPhone/iPad: use direct screen-to-model mapping lookup
    if (screenKey && (platform === 'iphone' || platform === 'ipad')) {
      const el = document.getElementById('deviceLists');
      if (el) {
        try {
          const lists = JSON.parse(el.textContent);
          const lookupKey = platform === 'iphone' ? 'iphone_screen_models' : 'ipad_screen_models';
          const screenModels = lists[lookupKey]?.[screenKey];
          if (screenModels && screenModels.length > 0) {
            devices = screenModels;
            console.log(`[Fingrasp] Direct lookup matched ${devices.length} models for ${screenKey}`);
          } else {
            console.log(`[Fingrasp] No mapping for key "${screenKey}", showing all ${platform} models`);
          }
        } catch (err) {
          console.error('Screen model lookup error:', err);
        }
      }
    }

    if (deviceModelSelect) populateModelDropdown(devices, deviceModelSelect, displayName);
  } else {
    // Show text input (Android, Windows, Linux have too many models to list)
    if (deviceModelSelect) {
      deviceModelSelect.classList.add('hidden');
      deviceModelSelect.value = '';
    }
    if (deviceModelInput) {
      const wrapper = deviceModelInput.closest('.input-wrapper');
      if (wrapper) wrapper.classList.remove('hidden');
      deviceModelInput.classList.remove('hidden');
      deviceModelInput.placeholder = `Enter your ${displayName} model`;
    }
    if (modelNote) modelNote.classList.remove('hidden');
  }
}

async function run() {
  // 1. Show detecting state (it's visible by default in HTML as an inline loader)
  // We keep the desktopLayout hidden until detection is complete

  // 2. Detect platform
  const detectedResult = await detectPlatform();

  // 3. If detection failed, show error and stop
  if (!detectedResult) {
    showPlatformError();
    return;
  }

  // 4. Configure the form with the detected platform
  await initFormLogic(detectedResult.platform, detectedResult.screenKey);

  // 5. Show the UI (URL code parsing is removed since code flow is replaced)
  showCodeEntryUI(null);
}

window.addEventListener('DOMContentLoaded', () => {
  setupNestedToggles();

  // Add clear button functionality
  document.querySelectorAll('.clear-input-btn').forEach(btn => {
    const targetId = btn.dataset.target;
    const input = document.getElementById(targetId);
    if (!input) return;

    const toggleVisibility = () => {
      if (input.value.length > 0) btn.classList.remove('hidden');
      else btn.classList.add('hidden');
    };

    input.addEventListener('input', toggleVisibility);
    input.addEventListener('focus', toggleVisibility);

    btn.addEventListener('click', () => {
      input.value = '';
      btn.classList.add('hidden');
      input.focus();
    });
  });

  run();
});
