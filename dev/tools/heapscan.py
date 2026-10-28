# heapscan.py [file.html] [lo hi] [seeds] [torch|classic|both] [per=K] [kinds=noart,beam,shadow,relief] [dump=DIR]: heaps and drifts are opaque
# solids (round 46b, owner on a B3 heap before an opening, the Waters of Nun at night: "it looks transparent, the background wall art seems drawn
# over it, the shadow renders just over the far left of the heap"; dev/docs/layers.md R5-R7). For each hill on floors lo..hi (default 3-48), seeds
# (a count, default 2: 46000+97n+13s), up to K a floor (default 2), framed in the middle of the view with him beside it and the clock frozen: its
# pixels are the frame with it less the frame without it (LAYER_DBG.hide heap/drift; both without the beams, lamp shadow, relief, mist, the looks,
# caustics and bloom, whose cut round it would count; a drift's sand stream, air over the wall, left out by HILL_DBG.stream, and the wind's dust
# over it, air the beam lights, by emptying L.winds; its soft shadow on the
# floor, a pixel darkened evenly in every channel, left out: the floor's own footprint and relief belong there), eroded by one world px, and they
# must not change when what lies behind or over it changes:
#   noart  the back wall's art flattened (EGP.noart 'atop')         R5: nothing behind it shows through
#   beam   the sky beams off (window.__RYOFF; both modes)            R7: no haze, rim, pane or footprint on it
#   shadow the lamp shadow off (GLFX.shadow; Torchlight)             R6: carved out of its whole outline
#   relief the relief off (GLFX.relief; Torchlight)                  R6: no wall art embossed on it
# The bloom is held out of every frame (GLFX.bloom false, as layerscan's NOBLOOM): it spreads light, the beams' and caustics' too, a few px
# over any edge, which is light, not a draw-over. A hill fails a kind when more than 0.5% of its pixels change by more than 10 (sum of channels). Prints one line per hill and mode, a summary per
# mode and kind, and 'heapscan: ok'. dump=DIR writes each failure with the changed pixels in magenta. An older build (v87) without __RYOFF gets
# beamjag.py's patches. Run from dev/tools; HK_GPU=1 draws WebGL on the Radeon (suite.py runs it in the GPU browser).
import io, os, sys, re
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
SRC = os.path.abspath(next((x for x in a if x.endswith('.html') and '=' not in x), os.path.join(HERE, '..', 'hourglass-keep.html')))
NUM = [int(x) for x in a if re.match(r'^\d+$', x)]
LO, HI = (NUM[0], NUM[1]) if len(NUM) >= 2 else (3, 48)
NS = NUM[2] if len(NUM) > 2 else 2
MODES = ['torch', 'classic'] if 'both' in a or not any(m in a for m in ('torch', 'classic')) else [m for m in ('torch', 'classic') if m in a]
PER = int(next((x[4:] for x in a if x.startswith('per=')), '2'))
KINDS = next((x[6:] for x in a if x.startswith('kinds=')), 'noart,beam,shadow,relief').split(',')
DUMP = next((x[5:] for x in a if x.startswith('dump=')), None)
TH, LV, DSF = 0.005, 10, 2

SETUP = r'''([n,seed,i])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS){H.S.hints[id]=1;if(H.S.learned)H.S.learned[id]=1;}const L=H.load(n,seed,true);H.banner=null;
  const h=(L.hills||[])[i];if(!h)return null;const P=H.P;P.inv=1e9;for(const e of H.G||[])e.x=-9999;P.x=(h.c+h.n)*32+10;P.y=(h.r+1)*64-4;P.fallY=P.y;P.vx=P.vy=0;P.face=-1;P.state='stand';H.mode='play';
  if(H.HILL_DBG)H.HILL_DBG.stream=false;L.winds.length=0;return [h.c,h.r,h.n,h.v,H.hillEnd?H.hillEnd(h):null,H.themeName(n)];}'''
SHOW = r'''([fx,fy,o])=>{const H=__HK;H.banner=null;H.setClock(()=>1e6);H.setGT(10);
  const G=H.GLFX;H.LAYER_DBG.hide=o.hide?new Set(o.hide):null;H.EGP.noart=o.noart?'atop':false;G.shadow=!o.noshadow&&!o.clean;G.relief=!o.norelief&&!o.clean;window.__RYOFF=!!(o.nobeam||o.clean);G.ryClean=true;
  G.mist=G.lookfx=G.caustics=!o.clean;G.bloom=false;H.clearRooms();
  H.cam.x=fx-H.viewW/2;H.cam.y=fy-192*0.62;H.cam.gy=H.cam.y;if(H.GLP){H.GLP.pipe=false;H.GLP.rs=1;window.__HKnoauto=true;}for(let i=0;i<4;i++)H.render();
  const X=H.XF,cv=[...document.querySelectorAll('canvas')].find(c=>c.getBoundingClientRect().width>0);return X.VZ/cv.width*cv.getBoundingClientRect().width;}'''
OFF = {'noart': {'noart': 1}, 'beam': {'nobeam': 1}, 'shadow': {'noshadow': 1}, 'relief': {'norelief': 1}}


def prep(src):  # (an older build without round 46's switches: beamjag.py's patches; and the hooks heapscan reads)
    if 'window.__RYOFF' in src: return SRC
    P = [('if(ns||cs){\n    const U=GLC.S.u;', 'if((ns||cs)&&!window.__RYOFF){\n    const U=GLC.S.u;'),
         ('function ryBeams2D(ctx,a){', 'function ryBeams2D(ctx,a){if(window.__RYOFF)return;')]
    for x, y in P:
        assert x in src, 'heapscan: cannot patch the old build at %r' % x; src = src.replace(x, y, 1)
    p = os.path.join(os.path.dirname(SRC), '_heapscan_old.html'); open(p, 'w', encoding='utf-8').write(src); return p


def grab(pg, fx, fy, o):
    k = pg.evaluate(SHOW, [fx, fy, o])
    return np.asarray(Image.open(io.BytesIO(pg.screenshot())).convert('RGB')).astype(int), k * DSF


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
            kinds = [k for k in KINDS if mode == 'torch' or k in ('noart', 'beam')]
            for n in range(LO, HI + 1):
                for s in range(NS):
                    seed = 46000 + n * 97 + s * 13
                    nh = pg.evaluate('([n,s])=>{const L=__HK.load(n,s,true);return (L.hills||[]).length}', [n, seed])
                    for i in range(min(nh, PER)):
                        q = pg.evaluate(SETUP, [n, seed, i])
                        if not q: continue
                        c, r, nn, v, end, th = q
                        fx, fy = c * 32 + nn * 16, (r + 1) * 64 - 4
                        cl, k = grab(pg, fx, fy, {'clean': 1})  # (its pixels: with it less without it, both frames with every pass that it cuts off, so their cut's soft edge in the air is not taken for it)
                        hid, _ = grab(pg, fx, fy, {'hide': ['heap', 'drift'], 'clean': 1})
                        m = np.abs(cl - hid).sum(2) > 12
                        rt = (cl + 1.0) / (hid + 1.0)  # (its soft shadow on the floor round its foot is the floor's, darkened evenly: the floor's own passes may land there)
                        m &= ~((cl <= hid + 2).all(2) & (rt.max(2) - rt.min(2) < 0.08) & (rt.mean(2) < 0.97))
                        base, _ = grab(pg, fx, fy, {})
                        e = max(1, int(round(k)))  # (one world px)
                        mm = m.copy()
                        for dy in range(-e, e + 1):
                            for dx in range(-e, e + 1): mm &= np.roll(np.roll(m, dy, 0), dx, 1)
                        N = int(mm.sum()); row = ['%-7s' % mode, '%2d/%d' % (n, seed), 'c%d r%d' % (c, r), v + ('/' + end if end else ''), th[:24], '%5d px' % N]
                        if N < 50: print(*row, 'too small, skipped', flush=True); continue
                        for kd in kinds:
                            alt, _ = grab(pg, fx, fy, OFF[kd])
                            d = (np.abs(base - alt).sum(2) > LV) & mm
                            f = d.sum() / N; row.append('%s %.2f%%' % (kd, 100 * f)); tot.setdefault((mode, kd), []).append(f)
                            if f > TH:
                                bad.append('%s %s %d/%d c%d r%d %s %.2f%%' % (mode, kd, n, seed, c, r, v, 100 * f))
                                if DUMP:
                                    os.makedirs(DUMP, exist_ok=True); vis = base.copy().astype(np.uint8); vis[d] = [255, 0, 255]; ys, xs = np.where(mm)
                                    Image.fromarray(vis[max(0, ys.min() - 60):ys.max() + 30, max(0, xs.min() - 60):xs.max() + 60]).save(os.path.join(DUMP, 'hs_%s_%d_%d_%s.png' % (mode, n, c, kd)))
                        rows += 1; print(*row, flush=True)
            pg.close()
        b.close()
    if PAGE != SRC: os.remove(PAGE)
    for (m, kd), v in sorted(tot.items()):
        print('summary %-7s %-6s hills %3d  over %.1f%%: %3d  mean %.2f%%  max %.2f%%' % (m, kd, len(v), 100 * TH, sum(1 for x in v if x > TH), 100 * np.mean(v), 100 * max(v)))
    if bad: print('bad:', '; '.join(bad[:40]))
    if errs: print('errors', errs[:3])
    print('heapscan: ok' if not bad and not errs and rows else 'heapscan: FAIL (%d of %d hill frames, errors %d)' % (len(bad), rows, len(errs)))
    sys.exit(0 if not bad and not errs and rows else 1)
