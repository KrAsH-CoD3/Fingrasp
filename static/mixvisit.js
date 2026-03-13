function Ve() {
  return !!window.ActiveXObject;
}
function He() {
  const e = new Float32Array(1), t = new Uint8Array(e.buffer);
  return e[0] = 1 / 0, e[0] -= e[0], t[3];
}
var N = /* @__PURE__ */ ((e) => (e.UNSUPPORTED = "unsupported", e.SKIPPED = "skipped", e.UNSTABLE = "unstable", e))(N || {}), L = /* @__PURE__ */ ((e) => (e.TIMEOUT = "TimeoutError", e.INTERNAL = "InternalError", e.RESPONSE = "ResponseError", e))(L || {}), H = /* @__PURE__ */ ((e) => (e[e.LESS = -1] = "LESS", e[e.NONE = 0] = "NONE", e[e.MORE = 1] = "MORE", e[e.FORCED_COLORS = 10] = "FORCED_COLORS", e))(H || {});
/*!
 * +----------------------------------------------------------------------------------+
 * | murmurHash3.js v3.0.0 (http://github.com/karanlyons/murmurHash3.js)              |
 * | A TypeScript/JavaScript implementation of MurmurHash3's hashing algorithms.      |
 * |----------------------------------------------------------------------------------|
 * | Copyright (c) 2012-2020 Karan Lyons. Freely distributable under the MIT license. |
 * +----------------------------------------------------------------------------------+
 */
const Ge = {
  hash128: ze
}, We = {
  hash32: je,
  hash128: qe
}, Ce = 3432918353, Fe = 461845907, K = 597399067, $ = 2869860233, Y = 951274213, Z = 2716044179, J = [2277735313, 289559509], Q = [1291169091, 658871167], Xe = Array.from({ length: 256 }, (e, t) => `00${t.toString(16)}`.slice(-2)), de = (e) => TextEncoder.prototype.encode.bind(new TextEncoder())(e);
function je(e = new Uint8Array(0), t = 0, n = !0) {
  typeof e == "string" && (e = de(e));
  let o, r, a;
  if (typeof t == "number")
    o = t, r = 0, a = 0;
  else {
    ({ h1: o, len: a } = t);
    const { rem: m } = t;
    if (m.byteLength === 0)
      r = 0;
    else if (m.byteLength + e.byteLength >= 4) {
      a += 4, r = 4 - m.byteLength;
      const u = new Uint8Array(4), p = new DataView(u.buffer);
      u.set(m), u.set(e.subarray(0, r), m.byteLength), o = Ae(o, p.getUint32(0, !0));
    } else {
      const u = new Uint8Array(e.byteLength + m.byteLength);
      u.set(m), u.set(e, m.byteLength), e = u, r = 0;
    }
  }
  const i = new DataView(e.buffer, e.byteOffset), s = (e.byteLength - r) % 4, c = e.byteLength - r - s;
  for (a += c; r < c; r += 4)
    o = Ae(o, i.getUint32(r, !0));
  if (!n)
    return {
      h1: o,
      len: a,
      rem: e.slice(e.byteLength - s)
    };
  a += s;
  let l = 0;
  switch (s) {
    case 3:
      l ^= e[r + 2] << 16;
    case 2:
      l ^= e[r + 1] << 8;
    case 1:
      l ^= e[r], l = w(l, Ce), l = M(l, 15), l = w(l, Fe), o ^= l;
  }
  return o ^= a & 4294967295, o = G(o), o >>> 0;
}
function qe(e = new Uint8Array(0), t = 0, n = !0) {
  let o;
  typeof e == "string" ? (e = de(e), o = !0) : o = !1;
  let r, a, i, s, c, l;
  if (typeof t == "number")
    r = a = i = s = t, c = 0, l = 0;
  else {
    ({
      h1: r,
      h2: a,
      h3: i,
      h4: s,
      len: l
    } = t);
    const { rem: A } = t;
    if (A.byteLength === 0)
      c = 0;
    else if (A.byteLength + e.byteLength >= 16) {
      l += 16, c = 16 - A.byteLength;
      const b = new Uint8Array(16), v = new DataView(b.buffer);
      b.set(A), b.set(e.subarray(0, c), A.byteLength), [r, a, i, s] = be(
        r,
        a,
        i,
        s,
        v.getUint32(0, !0),
        v.getUint32(4, !0),
        v.getUint32(8, !0),
        v.getUint32(12, !0)
      );
    } else {
      const b = new Uint8Array(e.byteLength + A.byteLength);
      b.set(A), b.set(e, A.byteLength), e = b, c = 0;
    }
  }
  const m = new DataView(e.buffer, e.byteOffset), u = (e.byteLength - c) % 16, p = e.byteLength - c - u;
  for (l += p; c < p; c += 16)
    [r, a, i, s] = be(
      r,
      a,
      i,
      s,
      m.getUint32(c, !0),
      m.getUint32(c + 4, !0),
      m.getUint32(c + 8, !0),
      m.getUint32(c + 12, !0)
    );
  if (!n)
    return {
      h1: r,
      h2: a,
      h3: i,
      h4: s,
      len: l,
      rem: e.subarray(e.byteLength - u)
    };
  l += u;
  let y = 0, d = 0, g = 0, h = 0;
  switch (u) {
    case 15:
      h ^= e[c + 14] << 16;
    case 14:
      h ^= e[c + 13] << 8;
    case 13:
      h ^= e[c + 12], h = w(h, Z), h = M(h, 18), h = w(h, K), s ^= h;
    case 12:
      g ^= e[c + 11] << 24;
    case 11:
      g ^= e[c + 10] << 16;
    case 10:
      g ^= e[c + 9] << 8;
    case 9:
      g ^= e[c + 8], g = w(g, Y), g = M(g, 17), g = w(g, Z), i ^= g;
    case 8:
      d ^= e[c + 7] << 24;
    case 7:
      d ^= e[c + 6] << 16;
    case 6:
      d ^= e[c + 5] << 8;
    case 5:
      d ^= e[c + 4], d = w(d, $), d = M(d, 16), d = w(d, Y), a ^= d;
    case 4:
      y ^= e[c + 3] << 24;
    case 3:
      y ^= e[c + 2] << 16;
    case 2:
      y ^= e[c + 1] << 8;
    case 1:
      y ^= e[c], y = w(y, K), y = M(y, 15), y = w(y, $), r ^= y;
  }
  r ^= l & 4294967295, a ^= l & 4294967295, i ^= l & 4294967295, s ^= l & 4294967295, r += a + i + s, a += r, i += r, s += r, r = G(r), a = G(a), i = G(i), s = G(s), r += a + i + s, a += r, i += r, s += r;
  const I = new DataView(new ArrayBuffer(16));
  return I.setUint32(0, r, !1), I.setUint32(4, a, !1), I.setUint32(8, i, !1), I.setUint32(12, s, !1), o ? fe(new Uint8Array(I.buffer)) : new Uint8Array(I.buffer);
}
function ze(e = new Uint8Array(0), t = 0, n = !0) {
  let o;
  typeof e == "string" ? (e = de(e), o = !0) : o = !1;
  let r, a, i, s;
  if (typeof t == "number")
    r = [0, t], a = [0, t], i = 0, s = 0;
  else {
    ({ h1: r, h2: a, len: s } = t);
    const { rem: d } = t;
    if (d.byteLength === 0)
      i = 0;
    else if (d.byteLength + e.byteLength >= 16) {
      s += 16, i = 16 - d.byteLength;
      const g = new Uint8Array(16), h = new DataView(g.buffer);
      g.set(d), g.set(e.subarray(0, i), d.byteLength), [r, a] = Ee(
        r,
        a,
        [h.getUint32(4, !0), h.getUint32(0, !0)],
        [h.getUint32(12, !0), h.getUint32(8, !0)]
      );
    } else {
      const g = new Uint8Array(e.byteLength + d.byteLength);
      g.set(d), g.set(e, d.byteLength), e = g, i = 0;
    }
  }
  const c = new DataView(e.buffer, e.byteOffset), l = (e.byteLength - i) % 16, m = e.byteLength - i - l;
  for (s += m; i < m; i += 16)
    [r, a] = Ee(
      r,
      a,
      [c.getUint32(i + 4, !0), c.getUint32(i, !0)],
      [c.getUint32(i + 12, !0), c.getUint32(i + 8, !0)]
    );
  if (!n)
    return {
      h1: r,
      h2: a,
      len: s,
      rem: e.subarray(e.byteLength - l)
    };
  s += l;
  let u = [0, 0], p = [0, 0];
  switch (l) {
    case 15:
      p = T(p, x([0, e[i + 14]], 48));
    case 14:
      p = T(p, x([0, e[i + 13]], 40));
    case 13:
      p = T(p, x([0, e[i + 12]], 32));
    case 12:
      p = T(p, x([0, e[i + 11]], 24));
    case 11:
      p = T(p, x([0, e[i + 10]], 16));
    case 10:
      p = T(p, x([0, e[i + 9]], 8));
    case 9:
      p = T(p, [0, e[i + 8]]), p = R(p, Q), p = B(p, 33), p = R(p, J), a = T(a, p);
    case 8:
      u = T(u, x([0, e[i + 7]], 56));
    case 7:
      u = T(u, x([0, e[i + 6]], 48));
    case 6:
      u = T(u, x([0, e[i + 5]], 40));
    case 5:
      u = T(u, x([0, e[i + 4]], 32));
    case 4:
      u = T(u, x([0, e[i + 3]], 24));
    case 3:
      u = T(u, x([0, e[i + 2]], 16));
    case 2:
      u = T(u, x([0, e[i + 1]], 8));
    case 1:
      u = T(u, [0, e[i]]), u = R(u, J), u = B(u, 31), u = R(u, Q), r = T(r, u);
  }
  r = T(r, [0, s & 4294967295]), a = T(a, [0, s & 4294967295]), r = _(r, a), a = _(a, r), r = Te(r), a = Te(a), r = _(r, a), a = _(a, r);
  const y = new DataView(new ArrayBuffer(16));
  return y.setUint32(0, r[0], !1), y.setUint32(4, r[1], !1), y.setUint32(8, a[0], !1), y.setUint32(12, a[1], !1), o ? fe(new Uint8Array(y.buffer)) : new Uint8Array(y.buffer);
}
function be(e, t, n, o, r, a, i, s) {
  return r = w(r, K), r = M(r, 15), r = w(r, $), e ^= r, e = M(e, 19), e += t, e = w(e, 5) + 1444728091, a = w(a, $), a = M(a, 16), a = w(a, Y), t ^= a, t = M(t, 17), t += n, t = w(t, 5) + 197830471, i = w(i, Y), i = M(i, 17), i = w(i, Z), n ^= i, n = M(n, 15), n += o, n = w(n, 5) + 2530024501, s = w(s, Z), s = M(s, 18), s = w(s, K), o ^= s, o = M(o, 13), o += e, o = w(o, 5) + 850148119, [e, t, n, o];
}
function Te(e) {
  return e = T(e, [0, e[0] >>> 1]), e = R(e, [4283543511, 3981806797]), e = T(e, [0, e[0] >>> 1]), e = R(e, [3301882366, 444984403]), e = T(e, [0, e[0] >>> 1]), e;
}
function Ee(e, t, n, o) {
  return n = R(n, J), n = B(n, 31), n = R(n, Q), e = T(e, n), e = B(e, 27), e = _(e, t), e = _(R(e, [0, 5]), [0, 1390208809]), o = R(o, Q), o = B(o, 33), o = R(o, J), t = T(t, o), t = B(t, 31), t = _(t, e), t = _(R(t, [0, 5]), [0, 944331445]), [e, t];
}
function _(e, t) {
  const n = [e[0] >>> 16, e[0] & 65535, e[1] >>> 16, e[1] & 65535], o = [t[0] >>> 16, t[0] & 65535, t[1] >>> 16, t[1] & 65535], r = [0, 0, 0, 0];
  return r[3] += n[3] + o[3], r[2] += r[3] >>> 16, r[3] &= 65535, r[2] += n[2] + o[2], r[1] += r[2] >>> 16, r[2] &= 65535, r[1] += n[1] + o[1], r[0] += r[1] >>> 16, r[1] &= 65535, r[0] += n[0] + o[0], r[0] &= 65535, [r[0] << 16 | r[1], r[2] << 16 | r[3]];
}
function R(e, t) {
  const n = [e[0] >>> 16, e[0] & 65535, e[1] >>> 16, e[1] & 65535], o = [t[0] >>> 16, t[0] & 65535, t[1] >>> 16, t[1] & 65535], r = [0, 0, 0, 0];
  return r[3] += n[3] * o[3], r[2] += r[3] >>> 16, r[3] &= 65535, r[2] += n[2] * o[3], r[1] += r[2] >>> 16, r[2] &= 65535, r[2] += n[3] * o[2], r[1] += r[2] >>> 16, r[2] &= 65535, r[1] += n[1] * o[3], r[0] += r[1] >>> 16, r[1] &= 65535, r[1] += n[2] * o[2], r[0] += r[1] >>> 16, r[1] &= 65535, r[1] += n[3] * o[1], r[0] += r[1] >>> 16, r[1] &= 65535, r[0] += n[0] * o[3] + n[1] * o[2] + n[2] * o[1] + n[3] * o[0], r[0] &= 65535, [r[0] << 16 | r[1], r[2] << 16 | r[3]];
}
function B(e, t) {
  return t %= 64, t === 32 ? [e[1], e[0]] : t < 32 ? [
    e[0] << t | e[1] >>> 32 - t,
    e[1] << t | e[0] >>> 32 - t
  ] : (t -= 32, [
    e[1] << t | e[0] >>> 32 - t,
    e[0] << t | e[1] >>> 32 - t
  ]);
}
function x(e, t) {
  return t %= 64, t === 0 ? e : t < 32 ? [e[0] << t | e[1] >>> 32 - t, e[1] << t] : [e[1] << t - 32, 0];
}
function G(e) {
  return e ^= e >>> 16, e = w(e, 2246822507), e ^= e >>> 13, e = w(e, 3266489909), e ^= e >>> 16, e;
}
function Ae(e, t) {
  return t = w(t, Ce), t = M(t, 15), t = w(t, Fe), e ^= t, e = M(e, 13), e = w(e, 5) + 3864292196, e;
}
function T(e, t) {
  return [e[0] ^ t[0], e[1] ^ t[1]];
}
function fe(e = new Uint8Array(0)) {
  let t = "";
  for (let n = 0; n < e.byteLength; n++)
    t += Xe[e[n]];
  return t;
}
function w(e, t) {
  return (e & 65535) * t + (((e >>> 16) * t & 65535) << 16);
}
function M(e, t) {
  return e << t | e >>> 32 - t;
}
function P(e) {
  return (Object.prototype.toString.call(e).match(/^\[object (\S+?)\]$/) || [])[1]?.toLowerCase() || "undefined";
}
const E = {
  isString: (e) => P(e) === "string",
  isNumber: (e) => P(e) === "number",
  isNumberFinity: (e) => Number.isFinite(e),
  isNegativeInfinity: (e) => e === Number.NEGATIVE_INFINITY,
  isPositiveInfinity: (e) => e === Number.POSITIVE_INFINITY,
  isNaN: (e) => Number.isNaN(e),
  isObject: (e) => P(e) === "object",
  isArray: (e) => P(e) === "array",
  isBoolean: (e) => P(e) === "boolean",
  isSymbol: (e) => P(e) === "symbol",
  isUndefined: (e) => P(e) === "undefined",
  isNull: (e) => P(e) === "null",
  isDate: (e) => P(e) === "date",
  isBigIng: (e) => P(e) === "bigint",
  isMap: (e) => P(e) === "map",
  isSet: (e) => P(e) === "set",
  isWeakMap: (e) => P(e) === "weakmap",
  isWeakSet: (e) => P(e) === "weakset",
  isRegExp: (e) => P(e) === "regexp",
  isFunc: (e) => ["asyncfunction", "function"].includes(P(e)),
  isError: (e) => P(e) === "error",
  isNil: (e) => E.isUndefined(e) || E.isNull(e)
};
function re(e) {
  return e ? [...e].reduce((t, n) => t += Math.abs(n), 0) : 0;
}
function X(e, t) {
  return new Promise((n) => {
    setTimeout(n, e, t);
  });
}
function ce(e) {
  if (!E.isString(e))
    throw new TypeError("Expected a string");
  return e && We.hash128(e).slice(0, 10);
}
function _e(e) {
  return parseInt(e, 10);
}
function C(e) {
  return parseFloat(e);
}
function O(e, t) {
  return E.isNumber(e) && Number.isNaN(e) ? t : e;
}
function k(e) {
  return e.reduce((t, n) => t + (n ? 1 : 0), 0);
}
function f(e, t) {
  return E.isNil(e) ? !1 : Object.hasOwn(e, t) ? !0 : t in e;
}
function W(e, t = /* @__PURE__ */ new WeakMap()) {
  if (E.isNull(e) || !E.isObject(e))
    return e;
  if (t.has(e))
    return t.get(e);
  switch (P(e)) {
    case "array":
      return e.map((n) => W(n, t));
    case "object": {
      const n = {};
      t.set(e, n);
      for (const o in e)
        f(e, o) && (n[o] = W(e[o], t));
      return n;
    }
    case "date":
      return new Date(e);
    case "regexp":
      return new RegExp(e);
    case "map":
      return new Map([...e.entries()].map(([n, o]) => [n, W(o, t)]));
    case "set":
      return new Set([...e].map((n) => W(n, t)));
    default:
      return e;
  }
}
function Ke(e) {
  return /^function\s.*?\{\s*\[native code]\s*}$/.test(String(e));
}
function F(e, t) {
  return t ? matchMedia(`(${e}: ${t})`).matches : (n) => matchMedia(`(${e}: ${n})`).matches;
}
class $e extends Error {
  data;
  response;
  status;
  constructor(t, n) {
    super(`Request failed with status ${t.status}`), this.data = n, this.name = L.RESPONSE, this.response = t, this.status = t.status;
  }
}
async function Ye(e, t) {
  const n = await fetch(e, t), o = await n.json();
  if (n.ok)
    return o;
  throw new $e(n, o);
}
function Ze(e, t = 1) {
  if (Math.abs(t) >= 1)
    return Math.round(e / t) * t;
  const n = 1 / t;
  return Math.round(e * n) / n;
}
function Je() {
  return document.fullscreenElement || document.msFullscreenElement || document.mozFullScreenElement || document.webkitFullscreenElement || null;
}
function Qe() {
  return (document.exitFullscreen || document.msExitFullscreen || document.mozCancelFullScreen || document.webkitExitFullscreen).call(document);
}
function et(e, t) {
  return E.isObject(e) ? Object.fromEntries(
    Object.entries(e).map(([n, o]) => {
      if (E.isObject(o)) {
        const r = Object.fromEntries(
          Object.entries(o).filter(([a]) => !t.includes(a))
        );
        return [n, r];
      }
      return [n, o];
    })
  ) : e;
}
async function pe({
  action: e,
  initialHtml: t,
  domPollInterval: n = 50
}, ...o) {
  for (; !document.body; )
    await X(n);
  const r = document.createElement("iframe");
  try {
    for (await new Promise((a, i) => {
      let s = !1;
      const c = () => {
        s = !0, a();
      }, l = (p) => {
        s = !0, i(p);
      };
      r.onload = c, r.onerror = l;
      const { style: m } = r;
      m.setProperty("display", "block", "important"), m.position = "absolute", m.top = "0", m.left = "0", m.visibility = "hidden", t && "srcdoc" in r ? r.srcdoc = t : r.src = "about:blank", document.body.appendChild(r);
      const u = () => {
        s || (r.contentWindow?.document?.readyState === "complete" ? c() : setTimeout(u, 10));
      };
      u();
    }); !r.contentWindow?.document?.body; )
      await X(n);
    return await e(r, r.contentWindow, ...o);
  } finally {
    r.parentNode?.removeChild(r);
  }
}
const ve = Math.random();
function tt(e, t) {
  return Math.floor(Math.random() * (t - e + 1)) + e;
}
function nt(e, t, n) {
  const { length: o } = t, r = 20, a = tt(275, o - (r + 1)), i = a + r / 2, s = a + r;
  t.getChannelData(0)[a] = e, t.getChannelData(0)[i] = e, t.getChannelData(0)[s] = e, t.copyFromChannel(n, 0);
  const c = [
    t.getChannelData(0)[a] === 0 ? Math.random() : 0,
    t.getChannelData(0)[i] === 0 ? Math.random() : 0,
    t.getChannelData(0)[s] === 0 ? Math.random() : 0
  ], m = [...t.getChannelData(0), ...n, ...c];
  return [...new Set(m)].filter((y) => y !== 0);
}
function rt(e, t, n) {
  const o = n.map(() => e);
  t.copyToChannel(o, 0);
  const r = t.getChannelData(0), [a] = r;
  return [...r].map((s) => s !== a || s === 0 ? Math.random() : s).filter((s) => s !== a);
}
function ot(e) {
  return new Promise((t) => {
    const n = e.createAnalyser(), o = e.createOscillator(), r = e.createDynamicsCompressor();
    try {
      o.type = "triangle", o.frequency.value = 1e4, r.threshold.value = -50, r.knee.value = 40, r.attack.value = 0;
    } catch {
    }
    o.connect(r), r.connect(n), r.connect(e.destination), o.start(0), e.startRendering(), e.addEventListener("complete", (a) => {
      try {
        r.disconnect(), o.disconnect();
        const i = new Float32Array(n.frequencyBinCount);
        n.getFloatFrequencyData(i);
        const s = new Float32Array(n.fftSize);
        return f(n, "getFloatTimeDomainData") && n.getFloatTimeDomainData(s), t({
          floatFrequencyData: i,
          floatTimeDomainData: s,
          buffer: a.renderedBuffer,
          compressorGainReduction: (
            // @ts-expect-error if unsupported
            r.reduction.value || r.reduction
          )
        });
      } catch {
        return t(null);
      }
    });
  });
}
function at() {
  const e = new OfflineAudioContext(1, 100, 44100), t = e.createOscillator();
  return t.frequency.value = 0, t.start(0), e.startRendering(), new Promise((n) => {
    const o = setTimeout(() => n(!1), 2500);
    e.oncomplete = (r) => {
      clearTimeout(o);
      const a = r.renderedBuffer.getChannelData?.(0);
      if (!a) {
        n(!1);
        return;
      }
      const i = `${[...new Set(a)]}` != "0";
      n(i);
    };
  }).finally(() => t.disconnect());
}
function it() {
  try {
    const t = new AudioBuffer({ length: 2e3, sampleRate: 44100 }), n = new Float32Array(2e3), o = nt(ve, t, n), r = rt(ve, t, n), a = [.../* @__PURE__ */ new Set([...o, ...r])], i = a.reduce((s, c) => s + +c, 0);
    return +(a.length !== 1 && i);
  } catch {
    return 0;
  }
}
function oe(e, t, n) {
  const o = [];
  for (let r = t; r < n; r++)
    o.push(e[r]);
  return o;
}
async function st() {
  try {
    window.OfflineAudioContext = OfflineAudioContext || webkitOfflineAudioContext;
  } catch {
  }
  if (!window.OfflineAudioContext)
    return null;
  const e = 5e3, t = {
    sampleNoiseDetected: !1,
    channelDataMismatch: !1,
    audioFake: !1,
    unexpectedFrequency: !1
  }, n = new OfflineAudioContext(1, e, 44100), o = n.createAnalyser(), r = n.createOscillator(), a = n.createDynamicsCompressor(), i = n.createBiquadFilter(), s = new Float32Array(o.frequencyBinCount);
  o.getFloatFrequencyData?.(s), new Set(s).size > 1 && (t.unexpectedFrequency = !0);
  const [
    l,
    m
  ] = await Promise.all([
    ot(new OfflineAudioContext(1, e, 44100)),
    at().catch(() => !1)
  ]);
  m && (t.audioFake = !0);
  const {
    floatFrequencyData: u,
    floatTimeDomainData: p,
    buffer: y,
    compressorGainReduction: d
  } = l || {}, g = re(u), h = re(p), I = new Float32Array(e);
  let A = new Float32Array();
  y && (y.copyFromChannel(I, 0), A = y.getChannelData(0) || []);
  const b = oe([...I], 4500, 4600), v = oe([...A], 4500, 4600), ee = re(oe([...A], 4500, e)), te = `${v}` == `${b}`;
  "copyFromChannel" in AudioBuffer.prototype && !te && (t.channelDataMismatch = !0);
  const ne = (/* @__PURE__ */ new Set([...A])).size, we = it() || [...new Set(A.slice(0, 100))].reduce((Se, ke) => Se += ke, 0);
  we && (t.sampleNoiseDetected = !0);
  const Ue = E.isUndefined(v[0]) ? null : ce(`${v}`), Be = E.isUndefined(b[0]) ? null : ce(`${b}`);
  return {
    lies: t,
    noise: we,
    binsSample: Ue,
    copySample: Be,
    sampleSum: ee || null,
    totalUniqueSamples: ne,
    compressorGainReduction: d || null,
    floatFrequencyDataSum: g || null,
    floatTimeDomainDataSum: h || null,
    analyserNode: {
      channelCount: o.channelCount,
      channelCountMode: o.channelCountMode,
      channelInterpretation: o.channelInterpretation,
      fftSize: o.fftSize,
      frequencyBinCount: o.frequencyBinCount,
      maxDecibels: o.maxDecibels,
      minDecibels: o.minDecibels,
      numberOfInputs: o.numberOfInputs,
      numberOfOutputs: o.numberOfOutputs,
      smoothingTimeConstant: o.smoothingTimeConstant,
      context: {
        sampleRate: o.context.sampleRate,
        listener: {
          forwardX: {
            maxValue: o.context.listener.forwardX.maxValue
          }
        }
      }
    },
    biquadFilterNode: {
      gain: {
        maxValue: i.gain.maxValue
      },
      frequency: {
        defaultValue: i.frequency.defaultValue,
        maxValue: i.frequency.maxValue
      }
    },
    dynamicsCompressorNode: {
      attack: {
        defaultValue: a.attack.defaultValue
      },
      knee: {
        defaultValue: a.knee.defaultValue,
        maxValue: a.knee.maxValue
      },
      ratio: {
        defaultValue: a.ratio.defaultValue,
        maxValue: a.ratio.maxValue
      },
      release: {
        defaultValue: a.release.defaultValue,
        maxValue: a.release.maxValue
      },
      threshold: {
        defaultValue: a.threshold.defaultValue,
        minValue: a.threshold.minValue
      }
    },
    oscillatorNode: {
      detune: {
        maxValue: r.detune.maxValue,
        minValue: r.detune.minValue
      },
      frequency: {
        defaultValue: r.frequency.defaultValue,
        maxValue: r.frequency.maxValue,
        minValue: r.frequency.minValue
      }
    }
  };
}
function ct() {
  const e = window.AudioContext || window.webkitAudioContext;
  return e ? new e().baseLatency ?? null : null;
}
function lt() {
  return !!f(navigator, "getBattery");
}
function ut() {
  return f(navigator, "bluetooth");
}
const mt = [
  "AbortSignal",
  "Array",
  "ArrayBuffer",
  "Atomics",
  "BigInt",
  "Boolean",
  "Date",
  "Document",
  "Element",
  "Error",
  "Function",
  "GPU",
  "Intl",
  "JSON",
  "Map",
  "Math",
  "Navigation",
  "Navigator",
  "Number",
  "Object",
  "PerformanceNavigationTiming",
  "Promise",
  "Proxy",
  "RTCRtpReceiver",
  "ReadableStream",
  "Reflect",
  "RegExp",
  "SVGAElement",
  "Set",
  "ShadowRoot",
  "String",
  "Symbol",
  "WeakMap",
  "WeakSet",
  "WebAssembly",
  "WebSocketStream"
];
function dt() {
  const e = {};
  for (const t of mt)
    if (f(window, t)) {
      const n = window[t], r = Object.getOwnPropertyNames(n).filter((a) => E.isFunc(n[a]));
      e[t] = r;
    }
  return e;
}
async function ft(e, t) {
  gt(e, t), await X(0);
  const n = e.toDataURL(), o = e.toDataURL();
  return n !== o ? [N.UNSTABLE, N.UNSTABLE] : (ht(e, t), await X(0), [e.toDataURL(), n]);
}
function pt(e, t) {
  e.width = 21, e.height = 120, t.fillStyle = "#66666666", t.fillRect(0, 0, 21, 120), t.font = "8pt Times New Roman", t.fillText("H", 6, 14);
}
function gt(e, t) {
  e.width = 240, e.height = 60, t.textBaseline = "alphabetic", t.fillStyle = "#f60", t.fillRect(100, 1, 62, 20), t.fillStyle = "#069", t.font = '11pt "Times New Roman"';
  const n = "Cwm fjordbank gly 😃";
  t.fillText(n, 2, 15), t.fillStyle = "rgba(102, 204, 0, 0.2)", t.font = "18pt Arial", t.fillText(n, 4, 45);
}
function ht(e, t) {
  e.width = 122, e.height = 110, t.globalCompositeOperation = "multiply";
  for (const [n, o, r] of [
    ["#f2f", 40, 40],
    ["#2ff", 80, 40],
    ["#ff2", 60, 80]
  ])
    t.fillStyle = n, t.beginPath(), t.arc(o, r, 40, 0, Math.PI * 2, !0), t.closePath(), t.fill();
  t.fillStyle = "#f9c", t.arc(60, 60, 60, 0, Math.PI * 2, !0), t.arc(60, 60, 20, 0, Math.PI * 2, !0), t.fill("evenodd");
}
function le() {
  const e = document.createElement("canvas");
  return e.width = 1, e.height = 1, [e, e.getContext("2d")];
}
function yt(e) {
  return e.rect(0, 0, 10, 10), e.rect(2, 2, 6, 6), !e.isPointInPath(5, 5, "evenodd");
}
function Oe(e, t) {
  return !!(t && e.toDataURL) && e.toDataURL().indexOf("data:image/png;base64") !== -1;
}
function De() {
  return k([
    f(window, "MSCSSMatrix"),
    f(window, "msSetImmediate"),
    f(window, "msIndexedDB"),
    f(navigator, "msMaxTouchPoints"),
    f(navigator, "msPointerEnabled")
  ]) >= 4;
}
function wt() {
  return k([
    f(window, "msWriteProfilerMark"),
    f(window, "MSStream"),
    f(navigator, "msLaunchUri"),
    f(navigator, "msSaveBlob")
  ]) >= 3 && !De();
}
function ge() {
  return Ke(window.print) ? k([
    String(window.browser) === "[object WebPageNamespace]",
    f(window, "MicrodataExtractor")
  ]) >= 1 : !1;
}
function j() {
  return k([
    f(window, "ApplePayError"),
    f(window, "CSSPrimitiveValue"),
    f(window, "WebKitMediaKeys"),
    f(window, "Counter"),
    f(navigator, "getStorageUpdates"),
    navigator.vendor.indexOf("Apple") === 0
  ]) >= 4;
}
function he() {
  const { CSS: e, HTMLButtonElement: t } = window;
  return k([
    f(window, "CSSCounterStyleRule"),
    !f(navigator, "getStorageUpdates"),
    t && f(t.prototype, "popover"),
    e.supports("font-size-adjust: ex-height 0.5"),
    e.supports("text-transform: full-width")
  ]) >= 4;
}
function Ne() {
  return k([
    f(window, "webkitResolveLocalFileSystemURL"),
    f(window, "BatteryManager"),
    f(window, "webkitMediaStream"),
    f(window, "webkitSpeechGrammar"),
    f(navigator, "webkitPersistentStorage"),
    f(navigator, "webkitTemporaryStorage"),
    navigator.vendor.indexOf("Google") === 0
  ]) >= 5;
}
function St() {
  return Ne() && !j();
}
async function bt() {
  const [e, t] = le(), [n, o] = le();
  if (!(St() && Oe(e, t) && o))
    return null;
  const r = 21, a = 120, i = [
    131,
    132,
    133,
    134,
    135,
    136,
    137,
    138,
    139,
    140,
    153,
    154,
    155,
    158,
    159,
    174,
    175,
    176,
    179,
    180,
    195,
    196,
    197,
    198,
    199,
    200,
    201,
    216,
    217,
    218,
    221,
    222,
    237,
    238,
    239,
    242,
    243,
    258,
    259,
    260,
    263,
    264,
    278,
    279,
    280,
    281,
    282,
    283,
    284,
    285,
    286,
    287,
    156,
    157,
    160,
    219,
    220
  ];
  e.width = r, e.height = a, n.width = r, n.height = a, pt(e, t);
  const s = e.toDataURL();
  return new Promise((c) => {
    const l = new Image();
    l.onload = () => {
      const m = [], u = [];
      o.drawImage(l, 0, 0);
      const p = t.getImageData(0, 0, e.width, e.height), y = o.getImageData(0, 0, n.width, n.height), d = Array.from(p.data), g = Array.from(y.data);
      let h = [];
      d.forEach((b, v) => {
        b !== 102 && h.push(Math.floor(v / 4));
      }), h = [...new Set(h)];
      const I = h.filter((b) => !i.includes(b)), A = I.map(
        (b) => [b * 4, b * 4 + 1, b * 4 + 2, b * 4 + 3].map((v) => d[v])
      );
      g.forEach((b, v) => {
        b !== d[v] && (m.push(v), u.push(b - d[v]));
      }), c({
        diffIndexes: m,
        diffValues: u,
        significantPixelIndexes: I,
        significantPixelValues: A
      });
    }, l.onerror = () => c(null), l.src = s;
  });
}
async function Tt() {
  let e = !1, t = !1, n, o;
  const [r, a] = le();
  if (!Oe(r, a))
    n = N.UNSUPPORTED, o = N.UNSUPPORTED;
  else if (e = yt(a), j() && he() && ge())
    n = N.SKIPPED, o = N.SKIPPED;
  else {
    const { diffIndexes: i } = await bt() ?? {};
    t = !!i && !!i.join(""), [n, o] = await ft(r, a);
  }
  return {
    spoofing: t,
    winding: e,
    geometry: n,
    text: o
  };
}
const Et = {
  simpleTest: {
    style: `
      border: solid 2.715px green;
      padding: 3.98px;
      margin-left: 12.12px;
    `,
    block: "<div>Simple Test (1)</div>"
  },
  transformTest: {
    style: `
      border: solid 2px purple;
      font-size: 30px;
      margin-top: 200px;
      -webkit-transform: skewY(23.1753218deg);
      -moz-transform: skewY(23.1753218deg);
      -ms-transform: skewY(23.1753218deg);
      -o-transform: skewY(23.1753218deg);
      transform: skewY(23.1753218deg);
    `,
    block: "<div>Transformation Test (2)</div>"
  },
  scaleTest: {
    style: `
      border: solid 2.89px orange;
      font-size: 45px;
      transform: scale(100000000000000000000009999999999999.99, 1.89);
      margin-top: 50px;
    `,
    block: "<div>WW&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Scale Test (3)</div>"
  },
  vendorSpecificTransformationTest: {
    style: `
      border: solid 2px silver;
      transform: matrix(1.11, 2.0001, -1.0001, 1.009, 150, 94.4);
      -webkit-transform: matrix(0.95559, 2.13329, -0.9842, 0.98423, 150, 95);
      -moz-transform: matrix(
        0.66371,
        1.94587,
        -0.6987,
        0.98423,
        150,
        103.238
      );
      -ms-transform: matrix(0.5478, 1.94587, -0.7383, 0.98423, 150, 100.569);
      -o-transform: matrix(0.4623, 1.83523, -0.6734, 0.81231, 150, 99.324);
      position: absolute;
      margin-top: 11.1331px;
      margin-left: 12.1212px;
      padding: 4.4545px;
      left: 239.4141px;
      top: 178.505px;
    `,
    block: "<div>Vendor specific transformation Test (4)</div>"
  },
  tableCaptionTest: {
    style: `
      border: solid 2pt red;
      margin-left: 42.395pt;
    `,
    block: `
      <table>
        <caption>Table caption Test (5)</caption>
        <thead><tr><th>Table head</th></tr></thead>
        <tbody><tr><td>Table body</td></tr></tbody>
      </table>
    `
  },
  transformPerspectiveTest: {
    style: `
      border: solid 2px darkblue;
      -webkit-transform: perspective(12890px) translateZ(101.5px);
      -moz-transform: perspective(12890px) translateZ(101.5px);
      -ms-transform: perspective(12890px) translateZ(101.5px);
      -o-transform: perspective(12890px) translateZ(101.5px);
      transform: perspective(12890px) translateZ(101.5px);
      padding: 12px;
    `,
    block: "<div>transform: perspective(12890px) translateZ(101.5px); Test (6)</div>"
  },
  selectionOptionTest: {
    style: `
      position: absolute;
      margin-top: -350.552px;
      margin-left: 0.9099rem;
      border: solid 2px burlywood;
    `,
    block: `
      <div>
        <select>
            <option>selection-option (Test 7)</option>
        </select>
      </div>
    `
  },
  detailSummaryTest: {
    style: `
      position: absolute;
      margin-top: -150.552px;
      margin-left: 15.9099rem;
      border: solid 2px sandybrown;
    `,
    block: `
      <div>
        <details>
          <summary>detail summary (Test 8)</summary>
        </details>
      </div>
    `
  },
  progressTest: {
    style: `
      position: absolute;
      margin-top: -110.552px;
      margin-left: 15.9099rem;
      border: solid 2px orchid;
    `,
    block: '<div><progress value="49" max="100"></progress></div>'
  },
  buttonTest: {
    style: `
      position: absolute;
      margin-top: -315.552px;
      margin-left: 15.9099rem;
      border: solid 2px turquoise;
    `,
    block: '<div><button type="button"></button></div>'
  }
};
function At(e) {
  if (!e)
    throw new Error("No element");
  const t = document.createElement("template");
  t.innerHTML = e.block.trim();
  const n = t.content.firstChild;
  return n.style.cssText = e.style, n.outerHTML;
}
async function vt() {
  return pe({ action: Pt });
}
async function Pt(e, t) {
  const n = [];
  e.style.width = "700px", e.style.height = "600px";
  const o = t.document, { head: r, body: a } = o, i = Object.values(Et).map(At).join(""), s = o.createElement("style");
  s.textContent = `
    caption {
      border: solid 2px darkred;
      font-size: 20.99px;
      margin-left: 20.8px;
    }
  `, r.appendChild(s), a.innerHTML = i;
  const c = Array.from(a.children);
  for (const l of c) {
    const {
      bottom: m,
      top: u,
      left: p,
      right: y,
      width: d,
      height: g,
      x: h,
      y: I
    } = l.getBoundingClientRect();
    n.push({
      bottom: m,
      top: u,
      left: p,
      right: y,
      width: d,
      height: g,
      x: h,
      y: I
    });
  }
  return n;
}
function It() {
  return window.screen.colorDepth;
}
function Mt() {
  for (const e of ["srgb", "p3", "rec2020"])
    if (F("color-gamut", e))
      return e;
  return null;
}
function xt() {
  const e = ["srgb", "p3", "rec2020"], t = {};
  return f(window, "matchMedia") ? e.forEach((n) => {
    t[n] = window.matchMedia(`(color-gamut: ${n})`).matches;
  }) : e.forEach((n) => {
    t[n] = !1;
  }), t;
}
function Rt() {
  const e = document.createElement("div");
  document.body.appendChild(e);
  const t = window.getComputedStyle(e), n = [];
  for (let o = 0; o < t.length; o++)
    n.push(t[o]);
  for (const o in t)
    !n.includes(o) && Number.isNaN(Number(o)) && n.push(o);
  return document.body.removeChild(e), n.sort();
}
function Ct() {
  const e = F("prefers-contrast");
  return e("no-preference") ? H.NONE : e("high") || e("more") ? H.MORE : e("low") || e("less") ? H.LESS : e("forced") ? H.FORCED_COLORS : null;
}
function Ft() {
  try {
    document.cookie = "cookietest=1; SameSite=Strict;";
    const e = document.cookie.indexOf("cookietest=") !== -1;
    return document.cookie = "cookietest=1; SameSite=Strict; expires=Thu, 01-Jan-1970 00:00:01 GMT", e;
  } catch {
    return !1;
  }
}
const _t = {
  "accent-color": ["initial"],
  "anchor-name": ["--tooltip"],
  "border-end-end-radius": ["initial"],
  color: ["light-dark"],
  fill: ["context-fill", "context-stroke"],
  float: ["inline-start", "inline-end"],
  "font-size": ["1cap", "1rcap"],
  "grid-template-rows": ["subgrid"],
  "paint-order": ["normal", "stroke", "markers", "fill", "revert"],
  stroke: ["context-fill", "context-stroke"],
  "text-decoration": ["spelling-error"],
  "text-wrap": ["pretty"],
  "transform-box": ["stroke-box"]
};
function Ot() {
  const e = document.createElement("div");
  document.body.appendChild(e);
  const t = {};
  for (const [n, o] of Object.entries(_t)) {
    t[n] = {};
    for (const r of o)
      e.style[n] = r, t[n][r] = e.style[n] === r;
  }
  return document.body.removeChild(e), t;
}
function Dt() {
  return window.devicePixelRatio;
}
async function Nt() {
  if (!navigator.requestMediaKeySystemAccess)
    return { supported: !1 };
  const e = ["com.widevine.alpha", "com.microsoft.playready", "com.apple.fps.1_0", "org.w3.clearkey"], t = [
    {
      initDataTypes: ["cenc"],
      audioCapabilities: [{ contentType: 'audio/mp4; codecs="mp4a.40.2"' }],
      videoCapabilities: [{ contentType: 'video/mp4; codecs="avc1.42E01E"' }]
    }
  ];
  try {
    const n = await Promise.all(
      e.map((o) => navigator.requestMediaKeySystemAccess(o, t).then(() => ({ [o]: !0 })).catch(() => ({ [o]: !1 })))
    );
    return {
      supported: !0,
      systems: Object.assign({}, ...n)
    };
  } catch {
    return { supported: !1 };
  }
}
function Lt() {
  return [
    "FileReader",
    "FileList",
    "File",
    "FileSystemDirectoryHandle",
    "FileSystemFileHandle",
    "FileSystemHandle",
    "FileSystemWritableFileStream",
    "showOpenFilePicker",
    "showSaveFilePicker",
    "webkitRequestFileSystem",
    "webkitResolveLocalFileSystemURL"
  ].filter((t) => f(window, t));
}
function Ut() {
  const { mimeTypes: e } = navigator;
  let t = !1;
  try {
    t = new ActiveXObject("ShockwaveFlash.ShockwaveFlash");
  } catch {
    e && e["application/x-shockwave-flash"] && e["application/x-shockwave-flash"].enabledPlugin && (t = !0);
  }
  return t;
}
const Bt = "mmMwWLliI0fiflO&1", ae = {
  /**
   * The default font. User can change it in desktop Chrome, desktop Firefox, IE 11,
   * Android Chrome (but only when the size is ≥ than the default) and Android Firefox.
   */
  default: [],
  /** OS font on macOS. User can change its size and weight. Applies after Safari restart. */
  apple: [{ font: "-apple-system-body" }],
  /** User can change it in desktop Chrome and desktop Firefox. */
  serif: [{ fontFamily: "serif" }],
  /** User can change it in desktop Chrome and desktop Firefox. */
  sans: [{ fontFamily: "sans-serif" }],
  /** User can change it in desktop Chrome and desktop Firefox. */
  mono: [{ fontFamily: "monospace" }],
  /**
   * Check the smallest allowed font size. User can change it in desktop Chrome, desktop Firefox and desktop Safari.
   * The height can be 0 in Chrome on a retina display.
   */
  min: [{ fontSize: "1px" }],
  /** Tells one OS from another in desktop Chrome. */
  system: [{ fontFamily: "system-ui" }]
};
function kt() {
  return Vt((e, t) => {
    const n = {}, o = {};
    for (const r of Object.keys(ae)) {
      const [a = {}, i = Bt] = ae[r], s = e.createElement("span");
      s.textContent = i, s.style.whiteSpace = "nowrap";
      for (const c of Object.keys(a)) {
        const l = a[c];
        l && (s.style[c] = l);
      }
      n[r] = s, t.append(e.createElement("br"), s);
    }
    for (const r of Object.keys(ae))
      o[r] = n[r].getBoundingClientRect().width;
    return o;
  });
}
function Vt(e, t = 4e3) {
  return pe({
    action: (r, a) => {
      const i = a.document, s = i.body, c = s.style;
      c.width = `${t}px`, c.webkitTextSizeAdjust = "none", c.textSizeAdjust = "none", Ne() ? s.style.zoom = `${1 / a.devicePixelRatio}` : j() && (s.style.zoom = "reset");
      const l = i.createElement("div");
      return l.textContent = [...Array(t / 20 << 0)].map(() => "word").join(" "), s.appendChild(l), e(i, s);
    },
    initialHtml: '<!doctype html><html><head><meta name="viewport" content="width=device-width, initial-scale=1">'
  });
}
function Ht() {
  const e = ["Consolas", "Windows sans-serif", "Windows serif", "mix Consolas"], t = document.createElement("span");
  t.style.position = "absolute", t.style.left = "-9999px", t.style.fontSize = "12px", t.style.lineHeight = "normal", t.textContent = "abcdefghijklmnopqrstuvwxyz0123456789", document.body.appendChild(t);
  const n = e.map((o) => (t.style.fontFamily = o, {
    font: o,
    offsetWidth: t.offsetWidth,
    offsetHeight: t.offsetHeight
  }));
  return document.body.removeChild(t), n;
}
const Gt = "48px", Wt = "mmmMMMmmmlllmmmLLL₹▁₺ꜽ�₸׆ẞॿmmmiiimmmIIImmmwwwmmmWWW", U = ["monospace", "sans-serif", "serif"], Le = [
  "ARNO PRO",
  "Agency FB",
  "Andale Mono",
  "Apple Braille",
  "Apple Chancery",
  "Apple Color Emoji",
  "Apple SD Gothic Neo",
  "Apple Symbols",
  "AppleGothic",
  "Arabic Typesetting",
  "Arial",
  "Arial Black",
  "Arial Hebrew",
  "Arial MT",
  "Arial Narrow",
  "Arial Rounded MT Bold",
  "Arial Unicode MS",
  "AvantGarde Bk BT",
  "BankGothic Md BT",
  "Batang",
  "Bitstream Vera Sans Mono",
  "Book Antiqua",
  "Bookman Old Style",
  "Calibri",
  "Cambria",
  "Cambria Math",
  "Century",
  "Century Gothic",
  "Century Schoolbook",
  "Clarendon",
  "Comic Sans",
  "Comic Sans MS",
  "Consolas",
  "Courier",
  "Courier New",
  "EUROSTILE",
  "Franklin Gothic",
  "Futura Bk BT",
  "Futura Md BT",
  "GOTHAM",
  "Garamond",
  "Geneva",
  "Georgia",
  "Gill Sans",
  "HELV",
  "Haettenschweiler",
  "Helvetica",
  "Helvetica Neue",
  "Humanst521 BT",
  "Impact",
  "LUCIDA GRANDE",
  "Leelawadee",
  "Letter Gothic",
  "Levenim MT",
  "Lucida Bright",
  "Lucida Calligraphy",
  "Lucida Console",
  "Lucida Fax",
  "Lucida Grande",
  "Lucida Handwriting",
  "Lucida Sans",
  "Lucida Sans Typewriter",
  "Lucida Sans Unicode",
  "MS Gothic",
  "MS Mincho",
  "MS Outlook",
  "MS PGothic",
  "MS Reference Sans Serif",
  "MS Reference Specialty",
  "MS Sans Serif",
  "MS Serif",
  "MS UI Gothic",
  "MT Extra",
  "MYRIAD",
  "MYRIAD PRO",
  "Marlett",
  "Meiryo UI",
  "Menlo",
  "Microsoft Himalaya",
  "Microsoft JhengHei",
  "Microsoft Sans Serif",
  "Microsoft Tai Le",
  "Microsoft Uighur",
  "Microsoft YaHei",
  "Microsoft Yi Baiti",
  "Minion Pro",
  "Monaco",
  "Monotype Corsiva",
  "PMingLiU",
  "Palatino",
  "Palatino Linotype",
  "Pristina",
  "SCRIPTINA",
  "Segoe Print",
  "Segoe Script",
  "Segoe UI",
  "Segoe UI Light",
  "Segoe UI Semibold",
  "Segoe UI Symbol",
  "Serifa",
  "SimHei",
  "Small Fonts",
  "Staccato222 BT",
  "TRAJAN PRO",
  "Tahoma",
  "Times",
  "Times New Roman",
  "Times New Roman PS",
  "Trebuchet MS",
  "Univers CE 55 Medium",
  "Verdana",
  "Vrinda",
  "Webdings",
  "Wingdings",
  "Wingdings 2",
  "Wingdings 3",
  "ZWAdobeF",
  "sans-serif-thin"
];
function Xt(e = Le) {
  return pe({
    action: jt
  }, e);
}
async function jt(e, { document: t }, n) {
  const o = t.body;
  o.style.fontSize = Gt;
  const r = t.createElement("div");
  r.style.setProperty("visibility", "hidden", "important");
  const a = {}, i = {}, s = (d) => {
    const g = t.createElement("span"), { style: h } = g;
    return h.position = "absolute", h.top = "0", h.left = "0", h.fontFamily = d, g.textContent = Wt, r.appendChild(g), g;
  }, c = (d, g) => s(`'${d}',${g}`), l = () => U.map(s), m = () => {
    const d = {};
    for (const g of n)
      d[g] = U.map((h) => c(g, h));
    return d;
  }, u = (d) => U.some(
    (g, h) => d[h].offsetWidth !== a[g] || d[h].offsetHeight !== i[g]
  ), p = l(), y = m();
  o.appendChild(r), await X(0);
  for (let d = 0; d < U.length; d++)
    a[U[d]] = p[d].offsetWidth, i[U[d]] = p[d].offsetHeight;
  return Le.filter((d) => u(y[d]));
}
function qt() {
  const e = F("forced-colors");
  return e("active") ? !0 : e("none") ? !1 : null;
}
function zt() {
  return navigator.globalPrivacyControl ?? null;
}
const Kt = [
  "1.0",
  "1.1",
  "1.2",
  "1.3",
  "1.4",
  "2.0",
  "2.1",
  "2.2",
  "2.3"
], $t = [{
  videoCapabilities: [{
    contentType: 'video/webm; codecs="vp09.00.10.08"',
    robustness: "SW_SECURE_DECODE"
  }]
}];
async function Yt() {
  try {
    const t = await (await navigator.requestMediaKeySystemAccess("com.widevine.alpha", $t)).createMediaKeys();
    if (!("getStatusForPolicy" in t))
      return "HDCP Policy Check API is not available";
    const n = {}, o = [];
    for (const r of Kt) {
      const i = t.getStatusForPolicy({ minHdcpVersion: r }).then((s) => {
        n[r] = s !== "usable" ? s : "available";
      });
      o.push(i);
    }
    return await Promise.all(o), n;
  } catch (e) {
    return console.log(e), null;
  }
}
function Zt() {
  const e = F("dynamic-range");
  return e("high") ? !0 : e("standard") ? !1 : null;
}
function Jt() {
  if (De() || wt())
    return null;
  try {
    return !!window.indexedDB;
  } catch {
    return !0;
  }
}
function Qt() {
  return E.isUndefined(Intl) ? null : {
    dateTimeOptions: V(Intl.DateTimeFormat),
    numberFormatOptions: V(Intl.NumberFormat),
    collatorOptions: V(Intl.Collator),
    pluralRulesOptions: V(Intl.PluralRules),
    relativeTimeFormatOptions: V(Intl.RelativeTimeFormat)
  };
}
function V(e) {
  return new e().resolvedOptions();
}
function en() {
  const e = F("inverted-colors");
  return e("inverted") ? !0 : e("none") ? !1 : null;
}
function tn() {
  return navigator.javaEnabled();
}
function nn() {
  try {
    return !!window.localStorage;
  } catch {
    return !0;
  }
}
function rn() {
  const e = () => 0, t = Math.acos || e, n = Math.acosh || e, o = Math.asin || e, r = Math.asinh || e, a = Math.atanh || e, i = Math.atan || e, s = Math.sin || e, c = Math.sinh || e, l = Math.cos || e, m = Math.cosh || e, u = Math.tan || e, p = Math.tanh || e, y = Math.exp || e, d = Math.expm1 || e, g = Math.log1p || e, h = (S) => Math.PI ** S, I = (S) => Math.log(S + Math.sqrt(S * S - 1)), A = (S) => Math.log(S + Math.sqrt(S * S + 1)), b = (S) => Math.log((1 + S) / (1 - S)) / 2, v = (S) => Math.exp(S) - 1 / Math.exp(S) / 2, ee = (S) => (Math.exp(S) + 1 / Math.exp(S)) / 2, te = (S) => Math.exp(S) - 1, ye = (S) => (Math.exp(2 * S) - 1) / (Math.exp(2 * S) + 1), ne = (S) => Math.log(1 + S);
  return {
    acos: t(0.12312423423423424),
    acosh: n(1e308),
    acoshPf: I(1e154),
    asin: o(0.12312423423423424),
    asinh: r(1),
    asinhPf: A(1),
    atanh: a(0.5),
    atanhPf: b(0.5),
    atan: i(0.5),
    sin: s(-1e300),
    sinh: c(1),
    sinhPf: v(1),
    cos: l(10.000000000123),
    cosh: m(1),
    coshPf: ee(1),
    tan: u(-1e300),
    tanh: p(1),
    tanhPf: ye(1),
    exp: y(1),
    expm1: d(1),
    expm1Pf: te(1),
    log1p: g(10),
    log1pPf: ne(10),
    powPI: h(-100)
  };
}
function on() {
  if (!(navigator.mediaDevices && navigator.mediaDevices.getSupportedConstraints))
    return console.warn("MediaDevices API is not supported"), null;
  const e = {}, t = navigator.mediaDevices.getSupportedConstraints();
  for (const n in t)
    e[n] = t[n];
  return e;
}
async function an() {
  if (!f(navigator, "mediaCapabilities"))
    return [];
  const e = [
    {
      type: "file",
      video: {
        contentType: 'video/mp4; codecs="avc1.42E01E"',
        width: 1920,
        height: 1080,
        bitrate: 2646242,
        framerate: 30
      }
    },
    {
      type: "file",
      video: {
        contentType: 'video/webm; codecs="vp9"',
        width: 1920,
        height: 1080,
        bitrate: 2646242,
        framerate: 30
      }
    },
    {
      type: "file",
      video: {
        contentType: 'video/ogg; codecs="theora"',
        width: 1280,
        height: 720,
        bitrate: 15e5,
        framerate: 30
      }
    },
    {
      type: "media-source",
      video: {
        contentType: 'video/mp4; codecs="avc1.42E01E"',
        width: 1920,
        height: 1080,
        bitrate: 2646242,
        framerate: 30
      }
    },
    {
      type: "media-source",
      video: {
        contentType: 'video/webm; codecs="vp9"',
        width: 1920,
        height: 1080,
        bitrate: 2646242,
        framerate: 30
      }
    },
    {
      type: "media-source",
      video: {
        contentType: 'video/ogg; codecs="theora"',
        width: 1280,
        height: 720,
        bitrate: 15e5,
        framerate: 30
      }
    }
  ];
  return await Promise.all(
    e.map(async (n) => {
      try {
        const o = await navigator.mediaCapabilities.decodingInfo(n);
        return {
          contentType: n.video.contentType,
          powerEfficient: o.powerEfficient,
          smooth: o.smooth,
          supported: o.supported,
          keySystemAccess: o.keySystemAccess
        };
      } catch {
        return {
          contentType: n.video.contentType,
          powerEfficient: !1,
          smooth: !1,
          supported: !1,
          keySystemAccess: null
        };
      }
    })
  );
}
function sn() {
  if (!F("min-monochrome", "0"))
    return null;
  for (let n = 0; n <= 100; ++n)
    if (F("max-monochrome", n.toString()))
      return n;
  throw new Error("Too high value");
}
async function cn() {
  const e = {}, { plugins: t, mimeTypes: n, userAgentData: o } = navigator, r = [
    "userAgent",
    "appName",
    "appVersion",
    "appCodeName",
    "deviceMemory",
    "hardwareConcurrency",
    "platform",
    "product",
    "language",
    "languages",
    "oscpu",
    "cpuClass",
    "productSub",
    "vendorSub",
    "vendor",
    "maxTouchPoints",
    "doNotTrack",
    "pdfViewerEnabled",
    "cookieEnabled",
    "onLine",
    "webdriver",
    "userAgentData"
  ], a = [
    "architecture",
    "bitness",
    "brands",
    "mobile",
    "model",
    "platform",
    "platformVersion",
    "uaFullVersion",
    "wow64",
    "fullVersionList"
  ];
  for (const i of r)
    E.isUndefined(navigator[i]) || (e[i] = navigator[i]);
  e.mimeTypes = n ? {} : null;
  for (const i of n)
    e.mimeTypes[i.type] = {
      description: i.description,
      suffixes: i.suffixes,
      enabledPlugin: i.enabledPlugin.name
    };
  e.plugins = t ? [] : null;
  for (let i = 0; i < t?.length; ++i) {
    const s = t[i];
    if (!s)
      continue;
    const c = [];
    for (let l = 0; l < s.length; ++l) {
      const m = s[l];
      c.push({
        type: m.type,
        suffixes: m.suffixes
      });
    }
    e.plugins.push({
      name: s.name,
      description: s.description,
      filename: s.filename,
      mimeTypes: c
    });
  }
  return e.highEntropyValues = await o?.getHighEntropyValues(a) ?? null, e;
}
function ln() {
  const e = [];
  for (const t in window.navigator)
    e.push(t);
  return e;
}
async function un() {
  return f(navigator, "connection");
}
function mn() {
  return !!window.openDatabase;
}
function dn() {
  const e = F("prefers-reduced-motion");
  return e("reduce") ? !0 : e("no-preference") ? !1 : null;
}
function fn() {
  const e = F("prefers-reduced-transparency");
  return e("reduce") ? !0 : e("no-preference") ? !1 : null;
}
function pn() {
  return f(navigator, "scheduling") ? {
    isInputPending: navigator.scheduling.isInputPending ? navigator.scheduling.isInputPending() : null
  } : null;
}
function q(e) {
  return e === null ? null : Ze(e, 10);
}
function ue() {
  return [
    O(C(window.screen.availTop), null),
    O(C(window.screen.width) - C(window.screen.availWidth) - O(C(window.screen.availLeft), 0), null),
    O(C(window.screen.height) - C(window.screen.availHeight) - O(C(window.screen.availTop), 0), null),
    O(C(window.screen.availLeft), null)
  ];
}
function me(e) {
  for (let t = 0; t < 4; ++t)
    if (e[t])
      return !1;
  return !0;
}
let z = null, ie = null;
async function gn() {
  hn();
  let e = ue();
  if (me(e)) {
    if (z)
      return [...z];
    Je() && (await Qe(), e = ue());
  }
  return me(e) || (z = e), e;
}
function hn() {
  if (ie !== null)
    return;
  const e = 2500, t = () => {
    const n = ue();
    me(n) ? ie = setTimeout(t, e) : (z = n, ie = null);
  };
  t();
}
async function yn() {
  if (j() && he() && ge())
    return null;
  const e = await gn();
  return [
    q(e[0]),
    q(e[1]),
    q(e[2]),
    q(e[3])
  ];
}
function wn() {
  if (j() && he() && ge())
    return null;
  const t = (o) => O(_e(o), null), n = [
    t(window.screen.width),
    t(window.screen.height)
  ];
  return n.sort().reverse(), n;
}
function Sn() {
  try {
    return !!window.sessionStorage;
  } catch {
    return !0;
  }
}
function bn() {
  if (f(window, "ActiveXObject"))
    try {
      return new window.ActiveXObject("AgControl.AgControl"), !0;
    } catch {
      return !1;
    }
  const e = navigator.mimeTypes["application/x-silverlight-2"];
  return !E.isUndefined(e) && !E.isNull(e.enabledPlugin);
}
async function Tn() {
  return f(window, "speechSynthesis") ? new Promise((e) => {
    let t = window.speechSynthesis.getVoices();
    t.length ? e(Pe(t)) : window.speechSynthesis.onvoiceschanged = () => {
      t = window.speechSynthesis.getVoices(), e(Pe(t));
    };
  }) : null;
}
function Pe(e) {
  return e.map((t) => ({
    default: t.default,
    lang: t.lang,
    localService: t.localService,
    name: t.name,
    voiceURI: t.voiceURI
  }));
}
async function En() {
  if (navigator.storage && navigator.storage.estimate)
    try {
      const e = await navigator.storage.estimate();
      return {
        quota: e.quota,
        usage: e.usage
      };
    } catch (e) {
      return console.error("Error when retrieving storage information: ", e), null;
    }
  return console.warn("The storage API is not supported"), null;
}
function An() {
  return [
    "length",
    "name",
    "prototype",
    "for",
    "keyFor",
    "asyncIterator",
    "hasInstance",
    "isConcatSpreadable",
    "iterator",
    "match",
    "matchAll",
    "replace",
    "search",
    "species",
    "split",
    "toPrimitive",
    "toStringTag",
    "unscopables",
    "dispose"
  ].filter((t) => f(Symbol, t));
}
function vn() {
  const e = ["serif", "sans-serif", "monospace", "cursive", "fantasy", "system-ui"], t = [
    "ActiveText",
    "ButtonFace",
    "ButtonText",
    "Canvas",
    "CanvasText",
    "Field",
    "FieldText",
    "GrayText",
    "Highlight",
    "HighlightText",
    "LinkText",
    "Mark",
    "MarkText",
    "VisitedText"
  ], n = document.createElement("canvas"), o = n.getContext("2d");
  if (!o)
    return console.warn("Failed to get canvas context"), null;
  const r = t.map((i) => (o.fillStyle = i, o.fillStyle)), a = e.map((i) => (o.font = `12px ${i}`, o.font));
  return n.remove(), { colors: r, fonts: a };
}
function Pn() {
  const e = window.Intl?.DateTimeFormat;
  if (e) {
    const o = new e().resolvedOptions().timeZone;
    if (o)
      return o;
  }
  const t = (/* @__PURE__ */ new Date()).getFullYear(), n = -Math.max(
    C(new Date(t, 0, 1).getTimezoneOffset()),
    C(new Date(t, 6, 1).getTimezoneOffset())
  );
  return `UTC${n >= 0 ? "+" : ""}${n}`;
}
function In() {
  let e = 0, t;
  navigator.maxTouchPoints !== void 0 && (e = _e(navigator.maxTouchPoints));
  try {
    document.createEvent("TouchEvent"), t = !0;
  } catch {
    t = !1;
  }
  const n = f(window, "ontouchstart");
  return {
    maxTouchPoints: e,
    touchEvent: t,
    touchStart: n
  };
}
const Mn = [
  // Blink and some browsers on iOS
  "chrome",
  // Safari on macOS
  "safari",
  // Chrome on iOS (checked in 85 on 13 and 87 on 14)
  "__crWeb",
  "__gCrWeb",
  // Yandex Browser on iOS, macOS and Android (checked in 21.2 on iOS 14, macOS and Android)
  "yandex",
  // Yandex Browser on iOS (checked in 21.2 on 14)
  "__yb",
  "__ybro",
  // Firefox on iOS (checked in 32 on 14)
  "__firefox__",
  // Edge on iOS (checked in 46 on 14)
  "__edgeTrackingPreventionStatistics",
  "webkit",
  // Opera Touch on iOS (checked in 2.6 on 14)
  "oprt",
  // Samsung Internet on Android (checked in 11.1)
  "samsungAr",
  // UC Browser on Android (checked in 12.10 and 13.0)
  "ucweb",
  "UCShellJava",
  // Puffin on Android (checked in 9.0)
  "puffinDevice"
];
function xn() {
  const e = [];
  for (const t of Mn) {
    const n = window[t];
    n && typeof n == "object" && e.push(t);
  }
  return e.sort();
}
function Ie(e, t) {
  const n = e.getShaderPrecisionFormat(e[t], e.HIGH_FLOAT), o = e.getShaderPrecisionFormat(e[t], e.MEDIUM_FLOAT);
  if (!(n || o))
    return null;
  let r = n;
  return n.precision || (r = o), [r.precision, r.rangeMin, r.rangeMax];
}
function Rn(e) {
  const t = e.getShaderPrecisionFormat(e.FRAGMENT_SHADER, e.HIGH_FLOAT), n = e.getShaderPrecisionFormat(e.FRAGMENT_SHADER, e.HIGH_INT);
  if (!(t && n))
    return null;
  const o = t.precision !== 0 ? "highp/" : "mediump/", r = n.rangeMax !== 0 ? "highp" : "lowp";
  return `${o}${r}`;
}
function Cn(e) {
  const t = e.getExtension("EXT_texture_filter_anisotropic") || e.getExtension("WEBKIT_EXT_texture_filter_anisotropic") || e.getExtension("MOZ_EXT_texture_filter_anisotropic");
  if (!t)
    return null;
  let n = e.getParameter(t.MAX_TEXTURE_MAX_ANISOTROPY_EXT);
  return n === 0 && (n = 2), n;
}
function se(e, t) {
  const n = e.getParameter(e[t]);
  return n ? Object.values(n) : null;
}
function Me(e, t) {
  const n = t.map((r) => e.getParameter(e[r]));
  return n.some((r) => r != null) ? n : null;
}
const D = "n/a", Fn = ["FRAGMENT_SHADER", "VERTEX_SHADER"], _n = ["LOW_FLOAT", "MEDIUM_FLOAT", "HIGH_FLOAT", "LOW_INT", "MEDIUM_INT", "HIGH_INT"], On = [
  "copyBufferSubData",
  "getBufferSubData",
  "blitFramebuffer",
  "framebufferTextureLayer",
  "getInternalformatParameter",
  "invalidateFramebuffer",
  "invalidateSubFramebuffer",
  "readBuffer",
  "renderbufferStorageMultisample",
  "texStorage2D",
  "texStorage3D",
  "texImage3D",
  "texSubImage3D",
  "copyTexSubImage3D",
  "compressedTexImage3D",
  "compressedTexSubImage3D",
  "getFragDataLocation",
  "uniform1ui",
  "uniform2ui",
  "uniform3ui",
  "uniform4ui",
  "uniform1uiv",
  "uniform2uiv",
  "uniform3uiv",
  "uniform4uiv",
  "uniformMatrix2x3fv",
  "uniformMatrix3x2fv",
  "uniformMatrix2x4fv",
  "uniformMatrix4x2fv",
  "uniformMatrix3x4fv",
  "uniformMatrix4x3fv",
  "vertexAttribI4i",
  "vertexAttribI4iv",
  "vertexAttribI4ui",
  "vertexAttribI4uiv",
  "vertexAttribIPointer",
  "vertexAttribDivisor",
  "drawArraysInstanced",
  "drawElementsInstanced",
  "drawRangeElements",
  "drawBuffers",
  "clearBufferiv",
  "clearBufferuiv",
  "clearBufferfv",
  "clearBufferfi",
  "createQuery",
  "deleteQuery",
  "isQuery",
  "beginQuery",
  "endQuery",
  "getQuery",
  "getQueryParameter",
  "createSampler",
  "deleteSampler",
  "isSampler",
  "bindSampler",
  "samplerParameteri",
  "samplerParameterf",
  "getSamplerParameter",
  "fenceSync",
  "isSync",
  "deleteSync",
  "clientWaitSync",
  "waitSync",
  "getSyncParameter",
  "createTransformFeedback",
  "deleteTransformFeedback",
  "isTransformFeedback",
  "bindTransformFeedback",
  "beginTransformFeedback",
  "endTransformFeedback",
  "transformFeedbackVaryings",
  "getTransformFeedbackVarying",
  "pauseTransformFeedback",
  "resumeTransformFeedback",
  "bindBufferBase",
  "bindBufferRange",
  "getIndexedParameter",
  "getUniformIndices",
  "getActiveUniforms",
  "getUniformBlockIndex",
  "getActiveUniformBlockParameter",
  "getActiveUniformBlockName",
  "uniformBlockBinding",
  "createVertexArray",
  "deleteVertexArray",
  "isVertexArray",
  "bindVertexArray"
], xe = {
  vertexShader: [
    "MAX_VERTEX_ATTRIBS",
    "MAX_VERTEX_UNIFORM_VECTORS",
    "MAX_VERTEX_TEXTURE_IMAGE_UNITS",
    "MAX_VARYING_VECTORS",
    "VERTEX_BEST_FLOAT_PRECISION",
    "MAX_VERTEX_UNIFORM_COMPONENTS",
    "MAX_VERTEX_UNIFORM_BLOCKS",
    "MAX_VERTEX_OUTPUT_COMPONENTS",
    "MAX_VARYING_COMPONENTS"
  ],
  transformFeedback: [
    "MAX_TRANSFORM_FEEDBACK_INTERLEAVED_COMPONENTS",
    "MAX_TRANSFORM_FEEDBACK_SEPARATE_ATTRIBS",
    "MAX_TRANSFORM_FEEDBACK_SEPARATE_COMPONENTS"
  ],
  rasterizer: [
    "ALIASED_POINT_SIZE_RANGE",
    "ALIASED_LINE_WIDTH_RANGE"
  ],
  fragmentShader: [
    "MAX_FRAGMENT_UNIFORM_VECTORS",
    "MAX_TEXTURE_IMAGE_UNITS",
    "FLOAT_INT_PRECISION",
    "FRAGMENT_BEST_FLOAT_PRECISION",
    "MAX_FRAGMENT_UNIFORM_COMPONENTS",
    "MAX_FRAGMENT_UNIFORM_BLOCKS",
    "MAX_FRAGMENT_INPUT_COMPONENTS",
    "MIN_PROGRAM_TEXEL_OFFSET",
    "MAX_PROGRAM_TEXEL_OFFSET"
  ],
  framebuffer: [
    "MAX_DRAW_BUFFERS",
    "MAX_COLOR_ATTACHMENTS",
    "MAX_SAMPLES",
    "RGBA_BITS",
    "DEPTH_STENCIL_BITS",
    "MAX_RENDERBUFFER_SIZE",
    "MAX_VIEWPORT_DIMS"
  ],
  textures: [
    "MAX_TEXTURE_SIZE",
    "MAX_CUBE_MAP_TEXTURE_SIZE",
    "MAX_COMBINED_TEXTURE_IMAGE_UNITS",
    "MAX_TEXTURE_MAX_ANISOTROPY_EXT",
    "MAX_3D_TEXTURE_SIZE",
    "MAX_ARRAY_TEXTURE_LAYERS",
    "MAX_TEXTURE_LOD_BIAS"
  ],
  uniformBuffers: [
    "MAX_UNIFORM_BUFFER_BINDINGS",
    "MAX_UNIFORM_BLOCK_SIZE",
    "UNIFORM_BUFFER_OFFSET_ALIGNMENT",
    "MAX_COMBINED_UNIFORM_BLOCKS",
    "MAX_COMBINED_VERTEX_UNIFORM_COMPONENTS",
    "MAX_COMBINED_FRAGMENT_UNIFORM_COMPONENTS"
  ]
}, Dn = [
  "r8unorm",
  "r8snorm",
  "r8uint",
  "r8sint",
  "r16uint",
  "r16sint",
  "r16float",
  "rg8unorm",
  "rg8snorm",
  "rg8uint",
  "rg8sint",
  "r32uint",
  "r32sint",
  "r32float",
  "rg16uint",
  "rg16sint",
  "rg16float",
  "rgba8unorm",
  "rgba8unorm-srgb",
  "rgba8snorm",
  "rgba8uint",
  "rgba8sint",
  "bgra8unorm",
  "bgra8unorm-srgb",
  "rgb9e5ufloat",
  "rgb10a2unorm",
  "rg11b10ufloat",
  "rg32uint",
  "rg32sint",
  "rg32float",
  "rgba16uint",
  "rgba16sint",
  "rgba16float",
  "rgba32uint",
  "rgba32sint",
  "rgba32float",
  "stencil8",
  "depth16unorm",
  "depth24plus",
  "depth24plus-stencil8",
  "depth32float",
  "depth32float-stencil8",
  "bc1-rgba-unorm",
  "bc1-rgba-unorm-srgb",
  "bc2-rgba-unorm",
  "bc2-rgba-unorm-srgb",
  "bc3-rgba-unorm",
  "bc3-rgba-unorm-srgb",
  "bc4-r-unorm",
  "bc4-r-snorm",
  "bc5-rg-unorm",
  "bc5-rg-snorm",
  "bc6h-rgb-ufloat",
  "bc6h-rgb-float",
  "bc7-rgba-unorm",
  "bc7-rgba-unorm-srgb",
  "etc2-rgb8unorm",
  "etc2-rgb8unorm-srgb",
  "etc2-rgb8a1unorm",
  "etc2-rgb8a1unorm-srgb",
  "etc2-rgba8unorm",
  "etc2-rgba8unorm-srgb",
  "eac-r11unorm",
  "eac-r11snorm",
  "eac-rg11unorm",
  "eac-rg11snorm",
  "astc-4x4-unorm",
  "astc-4x4-unorm-srgb",
  "astc-5x4-unorm",
  "astc-5x4-unorm-srgb",
  "astc-5x5-unorm",
  "astc-5x5-unorm-srgb",
  "astc-6x5-unorm",
  "astc-6x5-unorm-srgb",
  "astc-6x6-unorm",
  "astc-6x6-unorm-srgb",
  "astc-8x5-unorm",
  "astc-8x5-unorm-srgb",
  "astc-8x6-unorm",
  "astc-8x6-unorm-srgb",
  "astc-8x8-unorm",
  "astc-8x8-unorm-srgb",
  "astc-10x5-unorm",
  "astc-10x5-unorm-srgb",
  "astc-10x6-unorm",
  "astc-10x6-unorm-srgb",
  "astc-10x8-unorm",
  "astc-10x8-unorm-srgb",
  "astc-10x10-unorm",
  "astc-10x10-unorm-srgb",
  "astc-12x10-unorm",
  "astc-12x10-unorm-srgb",
  "astc-12x12-unorm",
  "astc-12x12-unorm-srgb"
], Nn = `
	precision mediump float;
	attribute vec2 vertPosition;
	attribute vec3 vertColor;
	varying vec3 fragColor;
	void main() {
	  fragColor = vertColor;
	  gl_Position = vec4(vertPosition, 0.0, 1.0);
	}
`, Ln = `
	precision mediump float;
	varying vec3 fragColor;
	void main() {
		gl_FragColor = vec4(fragColor, 1.0);
	}
`;
function Un(e) {
  const t = [], n = ["webgl2", "experimental-webgl2", "webgl", "experimental-webgl", "moz-webgl"];
  for (const o of n) {
    let r = null;
    try {
      r = e.getContext(o);
    } catch {
    }
    r && t.push({
      context: r,
      contextName: o
    });
    const a = document.createElement("canvas");
    a.width = e.width, a.height = e.height, e.replaceWith(a), e = a;
  }
  return t;
}
function Bn(e) {
  const { context: t, contextName: n } = e || {};
  if (!t)
    return null;
  const o = t.getExtension("WEBGL_debug_renderer_info"), r = t.getParameter(t.VERSION) || D, a = t.getParameter(t.SHADING_LANGUAGE_VERSION) || D, i = t.getParameter(t.VENDOR) || D, s = t.getParameter(t.RENDERER) || D, c = o && t.getParameter(o.UNMASKED_VENDOR_WEBGL) || D, l = o && t.getParameter(o.UNMASKED_RENDERER_WEBGL) || D;
  return {
    contextName: n,
    version: r,
    shadingLanguageVersion: a,
    vendor: i,
    renderer: s,
    unmaskedVendor: c,
    unmaskedRenderer: l
  };
}
function kn(e) {
  if (!e)
    return null;
  const t = {};
  if (!!window.WebGL2RenderingContext) {
    const i = [];
    for (const s of On)
      e[s] && i.push(s);
    t.supportedFunctions = i.sort();
  }
  const o = e.getContextAttributes();
  o && (t.contextAttributes = o);
  for (const i in xe) {
    const s = {};
    for (const c of xe[i]) {
      let l = null;
      const m = {
        ALIASED_LINE_WIDTH_RANGE: () => se(e, c),
        ALIASED_POINT_SIZE_RANGE: () => se(e, c),
        DEPTH_STENCIL_BITS: () => Me(e, ["DEPTH_BITS", "STENCIL_BITS"]),
        FLOAT_INT_PRECISION: () => Rn(e),
        FRAGMENT_BEST_FLOAT_PRECISION: () => Ie(e, "FRAGMENT_SHADER"),
        MAX_TEXTURE_MAX_ANISOTROPY_EXT: () => Cn(e),
        MAX_VIEWPORT_DIMS: () => se(e, c),
        RGBA_BITS: () => Me(e, ["RED_BITS", "GREEN_BITS", "BLUE_BITS", "ALPHA_BITS"]),
        VERTEX_BEST_FLOAT_PRECISION: () => Ie(e, "VERTEX_SHADER")
      };
      try {
        m[c] ? l = m[c]() : l = e.getParameter(e[c]);
      } catch {
      }
      s[c] = l ?? D;
    }
    t[i] = s;
  }
  const r = {};
  for (const i of Fn) {
    r[i] = {};
    for (const s of _n) {
      const c = e.getShaderPrecisionFormat(e[i], e[s]), l = c ? [c.rangeMin, c.rangeMax, c.precision] : [];
      r[i][s] = l.join(",");
    }
  }
  t.shaderPrecisions = r;
  const a = e.getSupportedExtensions();
  if (a) {
    const i = [];
    for (const s of a)
      i.push(s);
    t.extensions = i.sort();
  }
  return t;
}
function Vn(e, t) {
  const { width: n, height: o } = e, r = new Uint8Array(n * o * 4);
  Hn(t), t.readPixels(0, 0, n, o, t.RGBA, t.UNSIGNED_BYTE, r);
  const a = fe(r);
  return ce(a);
}
function Hn(e) {
  e.clear(e.COLOR_BUFFER_BIT | e.DEPTH_BUFFER_BIT);
  const t = e.createShader(e.VERTEX_SHADER), n = e.createShader(e.FRAGMENT_SHADER);
  if (e.shaderSource(t, Nn), e.shaderSource(n, Ln), e.compileShader(t), !e.getShaderParameter(t, e.COMPILE_STATUS)) {
    console.error("ERROR compiling vertex shader!", e.getShaderInfoLog(t));
    return;
  }
  if (e.compileShader(n), !e.getShaderParameter(n, e.COMPILE_STATUS)) {
    console.error("ERROR compiling fragment shader!", e.getShaderInfoLog(n));
    return;
  }
  const o = e.createProgram();
  if (e.attachShader(o, t), e.attachShader(o, n), e.linkProgram(o), !e.getProgramParameter(o, e.LINK_STATUS)) {
    console.error("ERROR linking program!", e.getProgramInfoLog(o));
    return;
  }
  if (e.validateProgram(o), !e.getProgramParameter(o, e.VALIDATE_STATUS)) {
    console.error("ERROR validating program!", e.getProgramInfoLog(o));
    return;
  }
  const r = [
    // X, Y,   R, G, B
    0,
    0.5,
    1,
    1,
    0,
    -0.5,
    -0.5,
    0.7,
    0,
    1,
    0.5,
    -0.5,
    0.1,
    1,
    0.6
  ], a = e.createBuffer();
  e.bindBuffer(e.ARRAY_BUFFER, a), e.bufferData(e.ARRAY_BUFFER, new Float32Array(r), e.STATIC_DRAW);
  const i = e.getAttribLocation(o, "vertPosition"), s = e.getAttribLocation(o, "vertColor");
  e.vertexAttribPointer(i, 2, e.FLOAT, !1, 5 * Float32Array.BYTES_PER_ELEMENT, 0), e.vertexAttribPointer(s, 3, e.FLOAT, !1, 5 * Float32Array.BYTES_PER_ELEMENT, 2 * Float32Array.BYTES_PER_ELEMENT), e.enableVertexAttribArray(i), e.enableVertexAttribArray(s), e.useProgram(o), e.drawArrays(e.TRIANGLES, 0, 3);
}
function Gn() {
  const e = {
    webglImageHash: "",
    supportedWebGLContexts: []
  }, t = document.createElement("canvas");
  t.width = 256, t.height = 128;
  const n = Un(t);
  if (!n.length)
    return null;
  const [o] = n;
  e.webglImageHash = Vn(t, o.context);
  for (const r of n) {
    const a = Bn(r), {
      contextAttributes: i = null,
      shaderPrecisions: s = null,
      supportedFunctions: c = null,
      extensions: l = null,
      vertexShader: m = null,
      transformFeedback: u = null,
      rasterizer: p = null,
      fragmentShader: y = null,
      framebuffer: d = null,
      textures: g = null,
      uniformBuffers: h = null
    } = kn(r.context) || {};
    e.supportedWebGLContexts.push({
      basics: a,
      contextAttributes: i,
      shaderPrecisions: s,
      vertexShader: m,
      transformFeedback: u,
      rasterizer: p,
      fragmentShader: y,
      framebuffer: d,
      textures: g,
      uniformBuffers: h,
      extensions: l,
      supportedFunctions: c
    });
  }
  return e;
}
async function Wn() {
  const e = {}, t = document.createElement("canvas"), o = !!t.transferControlToOffscreen && t.transferControlToOffscreen();
  try {
    navigator.gpu && (e.api = !0);
    const r = await navigator.gpu.requestAdapter();
    if (r) {
      e.adapter = !0;
      const a = await navigator.gpu.requestAdapter({ compatibilityMode: !0 });
      e.compat = !!a, await r.requestDevice() && (e.device = !0, o && (e.context = !!o.getContext("webgpu")));
    }
  } catch (r) {
    console.error(r);
  }
  try {
    const a = new OffscreenCanvas(300, 150).getContext("2d");
    e.offscreen = !0, e.twoD = !!a;
  } catch (r) {
    console.error(r);
  }
  return e;
}
async function Xn(e) {
  try {
    const t = await navigator.gpu.requestAdapter(e);
    if (!t)
      return null;
    const n = Array.from(t.features), { limits: o } = t, [r, a] = await Promise.all([
      t.requestDevice({ requiredFeatures: n }),
      t.requestAdapterInfo()
    ]), i = await jn(r), s = {};
    for (const l in o)
      s[l] = o[l];
    const c = {};
    for (const l in a)
      c[l] = a[l];
    return {
      info: c,
      limits: s,
      features: n,
      textureFormatCapabilities: i,
      flags: {
        isCompatibilityMode: t.isCompatibilityMode,
        isFallbackAdapter: t.isFallbackAdapter
      }
    };
  } catch (t) {
    return console.error(t), null;
  }
}
async function jn(e) {
  try {
    const t = [];
    for (const n of Dn)
      try {
        let o = 1, r = 1;
        if ((n.startsWith("bc") || n.startsWith("e")) && (o = 4, r = 4), n.startsWith("astc")) {
          const i = n.match(/(\d+)x(\d+)/);
          i && (o = parseInt(i[1], 10), r = parseInt(i[2], 10));
        }
        const a = GPUTextureUsage;
        e.createTexture({
          size: [o, r, 1],
          format: n,
          usage: a.SAMPLED | a.OUTPUT_ATTACHMENT | a.STORAGE | a.COPY_SRC | a.COPY_DST
        }), t.push(n);
      } catch {
      }
    return t;
  } catch (t) {
    return console.error(t), null;
  }
}
const qn = {
  fallback: {
    powerPreference: "low-power",
    forceFallbackAdapter: !0
  },
  highPerformance: { powerPreference: "high-performance" }
};
async function zn() {
  try {
    const e = {
      statuses: null
    };
    if (e.statuses = await Wn(), !e.statuses.adapter)
      return e;
    e.supportedAdapters = {};
    const t = [];
    for (const [n, o] of Object.entries(qn)) {
      const r = Xn(o).then((a) => {
        e.supportedAdapters[n] = a;
      });
      t.push(r);
    }
    return await Promise.all(t), e;
  } catch (e) {
    return console.error(e), null;
  }
}
function Kn() {
  return [
    "onwebkitanimationend",
    "onwebkitanimationiteration",
    "onwebkitanimationstart",
    "onwebkittransitionend",
    "onwebkitfullscreenchange",
    "onwebkitfullscreenerror",
    "webkitMatchesSelector",
    "webkitRequestFullScreen",
    "webkitRequestFullscreen"
  ].filter((t) => f(document.documentElement, t));
}
const $n = {
  navigator: cn,
  cookiesEnabled: Ft,
  sessionStorage: Sn,
  localStorage: nn,
  openDatabase: mn,
  indexedDB: Jt,
  activeX: Ve,
  silverlight: bn,
  flash: Ut,
  java: tn,
  batteryAPI: lt,
  bluetoothAPI: ut,
  networkAPI: un,
  timezone: Pn,
  architecture: He,
  devicePixelRatio: Dt,
  globalPrivacyControl: zt,
  colorDepth: It,
  colorGamut: Mt,
  hdr: Zt,
  hdcp: Yt,
  invertedColors: en,
  forcedColors: qt,
  monochromeDepth: sn,
  contrastPreference: Ct,
  reducedMotion: fn,
  reducedTransparency: dn,
  vendorFlavors: xn,
  touchSupport: In,
  scheduling: pn,
  baseLatency: ct,
  screenResolution: wn,
  screenFrame: yn,
  intl: Qt,
  math: rn,
  fontPreferences: kt,
  fonts: Xt,
  audio: st,
  canvas: Tt,
  clientRects: vt,
  speechSynthesisVoices: Tn,
  webgl: Gn,
  webgpu: zn,
  storageQuota: En,
  mediaCapabilities: on,
  computedStyleProperties: Rt,
  systemInfo: vn,
  drmSupport: Nt,
  fileAPIs: Lt,
  symbolProperties: An,
  webkitAPIs: Kn,
  builtInObjects: dt,
  cssSupport: Ot,
  colorSpaceSupport: xt,
  fontRendering: Ht,
  navigatorProperties: ln,
  mediaDecodingCapabilities: an
};
async function Yn() {
  if (f(navigator, "getBattery")) {
    const e = await navigator.getBattery();
    return {
      charging: e.charging,
      chargingTime: e.chargingTime,
      dischargingTime: e.dischargingTime,
      level: e.level
    };
  }
  return null;
}
async function Zn() {
  return await Jn() || Qn();
}
function Jn() {
  let e = !1;
  const t = new Worker(
    URL.createObjectURL(
      new Blob(
        [
          `
          "use strict";
            onmessage = () => {
              postMessage({ isOpenBeat: true });
              debugger;
              postMessage({ isOpenBeat: false });
            };
          `
        ],
        { type: "text/javascript" }
      )
    )
  );
  return new Promise((n) => {
    let o;
    t.onmessage = (r) => {
      r.data.isOpenBeat ? o = setTimeout(() => {
        e = !0, t.terminate(), n(e);
      }, 100) : (clearTimeout(o), e = !1, t.terminate(), n(e));
    }, t.postMessage({});
  });
}
function Qn() {
  const t = window.outerWidth - window.innerWidth > 160, n = window.outerHeight - window.innerHeight > 160;
  return t || n;
}
const er = {
  enableHighAccuracy: !0,
  maximumAge: 0,
  timeout: 10 * 1e3
};
async function tr() {
  try {
    const e = {
      statuses: {
        api: !0
      }
    };
    if (!navigator.geolocation)
      return e.statuses.api = !1, e;
    const t = await navigator.permissions.query({ name: "geolocation" });
    if (e.statuses.permission = t.state, t.state === "denied")
      return e;
    const n = await nr();
    return rr(e, n), e;
  } catch (e) {
    return console.error(e), null;
  }
}
async function nr() {
  return new Promise((e) => {
    const t = (n) => {
      e({
        success: !1,
        error: {
          code: n.code,
          message: n.message
        }
      });
    };
    navigator.geolocation.getCurrentPosition(e, t, er);
  });
}
function rr(e, t) {
  or(t) ? e.geolocationPosition = {
    timestamp: t.timestamp,
    latitude: t.coords.latitude,
    longitude: t.coords.longitude,
    accuracy: t.coords.accuracy,
    altitude: t.coords.altitude,
    altitudeAccuracy: t.coords.altitudeAccuracy,
    heading: t.coords.heading,
    speed: t.coords.speed
  } : ar(t) ? e.error = t.error : console.error("Unknown result type from getGeolocationData() :>>", t);
}
function or(e) {
  return !!e.coords;
}
function ar(e) {
  return !!e.error;
}
function ir() {
  const e = [];
  for (const t in window)
    f(window, t) && e.push(t);
  return e;
}
async function sr() {
  try {
    const e = await Ye("https://ipgeo.myip.link/");
    return e ? Object.entries(e).reduce((t, [n, o]) => {
      if (!["isEu", "metroCode", "regionCode", "airport"].includes(n)) {
        const r = n === "timezone" && typeof o == "object" && f(o, "name");
        t[n] = r ? o.name : o;
      }
      return t;
    }, {}) : null;
  } catch (e) {
    return console.error(e), null;
  }
}
function cr() {
  const { performance: e } = window;
  return e && e.memory ? {
    jsHeapSizeLimit: e.memory.jsHeapSizeLimit,
    totalJSHeapSize: e.memory.totalJSHeapSize,
    usedJSHeapSize: e.memory.usedJSHeapSize
  } : (console.warn("The memory API is not supported"), null);
}
function lr() {
  if (f(navigator, "connection")) {
    const { connection: e } = navigator;
    return {
      type: e.type ?? null,
      effectiveType: e.effectiveType ?? null,
      downlink: e.downlink ?? null,
      downlinkMax: e.downlinkMax ?? null,
      rtt: e.rtt ?? null,
      saveData: e.saveData ?? null
    };
  }
  return null;
}
function ur() {
  const {
    performance: { navigation: e, timing: t }
  } = window, n = performance.getEntriesByType("navigation")[0], o = performance.getEntriesByType("paint");
  return {
    commitLoadTime: t.responseStart,
    finishDocumentLoadTime: t.domContentLoadedEventEnd,
    finishLoadTime: t.loadEventEnd,
    firstPaintAfterLoadTime: o.length > 0 ? o[0].startTime : 0,
    firstPaintTime: o.length > 0 ? o[0].startTime + t.navigationStart : 0,
    navigationType: ["navigate", "reload", "back_forward", "prerender"][e.type],
    npnNegotiatedProtocol: n ? n.nextHopProtocol : "unknown",
    requestTime: t.requestStart,
    startLoadTime: t.fetchStart,
    wasAlternateProtocolAvailable: n ? n.alternateProtocolUsage === "used" : !1,
    wasFetchedViaSpdy: n ? n.nextHopProtocol.includes("h2") || n.nextHopProtocol.includes("h3") : !1,
    wasNpnNegotiated: n ? n.nextHopProtocol !== "http/1.1" : !1
  };
}
function mr() {
  const e = {};
  return [
    "colorDepth",
    "pixelDepth",
    "height",
    "width",
    "availHeight",
    "availWidth",
    "availTop",
    "availLeft",
    "windowSize"
  ].forEach((n) => {
    n === "windowSize" ? e.windowSize = dr() : (window.screen[n] || Number.isInteger(window.screen[n])) && (e[n] = window.screen[n]);
  }), e;
}
function dr() {
  return {
    width: document.body?.clientWidth || window.innerWidth,
    height: document.body?.clientHeight || window.innerHeight
  };
}
async function fr(e = { iceServer: "stun.l.google.com:19302" }, t = 4e3) {
  const n = /* @__PURE__ */ new Set(), o = { iceServers: [{ urls: `stun:${e.iceServer}` }] }, r = new RTCPeerConnection(o);
  try {
    r.createDataChannel("");
    const a = await r.createOffer();
    await r.setLocalDescription(a), await new Promise((l) => {
      const m = setTimeout(() => {
        l();
      }, t);
      r.onicegatheringstatechange = () => {
        r.iceGatheringState === "complete" && (clearTimeout(m), l());
      };
    });
    const i = r.localDescription?.sdp || "", s = [...i.matchAll(/(?:c=IN IP4|c=IN IP6) ([\d.a-fA-F:]+)/g)];
    for (const l of s) {
      const m = l[1];
      m && !n.has(m) && n.add(m);
    }
    const c = {
      public: [],
      private: [],
      allRes: Array.from(n),
      log: i
    };
    for (const l of n)
      pr(l) ? c.private.push(l) : l.endsWith(".local") || c.public.push(l);
    return c;
  } catch (a) {
    throw a;
  } finally {
    r.close();
  }
}
function pr(e) {
  return [
    /^10\.\d{1,3}\.\d{1,3}\.\d{1,3}$/,
    /^172\.(1[6-9]|2[0-9]|3[0-1])\.\d{1,3}\.\d{1,3}$/,
    /^192\.168\.\d{1,3}\.\d{1,3}$/,
    /^127\.\d{1,3}\.\d{1,3}\.\d{1,3}$/
  ].some((t) => t.test(e));
}
const gr = {
  globalObjests: ir,
  devToolsOpen: Zn,
  screen: mr,
  location: sr,
  geolocation: tr,
  memory: cr,
  performance: ur,
  networkInfo: lr,
  batteryInfo: Yn,
  webrtc: fr
}, hr = 2e3, yr = 12e3;
async function Re(e, t) {
  const n = {}, { only: o, exclude: r, timeout: a } = t || {};
  if (o && r)
    throw new Error('Cannot use both "only" and "exclude" options');
  const i = o && !a ? yr : a || hr, s = o ? o.filter((c) => E.isFunc(e[c])) : Object.keys(e).filter((c) => E.isFunc(e[c]) && !r?.includes(c));
  for (const c of s)
    try {
      const l = e[c], m = Date.now();
      let u;
      l.constructor.name === "AsyncFunction" ? u = await Promise.race([
        l(),
        new Promise((p, y) => setTimeout(() => y(new Error("Timeout")), i))
      ]) : (u = l(), typeof u?.then == "function" && (u = await u)), n[c] = { value: u, duration: Date.now() - m };
    } catch (l) {
      const m = l.message === "Timeout";
      n[c] = {
        error: wr(
          m ? L.TIMEOUT : L.INTERNAL,
          m ? `Timeout exceeded by ${i} ms` : l.message
        )
      };
    }
  return n;
}
function wr(e, t) {
  return e === L.TIMEOUT ? {
    code: L.TIMEOUT,
    message: t || "Timeout exceeded"
  } : {
    code: L.INTERNAL,
    message: `An unexpected error occurred while collecting parameter data.${t ? ` Error: ${t}` : ""}`
  };
}
class Sr {
  loadTime = null;
  fingerprintHash = null;
  cache = null;
  async load(t) {
    try {
      const n = Date.now(), [o, r] = await Promise.all([
        Re($n, t),
        Re(gr, t)
      ]), a = Date.now();
      this.loadTime = a - n;
      const i = {
        ...o,
        ...r
      }, s = et(o, ["duration"]), c = JSON.stringify(s), m = !this.cache ? {} : W(this.cache);
      Object.assign(m, i), this.cache = m, this.fingerprintHash = Ge.hash128(c);
    } catch (n) {
      console.error(n);
    }
  }
  get(t) {
    return this.cache ? this.isClientDataKey(t) ? this.cache[t].error ?? this.cache[t].value : this.isArrayOfClientDataKey(t) ? Object.fromEntries(t.map((n) => [n, this.cache[n]])) : this.cache : null;
  }
  isClientDataKey(t) {
    return t && E.isString(t) && f(this.cache, t);
  }
  isArrayOfClientDataKey(t) {
    return t && E.isArray(t) && t.every((n) => this.isClientDataKey(n));
  }
}
export {
  Sr as MixVisit,
  Sr as default,
  Xt as getFonts,
  Re as loadParameters,
  pe as withIframe
};
