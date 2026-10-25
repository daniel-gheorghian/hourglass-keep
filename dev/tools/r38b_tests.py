#!/usr/bin/env python3
# r38b_tests.py [file] [--bot]: round 38b's play faults, one check per fault, each played in the page through the game's own input
# (__HK.load, setKey, tick). Prints one line per check, then 'r38b: ok' or 'r38b: FAIL n'. Run from dev/tools.
#  1 crush     a falling roof block respects his invulnerability: standing under one with P.inv 1.2 (as after a rewind) costs nothing;
#              with P.inv 0 it costs one life and gives trapHit's 0.9 s
#  2 hurtdrop  walking off either lip of a damaging drop (chamber hgap, fork kinds 2 and 4) with Grab held, from the start of the
#              fall or late: he never catches a lip (no hang), lands two storeys down and loses exactly one life
#  3 banner    a slide cuts a banner; a death and a rewind to before it: the cloth is whole again (bn.a, bn.b -1) and its cells
#              still share one cut record
#  4 sandhint  by a sand lift's slab the hint is its own ('sandlift', not the plate lift's words); riding it learns 'sandlift', not
#              'lift'; by a counterweight lift the hint is still 'lift'
#  5 sandtop   riding a sand lift he cannot walk off the slab; the top's play plane stands only while the slab is within the top
#              storey; once it is down, walking back at the top he steps into the hole (falls)
#  6 recruit   the recruit's HUD colour is not blue or white and reads apart from the other ranks' and the prince's hearts
#              (CIEDE2000 at least the closest existing pair of ranks, 16.5)
#  7 gatewaits every timed gate on floors 1-48 x seeds 1-3 (and with P4 forced, p4bot's seeds): the bot actions its timer covers;
#              none the bot waits at is missing from estPath's table (saw, darts); those it may wait at ('timed', 'crawl') have
#              entries. --bot also plays each such gate and prints the bot's waits and the timer's margin (slow)
import os, sys, re, json, math, colorsys, tempfile
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
args = [a for a in sys.argv[1:] if not a.startswith('--')]
SRC = os.path.abspath(args[0] if args else os.path.join(HERE, '..', 'hourglass-keep.html'))
BOT = '--bot' in sys.argv
ONLY = [a[7:] for a in sys.argv[1:] if a.startswith('--only=')]

PREP = r'''()=>{document.querySelectorAll('.screen').forEach(e=>e.hidden=true);window.__T={
  put(c,r,face){const P=__HK.P;P.x=c*32+16;P.y=(r+1)*64-4;P.fallY=P.y;P.face=face||1;P.state='stand';P.vx=0;P.vy=0;P.inv=0;P.lift=null;P.jumpKind=null;P.autoGrab=false;},
  keys(o){for(const k of ['l','r','u','d','j','g'])__HK.setKey('kb',k,!!(o&&o[k]));},
  find(lo,hi,ns,pred){for(let n=lo;n<=hi;n++)for(let s=1;s<=ns;s++){const L=__HK.genLevel(n,s,true);const x=pred(L);if(x)return {n,s,x};}return null;}};}'''

# 1. the roof block and invulnerability
J1 = r'''()=>{const H=__HK,T=__T;const fd=T.find(2,48,4,L=>{for(const o of L.dyn)if(o.f.t==='stone')return {c:o.c,r:o.r};return null;});
  if(!fd)return {err:'no roof block found'};const out={n:fd.n,s:fd.s,c:fd.x.c,r:fd.x.r};
  for(const inv of [1.2,0]){H.load(fd.n,fd.s,true);T.put(fd.x.c,fd.x.r,1);const P=H.P;P.inv=inv;const hp0=P.hp;let hit=false,inv1=null;
    for(let i=0;i<150;i++){H.tick(1);if(P.hp<hp0&&inv1===null)inv1=P.inv;if(H.L.debris.some(d=>d.hitP))hit=true;}
    const fell=H.L.dyn.some(o=>o.c===fd.x.c&&o.r===fd.x.r&&o.f.t==='stone'&&o.f.s>=2);
    out['inv'+inv]={lost:hp0-P.hp,fell,inv1};}
  return out;}'''

# 2. the damaging drop's lip, from a fall with Grab held
J2 = r'''([n,sd])=>{const H=__HK,T=__T;H.load(n,sd,true);const L=H.L,C=L.cols,out=[];const holes=[];
  for(let i=0;i<L.feat.length;i++){const f=L.feat[i];if(f&&f.t==='hurtdrop')holes.push({c:i%C,r:(i/C)|0,fork:f.fork||0});}
  for(const h of holes)for(const side of [1,-1])for(const late of [0,1]){H.load(n,sd,true);const P=H.P;T.put(h.c-side,h.r,side);const hp0=P.hp,k=side>0?'r':'l';
    T.keys({[k]:1});let st=[],landed=null;
    for(let fr=0;fr<300;fr++){H.tick(1);if(P.state==='air'){T.keys(!late||P.y>(h.r+1)*64-4+30?{g:1}:{});}
      if(st[st.length-1]!==P.state)st.push(P.state);
      if(['land','landHurt','stand','crouch','dead'].includes(P.state)&&Math.floor((P.y-1)/64)>h.r){landed=Math.floor((P.y-1)/64);if(P.t>0.05)break;}}
    T.keys({});out.push({hole:[h.c,h.r],fork:h.fork,side,late,hung:st.includes('hang'),landed,want:h.r+2,lost:hp0-P.hp,states:st.join('>')});}
  return out;}'''
FIND_HD = r'''()=>{const out=[];for(let n=5;n<=27&&out.length<4;n+=3)for(let s=0;s<60;s++){const seed=40000+s*131+n*17,L=__HK.genLevel(n,seed,true);
  if(L.hurtdrops&&L.hurtdrops.length){out.push([n,seed]);break;}}
  for(let n=6;n<=27;n+=3)for(let s=0;s<40;s++){const seed=41000+s*97+n*13,L=__HK.genLevel(n,seed,true);
    if(L.feat.some(f=>f&&f.t==='hurtdrop'&&f.fork)){out.push([n,seed]);break;}}
  return out;}'''

# 3. a banner's cut and the rewind
J3 = r'''()=>{const H=__HK,T=__T;const fd=T.find(4,30,4,L=>{for(const o of L.dyn)if(o.f.t==='banner'&&o.f.top)return {c:o.c,r:o.r};return null;});
  if(!fd)return {err:'no banner found'};const {c,r}=fd.x;H.load(fd.n,fd.s,true);const L=H.L,P=H.P;
  const cells=L.dyn.filter(o=>o.c===c&&o.f.t==='banner');const bn=cells[0].f.bn;
  T.put(L.start.c!==undefined?L.start.c:Math.floor(L.start.x/32),L.start.r,L.start.face||1);H.tick(340); // 5.7 s standing: the snapshots to come back to
  P.x=c*32+16;P.y=r*64+40;P.fallY=P.y;P.state='air';P.vx=0;P.vy=60;P.jumpKind=null;P.autoGrab=false;T.keys({g:1});
  let slid=false;for(let i=0;i<70;i++){H.tick(1);if(P.state==='slide')slid=true;}
  const cut={a:bn.a,b:bn.b};T.keys({});
  H.die('fall');H.tick(5);const sands=H.S.sands;H.startRewind();let k=0;while(H.mode!=='play'&&k<1200){H.tick(1);k++;}
  const same=cells.every(o=>o.f.bn===bn);
  return {n:fd.n,s:fd.s,c,r,slid,cut,after:{a:bn.a,b:bn.b},same,mode:H.mode,sands0:sands,sands:H.S.sands,state:P.state};}'''

# 4. the sand lift's hint and learned key, and the counterweight lift's
J4 = r'''()=>{const H=__HK,T=__T,S=H.S;const fd=T.find(4,40,4,L=>L.lifts.find(f=>f.sand)?1:null);if(!fd)return {err:'no sand lift'};
  const name=t=>Object.keys(H.HINTS).find(k=>H.HINTS[k]===t)||t;
  const seen=(fr,until)=>{const out=[];for(let i=0;i<fr;i++){H.tick(1);const b=H.banner;if(b&&b.kind==='hint'){const id=name(b.text);if(!out.includes(id))out.push(id);H.banner=null;}if(until&&until())break;}return out;};
  H.load(fd.n,fd.s,true);let f=H.L.lifts.find(q=>q.sand);S.learned={};S.hints={};H.banner=null;
  T.put(f.sc+2*f.sT,f.rT,-f.sT);const near=seen(120);
  const k=f.sT<0?'r':'l';T.keys({[k]:1});const ride=seen(240,()=>H.P.state==='lift');const rode=H.P.state==='lift';T.keys({});
  const res={n:fd.n,s:fd.s,hints:near,rideHints:ride,sandText:H.HINTS.sandlift,rode,learnedSand:!!S.learned.sandlift,learnedLift:!!S.learned.lift};
  const fc=T.find(3,40,4,L=>L.lifts.find(q=>q.t==='lift'&&!q.sand)?1:null);
  if(fc){seen(200);H.load(fc.n,fc.s,true);f=H.L.lifts.find(q=>q.t==='lift'&&!q.sand);S.learned={};S.hints={};H.banner=null;T.put(f.sc+2*f.sT,f.rT,-f.sT);
    res.cw={n:fc.n,s:fc.s,hints:seen(120)};}
  return res;}'''

# 5. the sand lift's top: the plane while the slab is in the top storey only; the hole afterwards
J5 = r'''()=>{const H=__HK,T=__T;const fd=T.find(4,40,4,L=>L.lifts.find(f=>f.sand)?1:null);if(!fd)return {err:'no sand lift'};
  H.load(fd.n,fd.s,true);const f=H.L.lifts.find(q=>q.sand),P=H.P;T.put(f.sc+1*f.sT,f.rT,-f.sT);const k=f.sT<0?'r':'l',ka=f.sT<0?'l':'r';
  T.keys({[k]:1});let i=0;for(;i<240&&P.state!=='lift';i++)H.tick(1);
  const cx=f.sc*32+16,x0=P.x;let dx=0,bad=[],n=0;
  for(i=0;i<900&&f.s!==2;i++){T.keys(i%60<30?{[ka]:1}:{[k]:1});H.tick(1);n++;dx=Math.max(dx,Math.abs(P.x-x0));
    const dy=f.y-f.yT,want=dy>0.01&&dy<64?0:1;if(f.gT!==want&&bad.length<4)bad.push({dy:Math.round(dy*10)/10,gT:f.gT});}
  T.keys({});H.tick(30);const down=f.s===2,foot=Math.floor((P.y-1)/64)===f.rB;
  T.put(f.sc+2*f.sT,f.rT,-f.sT);T.keys({[k]:1});let fell=false,minD=1e9;
  for(i=0;i<150;i++){H.tick(1);minD=Math.min(minD,Math.abs(P.x-cx));if(P.state==='air'&&Math.floor(P.x/32)===f.sc){fell=true;break;}}
  T.keys({});
  return {n:fd.n,s:fd.s,rode:n>0,maxDx:Math.round(dx*10)/10,planeBad:bad,down,foot,fell,closest:Math.round(minD)};}'''

# 7. timed gates and the waits in their stretches: an instrumented copy records what each timer covers
INSTR = [
 ("rem.g.est=estPath(bot.slice(rem.botIdx,next.botEnd),rem.pc,true);",
  "rem.g.est=estPath(bot.slice(rem.botIdx,next.botEnd),rem.pc,true);rem.g._acts=bot.slice(rem.botIdx,next.botEnd).map(q=>Object.assign({},q));rem.g._k='P4';"),
 ("if(timed)g.dur=Math.round((estPath([...br.backs,...exit],x0)*timerK()+0.3)*10)/10;",
  "if(timed){g.dur=Math.round((estPath([...br.backs,...exit],x0)*timerK()+0.3)*10)/10;g._acts=[...br.backs,...exit].map(q=>Object.assign({},q));g._k='detour';}"),
 ("const g={t:\"gate\",open:0,tm:0,dur:timed?Math.ceil(need*slack*10)/10:0,latch:!timed};",
  "const g={t:\"gate\",open:0,tm:0,dur:timed?Math.ceil(need*slack*10)/10:0,latch:!timed};if(timed){g._k='inline';g._acts=[];}"),
 ("G2.dur=Math.round((estPath([...brG.backs,{a:'walk',c:eg-2},{a:'hangdrop',from:eg-2},{a:'drop',from:eg-1},{a:'walk',c:g2c+1}],x0g)*timerK()+0.3)*10)/10;",
  "G2.dur=Math.round((estPath([...brG.backs,{a:'walk',c:eg-2},{a:'hangdrop',from:eg-2},{a:'drop',from:eg-1},{a:'walk',c:g2c+1}],x0g)*timerK()+0.3)*10)/10;G2._acts=[...brG.backs].map(q=>Object.assign({},q));G2._k='double';"),
 ("G2.dur=Math.round((estPath([...brC.backs,{a:'walk',c:ec},{a:'climb',from:ec},{a:'climb',from:ec+1},{a:'walk',c:g2c+1}],x0c)*timerK()+0.3)*10)/10;",
  "G2.dur=Math.round((estPath([...brC.backs,{a:'walk',c:ec},{a:'climb',from:ec},{a:'climb',from:ec+1},{a:'walk',c:g2c+1}],x0c)*timerK()+0.3)*10)/10;G2._acts=[...brC.backs].map(q=>Object.assign({},q));G2._k='double';"),
]
J7 = r'''([n,sd,p4])=>{if(p4){window.__PZ="P4";window.__FEAT={puzzle:"timed"};}else{delete window.__PZ;delete window.__FEAT;}
  const L=__HK.genLevel(n,sd,true),out=[];
  for(const o of L.dyn){const f=o.f;if(f.t!=='gate'||!(f.dur>0))continue;out.push({c:o.c,r:o.r,k:f._k||(f.blockGate?'block':'?'),dur:f.dur,acts:(f._acts||[]).map(a=>a.a)});}
  delete window.__PZ;delete window.__FEAT;return out;}'''
WAITS = {'saw', 'darts', 'timed', 'crawl', 'push', 'pull', 'dash'}  # bot actions that may wait (sawSafe, the darts' cycle, safeRun, a snake)

def de2000(h1, h2):
    def lab(h):
        r, g, b = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        f = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
        r, g, b = f(r), f(g), f(b)
        X = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047; Y = 0.2126 * r + 0.7152 * g + 0.0722 * b; Z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883
        t = lambda u: u ** (1 / 3) if u > 0.008856 else 7.787 * u + 16 / 116
        return 116 * t(Y) - 16, 500 * (t(X) - t(Y)), 200 * (t(Y) - t(Z))
    L1, a1, b1 = lab(h1); L2, a2, b2 = lab(h2)
    C1, C2 = math.hypot(a1, b1), math.hypot(a2, b2); Cb = (C1 + C2) / 2
    G = 0.5 * (1 - math.sqrt(Cb ** 7 / (Cb ** 7 + 25 ** 7))); a1p, a2p = (1 + G) * a1, (1 + G) * a2
    C1p, C2p = math.hypot(a1p, b1), math.hypot(a2p, b2)
    hh1, hh2 = math.degrees(math.atan2(b1, a1p)) % 360, math.degrees(math.atan2(b2, a2p)) % 360
    dL, dC = L2 - L1, C2p - C1p; dh = hh2 - hh1
    dh = dh - 360 if dh > 180 else dh + 360 if dh < -180 else dh
    dH = 2 * math.sqrt(C1p * C2p) * math.sin(math.radians(dh / 2)); Lb, Cbp = (L1 + L2) / 2, (C1p + C2p) / 2
    hb = (hh1 + hh2) / 2 if abs(hh1 - hh2) <= 180 else (hh1 + hh2 + 360) / 2
    T = 1 - 0.17 * math.cos(math.radians(hb - 30)) + 0.24 * math.cos(math.radians(2 * hb)) + 0.32 * math.cos(math.radians(3 * hb + 6)) - 0.2 * math.cos(math.radians(4 * hb - 63))
    SL = 1 + 0.015 * (Lb - 50) ** 2 / math.sqrt(20 + (Lb - 50) ** 2); SC = 1 + 0.045 * Cbp; SH = 1 + 0.015 * Cbp * T
    dth = 30 * math.exp(-((hb - 275) / 25) ** 2); RC = 2 * math.sqrt(Cbp ** 7 / (Cbp ** 7 + 25 ** 7)); RT = -math.sin(math.radians(2 * dth)) * RC
    return math.sqrt((dL / SL) ** 2 + (dC / SC) ** 2 + (dH / SH) ** 2 + RT * (dC / SC) * (dH / SH))

def page(b, f):
    pg = b.new_page(viewport={'width': 844, 'height': 390}); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://' + f); pg.wait_for_timeout(500); pg.evaluate(PREP)
    return pg, errs

results = []
def report(name, ok, msg):
    results.append((name, ok)); print('%-9s %s  %s' % (name, 'ok  ' if ok else 'FAIL', msg), flush=True)
def want(name):
    return not ONLY or name in ONLY

src = open(SRC, encoding='utf-8').read()
with sync_playwright() as p:
    b = p.chromium.launch()
    if want('crush'):
        pg, errs = page(b, SRC); r = pg.evaluate(J1); pg.close()
        if 'err' in r: report('crush', False, r['err'])
        else:
            a, z = r['inv1.2'], r['inv0']
            ok = a['fell'] and z['fell'] and a['lost'] == 0 and z['lost'] == 1 and z['inv1'] is not None and z['inv1'] > 0.8 and not errs
            report('crush', ok, 'floor %d seed %d block c%d r%d: invulnerable (P.inv 1.2) lost %d; not (P.inv 0) lost %d, P.inv after the hit %s %s' % (
                r['n'], r['s'], r['c'], r['r'], a['lost'], z['lost'], None if z['inv1'] is None else round(z['inv1'], 2), errs[:1]))
    if want('hurtdrop'):
        pg, errs = page(b, SRC); fl = pg.evaluate(FIND_HD); tot = hung = badland = badlost = ch = fk = 0; ex = []
        for n, sd in fl:
            for o in pg.evaluate(J2, [n, sd]):
                tot += 1; ch += o['fork'] == 0; fk += o['fork'] != 0
                if o['hung']: hung += 1
                if o['landed'] != o['want']: badland += 1
                if o['lost'] != 1: badlost += 1
                if (o['hung'] or o['landed'] != o['want'] or o['lost'] != 1) and len(ex) < 3: ex.append((n, sd, o))
        pg.close()
        ok = tot > 0 and ch > 0 and fk > 0 and hung == 0 and badland == 0 and badlost == 0 and not errs
        report('hurtdrop', ok, '%d falls off a broken lip with Grab held (%d chamber, %d fork; floors %s): caught a lip %d, not landed two storeys down %d, not exactly one life %d %s %s' % (
            tot, ch, fk, ' '.join('%d/%d' % (n, s) for n, s in fl), hung, badland, badlost, ex[:2], errs[:1]))
    if want('banner'):
        pg, errs = page(b, SRC); r = pg.evaluate(J3); pg.close()
        if 'err' in r: report('banner', False, r['err'])
        else:
            ok = r['slid'] and r['cut']['a'] >= 0 and r['cut']['b'] > r['cut']['a'] and r['after']['a'] == -1 and r['after']['b'] == -1 and r['same'] and r['mode'] == 'play' and not errs
            report('banner', ok, 'floor %d seed %d banner c%d r%d: slid %s, cut %s; after the rewind %s (mode %s, shared %s) %s' % (
                r['n'], r['s'], r['c'], r['r'], r['slid'], r['cut'], r['after'], r['mode'], r['same'], errs[:1]))
    if want('sandhint'):
        pg, errs = page(b, SRC); r = pg.evaluate(J4); pg.close()
        if 'err' in r: report('sandhint', False, r['err'])
        else:
            cw = r.get('cw') or {}
            ok = 'sandlift' in r['hints'] and 'lift' not in r['hints'] + r['rideHints'] and 'plate' not in r['sandText'] and r['rode'] and r['learnedSand'] and not r['learnedLift'] and 'lift' in cw.get('hints', []) and not errs
            report('sandhint', ok, 'floor %d seed %d: hints by the sand lift %s, stepping on %s (%r), rode %s, learned sandlift %s, lift %s; by a counterweight lift (floor %s seed %s) %s %s' % (
                r['n'], r['s'], r['hints'], r['rideHints'], r['sandText'], r['rode'], r['learnedSand'], r['learnedLift'], cw.get('n'), cw.get('s'), cw.get('hints'), errs[:1]))
    if want('sandtop'):
        pg, errs = page(b, SRC); r = pg.evaluate(J5); pg.close()
        if 'err' in r: report('sandtop', False, r['err'])
        else:
            ok = r['rode'] and r['maxDx'] < 1 and not r['planeBad'] and r['down'] and r['foot'] and r['fell'] and not errs
            report('sandtop', ok, 'floor %d seed %d: rode %s (moved on the slab, pressing either way, %s px), plane wrong at %s, down %s at the foot %s; back at the top he steps into the hole: %s (closest %s px) %s' % (
                r['n'], r['s'], r['rode'], r['maxDx'], r['planeBad'], r['down'], r['foot'], r['fell'], r['closest'], errs[:1]))
    if want('recruit'):
        m = re.search(r"\{name:'RECRUIT'[^}]*heart:'(#[0-9a-fA-F]{6})'", src)
        others = dict(re.findall(r"name:'(SOLDIER|VETERAN|CAPTAIN)'[^}]*heart:'(#[0-9a-fA-F]{6})'", src))
        pm = re.search(r"heart\(ctx,x\+i\*10,top\+2,P&&i<P\.hp,'(#[0-9a-fA-F]{6})'", src)
        if not m or len(others) != 3 or not pm: report('recruit', False, 'TIERS or the prince\'s heart not found')
        else:
            h = m.group(1); r_, g_, b_ = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]; H_, S_, V_ = colorsys.rgb_to_hsv(r_, g_, b_)
            blue = 170 <= H_ * 360 <= 270; white = S_ < 0.2
            d = {k: de2000(h, v) for k, v in others.items()}; d['prince'] = de2000(h, pm.group(1))
            ok = not blue and not white and min(d.values()) >= 16.5
            report('recruit', ok, 'heart %s (hue %d, saturation %.2f): blue %s, white %s; CIEDE2000 to %s' % (h, H_ * 360, S_, blue, white, ', '.join('%s %.1f' % kv for kv in d.items())))
    if want('gatewaits'):
        s7 = src; miss = [a for a, _ in INSTR if s7.count(a) != 1]
        for a, z in INSTR: s7 = s7.replace(a, z)
        tm = re.search(r"t\+=\(\{(runover:.*?)\}\)\[a\.a\]\|\|0;", src)
        if miss or not tm: report('gatewaits', False, 'instrumentation anchors or estPath table not found: %s' % [a[:50] for a in miss])
        else:
            table = set(re.findall(r"(?:^|,)([a-z0-9]+):", tm.group(1))) | {'walk'}
            fd, tmp = tempfile.mkstemp(suffix='.html', dir=HERE); os.close(fd)
            try:
                open(tmp, 'w', encoding='utf-8').write(s7)
                pg, errs = page(b, tmp); kinds = [{}, {}]; waits = [{}, {}]; nomiss = []; gl = []
                for p4 in (0, 1):
                    for n in range(1, 49):
                        for sd in ([1, 2, 3] if not p4 else [920000 + n * 97 + s * 13 for s in range(3)]):
                            for g in pg.evaluate(J7, [n, sd, p4]):
                                kinds[p4][g['k']] = kinds[p4].get(g['k'], 0) + 1
                                w = [a for a in g['acts'] if a in WAITS]
                                for a in w: waits[p4][g['k'] + ' ' + a] = waits[p4].get(g['k'] + ' ' + a, 0) + 1
                                if w and not p4: gl.append((n, sd, g['c'], g['r']))
                                for a in g['acts']:
                                    if a not in table: nomiss.append((n, sd, g['k'], a))
                pg.close()
            finally:
                os.remove(tmp)
            bad = [x for x in nomiss if x[3] in WAITS]
            allin = all(k.split(' ')[1] in table for w in waits for k in w)
            ok = not bad and allin and not errs
            report('gatewaits', ok, 'timed gates (floors 1-48 x seeds 1-3) %s, actions the bot may wait at in their stretches %s; with P4 forced (p4bot\'s seeds) %s, %s; '
                   'all of those actions have an estPath entry: %s; actions with no entry inside a timed stretch %d %s %s' % (
                kinds[0], waits[0], kinds[1], waits[1], allin, len(nomiss), sorted(set(x[3] for x in nomiss))[:6], errs[:1]))
            if BOT and gl:
                BJ = r'''([n,sd,c,r])=>{delete window.__PZ;delete window.__FEAT;const m={t0:null,pass:null,left:null,acts:[],cur:null};
                  const res=runBot(n,sd,{done:H=>{const L=H.L,f=L.feat[r*L.cols+c],P=H.P;if(!f)return false;if(f.tm>0&&f.tm>=f.dur-0.02)m.t0=H.gameTime;
                    if(m.t0!==null&&Math.floor((P.y-1)/64)===r&&Math.abs(P.x-(c*32+16))<4){m.pass=H.gameTime;m.left=f.tm;return true;}return false;}});
                  const f=__HK.L.feat[r*__HK.L.cols+c];return {ok:res.ok,dur:f&&f.dur,took:m.pass!==null?m.pass-m.t0:null,left:m.left};}'''
                pg = b.new_page(viewport={'width': 844, 'height': 390}); pg.goto('file://' + SRC); pg.wait_for_timeout(400); pg.add_script_tag(path=os.path.join(HERE, 'bot.js'))
                for j in gl:
                    q = pg.evaluate(BJ, list(j))
                    print('   floor %d seed %d gate c%d r%d: bot ok %s, timer %.1f s, from the plate to the gate %s s, left %s s' % (j + (q['ok'], q['dur'] or 0,
                          '%.2f' % q['took'] if q['took'] is not None else '-', '%.2f' % q['left'] if q['left'] is not None else '-')), flush=True)
                pg.close()
    b.close()
bad = [n for n, ok in results if not ok]
print('r38b: ok' if not bad else 'r38b: FAIL %d (%s)' % (len(bad), ', '.join(bad)))
sys.exit(0 if not bad else 1)
