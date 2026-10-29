# panscan.py [file.html] [lo hi] [seeds]: round 47b's pan check (owner: the courts' background "is moving way too fast"; chose C: the court's far
# side at its true depth and speed). For each theme and hour: a court that is not a light well, 6 cells or more, on floors lo..hi (default 3-180),
# seeds default 1,2, the first found. Classic, the camera at its rest centred on the court, then 32 px further right; no figures, lamps, jambs,
# hills, vine, dapple, wind, haze or atmosphere, the room lights and the grade off (the light map moves with the walls and the vignette stays on
# the screen: either would mix into what is measured). A band's factor is the shift that best matches the two frames (sum of absolute differences,
# sub-pixel) over the walls' shift.
# A build with the test hooks (ctLayersOf, CT_DBG): CT_DBG.top lays the court's opening, a flat key colour, over the finished frame with nothing in
# front, and each of the court's layers is drawn alone on it (what it adds to the key is measured, both frames' key covering it): a thing standing
# in the court (the far side, sphinxes, trees, stelae) is one band over the opening's height and must move at its layer's f within 0.01 (or match
# there nearly as well as at the best, for a layer that repeats along x); the floor is cut into bands 3 px high, each at its own rows' f
# (a row 44 f px under the horizon moves f; within 0.02 of the band's rows); then the theme's view in the bays alone, which must move no faster
# than the far side (+0.01). A layer or band with nothing along x to see (a plain row) is skipped.
# A build without them (v88 and before): the whole court as drawn, in bands 3 px high and segments 20 px wide (the room picture, factor over 0.97
# or matching at the walls' shift nearly as well, skipped); every band must move at the f of a layer it can show (the theme's view no nearer than
# the far side, the far side at the owner's depths: temple, pylon and rock courts 0.12, gardens 0.22, Aksum 0.2) and none faster than 0.25, or
# under the far side's foot at its floor rows' f. Prints each case's bands and failures and 'panscan: ok', or 'panscan: FAIL'. v88's strips slide
# at 0.18, 0.5 and 0.7 (Meroe's pyramids at 1.0, drawn with the walls): it fails all 33 cases. Run from dev/tools.
import io, os, sys, warnings
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
SRC = os.path.abspath(next((x for x in a if x.endswith('.html')), os.path.join(HERE, '..', 'hourglass-keep.html')))
NUM = [int(x) for x in a if x.isdigit()]
LO, HI = (NUM[0], NUM[1]) if len(NUM) >= 2 else (3, 180)
SEEDS = [int(s) for s in next((x for x in a if ',' in x), '1,2').split(',')]
FARF = {'peri': 0.12, 'kush': 0.12, 'mud': 0.12, 'rock': 0.12, 'granite': 0.2, 'perg': 0.22}
DSF, D = 2, 32
FIND = r'''([lo,hi,seeds])=>{const H=__HK,res={};for(let n=lo;n<=hi;n++){const look=H.themeOf(n).look,tod=Math.floor((n-1)/20)%3,key=look+'|'+tod;if(res[key])continue;
  for(const s of seeds){const L=H.genLevel(n,s,true),k=L.courts.find(q=>q.k!=='well'&&q.c1-q.c0>=5);if(k){res[key]={n,s,r:k.r,c0:k.c0,c1:k.c1,k:k.k,far:k.far,look,tod};break;}}}return res;}'''
SETUP = r'''([n,seed,c0,HIDE])=>{const H=__HK;for(const id in H.HINTS){H.S.hints[id]=1;H.S.learned[id]=1;}H.S.windDeaths={};const L=H.load(n,seed,true);H.banner=null;
  const P=H.P;P.inv=1e9;for(const e of H.G)e.x=-9999;for(const s of H.SN)s.x=-9999;P.x=-9999;P.state='stand';H.mode='play';H.LAYER_DBG.hide=new Set(['lamp','jamb','heap','drift','wind','atmo','dapple','vine','haze'].concat(HIDE));
  let q=12345;Math.random=()=>{q=(q*16807)%2147483647;return q/2147483647;};for(const kk of ['l','r','u','d','j','g'])H.setKey('kb',kk,false);H.tick(5);P.x=-9999;
  const k=L.courts.find(q=>q.c0===c0),art=H.BGART[L.theme.look]||H.BGART.nun;let fs=art.layers.map(q=>q.f).concat([0]);
  if(H.ctViewOf)fs=H.ctViewOf(k).ly.map(q=>q.f);const iso=H.ctLayersOf&&H.CT_DBG?H.ctLayersOf(k,0,416,1,0).map(q=>[q.f,q.fl]):[];return {fs,iso};}'''
SHOW = r'''([fx,fy,c0])=>{const H=__HK;H.banner=null;let T=1e6;H.setClock(()=>T);H.setGT(50);
  H.cam.x=fx-H.viewW/2;H.cam.y=fy-115.2;H.cam.gy=fy;window.__HKfreeze=true;document.body.classList.add('panelOpen');const pd=document.getElementById('pad');if(pd)pd.style.display='none';
  for(let i=0;i<3;i++)H.render();const X=H.XF,cv=[...document.querySelectorAll('canvas')].find(c=>c.getBoundingClientRect().width>0),R=cv.getBoundingClientRect(),k=X.VZ/cv.width*R.width;
  let hz=fy-4-44-H.cam.y;const L=H.L,kk=L.courts.find(q=>q.c0===c0);if(H.bgEyeY){H.BGV.y=H.cam.y;hz=H.bgEyeY(0.3,H.bgAnchor([kk.c0*32,(kk.r-1)*64,64,1,0,kk]));}
  return [R.left-X.camD/cv.width*R.width,R.top-X.camDY/cv.height*R.height,k,hz];}'''
def sadl(a, b, v):  # (a thing's own pixels: where it shows in either frame, both frames showing the bay there)
    m = v & ((a > 3) | (b > 3)); return np.abs(a - b)[m].mean() if m.sum() >= 40 else 1e3
def sad(a, b, m):
    return np.abs(a - b)[m].mean() if m.sum() >= 40 else 1e3
def grab(pg, fx, fy, c0):
    q = pg.evaluate(SHOW, [fx, fy, c0]); rgb = np.asarray(Image.open(io.BytesIO(pg.screenshot())).convert('RGB'), dtype=np.float32)
    return q, rgb.mean(axis=2), rgb
def keyc(rgb):  # (where a court's bays show: the key colour of CT_DBG.noview, magenta)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]; return (r > 70) & (b > 70) & (g < 0.3 * np.minimum(r, b))  # (shaded toward the edges by the scene's own fills)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 852, 'height': 393}); pg.goto('file://' + SRC); pg.wait_for_timeout(700)
    cases = pg.evaluate(FIND, [LO, HI, SEEDS]); pg.close(); bad, total = [], 0
    for key in sorted(cases):
        c = cases[key]; fy = (c['r'] + 1) * 64 - 4; xc = (c['c0'] + c['c1'] + 1) * 16; ff = FARF[c['far'] if c['k'] == 'fore' else c['k']]
        pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=DSF); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto('file://' + SRC); pg.wait_for_timeout(700)
        pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.body.classList.remove('panelOpen');__HK.S.set.lightMode='classic';(__HK.S.set.gfx||(__HK.S.set.gfx={})).light=false;__HK.S.set.gfx.grade=false")
        info = pg.evaluate(SETUP, [c['n'], c['s'], c['c0'], [x for x in os.environ.get('PANHIDE', '').split(',') if x]])
        top = (c['r'] - 1) * 64; cut = 2 * 64 - 4 - 4 - {'peri': 6, 'perg': 26, 'fore': 3}[c['k']]; camTop = fy - 115.2
        def bands(rule, base=None, fexp=None, whole=False):  # each band's factor between the two frames; rule(m, vy0, vy1, hz) True when it is right; base: the frames without the
            # thing measured, so only its own pixels count (columns and posts in front of it, moving with the walls, are left out)
            q0, A, _ = grab(pg, xc, fy, c['c0']); q1, B, _ = grab(pg, xc + D, fy, c['c0']); VA = VB = None
            if base: VA, VB = base[2], base[3]; A, B = np.abs(A - base[0]), np.abs(B - base[1])  # (a thing alone: what it adds to the frame without it, so the void, columns and posts in front of it, and the screen-fixed shading, all drop out)
            k = q0[2] * DSF; ox, oy = q0[0] * DSF, q0[1] * DSF; wall = D * k; hz = q0[3]; nb, fails = 0, []
            BHh = cut - 4 if whole else 3.0  # (a thing standing in the court is measured whole: one band over the opening's height)
            for yv in np.arange(top + 1, top + cut - 3, BHh):
                yy0, yy1 = max(0, int(oy + yv * k)), min(A.shape[0], int(oy + (yv + BHh) * k))
                if yy1 - yy0 < 4: continue
                vy0, vy1 = yv - camTop, yv + BHh - camTop  # (view y of the band)
                SW = (c['c1'] - c['c0'] + 1) * 32 - 36 if base else 20  # (a layer alone is measured over the court's whole width: its rows repeat, a short segment can alias)
                for xv in np.arange(c['c0'] * 32 + 18, (c['c1'] + 1) * 32 - 18 - SW + 0.1, 20.0):
                    x0, x1 = int(ox + xv * k), int(ox + (xv + SW) * k); a0 = A[yy0:yy1, x0:x1]; va = VA[yy0:yy1, x0:x1] if base else None; mk = (a0 > 3) & va if base else np.ones(a0.shape, bool)
                    if mk.sum() < (60 if base else 0.15 * mk.size) or (not base and a0[mk].std() < 4): continue
                    if base:  # (alone: it must vary along x where the court shows, or nothing moves to be measured: a floor's plain rows)
                        cv = a0[:, va.all(0)]
                        if cv.shape[1] < 8 or cv.mean(0).std() < 2: continue  # (a layer alone: lower contrast suffices, nothing else moves)
                    errs2 = np.array([sadl(a0, B[yy0:yy1, x0 - s:x1 - s], va & VB[yy0:yy1, x0 - s:x1 - s]) if base else sad(a0, B[yy0:yy1, x0 - s:x1 - s], mk) for s in range(0, int(wall) + 6)])
                    i = int(errs2.argmin())
                    if (i == 0 and not base) or i >= len(errs2) - 1 or np.median(errs2) - errs2[i] < (1 if base else 1.5): continue
                    dd = errs2[i - 1] - 2 * errs2[i] + errs2[i + 1] if i else 0; m = (i + (0.5 * (errs2[i - 1] - errs2[i + 1]) / dd if dd else 0)) / wall  # (alone, a shift of 0 is a still sky)
                    if not base and (m > 0.97 or errs2[max(0, int(wall) - 1):int(wall) + 3].min() - errs2[i] < 3): continue  # (the room picture, or a pattern that also matches it: the frieze's period)
                    nb += 1
                    if fexp is not None and not rule(m, vy0, vy1, hz):  # (a layer that repeats along x (columns, joints, fronds) can match an alias as well: right if it matches at its own f nearly as well as at the best, within a quarter of the curve's depth)
                        se = fexp * wall; j = int(se); e = errs2[j] + (se - j) * (errs2[j + 1] - errs2[j]); m = fexp if e - errs2[i] <= max(0.5, 0.25 * (np.median(errs2) - errs2[i])) else m
                    if fexp is None and base and not whole and not rule(m, vy0, vy1, hz):  # (a floor's band: right if it matches at a shift of its own rows nearly as well as at the best)
                        sa, sb = max(0, int(((vy0 - hz) / 44 - 0.02) * wall)), min(len(errs2) - 1, int(((vy1 - hz) / 44 + 0.02) * wall) + 1)
                        if sb >= sa and errs2[sa:sb + 1].min() - errs2[i] <= max(0.5, 0.25 * (np.median(errs2) - errs2[i])): m = (vy0 + vy1) / 2 / 44 - hz / 44
                    if not rule(m, vy0, vy1, hz): fails.append('y %.0f x %.0f: %.3f' % (vy0, xv - c['c0'] * 32, m))
            return nb, fails
        floor_rows = lambda m, vy0, vy1, hz: (vy0 - hz) / 44 - 0.02 <= m <= (vy1 - hz) / 44 + 0.02  # (the court floor's own rows: a row 44 f px under the horizon moves f)
        nb, fails = 0, []
        if info['iso']:  # (a build with the hooks: each court layer alone over nothing, then the theme's view alone)
            pg.evaluate("()=>{__HK.CT_DBG.top=true;__HK.CT_DBG.only=-1;__HK.CT_DBG.noview=true;}"); base = [grab(pg, xc, fy, c['c0']), grab(pg, xc + D, fy, c['c0'])]; base = [base[0][1], base[1][1], keyc(base[0][2]), keyc(base[1][2])]
            for i, (f, fl) in enumerate(info['iso']):
                pg.evaluate("i=>{__HK.CT_DBG.only=i;__HK.CT_DBG.noview=true;}", i)
                n1, f1 = bands((lambda m, a, b2, hz: floor_rows(m, a, b2, hz)) if fl else (lambda m, a, b2, hz, f=f: abs(m - f) <= 0.01), base, None if fl else f, not fl)
                nb += n1; fails += ['layer f %g%s: %s' % (f, ' (floor)' if fl else '', x) for x in f1]
            pg.evaluate("()=>{__HK.CT_DBG.only=-1;__HK.CT_DBG.noview=false;}")
            n1, f1 = bands(lambda m, a, b2, hz: m <= ff + 0.01, base, None, True); nb += n1; fails += ['view: ' + x for x in f1]
            pg.evaluate("()=>{__HK.CT_DBG.only=null;__HK.CT_DBG.top=false;}")
        else:  # (no hooks, v88 and before: the whole court; every band at a layer's f it can show, nothing over 0.25 but the floor's rows)
            allowed = sorted(set([round(f, 4) for f in info['fs'] + [ff]]))
            nb, fails = bands(lambda m, a, b2, hz: (any(abs(m - f) <= 0.01 for f in allowed) and m <= 0.26) or (a >= hz + 44 * ff and floor_rows(m, a, b2, hz)))
        nf = len(fails)
        total += nb
        print('%-10s floor %3d seed %d %s%s: %d bands, %d off (layers %s)' % (key, c['n'], c['s'], c['k'], '/' + c['far'] if c['far'] else '', nb, nf, ','.join('%g%s' % (f, 'fl' if fl else '') for f, fl in info['iso']) or '-'))
        for x in fails[:4]: print('    ' + x)
        if nf or not nb or errs: bad.append(key)
        if errs: print('    page errors', errs[:2])
        pg.close()
    print('panscan: ' + ('ok' if not bad and total else 'FAIL (%s)' % ', '.join(bad)))
    b.close()
