# egyptr43.py [new.html] [outdir] [nogif]: round 43's pictures: the heaps (B1 tumbled masonry, B2 mudbrick slump, B3 fallen column) and the sand
# drift (C2, now and then with half-buried blocks) as placeHills puts them on the floors, in several themes, Classic and Torchlight.
# r43_hills.png: one row per look and theme: him standing on it (in it, knee deep), then walking into it with the arrow held (the clamber, the
#   wade), each mode, crops at 3x (3 screen px a world px).
# r43_phone.png: the same scenes as the whole screen at the phone's size (852 x 393 css px), Torchlight and Classic.
# r43_hills.gif: real time, Classic, 2x: a wade through a drift and a clamber over a heap, the arrow held.
# old=FILE (round 43b, owner: "Wind truly against him"): the drift before | after instead: r43b_drift.png (each drift row: him 0.35 s and
#   1.1 s into it with the arrow held, Classic and Torchlight, before | after, 3x), r43b_phone.png (phone size, before | after, Torchlight),
#   r43b_wade.gif (after, Classic, 2x: a wade from one end to the other).
# Run from dev/tools (HK_GPU=1: Torchlight on the GPU).
import io, os, sys
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
NEW = os.path.abspath(next((x for x in a if x.endswith('.html') and '=' not in x), os.path.join(HERE, '..', 'hourglass-keep.html')))
OLD = next((os.path.abspath(x[4:]) for x in a if x.startswith('old=')), None)
OUTD = next((x for x in a if not x.endswith('.html') and x != 'nogif' and '=' not in x), os.path.join(HERE, 'egypt_themes'))
INK = (20, 16, 24)
BW, BH, ZK = 240, 112, 3
GPU = ['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist', '--force_high_performance_gpu'] if os.environ.get('HK_GPU') else []
# (look, theme) rows: a hill of that look on a floor of that theme
WANT = [('B1', 'west'), ('B1', 'hawara'), ('B1', 'aksum'), ('B2', 'deffufa'), ('B2', 'shali'), ('B3', 'osiris'), ('B3', 'meroe'), ('B3', 'nun'),
        ('C2', 'foggara'), ('C2', 'hawara'), ('C2', 'blue'), ('C2b', 'napata'), ('C2b', 'wells')]
FIND = r'''([v,look])=>{const H=__HK;for(let n=3;n<=120;n++){if(H.THEMES&&0){}for(let s=0;s<12;s++){const seed=43000+n*97+s*13,L=H.genLevel(n,seed,true);if(L.theme.look!==look)break;
  const h=(L.hills||[]).find(h=>(v==='C2b'?h.v==='C2'&&h.blk:v==='C2'?h.v==='C2'&&!h.blk:h.v===v));if(h)return [n,seed,h.c,h.r,h.n,h.dir,h.d];}}return null;}'''
# the prince at u px along the hill (standing), or 14 px before it (its plain margin cell) walking in with the arrow held for k ticks
SETUP = r'''([n,seed,c,r,u,walk,k])=>{const H=__HK;for(const id in H.HINTS){H.S.hints[id]=1;H.S.learned[id]=1;}const L=H.load(n,seed,true);H.banner=null;
  const h=L.hills.find(q=>q.c===c&&q.r===r),P=H.P;P.inv=1e9;for(const e of H.G)e.x=-9999;const dir=h.dir||1,x0=dir>0?c*32:(c+h.n)*32;
  P.x=walk?x0-dir*14:c*32+u;P.y=(r+1)*64-4;P.fallY=P.y;P.vx=0;P.face=dir;P.state='stand';H.mode='play';
  let q=12345;Math.random=()=>{q=(q*16807)%2147483647;return q/2147483647;};
  for(const kk of ['l','r','u','j','g'])H.setKey('kb',kk,false);H.tick(30);
  if(walk){H.setKey('kb',dir>0?'r':'l',true);H.tick(k);}
  return [P.x,P.state,Math.round(P.vx),H.themeName(n)];}'''
SHOW = r'''([fx,fy,hold])=>{const H=__HK;H.banner=null;let T=1e6+H.gameTime*1000;H.setClock(()=>T);
  H.cam.x=fx-H.viewW/2;H.cam.y=fy-192*0.62;H.cam.gy=fy;if(H.GLP){H.GLP.pipe=false;H.GLP.rs=1;window.__HKnoauto=true;}
  window.__HKfreeze=true;for(let i=0;i<3;i++)H.render();const X=H.XF,cv=[...document.querySelectorAll('canvas')].find(c=>c.getBoundingClientRect().width>0),R=cv.getBoundingClientRect(),k=X.VZ/cv.width*R.width;
  return [R.left-X.camD/cv.width*R.width,R.top-X.camDY/cv.height*R.height,k];}'''


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


def shot(pg, fx, fy, zk=ZK):
    q = pg.evaluate(SHOW, [fx, fy, 0])
    im = Image.open(io.BytesIO(pg.screenshot())).convert('RGB')
    d = pg.dsf
    ox, oy, k = q[0] * d, q[1] * d, q[2] * d
    x0, y0 = ox + (fx - BW / 2) * k, oy + (fy - 86) * k
    crop = im.crop((int(x0), int(y0), int(x0 + BW * k), int(y0 + BH * k))).resize((BW * zk, BH * zk), Image.LANCZOS)
    return crop, im.resize((852, 393), Image.LANCZOS)


def label(im, t):
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 8 + 6 * len(t), 13), fill=(0, 0, 0))
    d.text((4, 1), t, fill=(250, 240, 215))


NAMES = {'B1': 'B1 tumbled masonry', 'B2': 'B2 mudbrick slump', 'B3': 'B3 fallen column', 'C2': 'C2 sand drift', 'C2b': 'C2 drift, half-buried blocks'}

def before_after():
    spots = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=GPU)
        p0 = page(b, 'classic', 1)
        for v, lk in [x for x in WANT if x[0].startswith('C2')]:
            sp = p0.evaluate(FIND, [v, lk])
            if sp: spots.append((v, lk, sp))
        p0.close()
        res = {}
        for tag, html in (('before', OLD), ('after', NEW)):
            for mode in ('classic', 'torch'):
                pg = page(b, mode, 3, html)
                for v, lk, (n, seed, c, r, nn, dr, isd) in spots:
                    fx, fy = c * 32 + nn * 16, (r + 1) * 64 - 4
                    out = []
                    for k in (21, 66):
                        i = pg.evaluate(SETUP, [n, seed, c, r, 0, 1, k]); out.append(shot(pg, fx, fy) + (i,))
                    res[(tag, mode, lk, v)] = out
                    print(tag, mode, v, lk, flush=True)
                pg.close()
        rows = []
        for v, lk, sp in spots:
            for j, t in enumerate(('0.35 s in', '1.1 s in')):
                cells = []
                for mode in ('classic', 'torch'):
                    for tag in ('before', 'after'):
                        cr, ph, i = res[(tag, mode, lk, v)][j]
                        c2 = cr.copy(); label(c2, '%s  %s  %s  %s (%s): %s, the arrow held' % (NAMES[v], i[3], 'Torchlight' if mode == 'torch' else 'Classic', tag, 'round 43' if tag == 'before' else '43b, wind against him', t)); cells.append(c2)
                w, h = cells[0].size
                row = Image.new('RGB', (len(cells) * (w + 6), h + 6), INK)
                for q, cc in enumerate(cells): row.paste(cc, (q * (w + 6), 3))
                rows.append(row)
        sheet = Image.new('RGB', (max(r.width for r in rows), sum(r.height for r in rows)), INK); y = 0
        for r_ in rows: sheet.paste(r_, (0, y)); y += r_.height
        fn = os.path.join(OUTD, 'r43b_drift.png'); sheet.save(fn, optimize=True); print('wrote', fn, sheet.size)
        ph = []
        for v, lk, sp in spots:
            for tag in ('before', 'after'):
                im = res[(tag, 'torch', lk, v)][1][1].copy(); label(im, '%s  %s  %s  phone size' % (NAMES[v], lk, tag)); ph.append(im)
        sheet = Image.new('RGB', (2 * 858, ((len(ph) + 1) // 2) * 399), INK)
        for q, im in enumerate(ph): sheet.paste(im, ((q % 2) * 858, (q // 2) * 399))
        fn = os.path.join(OUTD, 'r43b_phone.png'); sheet.save(fn, optimize=True); print('wrote', fn, sheet.size)
        gp = page(b, 'classic', 2); frames = []
        v, lk, (n, seed, c, r, nn, dr, isd) = spots[0]
        fx, fy = c * 32 + nn * 16, (r + 1) * 64 - 4
        gp.evaluate(SETUP, [n, seed, c, r, 0, 1, 1])
        for i in range(int((nn * 32 + 50) / 42 * 60 / 3)):
            q = gp.evaluate(SHOW, [fx, fy, 0])
            im = Image.open(io.BytesIO(gp.screenshot())).convert('RGB'); d = gp.dsf
            ox, oy, k = q[0] * d, q[1] * d, q[2] * d; x0, y0 = ox + (fx - BW / 2) * k, oy + (fy - 86) * k
            frames.append(im.crop((int(x0), int(y0), int(x0 + BW * k), int(y0 + BH * k))).resize((BW * 2, BH * 2), Image.LANCZOS))
            gp.evaluate("()=>{__HK.tick(3);}")
        gp.close()
        fn = os.path.join(OUTD, 'r43b_wade.gif'); frames[0].save(fn, save_all=True, append_images=frames[1:], duration=50, loop=0, optimize=True); print('wrote', fn, len(frames), 'frames')
        b.close()


if __name__ == '__main__' and OLD:
    os.makedirs(OUTD, exist_ok=True)
    before_after()
elif __name__ == '__main__':
    os.makedirs(OUTD, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(args=GPU)
        p0 = page(b, 'classic', 1)
        spots = []
        for v, lk in WANT:
            s = p0.evaluate(FIND, [v, lk])
            print('spot', v, lk, s, flush=True)
            if s: spots.append((v, lk, s))
        p0.close()
        res = {}
        errs = []
        for mode in ('classic', 'torch'):
            pg = page(b, mode)
            for v, lk, (n, seed, c, r, nn, dr, isd) in spots:
                Ln = nn * 32; fx, fy = c * 32 + Ln / 2, (r + 1) * 64 - 4
                u = Ln * (0.55 if v == 'B3' else 0.5 if isd else 0.48)
                i1 = pg.evaluate(SETUP, [n, seed, c, r, u, 0, 0]); A = shot(pg, fx, fy)
                k = 60 if isd else 50  # (ticks: about 0.6 tile into a drift, onto the heap's near slope)
                i2 = pg.evaluate(SETUP, [n, seed, c, r, u, 1, k]); Bm = shot(pg, fx, fy)
                res[(mode, v, lk)] = (A, Bm, i1[3], 'floor %d seed %d' % (n, seed), i2)
                print(mode, v, lk, i1, i2, flush=True)
            errs += [(mode, e) for e in pg.errs[:3]]
            pg.close()
        rows = []
        for v, lk, s in spots:
            cells = []
            for mode in ('classic', 'torch'):
                A, Bm, th, fl, i2 = res[(mode, v, lk)]
                mt = 'Torchlight' if mode == 'torch' else 'Classic'
                c1 = A[0].copy(); label(c1, '%s  %s  %s  %s: standing' % (NAMES[v], th, fl, mt)); cells.append(c1)
                c2 = Bm[0].copy(); label(c2, '%s  %s: walking in, the arrow held (%d px/s)' % (NAMES[v], mt, abs(i2[2]))); cells.append(c2)
            w, h = cells[0].size
            row = Image.new('RGB', (len(cells) * (w + 6), h + 6), INK)
            for i, cc in enumerate(cells): row.paste(cc, (i * (w + 6), 3))
            rows.append(row)
        W = max(r.width for r in rows)
        sheet = Image.new('RGB', (W, sum(r.height for r in rows)), INK); y = 0
        for r in rows: sheet.paste(r, (0, y)); y += r.height
        fn = os.path.join(OUTD, 'r43_hills.png'); sheet.save(fn, optimize=True); print('wrote', fn, sheet.size)
        ph = []
        for v, lk, s in spots:
            for mode in ('torch', 'classic'):
                A, Bm, th, fl, i2 = res[(mode, v, lk)]
                im = Bm[1].copy(); label(im, '%s  %s  %s  phone size' % (NAMES[v], th, 'Torchlight' if mode == 'torch' else 'Classic')); ph.append(im)
        sheet = Image.new('RGB', (2 * 858, ((len(ph) + 1) // 2) * 399), INK)
        for i, im in enumerate(ph): sheet.paste(im, ((i % 2) * 858, (i // 2) * 399))
        fn = os.path.join(OUTD, 'r43_phone.png'); sheet.save(fn, optimize=True); print('wrote', fn, sheet.size)
        if 'nogif' not in a:
            gp = page(b, 'classic', 2)
            frames = []
            for v in ('C2', 'B1'):
                sp = next((s for vv, lk, s in spots if vv == v), None)
                if not sp: continue
                n, seed, c, r, nn, dr, isd = sp
                Ln = nn * 32; fx, fy = c * 32 + Ln / 2, (r + 1) * 64 - 4
                gp.evaluate(SETUP, [n, seed, c, r, 0, 1, 1])
                for i in range(int((Ln + 90) / (42 if isd else 35) * 60 / 3) + 10):
                    q = gp.evaluate(SHOW, [fx, fy, 0])
                    im = Image.open(io.BytesIO(gp.screenshot())).convert('RGB'); d = gp.dsf
                    ox, oy, k = q[0] * d, q[1] * d, q[2] * d; x0, y0 = ox + (fx - BW / 2) * k, oy + (fy - 86) * k
                    frames.append(im.crop((int(x0), int(y0), int(x0 + BW * k), int(y0 + BH * k))).resize((BW * 2, BH * 2), Image.LANCZOS))
                    gp.evaluate("()=>{__HK.tick(3);}")
            gp.close()
            if frames:
                fn = os.path.join(OUTD, 'r43_hills.gif'); frames[0].save(fn, save_all=True, append_images=frames[1:], duration=50, loop=0, optimize=True); print('wrote', fn, len(frames), 'frames')
        if errs: print('errors', errs)
        b.close()
