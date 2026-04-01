import { MixVisit } from '/static/js/mixvisit.js';

const MAX_ATTEMPTS = 3;
let attemptsRemaining = MAX_ATTEMPTS;
let validatedCode = null;

function setLoaderMessage(message) {
    const loaderMsg = document.getElementById('loaderMessage');
    if (loaderMsg) loaderMsg.textContent = message;
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

function isMobileDevice() {
  const userAgent = navigator.userAgent || navigator.vendor || window.opera;
  return /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(userAgent.toLowerCase());
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

function populateModelDropdown(devices, selectEl) {
  // Clear existing options except first placeholder
  selectEl.innerHTML = '<option value="" disabled selected>Select your device model</option>';
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
    return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
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

    loader.classList.add('hidden');
    if (codeEntry) codeEntry.classList.add('hidden');
    section.classList.remove('hidden');
    section.classList.add('visible');
    if (outerHe) {
        outerHe.classList.remove('hidden');
        outerHe.classList.add('visible');
    }
    if (heroWaiting) heroWaiting.classList.add('hidden');
    if (heroCollected) heroCollected.classList.remove('hidden');
    body.innerHTML = '';

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
        if (Object.keys(chunk).length > 0) appendSegment(body, name, chunk);
    });

    const other = {};
    Object.keys(flat).forEach(k => { if (!usedKeys.has(k)) other[k] = flat[k]; });
    if (Object.keys(other).length > 0) appendSegment(body, 'Other Signals', other);
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

async function validateCode(code) {
    const csrfMatch = document.cookie.match(/(?:^|; )csrf_token=([^;]+)/);
    const csrfToken = csrfMatch ? csrfMatch[1] : '';
    const res = await fetch('/api/validate-code', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': csrfToken },
        body: JSON.stringify({ code })
    });
    return res.ok;
}

async function collectAndSubmit(deviceModel) {
  try {
    setLoaderMessage('Obtaining fingerprint...');
    const mv = new MixVisit();
    await mv.load();

    const payload = {
      access_code: validatedCode,
      hash: mv.fingerprintHash,
      loadTime: mv.loadTime,
      fingerprint: mv.get()
    };

    if (deviceModel && deviceModel.trim()) {
      payload.device_model = deviceModel.trim();
    }

    renderUI({ hash: payload.hash, loadTime: payload.loadTime, fingerprint: payload.fingerprint });

    const csrfMatch = document.cookie.match(/(?:^|; )csrf_token=([^;]+)/);
    const csrfToken = csrfMatch ? csrfMatch[1] : '';
    const res = await fetch('/api/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': csrfToken },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      console.error('Submit failed:', res.status);
    }
  } catch (err) {
    console.error('Collection error:', err);
  }
}

function showCodeEntry(urlCode = null) {
  const desktopLayout = document.getElementById('desktopLayout');
  if (desktopLayout) desktopLayout.classList.add('show-code-entry');

  const form = document.getElementById('codeForm');
  const codeInput = document.getElementById('codeInput');
  const platformSelect = document.getElementById('platformSelect');
  const modelFieldContainer = document.getElementById('modelFieldContainer');
  const deviceModelSelect = document.getElementById('deviceModelSelect');
  const deviceModelInput = document.getElementById('deviceModelInput');
  const attemptsDisplay = document.getElementById('attemptsRemaining');

  if (attemptsDisplay) {
    attemptsDisplay.textContent = attemptsRemaining;
  }

  const isMobile = isMobileDevice();
  if (urlCode) {
    if (codeInput) codeInput.classList.add('hidden');
  } else {
    if (codeInput) codeInput.classList.remove('hidden');
  }

  // Handle platform dropdown change
  if (platformSelect) {
    platformSelect.addEventListener('change', async () => {
      const platform = platformSelect.value;
      if (!platform) {
        if (modelFieldContainer) modelFieldContainer.classList.add('hidden');
        return;
      }

      if (modelFieldContainer) modelFieldContainer.classList.remove('hidden');

      const iosPlatforms = ['iphone', 'ipad', 'mac'];
      if (iosPlatforms.includes(platform)) {
        // Show dropdown for iOS devices
        if (deviceModelSelect) deviceModelSelect.classList.remove('hidden');
        if (deviceModelInput) deviceModelInput.classList.add('hidden');
        
        // Populate device list
        const devices = getDeviceList(platform);
        if (deviceModelSelect) populateModelDropdown(devices, deviceModelSelect);
      } else {
        // Show text input for Android/Windows/Linux
        if (deviceModelSelect) deviceModelSelect.classList.add('hidden');
        if (deviceModelInput) {
          deviceModelInput.classList.remove('hidden');
          const placeholders = {
            'android': 'Enter your device model (e.g., Samsung Galaxy S24, Pixel 8)',
            'windows': 'Enter your device model (e.g., Surface Pro 9, Dell XPS)',
            'linux': 'Enter your device model (e.g., ThinkPad X1, Ubuntu PC)'
          };
          deviceModelInput.placeholder = placeholders[platform] || 'Enter your device model';
        }
      }
    });
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const platform = platformSelect ? platformSelect.value : '';
    if (!platform) {
      showToast('Please select your device platform.', 'error');
      return;
    }

    let deviceModel = '';
    const iosPlatforms = ['iphone', 'ipad', 'mac'];
    if (iosPlatforms.includes(platform)) {
      deviceModel = deviceModelSelect ? deviceModelSelect.value : '';
    } else {
      deviceModel = deviceModelInput ? deviceModelInput.value.trim() : '';
    }

    if (!deviceModel) {
      showToast('Please select or enter your device model.', 'error');
      return;
    }

    // "Not Sure" stays as-is, backend will use device detection
    // No transformation needed - backend handles fallback

    let code;
    if (urlCode) {
      code = urlCode;
    } else {
      code = codeInput ? codeInput.value.trim() : '';
      if (!code) return;
    }

    if (attemptsRemaining <= 0) {
      showToast('No attempts remaining. Please request a new code.', 'error');
      return;
    }

    const loader = document.getElementById('loader');
    const codeEntry = document.getElementById('codeEntrySection');
    setLoaderMessage('Validating access code...');
    loader.classList.remove('hidden');
    codeEntry.classList.add('hidden');

    const isValid = await validateCode(code);

    if (isValid) {
      validatedCode = code;
      setLoaderMessage('Obtaining fingerprint...');
      await collectAndSubmit(deviceModel);
    } else {
      attemptsRemaining--;
      loader.classList.add('hidden');
      codeEntry.classList.remove('hidden');

      if (attemptsRemaining > 0) {
        showToast('That code is not valid.', 'error');
      } else {
        showToast('No attempts remaining. Please request a new code.', 'error');
      }

      if (attemptsDisplay) {
        attemptsDisplay.textContent = attemptsRemaining;
      }
    }
  });
}

async function run() {
  const params = new URLSearchParams(window.location.search);
  const urlCode = params.get('code');

  if (urlCode) {
    const desktopLayout = document.getElementById('desktopLayout');
    const loader = document.getElementById('loader');
    const codeEntry = document.getElementById('codeEntrySection');
    const deviceModelInput = document.getElementById('deviceModelInput');
    const codeInput = document.getElementById('codeInput');

    if (desktopLayout) desktopLayout.classList.add('show-code-entry');

    setLoaderMessage('Validating access code...');
    loader.classList.remove('hidden');

    const isValid = await validateCode(urlCode);

    if (isValid) {
      validatedCode = urlCode;
      loader.classList.add('hidden');
      codeEntry.classList.remove('hidden');
      const platformSelect = document.getElementById('platformSelect');
      const modelFieldContainer = document.getElementById('modelFieldContainer');
      if (platformSelect) platformSelect.classList.remove('hidden');
      if (modelFieldContainer) modelFieldContainer.classList.remove('hidden');
      if (codeInput) codeInput.classList.add('hidden');
      showCodeEntry(urlCode);
    } else {
      loader.classList.add('hidden');
      codeEntry.classList.remove('hidden');
      showToast('The access code in the URL is invalid.', 'error');
      showCodeEntry();
    }
  } else {
    showCodeEntry();
  }
}

window.addEventListener('DOMContentLoaded', () => {
	setupNestedToggles();
	run();
});
