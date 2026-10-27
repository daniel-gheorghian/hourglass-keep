# egyptr44.py [new.html] [old=FILE] [outdir] [nogif] [measure]: round 44's pictures and numbers: the wind (L.winds, placeWinds).
# r44_wind.png: one row per kind and theme (a steady draught in a sandy theme and in Nun/Osiris/Aksum, a gust at a window in its lull,
#   warning and peak, the wind over a drift): him running into it with the arrow held, Classic and Torchlight, before (old=FILE, no wind)
#   | after, 3x (3 screen px a world px).
# r44_phone.png: the same scenes as the whole screen at the phone's size (852 x 393 css px), after, both modes.
# r44_jump.png: a running and a standing jump into the steady draught and into a gust's peak, the still-air arc (old=FILE, or the wind
#   taken out) against the arc in the wind, dots at his hip, with the reach of each.
# r44_gust.gif: real time, Classic, 2x: standing in a gust he is pushed back, then crouches and holds; r44_jump.gif: a running jump into it.
# measure: the reach of the running and standing jump in still air, the steady draught and a gust's peak (prints JSON).
# Run from dev/tools (HK_GPU=1: Torchlight on the GPU).
import io, os, sys, json
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
NEW = os.path.abspath(next((x for x in a if x.endswith('.html') and '=' not in x), os.path.join(HERE, '..', 'hourglass-keep.html')))
OLD = next((os.path.abspath(x[4:]) for x in a if x.startswith('old=')), None)
OUTD = next((x for x in a if not x.endswith('.html') and x not in ('nogif', 'measure') and '=' not in x), os.path.join(HERE, 'egypt_themes'))
INK = (20, 16, 24)
BW, BH, ZK = 240, 112, 3
GPU = ['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist', '--force_high_performance_gpu'] if os.environ.get('HK_GPU') else []
# (kind, look or '', want a hanging) rows
WANT = [('s', 'meroe'), ('s', 'west'), ('s', 'nun'), ('s', 'aksum'), ('g', ''), ('d', 'foggara'), ('h', '')]
FIND = r'''([k,look])=>{const H=__HK;for(let n=3;n<=60;n++){for(let s=0;s<12;s++){const seed=44000+n*97+s*13,L=H.genLevel(n,seed,true);if(look&&L.theme.look!==look)break;
  const z=(L.winds||[]).find(z=>k==='h'?(L.hangings||[]).some(h=>h.wz===z):z.k===k&&(z.k!=='s'||z.n>=4));if(z)return [n,seed,z.c,z.r,z.n,z.dir,z.k];}}return null;}'''
# the prince walking into the zone (k ticks with the arrow held), or standing at u px into it; ph: the gust's phase at the picture
SETUP = r'''([n,seed,c,r,nn,dir,walk,k,u,ph,crouch])=>{const H=__HK;for(const id in H.HINTS){H.S.hints[id]=1;H.S.learned[id]=1;}const L=H.load(n,seed,true);H.banner=null;
  const P=H.P;P.inv=1e9;for(const e of H.G)e.x=-9999;const rd=-dir,x0=rd>0?c*32:(c+nn)*32;
  P.x=walk?x0-rd*10:x0+rd*u;P.y=(r+1)*64-4;P.fallY=P.y;P.vx=0;P.face=rd;P.state='stand';H.mode='play';
  let q=12345;Math.random=()=>{q=(q*16807)%2147483647;return q/2147483647;};
  for(const kk of ['l','r','u','d','j','g'])H.setKey('kb',kk,false);H.tick(20);
  const z=(L.winds||[]).find(z=>z.c===c&&z.r===r);if(z&&ph!==null)z.ph=ph-H.gameTime-k/60;
  if(walk)H.setKey('kb',rd>0?'r':'l',true);if(crouch)H.setKey('kb','d',true);H.tick(k);
  return [P.x,P.state,Math.round(P.vx),H.themeName(n),z?Math.round(H.windE(z,H.gameTime)*100)/100:0];}'''
SHOW = r'''([fx,fy])=>{const H=__HK;H.banner=null;let T=1e6+H.gameTime*1000;H.setClock(()=>T);
  H.cam.x=fx-H.viewW/2;H.cam.y=fy-192*0.62;H.cam.gy=fy;if(H.GLP){H.GLP.pipe=false;H.GLP.rs=1;window.__HKnoauto=true;}
  window.__HKfreeze=true;for(let i=0;i<3;i++)H.render();const X=H.XF,cv=[...document.querySelectorAll('canvas')].find(c=>c.getBoundingClientRect().width>0),R=cv.getBoundingClientRect(),k=X.VZ/cv.width*R.width;
  return [R.left-X.camD/cv.width*R.width,R.top-X.camDY/cv.height*R.height,k];}'''
# a jump into the zone's wind: run-up (or stand) from its downwind end, the jump, the flight sampled each tick; still: the wind taken out
JUMP = r'''([n,seed,c,r,nn,dir,run,ph,still])=>{const H=__HK;const L=H.load(n,seed,true);H.banner=null;const P=H.P;P.inv=1e9;for(const e of H.G)e.x=-9999;
  const rd=-dir,x0=rd>0?c*32:(c+nn)*32;P.x=x0+rd*(run?4:24);P.y=(r+1)*64-4;P.fallY=P.y;P.vx=0;P.face=rd;P.state='stand';H.mode='play';
  for(const kk of ['l','r','u','d','j','g'])H.setKey('kb',kk,false);H.tick(20);
  const z=(L.winds||[]).find(z=>z.c===c&&z.r===r);if(z&&still)L.winds.length=0;if(z&&ph!==null)z.ph=ph-H.gameTime;
  const k=rd>0?'r':'l',pts=[];if(run){H.setKey('kb',k,true);H.tick(8);}H.setKey('kb','j',true);H.tick(1);H.setKey('kb','j',false);
  for(let i=0;i<200;i++){H.tick(1);if(P.state==='air'||P.state==='jumpPrep'){if(P.state==='air')pts.push([P.x,P.y]);}else if(pts.length)break;}
  H.setKey('kb',k,false);return {pts,x0:pts.length?pts[0][0]:0,x1:pts.length?pts[pts.length-1][0]:0,st:P.state,e:z?H.windE(z,H.gameTime):0};}'''


def page(b, mode, dsf=3, html=None):
    pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=dsf)
    pg.errs = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e)))
    pg.goto('file://' + (html or NEW))
    pg.wait_for_timeout(800)
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.body.classList.remove('panelOpen')")
    pg.evaluate("m=>{__HK.S.set.lightMode=m;}", mode)
    pg.dsf = dsf
    return pg


def shot(pg, fx, fy, zk=ZK, bh=BH, up=86):
    q = pg.evaluate(SHOW, [fx, fy])
    im = Image.open(io.BytesIO(pg.screenshot())).convert('RGB')
    d = pg.dsf
    ox, oy, k = q[0] * d, q[1] * d, q[2] * d
    x0, y0 = ox + (fx - BW / 2) * k, oy + (fy - up) * k
    crop = im.crop((int(x0), int(y0), int(x0 + BW * k), int(y0 + bh * k))).resize((BW * zk, bh * zk), Image.LANCZOS)
    return crop, im.resize((852, 393), Image.LANCZOS), (x0, y0, k)


def label(im, t):
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 8 + 6 * len(t), 13), fill=(0, 0, 0))
    d.text((4, 1), t, fill=(250, 240, 215))


def row(cells):
    w, h = cells[0].size
    R = Image.new('RGB', (len(cells) * (w + 6), h + 6), INK)
    for i, c in enumerate(cells): R.paste(c, (i * (w + 6), 3))
    return R


def sheet(rows, fn):
    S = Image.new('RGB', (max(r.width for r in rows), sum(r.height for r in rows)), INK); y = 0
    for r in rows: S.paste(r, (0, y)); y += r.height
    S.save(fn, optimize=True); print('wrote', fn, S.size)


NAMES = {'s': 'steady draught', 'g': 'gust at a window', 'd': 'wind over a drift', 'h': 'a hanging billowing'}
KN = {'s': 'W1', 'g': 'W2', 'd': 'W3', 'h': 'W1'}


def moments(k):
    if k == 'g': return [('lull, running in', 1, 36, 1.0, 0), ('warning: sand pours in', 1, 36, 2.35, 0), ('gust: running in', 1, 36, 3.3, 0), ('gust: standing, pushed back', 0, 40, 3.3, 0)]
    if k == 'd': return [('running in, the arrow held', 1, 30, None, 0), ('wading into it', 1, 80, None, 0)]
    return [('running in, the arrow held', 1, 40, None, 0)]


def stills(b, spots):
    rows, ph = [], []
    for mode in ('classic', 'torch'):
        for tag, html in ((('before', OLD),) if OLD else ()) + (('after', NEW),):
            pg = page(b, mode, 3, html)
            for (k, lk, sp) in spots:
                n, seed, c, r, nn, dr, kk = sp
                fx, fy = (c + nn / 2) * 32, (r + 1) * 64 - 4
                up, bh = (150, 176) if k == 'h' else (86, BH)
                for j, (lab, walk, tk, phs, cr) in enumerate(moments(k)):
                    i = pg.evaluate(SETUP, [n, seed, c, r, nn, dr, walk, tk, 32, phs, cr])
                    cp, phone, _ = shot(pg, fx, fy, bh=bh, up=up)
                    label(cp, '%s %s  %s  %s  %s: %s (%d px/s, e %.2f)' % (KN[k], NAMES[k], i[3], 'Torchlight' if mode == 'torch' else 'Classic', tag, lab, abs(i[2]), i[4]))
                    STILL.setdefault((k, lk, j), {})[(mode, tag)] = cp
                    if tag == 'after' and j == len(moments(k)) - 1 and k != 'h':
                        p2 = phone.copy(); label(p2, '%s %s  %s  %s  phone size' % (KN[k], NAMES[k], i[3], 'Torchlight' if mode == 'torch' else 'Classic')); ph.append(p2)
                if pg.errs: print('ERR', pg.errs[:2])
            pg.close()
            print(mode, tag, flush=True)
    for (k, lk, sp) in spots:
        for j in range(len(moments(k))):
            d = STILL[(k, lk, j)]
            rows.append(row([d[x] for x in [(m, t) for m in ('classic', 'torch') for t in (('before', 'after') if OLD else ('after',))]]))
    sheet(rows, os.path.join(OUTD, 'r44_wind.png'))
    S = Image.new('RGB', (2 * 858, ((len(ph) + 1) // 2) * 399), INK)
    for q, im in enumerate(ph): S.paste(im, ((q % 2) * 858, (q // 2) * 399))
    fn = os.path.join(OUTD, 'r44_phone.png'); S.save(fn, optimize=True); print('wrote', fn, S.size)


STILL = {}


def jumps(b, spots, draw=True):
    sp = next(s for k, lk, s in spots if k == 'g')
    n, seed, c, r, nn, dr, kk = sp
    out = {}
    pg = page(b, 'classic', 3)
    cells = []
    for run in (1, 0):
        for phs, nm in ((None, 'steady'), (3.3, 'gust peak')):
            if nm == 'steady':
                s2 = next(s for k, lk, s in spots if k == 's')
            else:
                s2 = sp
            n, seed, c, r, nn, dr, kk = s2
            st = pg.evaluate(JUMP, [n, seed, c, r, nn, dr, run, phs, True])
            wi = pg.evaluate(JUMP, [n, seed, c, r, nn, dr, run, phs, False])
            ls, lw = abs(st['x1'] - st['x0']), abs(wi['x1'] - wi['x0'])
            key = ('running' if run else 'standing') + ' jump, ' + nm
            out[key] = {'still': round(ls, 1), 'wind': round(lw, 1), 'lost %': round(100 * (1 - lw / ls), 1) if ls else None, 'e': round(wi['e'], 2)}
            if draw:
                fx = (st['x0'] + st['x1']) / 2; fy = (r + 1) * 64 - 4
                cp, _, (X0, Y0, k) = shot(pg, fx, fy)
                d = ImageDraw.Draw(cp)
                for pts, col in ((st['pts'], (120, 230, 255)), (wi['pts'], (255, 150, 90))):
                    for x, y in pts:
                        X = (x - (fx - BW / 2)) * ZK; Y = (y - 30 - (fy - 86)) * ZK
                        d.ellipse((X - 3, Y - 3, X + 3, Y + 3), fill=col)
                label(cp, 'W  %s: still air (blue) %.1f px, into the wind (orange, e %.2f) %.1f px: %.0f%% shorter' % (key, ls, wi['e'], lw, 100 * (1 - lw / ls) if ls else 0))
                cells.append(cp)
    pg.close()
    if draw: sheet([row(cells[:2]), row(cells[2:])], os.path.join(OUTD, 'r44_jump.png'))
    print(json.dumps(out, indent=1))
    return out


def gifs(b, spots):
    sp = next(s for k, lk, s in spots if k == 'g')
    n, seed, c, r, nn, dr, kk = sp
    fx, fy = (c + nn / 2) * 32, (r + 1) * 64 - 4
    gp = page(b, 'classic', 2)
    frames = []
    gp.evaluate(SETUP, [n, seed, c, r, nn, dr, 0, 1, 56, 0.5, 0])
    for i in range(110):  # lull, warning, the gust pushes him back; then he crouches through the next one
        if i == 75: gp.evaluate("()=>__HK.setKey('kb','d',true)")
        cp, _, _ = shot(gp, fx, fy, zk=2); frames.append(cp); gp.evaluate("()=>{__HK.tick(3);}")
    gp.evaluate("()=>__HK.setKey('kb','d',false)")
    fn = os.path.join(OUTD, 'r44_gust.gif'); frames[0].save(fn, save_all=True, append_images=frames[1:], duration=50, loop=0, optimize=True); print('wrote', fn, len(frames))
    frames = []
    s2 = next(s for k, lk, s in spots if k == 's')
    n, seed, c, r, nn, dr, kk = s2
    fx, fy = (c + nn / 2) * 32, (r + 1) * 64 - 4
    gp.evaluate(SETUP, [n, seed, c, r, nn, dr, 1, 1, 0, None, 0])
    for i in range(50):
        if i == 6: gp.evaluate("()=>{__HK.setKey('kb','j',true);}")
        if i == 7: gp.evaluate("()=>{__HK.setKey('kb','j',false);}")
        cp, _, _ = shot(gp, fx, fy, zk=2); frames.append(cp); gp.evaluate("()=>{__HK.tick(2);}")
    gp.close()
    fn = os.path.join(OUTD, 'r44_jump.gif'); frames[0].save(fn, save_all=True, append_images=frames[1:], duration=33, loop=0, optimize=True); print('wrote', fn, len(frames))


if __name__ == '__main__':
    os.makedirs(OUTD, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(args=GPU)
        p0 = page(b, 'classic', 1)
        spots = []
        for k, lk in WANT:
            s = p0.evaluate(FIND, [k, lk])
            print('spot', k, lk, s, flush=True)
            if s: spots.append((k, lk, s))
        p0.close()
        if 'measure' in a:
            jumps(b, spots, False)
        else:
            stills(b, spots)
            jumps(b, spots)
            if 'nogif' not in a: gifs(b, spots)
        b.close()
