// Plays a generated floor from its own path plan. opts.fight: keep guards and fight them.
// Every action takes an optional dir (1 = rightward, the default; -1 = leftward).
// Every run is repeatable: Math.random (the guards' choices, the bot's own strikes, effects) is replaced for the run by a
// stream seeded from the floor and seed (opts.rseed overrides), so a failure in a fight run can be replayed exactly.
window.runBot = function (n, seed, opts) {
  opts = opts || {};
  let a = ((opts.rseed != null ? opts.rseed : n * 7919 + seed) >>> 0) || 1;
  const mr = Math.random;
  Math.random = () => { a = (a + 0x6D2B79F5) >>> 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
  try { return runBot0(n, seed, opts); } finally { Math.random = mr; }
};
// The bot as a generator: it yields before each game tick and goes on after it. runBot drives it with H.tick (tests);
// the game's ?bench mode drives it from the real frame loop, one step per game tick (window.botGen).
function runBot0(n, seed, opts) {
  const H = window.__HK, g = botGen(n, seed, opts);
  let r = g.next();
  while (!r.done) { H.tick(1); r = g.next(); }
  return r.value;
}
window.botGen = botGen;
function* botGen(n, seed, opts) {
  const H = window.__HK;
  const L = H.load(n, seed, !opts.fight);
  const TW = 32, cx = c => c * TW + 16;
  const keys = ['l', 'r', 'u', 'd', 'j', 'g'];
  const held = {};
  const set = (k, v) => { if (!!held[k] !== !!v) { held[k] = !!v; H.setKey('kb', k, !!v); } };
  const allOff = () => keys.forEach(k => set(k, false));
  const dk = d => d > 0 ? 'r' : 'l';
  let pulse = null;
  const press = k => { set(k, false); H.setKey('kb', k, true); held[k] = true; pulse = k; };
  const path = opts.path || L.path;
  // a test may start the prince anywhere (opts.at: column, row, facing) and end on a condition of its own (opts.done)
  if (opts.at) { const P0 = H.P; P0.x = opts.at.c * 32 + 16; P0.y = (opts.at.r + 1) * 64 - 4; P0.fallY = P0.y; P0.face = opts.at.face || 1; P0.state = 'stand'; }
  // (round 26f) a floor's entry (opts.entry plays it, as the game does on a fresh floor): the bot waits, keys up, until control is given
  if (opts.entry && !opts.at) H.startEntry();
  while (H.P.state === 'enter') { allOff(); yield 0; }
  let f1 = 0, i = 0, ph = 0, f0 = 0, frames = 0, r0 = 0, hurtCount = 0, lastHp = H.P.hp, fights = 0, swGo = false;
  const maxPer = 60 * 90;
  const P = () => H.P;
  const row = () => Math.floor((P().y - 1) / 64);
  const col = () => Math.floor(P().x / 32);
  const past = (c, dir) => (col() - c) * dir >= 0;
  const trace = [];
  function goto(tx) {
    const p = P(), dx = tx - p.x;
    // never tiptoe (Grab held) toward a block right beside us: that would push it
    const nb = H.L.blockAt && H.L.blockAt.get(row() * H.L.cols + (col() + Math.sign(dx)));
    if (p.state === 'stand' && Math.abs(dx) < (nb ? 14 : 7)) { allOff(); return true; }
    if (!['stand', 'run', 'stop', 'step', 'turn'].includes(p.state)) { return false; }
    if (Math.abs(dx) < 24) { set('g', !nb); set('r', dx > 0); set('l', dx < 0); }
    else { set('g', false); set('r', dx > 0); set('l', dx < 0); }
    return false;
  }
  function gotoD(tx, dir) {
    if (!goto(tx)) return false;
    if (P().face !== dir) { if (P().state === 'stand') { set(dk(dir), true); } return false; }
    allOff(); return true;
  }
  // will a run from here to `to` pass every timed hazard while it is safe?
  function safeRun(ins) {
    const dir = ins.dir || 1, r = row();
    const hz = H.L.dyn.filter(o => o.r === r && (o.c - ins.from) * dir > 0 && (ins.to - o.c) * dir >= 0 && (o.f.t === 'chomp' || o.f.t === 'vent'));
    let x = P().x, v = 35, t = 2 / 60; const dt = 1 / 60, endX = cx(ins.to) + 6 * dir;
    while ((endX - x) * dir > 0 && t < 6) {
      v = Math.min(100, v + 650 * dt); x += v * dt * dir; t += dt;
      for (const o of hz) { const hx = o.c * 32 + 16, m = o.f.t === 'chomp' ? 17 : 21; if (Math.abs(x - hx) < m && H.danger(o.f, H.gameTime + t)) return false; }
    }
    return true;
  }
  // simulate a run from here with one running jump at jx; is it clear of the saw the whole way?
  function sawSafe(ins) {
    const dir = ins.dir || 1, lo = Math.min(ins.from, ins.to), hi = Math.max(ins.from, ins.to);
    const o = H.L.dyn.find(q => q.f.t === 'saw' && q.r === row() && q.c >= lo && q.c <= hi); if (!o) return true;
    let x = P().x, v = 0, y = 0, vy = 0, air = false, land = 0, t = 2 / 60, jumped = false; const dt = 1 / 60, jx = cx(ins.from + dir) - 22 * dir;
    while ((cx(ins.to) - x) * dir > 0 && t < 6) {
      t += dt;
      if (!air) { if (land > 0) land -= dt; else { v = Math.min(100, (v || 35) + 650 * dt); x += v * dt * dir; } if (!jumped && (x - jx) * dir >= 0 && v > 45) { air = true; jumped = true; vy = -190; } }
      else { x += 183 * dt * dir; vy += 700 * dt; y += vy * dt; if (y >= 0) { y = 0; air = false; land = 0; v = 100; } } // (round 32: forward held through the landing, he runs straight on)
      if (Math.abs(x - H.sawX(o.f, H.gameTime + t)) < 16 && y > -13) return false;
    }
    return true;
  }
  const next = () => { i++; ph = 0; f0 = frames; allOff(); };
  const post = () => { if (pulse) { H.setKey('kb', pulse, false); held[pulse] = false; pulse = null; } frames++; };
  const fail = (ins, why) => ({ ok: false, n, seed, i, ins, why, x: P().x, col: col(), row: row(), trace: trace.slice(-10) });
  while (frames < 60 * 3000) {
    if (opts.stop && opts.stop(H)) return { ok: 'stopped', frames };
    const ins = path[i];
    const p = P();
    if (p.hp < lastHp) { hurtCount++; (window.__hurts = window.__hurts || []).push(n + ':i' + i + ':' + (ins && ins.a) + '@' + (ins && (ins.from ?? ins.c)) + ':' + p.state + ':ph' + ph + ':x' + Math.round(p.x) + ':c' + col() + ':' + (p.cause || '')); } lastHp = p.hp;
    if (H.mode === 'dead' || p.state === 'dead') return { ok: false, n, seed, i, ins, why: 'died:' + p.cause, x: p.x, y: p.y, state: p.state, trace: trace.slice(-10), hurt: hurtCount };
    if (H.mode === 'card') return { ok: true, n, seed, frames, hurt: hurtCount, fights };
    if (opts.done && opts.done(H)) return { ok: true, n, seed, frames, hurt: hurtCount, fights };
    if (!ins) return opts.path ? { ok: 'path done', n, seed, frames, hurt: hurtCount, x: p.x, y: p.y, col: col(), row: row(), state: p.state } : { ok: false, n, seed, why: 'path ended', i };
    if (frames - f0 > maxPer) return { ok: false, n, seed, i, ins, why: 'timeout ph' + ph, x: p.x, y: p.y, state: p.state, col: col(), row: row(), trace: trace.slice(-10) };
    // snakes: strike first, turning to face them
    const sn = H.SN.find(s => s.alive && s.r === row() && Math.abs(s.x - p.x) < (p.lowSword ? 36 : 44));
    if (sn && ['stand', 'crouch'].includes(p.state) && !(p.state === 'crouch' && ph >= 3 && ins.a === 'crawl')) {
      allOff(); const d = sn.x - p.x;
      if (Math.sign(d) !== p.face && Math.abs(d) > 3) press(d > 0 ? 'r' : 'l'); else press('g');
      yield 0; post(); continue;
    }
    // sword fights
    if (p.foe && p.foe.alive && ['garde', 'advance', 'retreat', 'strike', 'parry', 'blocked', 'hurt'].includes(p.state)) {
      const g = p.foe; allOff(); fights++;
      const wu = g.wu || g.windup, incoming = g.state === 'strike' && g.t >= Math.max(0.02, wu - 0.24) && g.t < wu - 0.02;
      if ((p.state === 'garde' || p.state === 'blocked') && incoming) press('u');
      else if (p.state === 'garde') {
        if (g.state === 'blocked' || g.state === 'hurt') press('g');
        else if (Math.abs(g.x - p.x) > 34) press(g.x > p.x ? 'r' : 'l');
        else if (g.state !== 'strike' && (window.botRnd || Math.random)() < (g.skel ? 0.16 : 0.08)) press('g');
      }
      yield 0; post(); continue;
    }
    if (ph === 0) trace.push(ins.a + '@' + (ins.from ?? ins.c) + (ins.dir < 0 ? '<' : ''));
    const dir = ins.dir || 1, fwd = dk(dir), back = dk(-dir);
    switch (ins.a) {
      case 'walk': if (goto(cx(ins.c))) next(); break;
      case 'look': allOff(); if (frames - f0 > (ins.f || 30)) next(); break; // stand a moment (a test looking at something)
      case 'sjump':
        // racing a gate's sand back: no stopping for a standing jump, take it from the run (as a player in a hurry would),
        // when there is floor to land on beyond it
        if (ph === 0 && !ins.calm && H.L.dyn.some(o => o.f.t === 'gate' && o.f.tm > 0 && o.f.tm < Infinity && !o.f.blockGate)) {
          const c2 = ins.to + dir, fl = c => H.L.base[row() * H.L.cols + c] === 1 && !H.L.feat[row() * H.L.cols + c];
          if (fl(ins.to) && fl(c2) && fl(ins.from) && fl(ins.from - dir) && row() === Math.floor((P().y - 1) / 64)) { ins.a = 'dashjump'; ins._was = 'sjump'; break; }
          ins.calm = true;
        }
        if (ph === 0) { if (gotoD(cx(ins.from), dir)) ph = 1; }
        else if (ph === 1) { press('j'); ph = 2; }
        else if (ph === 2) { if (p.state === 'stand' && frames - f0 > 5) { if (past(ins.to, dir)) next(); else return fail(ins, 'sjump short'); } }
        break;
      case 'rjump': case 'rjumpg':
        if (ph === 0) { if (gotoD(cx(ins.from - 2 * dir), dir)) ph = 1; }
        else if (ph === 1) { set('g', false); set(back, false); set(fwd, true); if (p.state === 'run' && (p.x - (cx(ins.from) - 44 * dir)) * dir >= 0) { press('j'); ph = 2; } }
        else if (ph === 2) { if (p.state === 'air' || p.state === 'hang') { set(fwd, false); ph = 3; } }
        else if (ph === 3) {
          if (p.state === 'hang') set('u', true);
          if (p.state === 'stand') { if (past(ins.to, dir)) next(); else return fail(ins, 'rjump short'); }
        }
        break;
      case 'collapse': // stand on the loose ledge and let it drop him a storey
        if (ph === 0) { if (gotoD(cx(ins.to), dir)) { ph = 1; r0 = row(); } }
        else if (ph === 1) { allOff(); if (p.state === 'air') ph = 2; else if (frames - f0 > 60 * 20) return fail(ins, 'ledge did not give way'); }
        else if (ph === 2) { if (p.state === 'stand' && row() > r0) next(); }
        break;
      case 'jgrab': // a running jump with Grab held in the air catches a ledge a storey up; then climb
        if (ph === 0) { if (gotoD(cx(ins.from - 2 * dir), dir)) { ph = 1; r0 = row(); } }
        else if (ph === 1) { set('g', false); set(back, false); set(fwd, true); if (p.state === 'run' && (p.x - (cx(ins.from) - 44 * dir)) * dir >= 0) { press('j'); ph = 2; } }
        else if (ph === 2) { if (p.state === 'air' || p.state === 'hang') { set(fwd, false); set('g', true); ph = 3; } }
        else if (ph === 3) {
          if (p.state === 'hang') { set('g', false); set('u', true); }
          if (p.state === 'stand') { if (row() < r0 && past(ins.to, dir)) next(); else return fail(ins, 'jgrab missed'); }
        }
        break;
      case 'climb':
        if (ph === 0) { if (gotoD(cx(ins.from), dir)) { ph = 1; r0 = row(); } }
        else if (ph === 1) { set('u', true); if (p.state === 'stand' && row() < r0) next(); }
        break;
      case 'drop':
        if (ph === 0) { if (gotoD(cx(ins.from), dir)) ph = 1; }
        else if (ph === 1) { set('g', false); set(fwd, true); if (p.state === 'air') { set(fwd, false); ph = 2; } }
        else if (ph === 2) { if (p.state === 'stand') next(); }
        break;
      case 'hangdrop':
        if (ph === 0) { if (gotoD(cx(ins.from), dir)) ph = 1; }
        else if (ph === 1) { press('d'); ph = 2; }
        else if (ph === 2) { if (p.state === 'hang') { press('d'); ph = 3; } }
        else if (ph === 3) { if (p.state === 'stand') next(); }
        break;
      case 'dashjump': // run on without stopping and tap Jump early: the game times a running jump to the edge
        if (ph === 0) { set('g', false); set(back, false); set(fwd, true); if (p.state === 'run' && (p.x - (cx(ins.from) - 50 * dir)) * dir >= 0) { press('j'); ph = 1; } }
        else if (ph === 1) { if (p.state === 'air' || p.state === 'hang') { set(fwd, false); ph = 2; } else set(fwd, true); }
        else if (ph === 2) { if (p.state === 'hang') set('u', true); if (p.state === 'stand') { if (past(ins.to, dir)) next(); else return fail(ins, 'dashjump short'); } }
        break;
      case 'tiptoe':
        if (ph === 0) { if (gotoD(cx(ins.from), dir)) ph = 1; }
        else if (ph === 1) { set('g', true); set(fwd, true); if (past(ins.to, dir)) { allOff(); ph = 2; } }
        else if (ph === 2) { if (p.state === 'stand') next(); }
        break;
      case 'runover':
        if (ph === 0) { if (gotoD(cx(ins.from), dir)) ph = 1; }
        else if (ph === 1) { set('g', false); set(fwd, true); if (past(ins.to, dir)) { allOff(); ph = 2; } }
        else if (ph === 2) { if (p.state === 'stand') next(); }
        break;
      case 'timed':
        if (ph === 0) { if (gotoD(cx(ins.from), dir)) ph = 1; }
        else if (ph === 1) { if (safeRun(ins)) { set('g', false); set(fwd, true); ph = 2; } }
        else if (ph === 2) { set(fwd, true); if ((p.x - (cx(ins.to) - 4 * dir)) * dir >= 0) { allOff(); ph = 3; } }
        else if (ph === 3) { if (p.state === 'stand') next(); }
        break;
      case 'crawl':
        if (ph === 0) { if (gotoD(cx(ins.from), dir)) ph = 1; }
        else if (ph === 1) { const lurk = H.SN.find(s => s.alive && s.r === row() && s.lo <= cx(ins.from) + 8 && s.hi >= ins.from * TW); if (lurk && !opts.wait) { ins.arm = true; ph = 2; } else if (!lurk || frames - f0 > 60 * 40) ph = 2; }
        else if (ph === 2) { if (p.state === 'stand') { press('d'); ph = 3; } }
        else if (ph === 3) {
          if (p.state === 'stand' && (frames - f0) % 15 === 0) press('d');
          if (p.state === 'crouch') {
            const s2 = H.SN.find(s => s.alive && s.r === row() && Math.abs(s.x - p.x) < 36);
            if (ins.arm && !p.lowSword && H.SN.some(s => s.alive && s.r === row() && s.lo <= cx(ins.to) && s.hi >= cx(ins.from) - 40)) { allOff(); if (!H.L.feat[row() * H.L.cols + col()] || H.L.feat[row() * H.L.cols + col()].t !== 'low') press('g'); }
            else if (s2 && p.lowSword) { allOff(); const d = s2.x - p.x; if (Math.sign(d) !== p.face && Math.abs(d) > 3) press(dk(Math.sign(d))); else press('g'); window.__pokes = (window.__pokes || 0) + 1; }
            else { set(fwd, true); if (dir > 0 ? p.x >= ins.to * TW + 16 : p.x <= ins.to * TW + 16) { set(fwd, false); ph = 4; } }
          }
        }
        else if (ph === 4) { press('u'); ph = 5; }
        else if (ph === 5) { if (p.state === 'stand') next(); else if (p.state === 'crouch' && frames % 10 === 0) press('u'); }
        break;
      case 'wallrun':
        if (ph === 0) { if (gotoD(cx(ins.from - 2 * dir), dir)) { ph = 1; r0 = row(); } }
        else if (ph === 1) { set('g', false); set(fwd, true); if (p.state === 'run' && (p.x - (cx(ins.from) - 34 * dir)) * dir >= 0) { press('j'); ph = 2; f1 = frames; } }
        else if (ph === 2) {
          if (p.state !== 'run') set(fwd, false);
          if (p.state === 'hang') set('u', true);
          if (p.state === 'stand' && row() < r0) next();
          else if (p.state === 'stand' && frames - f1 > 30) { allOff(); ph = 0; }
        }
        break;
      case 'walljump':
        if (ph === 0) { if (gotoD(cx(ins.from), dir)) { ph = 1; r0 = row(); } }
        else if (ph === 1) { press('j'); ph = 2; f1 = frames; }
        else if (ph === 2) {
          const topYs = (r0 - ins.k + 1) * 64 - 4;
          const wt = H.wallTouch(); // on the wall across from the ledge, kick for it even with the hands above it already
          if (p.state === 'air' && wt && p.vy > -170 && frames - f1 > 3 && (p.y - 57 > topYs + 2 || wt === -dir)) { press('j'); f1 = frames; }
          if (p.state === 'hang') set('u', true);
          if (p.state === 'stand' && row() < r0) next();
          else if (p.state === 'stand' && frames - f1 > 30) { allOff(); ph = 0; }
        }
        break;
      case 'slide':
        if (ph === 0) { if (gotoD(cx(ins.from), dir)) ph = 1; }
        else if (ph === 1) { set('g', false); set(fwd, true); if (p.state === 'air') { set(fwd, false); ph = 2; f1 = frames; } }
        else if (ph === 2) {
          if (p.state === 'hang') { set('g', false); press('d'); f1 = frames; }
          else if (frames - f1 > 8) set('g', true);
          if (['stand', 'land', 'landHurt'].includes(p.state)) { set('g', false); ph = 3; }
        }
        else if (ph === 3) { if (goto(cx(ins.to))) next(); }
        break;
      case 'swing':
        if (ph === 0) { if (gotoD(cx(ins.from - 2 * dir), dir)) ph = 1; }
        else if (ph === 1) { set('g', false); set(fwd, true); if (p.state === 'run' && (p.x - (cx(ins.from) - 44 * dir)) * dir >= 0) { press('j'); ph = 2; } }
        else if (ph === 2) { if (p.state === 'air') set(fwd, false); if (p.state === 'swing') ph = 3; else if (p.state === 'stand') return fail(ins, 'missed the bar'); }
        else if (ph === 3) {
          // the swing is a damped pendulum: pump (hold the way he is moving) until it is big enough, then let go moving forward
          // while still low on the front swing
          if (p.state === 'swing') {
            const th = p.swTh, om = p.swOm, W = H.SW_W, e = 0.5 * om * om / (W * W) + 1 - Math.cos(th), A = Math.acos(Math.max(-1, 1 - e));
            if (A < 0.6) swGo = false;
            if (A < 0.8 && !swGo) { set(fwd, om >= 0); set(back, om < 0); }
            else { swGo = true; set(fwd, false); set(back, false); if (om > 0 && th >= 0.15 && th <= 0.3) press('j'); }
          }
          if (p.state !== 'swing') { set(fwd, false); set(back, false); swGo = false; ph = 4; }
        }
        else if (ph === 4) { if (p.state === 'hang') set('u', true); if (p.state === 'stand') { if (past(ins.to, dir)) next(); else return fail(ins, 'swing short'); } }
        break;
      case 'saw':
        if (ph === 0) { if (gotoD(cx(ins.from), dir)) ph = 1; }
        else if (ph === 1) { if (sawSafe(ins)) { ph = 2; set('g', false); set(fwd, true); } }
        else if (ph === 2) { set(fwd, true); if (p.state === 'run' && (p.x - (cx(ins.from + dir) - 22 * dir)) * dir >= 0) { press('j'); ph = 3; } }
        else if (ph === 3) { set(fwd, true); if (past(ins.to, dir)) { allOff(); ph = 4; } }
        else if (ph === 4) { if (p.state === 'stand') next(); }
        break;
      case 'darts':
        if (ph === 0) { if (gotoD(cx(ins.from) - 8 * dir, dir)) { ph = 1; r0 = row(); } } // wait a step short of the darts' lane (it ends 11px before this tile's middle)
        else if (ph === 1) { if (p.state === 'stand') press('d'); if (p.state === 'crouch') ph = 2; }
        else if (ph === 2) { if (p.state === 'crouch') { set(fwd, true); if ((p.x - (cx(ins.to) - 4 * dir)) * dir >= 0) { set(fwd, false); ph = 3; } } }
        else if (ph === 3) { const near = H.L.ext.darts.some(d => d.r === row() && (d.x - p.x) * dir > -4 && (d.x - p.x) * dir < 75), dr = H.L.dyn.find(o => o.f.t === 'darter' && o.r === row() && Math.abs(o.c - col()) < 4), fresh = !dr || dr.f.lastPh < 0.45; if (!near && fresh && p.state === 'crouch') { press('u'); ph = 4; } } // stand just after a dart has flown, not just before the next
        else if (ph === 4) { if (p.state === 'stand') { press('u'); ph = 5; } else if (p.state === 'crouch') ph = 3; }
        else if (ph === 5) { if (p.state === 'hang' || p.state === 'jumpUp' || p.state === 'climb') set('u', true); if (p.state === 'stand' && row() < r0) next(); else if (p.state === 'stand' && frames - f0 > 600) { allOff(); ph = 3; press('d'); } }
        break;
      case 'push': case 'pull': {
        // approach from a tile further back (tiptoeing with Grab next to a block would push it), then edge in
        const face = dir > 0 ? (ins.from + 1) * TW : ins.from * TW, dB = (face - p.x) * dir;
        if (ph === 0) { if (gotoD(cx(ins.from - dir), dir)) { ph = 1; f1 = ins.n; } }
        else if (ph === 1) {
          if (ins.a === 'pull' && dB <= 26 && p.state === 'stand') { allOff(); ph = 3; }
          else { set('g', true); set(fwd, true); if (p.state === 'push') ph = 2; }
        }
        else if (ph === 2) { if (p.state === 'stand') { f1--; if (f1 <= 0) { allOff(); next(); } else ph = 1; } }
        else if (ph === 3) { set('g', true); set(back, true); if (p.state === 'pull') ph = 4; }
        else if (ph === 4) { if (p.state === 'stand') { f1--; allOff(); if (f1 <= 0) next(); else ph = 3; } }
        break; }
      case 'dash':
        if (ph === 0) { ph = 1; ins._j = ins.jumps.slice(); ins._u = ins.ups.slice(); ins._p = -1; window.__dashStart = H.gameTime; }
        else if (ph === 1) {
          const nj = ins._j[0], nu = ins._u[0];
          if (nu !== undefined && col() >= nu && (nj === undefined || nu <= nj)) { ph = 2; r0 = row(); allOff(); break; }
          set('g', false); set('r', true);
          if (nj !== undefined) {
            if (ins._for === nj && ['air', 'jumpPrep', 'edgeWalk'].includes(p.state)) { ins._j.shift(); ins._for = null; }   // that jump is under way
            else if (col() > nj + 1 && !['air', 'jumpPrep'].includes(p.state)) { ins._j.shift(); ins._for = null; }              // already past it on foot
            else if (p.x >= cx(nj) - 46 && p.state === 'run' && frames - ins._p > 8) { press('j'); ins._p = frames; ins._for = nj; }
          }
          if (col() >= ins.to && ['run', 'stand', 'stop', 'land'].includes(p.state)) { allOff(); (window.__dash = window.__dash || []).push({ n, took: +(H.gameTime - window.__dashStart).toFixed(2), info: H.L.chaseInfo }); next(); }
        }
        else if (ph === 2) { if (p.state === 'stand' && row() === r0) press('u'); if (p.state === 'hang') set('u', true); if (p.state === 'stand' && row() < r0) { set('u', false); ins._u.shift(); ph = 1; } }
        break;
      case 'lift': { // a lift. Counterweight: stand on the call plate at the landing until the platform is here, step on, hold Up or
        // Down until it stops, step off. Chain-loop: stand at the landing's edge, step on as a slab passes, hold on to the far landing.
        const sc = ins.from + dir;
        if (ins.chn) {
          if (ins._r0 === undefined) { ins._r0 = row(); ins._lf = H.L.lifts.find(q => q.t === 'chain' && q.c0 === sc && q.entryRow === row()); if (!ins._lf) return fail(ins, 'no chain lift here'); }
          const f = ins._lf;
          if (ph === 0) { if (p.state === 'lift') ph = 2; else if (gotoD((dir > 0 ? sc * TW : (sc + 1) * TW) - dir * 8, dir)) ph = 1; }   // (a tiptoe up to the edge may already step on a slab)
          else if (ph === 1) { // press toward the shaft only on a frame when a slab is passing the landing
            if (p.state === 'lift') ph = 2;
            else if (p.state === 'stand' && H.chainWin(f, 0, H.gameTime + 1 / 60) >= 0) { set('g', false); set(fwd, true); }
            else allOff();
            if (frames - f0 > 60 * 90) return fail(ins, 'no slab came');
          }
          else if (ph === 2) { set(fwd, true); if (p.state === 'step') ph = 3; }   // holding on toward the far landing: he steps off as a slab passes it
          else if (ph === 3) { allOff(); if (p.state === 'stand') { if (ins.up ? row() < ins._r0 : row() > ins._r0) ph = 4; else return fail(ins, 'stepped off at the wrong landing'); } }
          else if (ph === 4) { if (goto(cx(ins.to))) next(); }
          break;
        }
        if (ph === 0) { if (gotoD(cx(ins.from), dir)) { ins._lf = H.L.lifts.find(q => q.t === 'lift' && q.sc === sc && (ins.up ? q.rB : q.rT) === row()); if (!ins._lf) return fail(ins, 'no lift here'); ph = 1; } }
        else if (ph === 1) {
          const f = ins._lf, here = ins.up ? f.yB : f.yT;
          if (Math.abs(f.y - here) < 0.01 && f[ins.up ? 'gB' : 'gT'] > 0.9) ph = 2;               // it is here and the grating is open
          else if (frames - f0 > 60 * 60) return fail(ins, 'lift never came');                     // (standing on the plate calls it)
        }
        else if (ph === 2) { if (goto(cx(sc))) { ph = 3; f1 = frames; } }
        else if (ph === 3) {
          const f = ins._lf, far = ins.up ? f.yT : f.yB;
          set(ins.up ? 'u' : 'd', p.state === 'stand' || p.state === 'lift');
          if (p.state === 'stand' && Math.abs(f.y - far) < 0.01 && frames - f1 > 5) { allOff(); ph = 4; }
          else if (frames - f1 > 60 * 80) return fail(ins, 'ride never ended');
        }
        else if (ph === 4) { if (goto(cx(ins.to))) next(); }
        break; }
      case 'sandlift': { // (round 16a) the sand lift: walk onto its slab (stopping on it starts it), ride it down, walk off
        const sc = ins.from + dir;
        if (ph === 0) { r0 = row(); ins._lf = H.L.lifts.find(q => q.sand && q.sc === sc && q.rT === row()); if (!ins._lf) return fail(ins, 'no sand lift here'); ph = 1; }
        else if (ph === 1) { if (p.state === 'lift') ph = 2; else if (goto(cx(sc)) && frames - f0 > 60 * 6) return fail(ins, 'sand lift did not start'); }
        else if (ph === 2) { allOff(); if (p.state === 'stand' && row() > r0) ph = 3; else if (frames - f0 > 60 * 30) return fail(ins, 'sand lift ride never ended'); }
        else if (ph === 3) { if (goto(cx(ins.to))) next(); }
        break; }
      case 'drink':
        if (ph === 0) { allOff(); if (p.state === 'stand') { press('g'); ph = 1; } }
        else if (ph === 1) { if (p.state === 'stand') next(); }
        break;
      case 'door':
        if (ph === 0) { if (goto(L.door.x) && L.door.open >= 0.95) ph = 1; }
        else if (ph === 1) { press('u'); ph = 2; }
        break;
    }
    yield 0; post();
  }
  return { ok: false, n, seed, why: 'global timeout', i };
};
