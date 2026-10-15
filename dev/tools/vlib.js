// vlib.js: page-side helpers for the visual-review snapshots (vlib.py / vshots.py). Loaded after the page and bot.js.
// Everything hangs off window.V and uses only the game's own test hooks (window.__HK).
window.V = (() => {
  const H = __HK, TW = 32, TH = 64, SURF = r => (r + 1) * TH - 4, V = {};
  const cv = document.getElementById('game');
  const realRandom = Math.random;
  // the game's simulation draws on Math.random (guards, sparks). A seeded stream makes a bot run replayable; render() must not
  // consume it, so V.R() swaps the real one in around a render.
  V.seed = s => { let a = s | 0; Math.random = function () { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; };
  V.R = () => { const s = Math.random; Math.random = realRandom; try { H.render(); } finally { Math.random = s; } };
  // count ticks and (optionally) log key changes, so a bot run can be replayed frame for frame on a fresh page
  const T0 = H.tick, SK0 = H.setKey; let tc = 0, rec = null;
  H.tick = function (n = 1) { tc += n; T0(n); };
  H.setKey = function (s, k, v) { if (rec) rec.push([tc, s, k, v]); return SK0(s, k, v); };
  V.tc = () => tc;
  // quiet start: no hint banners, no "learned" noise, Torchlight untouched, no auto downgrade
  V.init = () => {
    window.__HKfreeze = true; window.__HKnoauto = true; window.H = H;
    document.querySelectorAll('.screen').forEach(e => e.hidden = true);
    for (const id in H.HINTS) H.S.hints[id] = 1;
    for (const id of H.HINT_MOVE) H.S.learned[id] = 1;
    H.S.sands = 3;
  };
  V.light = m => { H.S.set.lightMode = m; };
  // ---- level queries
  const L_ = () => H.L;
  V.B = (c, r) => { const L = L_(); if (c < 0 || c >= L.cols || r < 0) return 2; if (r >= L.rows) return 0; return L.base[r * L.cols + c]; };
  V.F = (c, r) => { const L = L_(); if (c < 0 || c >= L.cols || r < 0 || r >= L.rows) return null; return L.feat[r * L.cols + c]; };
  V.sb = (c, r) => { const b = V.B(c, r); if (b === 1) return true; if (b === 2) return false; return V.B(c, r + 1) === 2; };
  // a stretch of n floor tiles ending just before column c on row r (so he can walk up to c), none of them a feature that
  // would hurt him when he settles there
  V.walkway = (c, r, dir, n) => { for (let k = 1; k <= n; k++) { const cc = c - dir * k; if (!V.sb(cc, r) || V.B(cc, r) === 2) return false; const f = V.F(cc, r); if (f) return false; const d = L_().dyn.find(o => o.c === cc && o.r === r); if (d) return false; } return true; };
  V.load = (n, seed, o = {}) => {
    V.seed(seed); tc = 0;
    const L = H.load(n, seed, false);
    if (o.guards === false) { H.G.length = 0; H.SN.length = 0; H.PGQ.length = 0; }
    H.banner = null; return L;
  };
  // put the prince on the floor of row r at x; invulnerable unless o.inv === false
  V.place = (x, r, face = 1, o = {}) => {
    const P = H.P; P.x = x; P.y = SURF(r); P.fallY = P.y; P.state = 'stand'; P.t = 0; P.vx = P.vy = 0; P.face = face; P.foe = null;
    if (o.inv !== false) P.inv = 1e9;
    if (o.hp) P.hp = o.hp;
    H.cam.snap = true; H.tick(2); P.x = x; P.face = face; H.cam.snap = true; H.mode = 'play';
  };
  // let the world run n ticks with the prince held where he is (lights, flames and traps keep their own clocks)
  V.hold = (n, o = {}) => {
    const P = H.P, x = P.x, y = P.y, f = P.face, st = o.state || 'stand';
    for (let k = 0; k < n; k++) { P.x = x; P.y = y; P.face = f; P.state = st; P.vx = P.vy = 0; if (o.inv !== false) P.inv = 1e9; P.foe = null; H.tick(1); }
    P.x = x; P.y = y;
  };
  V.clean = () => { H.banner = null; };
  // ---- finders. pred(L, V) returns a spot {x, r, face, ...} or a falsy value; searched over seeds
  V.find = (n, seed0, tries, predSrc, o = {}) => {
    const pred = new Function('L', 'V', 'H', predSrc);
    for (let s = seed0; s < seed0 + tries; s++) {
      const L = V.load(n, s, o); let sp = null;
      try { sp = pred(L, V, H); } catch (e) { sp = null; }
      if (sp) return { seed: s, spot: sp };
    }
    return null;
  };
  // first dyn feature of type t (extra: a body with o, L, V in scope returning true) with a walkway of `walk` tiles in front of it
  V.dynSpot = (L, t, extraSrc, walk = 3, dirs = [1, -1]) => {
    const ex = extraSrc ? new Function('o', 'L', 'V', 'H', 'return (' + extraSrc + ')') : null;
    for (const o of L.dyn) {
      if (o.f.t !== t || (ex && !ex(o, L, V, H))) continue;
      for (const dir of dirs) if (V.walkway(o.c, o.r, dir, walk)) return { x: (o.c - dir * walk) * TW + 16, r: o.r, face: dir, c: o.c, dir, t };
    }
    return null;
  };
  // ---- camera box helpers (css px, for screenshot clips)
  V.css = (wx, wy) => { const rc = cv.getBoundingClientRect(), X = H.XF, sc = rc.width / cv.width; return [rc.left + (wx * X.VZ - X.camD) * sc, rc.top + (wy * X.VZ - X.camDY) * sc]; };
  V.box = (wx0, wy0, wx1, wy1) => { const a = V.css(wx0, wy0), b = V.css(wx1, wy1), x = Math.max(0, a[0]), y = Math.max(0, a[1]); return { x, y, width: Math.min(844, b[0]) - x, height: Math.min(390, b[1]) - y }; };
  V.princeBox = (hw = 80, up = 95, down = 25) => { const P = H.P; return V.box(P.x - hw, P.y - up, P.x + hw, P.y + down); };
  V.meta = () => { const P = H.P, L = H.L; return { floor: L.n, seed: L.seed, theme: L.theme.name, style: L.theme.style, state: P.state, face: P.face, hp: P.hp, x: Math.round(P.x), row: Math.floor((P.y - 1) / TH), light: H.S.set.lightMode, jk: P.jumpKind || null, feature: L.feature || null }; };
  // ---- bot recording, state episodes, replay
  // scan: play floor n with the bot and note the first few episodes of every prince state / guard state / event
  V.scan = (n, seed, fight, limit, want) => {
    V.seed(seed); tc = 0; rec = [];
    { let a = (seed * 7 + 3) | 0; window.botRnd = function () { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
    const eps = {}, open = {}; const wantSet = want && want.length ? new Set(want) : null; const done = new Set();
    const note = (tag, now, extra) => {
      if (!open[tag]) { const a = eps[tag] || (eps[tag] = []); if (a.length >= 3) return; open[tag] = { f0: now, f1: now, extra }; a.push(open[tag]); }
      else open[tag].f1 = now;
    };
    let lastHp = null;
    const stop = Hh => {
      const P = Hh.P, now = tc, cur = new Set();
      cur.add('s:' + P.state);
      if (P.state === 'air' && P.jumpKind) cur.add('jk:' + P.jumpKind);
      if (P.sword) cur.add('sword');
      if (P.hp < lastHp) cur.add('hurt');
      lastHp = P.hp;
      for (const g of Hh.G) {
        const near = Math.abs(g.x - P.x) < 260 && Math.abs(g.y - P.y) < (g.state === 'fall' || g.state === 'drop' ? 400 : 70);
        if (!near) continue;
        cur.add('g:' + (g.state === 'dying' ? 'dying' : g.alive === false ? 'dead' : g.state));
        if (g.alive !== false || g.state === 'dying') cur.add('gr:' + (g.skel ? 'skel' : g.cap ? 'cap' : 't' + (g.tier || 0)));
      }
      if (Hh.mode === 'dead') cur.add('dead');
      if (Hh.PGQ.length) cur.add('pg');
      for (const tag of Object.keys(open)) if (!cur.has(tag)) { delete open[tag]; if (wantSet) done.add(tag); }
      for (const tag of cur) note(tag, now, { x: Math.round(P.x), row: Math.floor((P.y - 1) / TH) });
      if (wantSet && [...wantSet].every(t => done.has(t))) return true;
      return now > limit;
    };
    let res; try { res = runBot(n, seed, { fight: !!fight, stop }); } catch (e) { res = { ok: false, err: String(e) }; }
    const out = { res, frames: tc, eps, rec }; rec = null; window.botRnd = null; return out;
  };
  let rp = null;
  V.replayInit = (n, seed, fight, r) => { V.seed(seed); tc = 0; rec = null; const L = H.load(n, seed, !fight); H.banner = null; rp = { rec: r, i: 0 }; return L.theme.name; };
  V.rstep = k => {
    for (let j = 0; j < k; j++) {
      while (rp.i < rp.rec.length && rp.rec[rp.i][0] <= tc) { const e = rp.rec[rp.i++]; SK0(e[1], e[2], e[3]); }
      T0(1); tc++;
    }
  };
  return V;
})();
// a standing spot on row r near column c (offset first, then closer), facing c; null if none
window.V.near = (c, r, off = 2) => { const V = window.V; for (const d of [-off, off, -off - 1, off + 1, -1, 1, 0]) { const cc = c + d; if (V.sb(cc, r) && V.B(cc, r) !== 2) return { x: cc * 32 + 16, r, face: d > 0 ? -1 : 1, c, dir: d > 0 ? -1 : 1 }; } return null; };
// a spot beside the first segment of kind k (a regex source) satisfying extra; the segment's start column
window.V.segSpot = (L, kre, extraSrc, off = 2) => {
  const re = new RegExp(kre), ex = extraSrc ? new Function('s', 'L', 'V', 'return (' + extraSrc + ')') : null;
  for (const s of L.segs) { if (!re.test(s.k) || (ex && !ex(s, L, V))) continue; const sp = V.near(s.c0, s.r0, off); if (sp) { sp.seg = s.k; return sp; } }
  return null; };

window.V.dynAt = s => H.L.dyn.find(o => o.c === s.c && o.r === s.r && o.f.t === s.t);
// an overview picture (no HUD or controls): tiles c0..c1, rows r0..r1 (inclusive) drawn from the room caches with the moving parts; returns a PNG data URL
window.V.overview = (c0, c1, r0, r1, Z) => {
  const x0 = c0 * 32, x1 = (c1 + 1) * 32, y0 = r0 * 64 - 8, y1 = (r1 + 1) * 64 + 8, Wd = x1 - x0, Hh = y1 - y0;
  const cv2 = document.createElement('canvas'); cv2.width = Wd * Z; cv2.height = Hh * Z; const g2 = cv2.getContext('2d'); g2.fillStyle = '#000'; g2.fillRect(0, 0, cv2.width, cv2.height);
  for (let ry = Math.floor(y0 / 192); ry <= Math.floor(y1 / 192); ry++) for (let rx = Math.floor(x0 / 320); rx <= Math.floor(x1 / 320); rx++) {
    const rc = document.createElement('canvas'); rc.width = 320 * Z; rc.height = 192 * Z; const rg = rc.getContext('2d'); rg.setTransform(Z, 0, 0, Z, 0, 0); H.drawRoomStatic(rg, rx, ry); g2.drawImage(rc, (rx * 320 - x0) * Z, (ry * 192 - y0) * Z); }
  g2.save(); g2.setTransform(Z, 0, 0, Z, -x0 * Z, -y0 * Z); H.drawDynamic(g2, x0, x1, y0, y1); g2.restore();
  return cv2.toDataURL(); };
