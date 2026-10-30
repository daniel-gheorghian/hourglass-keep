# solidscan.py [file.html] [lo hi] [seeds] [torch|classic|both] [per=K] [things=block,roof,jamb,lift,clock] [kinds=noart,beam,shadow,relief] [strict] [dump=DIR]:
# the solids are opaque (round 46c; dev/docs/layers.md R5-R7, round 46b's heapscan.py over the other solids). For each solid on floors lo..hi
# (default 1-48), seeds (a count, default 1: 46000+97n+13s), up to K of each kind a floor (default 2), framed in the middle of the view with him
# beside it and the clock frozen: a pushed block ('block'), a fallen roof block lying across the corridor ('roof': each roof block on the floor
# is laid down for the test, f.s 3 and its rubble), a court's jambs ('jamb'), a lift with its platform, counterweight, slabs, sand lift or
# paternoster ('lift', framed at its foot), the sky clock ('clock'). Its pixels are the frame with it less the frame without it (LAYER_DBG.hide;
# both without the beams, lamp shadow, relief, mist, the looks, caustics and bloom, and with the back wall's art flattened, so an even darkening
# or lightening of the flat wall, a shadow, a shaft's shade on its back wall or a glow, is told from the thing's own colour and left out: those
# are L1's or light; a lift's shaft back, L1, is left out of every frame, LIFT_DBG.noback), inside its own box (a fallen block's slot high in
# the ceiling's face is not it), eroded by one world px, and they must not change when what lies behind or over it changes:
#   noart  the back wall's art flattened (EGP.noart 'atop')     R5: nothing behind it shows through
#   beam   the sky beams off (window.__RYOFF; both modes)        R7: no haze, rim, pane or footprint on it (not for the clock: it stands at mid
#                                                                    depth with air in front of it, as a figure does)
#   shadow the lamp shadow off (GLFX.shadow; Torchlight)         R6: carved out of its whole outline
#   relief the relief off (GLFX.relief; Torchlight)              R6: no wall art embossed on it
# A thing fails a kind when more than 0.5% of its pixels change by more than 10 (sum of channels). Lamps' drawn glows are left out of every frame
# (LAYER_DBG.glow false), and the bloom. Prints one line per thing and mode, a summary per mode, thing and kind, and 'solidscan: ok'.
# dump=DIR writes each failure with the changed pixels in magenta. Run from dev/tools; HK_GPU=1 draws WebGL on the Radeon (suite.py runs it in the GPU browser).
import io, os, sys, re
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
SRC = os.path.abspath(next((x for x in a if x.endswith('.html') and '=' not in x), os.path.join(HERE, '..', 'hourglass-keep.html')))
NUM = [int(x) for x in a if re.match(r'^\d+$', x)]
LO, HI = (NUM[0], NUM[1]) if len(NUM) >= 2 else (1, 48)
NS = NUM[2] if len(NUM) > 2 else 1
MODES = ['torch', 'classic'] if 'both' in a or not any(m in a for m in ('torch', 'classic')) else [m for m in ('torch', 'classic') if m in a]
PER = int(next((x[4:] for x in a if x.startswith('per=')), '2'))
THINGS = next((x[7:] for x in a if x.startswith('things=')), 'block,roof,jamb,lift,clock').split(',')
KINDS = next((x[6:] for x in a if x.startswith('kinds=')), 'noart,beam,shadow,relief').split(',')
DUMP = next((x[5:] for x in a if x.startswith('dump=')), None)
TH, LV, DSF = 0.005, 10, 2
# Left, reported and not failed (layers.md, "Left as they are"): specks of a Torchlight beam's haze on a fallen roof block lying
# (up to 4% of its pixels on 10 of 22, round 46c: the mark and the rubbing cover its box, the specks sit on its stone's glints), and the
# relief on a broken jamb's pieces lying on the floor beside it (4 of 92), and his lamp shadow on the edges of the sky clock's pedestal (8 of 94,
# up to 2.7%: the carve is the pedestal's outline and the quarter-size mask is read blurred; widening it fails shadowscan.py, which masks the
# clock by that outline); in Classic a speck of a beam's footprint by a pushed block's foot (1.3%, floor 21) and on a lift's mouth slab
# (1%, floor 44). Each is known only up to its cap (KNOWN); 'strict' fails them too. Round 47c's brighter ambient (AMB_LIFT) moved two of these
# specks over their old caps on the right edge of a lying roof block in Torchlight: the relief on floor 23 (x 6352) 5.6% and his
# lamp shadow on floor 3 (x 5104) 0.6% (.01, newly listed); 22 and 37 px. Round 47e: the relief specks on a lying roof block were its sand heap
# and those on the clock its pedestal's rubble chips, drawn live and never rubbed (glRelRoofRubble, glRelClock's chips): the roof's relief
# cap is gone (max 0.22% on floors 1-48), the clock's relief 0.15% at most.
KNOWN = {} if 'strict' in a else {('torch', 'roof', 'beam'): 0.05, ('torch', 'roof', 'shadow'): 0.01, ('torch', 'jamb', 'relief'): 0.03, ('torch', 'clock', 'shadow'): 0.03,
                                    ('classic', 'block', 'beam'): 0.02, ('classic', 'lift', 'beam'): 0.02}  # (each up to its cap: more fails)
HIDE = {'block': 'block', 'roof': 'stone', 'jamb': 'jamb', 'lift': 'lift', 'clock': 'clock'}

LIST = r'''([n,seed])=>{const H=__HK;window.__HKfreeze=true;const L=H.load(n,seed,true),TW=32,TH=64,S=r=>(r+1)*TH-4,out=[];
  for(const b of L.ext.blocks)out.push(['block',b.c*TW+16,S(b.r),0,0,[b.c*TW-12,b.r*TH-8,(b.c+1)*TW+8,S(b.r)+14]]);
  for(const o of L.dyn)if(o.f.t==='stone')out.push(['roof',o.c*TW+16,S(o.r),o.c,o.r,[o.c*TW-12,S(o.r)-20,(o.c+1)*TW+12,S(o.r)+10]]); // (the block lying; its slot in the ceiling is a hole in L3's face)
  for(const k of L.courts||[])for(const x of [k.c0*TW,(k.c1+1)*TW])out.push(['jamb',x,S(k.r),0,0,[x-26,(k.r-1)*TH-4,x+18,S(k.r)+14]]);
  for(const lf of L.lifts)out.push(['lift',(lf.ca+lf.cb+1)*TW/2,S(lf.rB)-24,0,0,[lf.ca*TW-24,lf.rT*TH-24,(lf.cb+1)*TW+24,S(lf.rB)+80]]);
  for(const q of L.cps)out.push(['clock',q.x,S(q.r),0,0,[q.x-24,S(q.r)-56,q.x+24,S(q.r)+8]]);
  return out;}'''
SETUP = r'''([n,seed,q])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS){H.S.hints[id]=1;if(H.S.learned)H.S.learned[id]=1;}const L=H.load(n,seed,true);H.banner=null;
  const P=H.P;P.inv=1e9;for(const e of H.G||[])e.x=-9999;for(const s of H.SN||[])s.x=-9999;
  if(q[0]==='roof'){const o=L.dyn.find(d=>d.f.t==='stone'&&d.c===q[3]&&d.r===q[4]);if(!o)return null;o.f.s=3;o.f.land=-99;L.rubble.add(o.r*L.cols+o.c);}
  const TW=32,c0=Math.floor(q[1]/TW),r=Math.round((q[2]+4)/64)-1,B=(c,rr)=>L.base[rr*L.cols+c];let px=q[1]+44;for(const dx of [44,-44,72,-72]){const c=Math.floor((q[1]+dx)/TW);if(B(c,r)!==2&&B(c,r+1)!==0){px=q[1]+dx;break;}}
  P.x=px;P.y=(r+1)*64-4;P.fallY=P.y;P.vx=P.vy=0;P.face=px>q[1]?-1:1;P.state='stand';H.mode='play';
  if(H.HILL_DBG)H.HILL_DBG.stream=false;L.winds.length=0;return [H.themeName(n)];}'''
SHOW = r'''([fx,fy,o])=>{const H=__HK;H.banner=null;H.setClock(()=>1e6);H.setGT(10);H.LAYER_DBG.glow=false;if(H.LIFT_DBG)H.LIFT_DBG.noback=true;
  const G=H.GLFX;H.LAYER_DBG.hide=o.hide?new Set(o.hide):null;H.EGP.noart=o.noart?'atop':false;G.shadow=!o.noshadow&&!o.clean;G.relief=!o.norelief&&!o.clean;window.__RYOFF=!!(o.nobeam||o.clean);G.ryClean=true;
  G.mist=G.lookfx=G.caustics=!o.clean;G.bloom=false;H.clearRooms();
  H.cam.x=fx-H.viewW/2;H.cam.y=fy-192*0.62;H.cam.gy=H.cam.y;if(H.GLP){H.GLP.pipe=false;H.GLP.rs=1;window.__HKnoauto=true;}for(let i=0;i<4;i++)H.render();
  const X=H.XF,cv=[...document.querySelectorAll('canvas')].find(c=>c.getBoundingClientRect().width>0),R=cv.getBoundingClientRect(),gm=document.getElementById('game'),k=R.width/gm.width;
  const bx=o.box?[(o.box[0]*X.VZ-X.camD)*k+R.left,(o.box[1]*X.VZ-X.camDY)*k+R.top,(o.box[2]*X.VZ-X.camD)*k+R.left,(o.box[3]*X.VZ-X.camDY)*k+R.top]:null;
  return [X.VZ*k,bx];}'''
OFF = {'noart': {'noart': 1}, 'beam': {'nobeam': 1}, 'shadow': {'noshadow': 1}, 'relief': {'norelief': 1}}


def prep(src):  # (an older build without round 46's switches: beamjag.py's patches)
    if 'window.__RYOFF' in src: return SRC
    P = [('if(ns||cs){\n    const U=GLC.S.u;', 'if((ns||cs)&&!window.__RYOFF){\n    const U=GLC.S.u;'),
         ('function ryBeams2D(ctx,a){', 'function ryBeams2D(ctx,a){if(window.__RYOFF)return;')]
    for x, y in P:
        assert x in src, 'solidscan: cannot patch the old build at %r' % x; src = src.replace(x, y, 1)
    p = os.path.join(os.path.dirname(SRC), '_solidscan_old.html'); open(p, 'w', encoding='utf-8').write(src); return p


def grab(pg, fx, fy, o):
    k, bx = pg.evaluate(SHOW, [fx, fy, o])
    im = np.asarray(Image.open(io.BytesIO(pg.screenshot())).convert('RGB')).astype(int)
    if bx: o['_box'] = [int(v * DSF) for v in bx]
    return im, k * DSF


if __name__ == '__main__':
    PAGE = prep(open(SRC, encoding='utf-8').read())
    bad, tot, rows, errs = [], {}, 0, []
    with sync_playwright() as p:
        b = p.chromium.launch(args=(['--use-angle=metal', '--force_high_performance_gpu'] if os.environ.get('HK_GPU') == '1' else []) + ['--enable-gpu', '--ignore-gpu-blocklist'])
        for mode in MODES:
            pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=DSF); pg.on('pageerror', lambda e: errs.append(str(e)))
            pg.goto('file://' + PAGE); pg.wait_for_timeout(800)
            pg.evaluate("()=>{document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.body.classList.remove('panelOpen');const st=document.createElement('style');st.textContent='.ctl,#pause,#pauseBtn,#pad{display:none!important}';document.head.appendChild(st);}")
            pg.evaluate("m=>{__HK.S.set.lightMode=m;__HK.GLFX.sheen=false;}", mode)
            for n in range(LO, HI + 1):
                for s in range(NS):
                    seed = 46000 + n * 97 + s * 13
                    li = pg.evaluate(LIST, [n, seed])
                    by = {}
                    for q in li:
                        if q[0] in THINGS: by.setdefault(q[0], []).append(q)
                    for th, v in by.items():
                        for q in [v[int(i * len(v) / PER)] for i in range(min(PER, len(v)))]:
                            r = pg.evaluate(SETUP, [n, seed, q])
                            if not r: continue
                            fx, fy = q[1], q[2]
                            ob = {'clean': 1, 'noart': 1, 'box': q[5]}
                            cl, k = grab(pg, fx, fy, ob)  # (its pixels over the flat wall: an even darkening or lightening of it there is a shade or a light, never a solid's own colour)
                            hid, _ = grab(pg, fx, fy, {'hide': [HIDE[th]], 'clean': 1, 'noart': 1})
                            m = np.abs(cl - hid).sum(2) > 12
                            bm = np.zeros_like(m); x0, y0, x1, y1 = ob['_box']; bm[max(0, y0):max(0, y1), max(0, x0):max(0, x1)] = True; m &= bm  # (its own box: nothing else that the hidden kind draws, as a fallen block's slot high in the ceiling's face)
                            rt = (cl + 1.0) / (hid + 1.0)  # (an even lightening: light; a darkening toward a near-black: a shadow, a shade laid over the wall)
                            ev = rt.max(2) - rt.min(2) < 0.08
                            hm = hid.max(2); ia = hid.argmax(2); cm = np.take_along_axis(cl, ia[..., None], 2)[..., 0]
                            al = np.clip(1 - (cm + 0.5) / (hm + 0.5), 0, 1)[..., None]
                            dk = (cl <= hid + 2).all(2) & (np.abs(cl - hid * (1 - al)) <= 3 + 16 * al).all(2) & (al[..., 0] > 0.03)
                            m &= ~(dk | ((cl >= hid - 2).all(2) & ev & (rt.mean(2) > 1.03)))
                            base, _ = grab(pg, fx, fy, {})
                            e = max(1, int(round(k)))
                            mm = m.copy()
                            for dy in range(-e, e + 1):
                                for dx in range(-e, e + 1): mm &= np.roll(np.roll(m, dy, 0), dx, 1)
                            N = int(mm.sum()); row = ['%-7s' % mode, '%2d/%d' % (n, seed), '%-5s' % th, 'x%d' % fx, r[0][:26], '%5d px' % N]
                            if N < 50: print(*row, 'too small, skipped', flush=True); continue
                            for kd in KINDS:
                                if mode != 'torch' and kd in ('shadow', 'relief'): continue
                                if th == 'clock' and kd == 'beam': continue
                                alt, _ = grab(pg, fx, fy, OFF[kd])
                                d = (np.abs(base - alt).sum(2) > LV) & mm
                                f = d.sum() / N; row.append('%s %.2f%%' % (kd, 100 * f)); tot.setdefault((mode, th, kd), []).append(f)
                                if TH < f <= KNOWN.get((mode, th, kd), 0): row.append('(known)')
                                elif f > TH:
                                    bad.append('%s %s %s %d/%d x%d %.2f%%' % (mode, th, kd, n, seed, fx, 100 * f))
                                    if DUMP:
                                        os.makedirs(DUMP, exist_ok=True); vis = base.copy().astype(np.uint8); vis[d] = [255, 0, 255]; ys, xs = np.where(mm)
                                        Image.fromarray(vis[max(0, ys.min() - 60):ys.max() + 30, max(0, xs.min() - 60):xs.max() + 60]).save(os.path.join(DUMP, 'ss_%s_%s_%d_%d_%s.png' % (mode, th, n, fx, kd)))
                            rows += 1; print(*row, flush=True)
            pg.close()
        b.close()
    if PAGE != SRC: os.remove(PAGE)
    for (m, th, kd), v in sorted(tot.items()):
        print('summary %-7s %-5s %-6s things %3d  over %.1f%%: %3d  mean %.2f%%  max %.2f%%' % (m, th, kd, len(v), 100 * TH, sum(1 for x in v if x > TH), 100 * np.mean(v), 100 * max(v)))
    if bad: print('bad:', '; '.join(bad[:40]))
    if errs: print('errors', errs[:3])
    print('solidscan: ok' if not bad and not errs and rows else 'solidscan: FAIL (%d of %d frames, errors %d)' % (len(bad), rows, len(errs)))
    sys.exit(0 if not bad and not errs and rows else 1)
