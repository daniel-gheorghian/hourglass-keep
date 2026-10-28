# beamjag.py [file.html] [lo hi] [modes=torch,classic] [rs=1,.75,.5] [nosaver] [noforced] [nothemes] [cases=F:S:K,...] [out=DIR] [shots] [heat] [static]
# (round 46, owner: "The jagged light beams. I think we fixed this at least half a dozen times. Let's try to specify it better and to document
# and enforce it.") Enforces rules S1-S7 of dev/docs/rendering.md ("Low-resolution passes (S, M): no staircases") on the sky beams.
# Static checks first: every shader that works out world positions (wpos, u_cam, tile() is compiled in highp where the device has it (its own
# 'precision highp' or GLCHEAD's guard; S7), and no texture read across a beam is set to NEAREST (the profiles in glcRy, the tile map in
# glcTiles; S4). Then pictures: each case is one opening's beam, the prince out of view (or in it), the guards away, the clock frozen and the beams' moving
# parts off (GLFX.ryClean: the haze's drift, the motes, the dither), drawn twice, with the beams and without them (window.__RYOFF), at a phone's
# 852 x 393 at device scale 2: D = the luma the beams add. D is sampled along lines parallel to the light inside the opening's box swept
# down the light (skyBeam); a beam's light changes slowly along the light, so what is left after a Gaussian of 3 quarter-size texels along
# each line is the staircase (pixels near an edge of the frame without beams, the stone's own detail, are left out). A line steps when its
# residual crosses zero NSC (3) or more times at more than AMP (2) levels; STEP is the share of lines that step. Pass: STEP <= 0.012 at
# GLP.rs 1, .75 and .5 (Torchlight; Classic once), <= 0.03 with Battery saver (canvas at 1x), both modes (th=, thsv= to change them).
# Cases: every theme at every hour it has (themeName and progOf over floors 1-180, its first floor; the first of seeds 2601-2619 with an
# opening whose beam is in the floor's middle, not over a heap or drift), and the forced ones: a low ceiling under a beam (floor 7), a floor's shadow across a beam (a
# beam over a slab's end, floor 50), a blocker in a beam (a shut gate or a slicer in the beam's haze, the first on floors 4-60), the prince in
# a beam (floor 11), sand in a beam (floor 17 seed 19). lo hi keep the cases whose floor is in lo..hi (suite.py splits the run that way).
# Prints one line per case and setting (floor, seed, opening, mode, GLP.rs, STEP, JAG = the 99.9th percentile of the residual), FAIL lines
# with the worst crop's path (on | off | the beams' light scaled to the crop, out=DIR, default dev/tools/beamjag/), and 'beamjag: ok'. Run from dev/tools; HK_GPU=0
# draws WebGL in SwiftShader (default: the GPU, as suite.py's heavy jobs).
import sys, os, io, json, math, re
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
A = dict(x.split('=', 1) for x in a if '=' in x and not x.endswith('.html'))
FL = set(x for x in a if '=' not in x and not x.endswith('.html') and not re.match(r'^\d+$', x))
SRC = os.path.abspath(next((x for x in a if x.endswith('.html') and '=' not in x), os.path.join(HERE, '..', 'hourglass-keep.html')))
NUM = [int(x) for x in a if re.match(r'^\d+$', x)]
LO, HI = (NUM[0], NUM[1]) if len(NUM) >= 2 else (1, 999)
MODES = A.get('modes', 'torch,classic').split(',')
RS = [float(x) for x in A.get('rs', '1,.75,.5').split(',')]
OUT = os.path.abspath(A.get('out', os.path.join(HERE, 'beamjag')))
TH_RS, TH_SV = float(A.get('th', '0.012')), float(A.get('thsv', '0.03'))  # (the research's 0.005 / 0.02 sit inside the GPU's run-to-run noise, +-0.002, on two dawn arch runs: 46a measures up to 0.0095 / 0.021, v87 80 of 164 frames over 0.01 and 15 of 82 over 0.03, up to 0.115)
AMP, NSC, GT = 2.0, 3, 0.6
DPR = 2
BAD = []

# ---- static checks (S4, S7) ----
def static_checks(s):
    bad = []
    head = re.search(r'const GLCHEAD=`(.*?)`;', s, re.S)
    hh = bool(head and 'precision highp float' in head.group(1))
    if not hh: bad.append('GLCHEAD has no precision highp float')
    n = 0
    # every template literal that is a fragment shader (it writes gl_FragColor or declares out vec4) and works out world positions
    for m in re.finditer(r'`([^`]*)`', s, re.S):
        t = m.group(1)
        if not ('gl_FragColor' in t or re.search(r'\bout vec4\b', t)): continue
        if not re.search(r'\bwpos\(|\bu_cam\b|\btile\(', t): continue
        n += 1
        pre = s[max(0, m.start() - 12):m.start()]
        if 'precision highp float' in t or (pre.endswith('GLCHEAD+') and hh): continue
        line = s.count('\n', 0, m.start()) + 1
        bad.append('shader at line %d uses world positions without precision highp (S7)' % line)
    for fn in ('glcRy', 'glcTiles'):
        m = re.search(r'\nfunction %s\(.*?(?=\nfunction |\n//)' % fn, s, re.S)
        if not m: bad.append('function %s not found' % fn); continue
        if 'NEAREST' in m.group(0): bad.append('%s sets NEAREST on a texture read across a beam (S4)' % fn)
    return n, bad

FIND = r'''([n,sd,kind])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS)H.S.hints[id]=1;
  const seeds=sd?[sd]:Array.from({length:19},(_,i)=>2601+i);
  for(const s of seeds){const L=H.load(n,s);H.banner=null;const sb=H.skyBeam();let k=0;
    for(const o of H.ryOps()){if(o.sh.own||o.x0<12*32||o.x1>(L.cols-12)*32)continue;if(o.kind==='arch'&&o.sh.key<'a2')continue;
      const r=(o.fl-o.y0),bx0=Math.min(o.x0,o.x0+sb.dx/sb.dy*r)-8,bx1=Math.max(o.x1,o.x1+sb.dx/sb.dy*r)+8,by0=o.y0,by1=o.fl+4;let ok=kind==='theme'||kind==='fig';
      if(ok&&(L.hills||[]).some(h=>h.r*64+64>=by0&&h.r*64<=by1+64&&(h.c+h.n+1)*32>=bx0&&(h.c-h.n-1)*32<=bx1))continue; // (not over a heap or drift: fpGate's footprint through their half-size canvas is not the S pass; left, rendering.md)
      if(kind==='low'){for(let c=Math.floor(bx0/32);c<=Math.floor(bx1/32)&&!ok;c++)for(let rr=Math.floor(by0/64);rr<=Math.floor(by1/64)&&!ok;rr++)ok=H.ryLow(c,rr,sb.dx>0?-1:1)>0;}
      if(kind==='floor'){const rr=Math.round((o.fl+4)/64)-1;let a1=false,a0=false;for(let c=Math.floor(bx0/32);c<=Math.floor(bx1/32);c++){if(H.tileB(c,rr)===H.WALL)continue;if(H.solidBelow(c,rr))a1=true;else a0=true;}ok=a1&&a0&&o.fl>o.y1+40;}
      if(kind==='blk'){H.ryProfile(o.sh);const nb=H.beamBlockers(bx0,bx1,by0,by1);for(let i=0;i<nb&&!ok;i++)ok=H.ryBlkLit(i,o,sb);}
      if(kind==='sand'){ok=H.sandSegs(bx0,bx1,by0,by1)>0;}
      if(!ok)continue;window.__O={x:(o.x0+o.x1)/2,y:(o.y0+o.y1)/2,fl:o.fl,y0:o.y0,o,fig:kind==='fig'};
      return [n,s,H.themeName(n),o.kind,o.sh.key,L.prog?L.prog.tod:0];}}return null;}'''
SHOW = r'''([mode,rs,off])=>{const H=__HK,O=window.__O,P=H.P,sb=H.skyBeam();P.inv=1e9;
  P.x=O.fig?O.x+sb.dx/sb.dy*(O.fl-O.y)+4:O.x+340+H.viewW/2;P.y=O.fl;P.state='stand';P.face=-1;for(const g of H.G||[])g.x=-1e5; /* (the guards out of the way: a figure in a beam is the forced case's, the prince) */H.cam.x=O.x-H.viewW/2;H.cam.y=O.y-40;H.cam.gy=H.cam.y;
  H.S.set.lightMode=mode;H.mode='play';H.GLP.pipe=false;H.GLP.rs=rs;H.GLP.inSession=true;window.__HKnoauto=true;H.GLFX.ryClean=true;H.GLFX.caustics=false;window.__RYOFF=off;
  for(let i=0;i<4;i++)H.render();if(mode==='torch'&&!(H.GLC&&H.GLC.on&&H.GLC.S&&H.GLC.S.p))return {dead:1}; // (the shafts' shader did not compile or link: Torchlight fell back)
  const X=(H.renderXf||H.XF),cv=document.getElementById('game'),kc=cv.getBoundingClientRect().width/cv.width; // (kc: CSS px per canvas px)
  const ops=H.ryOps().filter(o=>!o.sh.own).map(o=>[(o.x0*X.VZ-X.camD)*kc,(o.y0*X.VZ-X.camDY)*kc,(o.x1*X.VZ-X.camD)*kc,(o.y1*X.VZ-X.camDY)*kc,o.kind]);
  return {dx:sb.dx,dy:sb.dy,ops,css:kc,Ls:(sb.lq+8)*X.VZ*kc,rs:H.GLP.rs};}'''

def luma(im): a = np.asarray(im, dtype=np.float32); return a[..., 0] * .3 + a[..., 1] * .5 + a[..., 2] * .2
def bil(D, x, y):
    h, w = D.shape; x = np.clip(x, 0, w - 1.001); y = np.clip(y, 0, h - 1.001); x0 = np.floor(x).astype(int); y0 = np.floor(y).astype(int); fx = x - x0; fy = y - y0
    return (D[y0, x0] * (1 - fx) + D[y0, x0 + 1] * fx) * (1 - fy) + (D[y0 + 1, x0] * (1 - fx) + D[y0 + 1, x0 + 1] * fx) * fy
def gsm(v, s):
    r = int(3 * s); k = np.exp(-0.5 * (np.arange(-r, r + 1) / s) ** 2); k /= k.sum(); return np.convolve(v, k, mode='same'), r
def flatmask(off):
    from numpy.lib.stride_tricks import sliding_window_view as sw
    g = np.zeros_like(off); g[1:-1, 1:-1] = np.maximum(np.abs(off[1:-1, 2:] - off[1:-1, :-2]), np.abs(off[2:, 1:-1] - off[:-2, 1:-1])) / 2
    k = 3 * DPR; p = np.pad(g > GT, k); return ~sw(p, (2 * k + 1, 2 * k + 1)).max(axis=(2, 3))

HEAT = None  # ('heat': each frame's stepping lines, their residual, saved beside the shots)
def measure(D, FM, info, saver):
    dx, dy = info['dx'], info['dy']
    sig = 3 * 4 * info['css'] * DPR;  # (3 quarter-size texels in screenshot px: css is a canvas px in CSS px, so Battery saver's 1x canvas doubles it)
    res = []; lines = 0; steps = 0; H, W = D.shape; Ls = info['Ls'] * DPR; worst = (0, 0, 0)
    for (x0, y0, x1, y1, kind) in info['ops']:
        x0, y0, x1, y1 = [v * DPR for v in (x0, y0, x1, y1)]; x0 += 2; x1 -= 2; y0 += 2; y1 -= 2
        bx0 = min(x0, x0 + dx * Ls); bx1 = max(x1, x1 + dx * Ls); by0 = y0; by1 = y1 + dy * Ls
        if bx1 < 0 or bx0 > W or by1 < 0 or by0 > H or x1 - x0 < 8 or y1 - y0 < 8: continue
        nx, ny = dy, -dx; cx, cy = (bx0 + bx1) / 2, (by0 + by1) / 2; R = math.hypot(bx1 - bx0, by1 - by0) / 2; t = np.arange(-R, R, 1.0)
        def iv(p, a, b, d):
            if abs(d) < 1e-9: return np.where((p >= a) & (p <= b), -1e9, 1e9), np.where((p >= a) & (p <= b), 1e9, -1e9)
            t1 = (p - b) / d; t2 = (p - a) / d; return np.minimum(t1, t2), np.maximum(t1, t2)
        for u in np.arange(-R, R, 1.0):
            px = cx + nx * u + dx * t; py = cy + ny * u + dy * t
            lx, hx = iv(px, x0, x1, dx); ly, hy = iv(py, y0, y1, dy); lo = np.maximum(np.maximum(lx, ly), 0); hi = np.minimum(np.minimum(hx, hy), Ls)
            m = (lo <= hi) & (px >= 0) & (px < W - 1) & (py >= 0) & (py < H - 1)
            if m.sum() < 8 * sig + 4: continue
            v = bil(D, px[m], py[m]); sm, r = gsm(v, sig); rr = (v - sm)[r:-r]
            ok = FM[np.clip(py[m].astype(int), 0, H - 1), np.clip(px[m].astype(int), 0, W - 1)][r:-r]; rr = rr * ok
            if len(rr) < 4: continue
            lines += 1; res.append(np.abs(rr)); big = np.abs(rr) > AMP
            sc = int(np.sum(np.diff(np.sign(rr[big])) != 0)) if big.sum() > 2 else 0
            if sc >= NSC:
                if HEAT is not None: ii = np.where(m)[0][r:-r]; HEAT[np.clip(py[ii].astype(int), 0, H - 1), np.clip(px[ii].astype(int), 0, W - 1)] = np.abs(rr)
                steps += 1; j = int(np.argmax(np.abs(rr))); ii = np.where(m)[0][r:-r][j]
                if abs(rr[j]) > worst[0]: worst = (abs(rr[j]), px[ii], py[ii])
    if not res: return None
    q = np.concatenate(res)
    return {'step': steps / max(1, lines), 'jag': float(np.percentile(q, 99.9)), 'lines': lines, 'worst': worst}

def crop(on, off, D, x, y, path):
    W, H = on.size; s = 90; bx = (max(0, int(x) - s), max(0, int(y) - s), min(W, int(x) + s), min(H, int(y) + s))
    a = on.crop(bx); b = off.crop(bx); Dc = D[bx[1]:bx[3], bx[0]:bx[2]]; d = Image.fromarray(np.clip(Dc * (230 / max(1, Dc.max())), 0, 255).astype(np.uint8)).convert('RGB')  # (the beams' light, scaled to the crop's brightest)
    out = Image.new('RGB', (a.width * 3 + 8, a.height), (40, 0, 40)); out.paste(a, (0, 0)); out.paste(b, (a.width + 4, 0)); out.paste(d, (2 * a.width + 8, 0))
    out = out.resize((out.width * 2, out.height * 2), Image.NEAREST); out.save(path)

def theme_cases(pg):
    rows = pg.evaluate('''()=>{const H=__HK,seen={},o=[];for(let n=1;n<=180;n++){const k=H.themeOf(n).name+'|'+H.progOf(n).tod;if(seen[k])continue;seen[k]=1;o.push([n,k]);}return o;}''')
    return [(n, 0, 'theme', k) for n, k in rows]
FORCED = [(7, 0, 'low', 'low ceiling under a beam'), (50, 0, 'floor', "a floor's shadow"), (0, 0, 'blk', 'blocker in a beam'),
          (11, 0, 'fig', 'the prince in a beam'), (17, 19, 'sand', 'sand in a beam')]

# an older build (v87 and before) has none of round 46's hooks: a copy of it gets them as string patches, the same switches
def prep(src):
    if 'window.__RYOFF' in src: return SRC
    P = [('(.7+.6*nz+u_sk.z*mo)', '(1.)'), ('float lt=dot(t,vec3(.3,.5,.2)),dz=', 'float lt=dot(t,vec3(.3,.5,.2)),dz=0.*'),
         ('if(ns||cs){\n    const U=GLC.S.u;', 'if((ns||cs)&&!window.__RYOFF){\n    const U=GLC.S.u;'),
         ('function ryBeams2D(ctx,a){', 'function ryBeams2D(ctx,a){if(window.__RYOFF)return;'), ('  ryMotes2D(ctx,dr,sb,a);}', '  }'),
         ('Object.assign(window.__HK,{hurt,', 'Object.assign(window.__HK,{ryLow,beamBlockers,BLK,ryBlkLit,sandSegs,SDS,renderXf,tileB:(c,r)=>B(L,c,r),WALL});Object.assign(window.__HK,{hurt,')]
    for x, y in P:
        assert x in src, 'beamjag: cannot patch the old build at %r' % x; src = src.replace(x, y, 1)
    p = os.path.join(os.path.dirname(SRC), '_beamjag_old.html'); open(p, 'w', encoding='utf-8').write(src); return p

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True); src = open(SRC, encoding='utf-8').read()
    nsh, sbad = static_checks(src)
    print('static: %d world-position shaders, %s' % (nsh, 'ok' if not sbad else '; '.join(sbad)), flush=True)
    for b in sbad: BAD.append('FAIL static ' + b)
    if 'static' in FL:
        print('\n'.join(BAD) if BAD else 'beamjag: ok'); sys.exit(1 if BAD else 0)
    gpu = os.environ.get('HK_GPU', '1') != '0'; PAGE = prep(src)
    with sync_playwright() as p:
        b = p.chromium.launch(args=(['--use-angle=metal', '--force_high_performance_gpu'] if gpu else []) + ['--enable-gpu', '--ignore-gpu-blocklist'])
        errs = []
        def page(saver):
            pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=DPR); pg.on('pageerror', lambda e: errs.append(str(e)))
            pg.goto('file://' + PAGE); pg.wait_for_timeout(700)
            pg.evaluate("()=>{document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.body.classList.remove('panelOpen');const st=document.createElement('style');st.textContent='.ctl,#pause,#pauseBtn,#pad{display:none!important}';document.head.appendChild(st);}")
            if saver: pg.evaluate("()=>{__HK.S.set.saver=true;window.dispatchEvent(new Event('resize'));}"); pg.wait_for_timeout(300)
            return pg
        pg = page(False)
        print(pg.evaluate("()=>{__HK.S.set.lightMode='torch';__HK.render();return __HK.glPrecStr?__HK.glPrecStr():'no glPrecStr'}"), flush=True)
        cases = []
        if 'cases' in A: cases = [tuple(int(v) for v in c.split(':')) + ('theme', 'given') for c in A['cases'].split(',')]
        else:
            if 'nothemes' not in FL: cases += theme_cases(pg)
            if 'noforced' not in FL: cases += FORCED
        cases = [c for c in cases if (LO <= c[0] <= HI if c[0] else LO <= 4 <= HI)]  # (a case found by search runs in the job that holds floor 4)
        found = []
        for (n, sd, kind, what) in cases:
            if n == 0:  # (the first floor that has one)
                q = None
                for m in range(4, 61):
                    q = pg.evaluate(FIND, [m, 0, kind])
                    if q: break
            else: q = pg.evaluate(FIND, [n, sd, kind])
            if not q: BAD.append('FAIL no case: floor %d %s (%s)' % (n, kind, what)); print(BAD[-1], flush=True); continue
            found.append((q, kind, what))
        pg.close()
        rows = 0
        for saver in (False, True):
            if saver and 'nosaver' in FL: continue
            pg = page(saver)
            for (q, kind, what) in found:
                n, sd = q[0], q[1]; pg.evaluate(FIND, [n, sd, kind])
                for mode in MODES:
                    for rs in (RS if mode == 'torch' and not saver else [1.0]):
                        info = pg.evaluate(SHOW, [mode, rs, False])
                        if info.get('dead'): BAD.append('FAIL the shafts shader (GLCSH.s) is not live in Torchlight: it did not compile or link'); print(BAD[-1], flush=True); break
                        on = Image.open(io.BytesIO(pg.screenshot())).convert('RGB')
                        pg.evaluate(SHOW, [mode, rs, True]); off = Image.open(io.BytesIO(pg.screenshot())).convert('RGB')
                        lon, loff = luma(on), luma(off); D = lon - loff
                        if 'heat' in FL: HEAT = np.zeros(D.shape, np.float32)
                        m = measure(D, flatmask(loff), info, saver)
                        tag = 'f%d_s%d_%s_%s_%s%s' % (n, sd, q[4], kind, mode, '_saver' if saver else '_rs%g' % rs)
                        if 'shots' in FL: on.save(os.path.join(OUT, tag + '.png'))
                        if HEAT is not None: Image.fromarray(np.clip(HEAT * 40, 0, 255).astype(np.uint8)).save(os.path.join(OUT, tag + '_heat.png'))
                        rows += 1
                        if not m: print('%-44s %-44s no beam in view' % (tag, q[2][:44]), flush=True); continue
                        th = TH_SV if saver else TH_RS
                        print('%-44s %-44s STEP %.4f JAG %5.2f lines %d' % (tag, q[2][:44], m['step'], m['jag'], m['lines']), flush=True)
                        if m['step'] > th:
                            pth = os.path.join(OUT, tag + '_worst.png'); w = m['worst']; crop(on, off, D, w[1], w[2], pth)
                            BAD.append('FAIL floor %d seed %d opening %s (%s, %s) %s GLP.rs %s STEP %.4f > %.3f worst crop %s' % (
                                n, sd, q[4], q[3], what, mode, 'saver' if saver else '%g' % rs, m['step'], th, pth))
                            print(BAD[-1], flush=True)
            pg.close()
        b.close()
    if errs: BAD.append('FAIL page errors: %s' % errs[:3])
    if PAGE != SRC: os.remove(PAGE)
    print('%d frames measured' % rows)
    print('\n'.join(BAD) if BAD else 'beamjag: ok')
    sys.exit(1 if BAD else 0)
