# egyptr45.py [new.html] [old=FILE] [outdir] [nogif]: round 45's pictures: the courts (L.courts, placeCourts).
# r45_courts.png: one row per kind, hour and far side (a peristyle by day and by night, a vine pergola by day and by night, a pylon court in
#   Napata, a rubble-and-stelae court in Aksum, a light well, a pool court): him standing in it, Classic and Torchlight, before (old=FILE: the
#   same floor, seed and camera in the old build) | after, 3x (3 screen px a world px).
# r45_phone.png: the same scenes as the whole screen at the phone's size (852 x 393 css px), after, both modes.
# r45_pool.png: a fall into a court's pool, both modes: the splash at the surface, then under.
# r45_gust.gif: a gust coming in through a court's open side (Torchlight, 2x, real time); r45_vine.gif: a pergola's vine and dapple.
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
BW, BH, UP, ZK = 330, 182, 160, 3
GPU = ['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist', '--force_high_performance_gpu'] if os.environ.get('HK_GPU') else []
# (label, kind, far side or '', look or '', hour: 'day' (dusk or dawn) / 'night' / '', a pool, a gust through it)
WANT = [('peristyle, day', 'peri', '', '', 'day', 0, 0), ('peristyle, night', 'peri', '', '', 'night', 0, 0),
        ('vine pergola, day', 'perg', '', '', 'day', 0, 0), ('vine pergola, night', 'perg', '', '', 'night', 0, 0),
        ('pylon court (Kush)', 'fore', 'kush', '', 'day', 0, 0), ('stelae court (Aksum)', 'fore', 'granite', '', '', 0, 0),
        ('rock-cut court (Well Corridors)', 'fore', 'rock', '', '', 0, 0), ('light well', 'well', '', '', '', 0, 0),
        ('pool court', '', '', '', 'day', 1, 0), ('pool court by moonlight', '', '', '', 'night', 1, 0)]
FIND = r'''([k,far,look,hr,pool,gust,skip])=>{const H=__HK;let i=0;for(let n=3;n<=60;n++){for(let s=1;s<=6;s++){const L=H.genLevel(n,s,true),tod=L.prog.tod;
  if(look&&L.theme.look!==look)break;if(hr==='day'&&tod===1||hr==='night'&&tod!==1)break;
  for(const q of L.courts){if(k&&q.k!==k||far&&q.far!==far||pool&&!q.pits.length||!pool&&q.k!=='well'&&q.c1-q.c0<4)continue;
    if(gust&&!(L.winds||[]).some(z=>z.k==='g'&&z.src&&L._ctS.has(Math.floor(z.src.y/64)*L.cols+Math.floor(z.src.x/32))&&z.r===q.r))continue;
    if(L.guards.some(g=>g.r===q.r&&g.hi/32>q.c0-4&&g.lo/32<q.c1+4))continue;if(i++<skip)continue;
    return [n,s,q.k,q.r,q.c0,q.c1,q.pits.length?q.pits[0]:null,H.themeName(n),tod];}}}return null;}'''
SETUP = r'''([n,seed,r,px,face])=>{const H=__HK;for(const id in H.HINTS){H.S.hints[id]=1;H.S.learned[id]=1;}const L=H.load(n,seed,true);H.banner=null;
  const P=H.P;P.inv=1e9;for(const e of H.G)e.x=-9999;for(const s of H.SN)s.x=-9999;P.x=px;P.y=(r+1)*64-4;P.fallY=P.y;P.vx=0;P.face=face;P.state='stand';H.mode='play';
  let q=12345;Math.random=()=>{q=(q*16807)%2147483647;return q/2147483647;};for(const kk of ['l','r','u','d','j','g'])H.setKey('kb',kk,false);H.tick(30);return [P.x,P.state];}'''
SHOW = r'''([fx,fy])=>{const H=__HK;H.banner=null;let T=1e6+H.gameTime*1000;H.setClock(()=>T);
  H.cam.x=fx-H.viewW/2;H.cam.y=fy-160;H.cam.gy=fy;if(H.GLP){H.GLP.pipe=false;H.GLP.rs=1;window.__HKnoauto=true;}
  window.__HKfreeze=true;document.body.classList.add('panelOpen');const pd=document.getElementById('pad');if(pd)pd.style.display='none';
  for(let i=0;i<3;i++)H.render();const X=H.XF,cv=[...document.querySelectorAll('canvas')].find(c=>c.getBoundingClientRect().width>0),R=cv.getBoundingClientRect(),k=X.VZ/cv.width*R.width;
  return [R.left-X.camD/cv.width*R.width,R.top-X.camDY/cv.height*R.height,k];}'''
DROWN = r'''([wx,pc])=>{const H=__HK,P=H.P;P.inv=0;H.setKey('kb',P.face>0?'r':'l',true);let i=0;while(i++<240&&H.mode!=='dead')H.tick(1);H.setKey('kb','r',false);H.setKey('kb','l',false);return [H.mode,P.cause,P.y,i];}'''


def page(b, html, mode, dsf=3):
    pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=dsf); pg.errs = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e))); pg.goto('file://' + html); pg.wait_for_timeout(800)
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.body.classList.remove('panelOpen')")
    pg.evaluate("m=>{__HK.S.set.lightMode=m;}", mode); return pg


def shot(pg, fx, fy, zk=ZK, dsf=3):
    q = pg.evaluate(SHOW, [fx, fy]); im = Image.open(io.BytesIO(pg.screenshot())).convert('RGB')
    ox, oy, k = q[0] * dsf, q[1] * dsf, q[2] * dsf; x0, y0 = ox + (fx - BW / 2) * k, oy + (fy - UP) * k
    return im.crop((int(x0), int(y0), int(x0 + BW * k), int(y0 + BH * k))).resize((BW * zk, BH * zk), Image.LANCZOS), im.resize((852, 393), Image.LANCZOS)


def label(im, t):
    d = ImageDraw.Draw(im); d.rectangle((0, 0, 8 + 6 * len(t), 13), fill=(0, 0, 0)); d.text((4, 1), t, fill=(250, 240, 215))


def grid(cells, cols, fn):
    w, h = cells[0].size; S = Image.new('RGB', (cols * (w + 6), ((len(cells) + cols - 1) // cols) * (h + 6)), INK)
    for i, c in enumerate(cells): S.paste(c, ((i % cols) * (w + 6), (i // cols) * (h + 6)))
    S.save(fn, optimize=True); print('wrote', fn, S.size)


def scene(f):
    n, s, k, r, c0, c1, pit, th, tod = f
    if pit: px = (pit[0] - 1.6) * 32; fx = (pit[0] + 0.5) * 32
    else: px = (c0 + 1.6) * 32; fx = (c0 + c1 + 1) / 2 * 32
    return n, s, r, px, fx, (r + 1) * 64 - 4


if __name__ == '__main__':
    os.makedirs(OUTD, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(args=GPU)
        pg = page(b, NEW, 'classic'); found = [(w, pg.evaluate(FIND, list(w[1:]) + [0])) for w in WANT]; pg.close()
        rows, phones = [], []
        for w, f in found:
            if not f: print('none for', w[0]); continue
            n, s, r, px, fx, fy = scene(f); print(w[0], f)
            for mode in ('classic', 'torch'):
                for nm, html in (('before', OLD), ('after', NEW)):
                    if not html: continue
                    pg = page(b, html, mode); pg.evaluate(SETUP, [n, s, r, px, 1]); cr, ph = shot(pg, fx, fy)
                    label(cr, '%s  %s  floor %d seed %d  %s  %s' % (w[0], f[7], n, s, 'Torchlight' if mode == 'torch' else 'Classic', nm)); rows.append(cr)
                    if nm == 'after': label(ph, '%s  %s  %s' % (w[0], f[7], 'Torchlight' if mode == 'torch' else 'Classic')); phones.append(ph)
                    if pg.errs: print('ERR', pg.errs[:2])
                    pg.close()
        grid(rows, 4 if OLD else 2, os.path.join(OUTD, 'r45_courts.png'))
        grid(phones, 2, os.path.join(OUTD, 'r45_phone.png'))
        cells = []
        for w, f in found:
            if not f or not w[5]: continue
            n, s, r, px, fx, fy = scene(f)
            for mode in ('classic', 'torch'):
                pg = page(b, NEW, mode); pg.evaluate(SETUP, [n, s, r, px, 1]); st = pg.evaluate(DROWN, [0, 0])
                for dt, lab in ((0, 'the splash at the surface'), (40, 'under, 0.7 s on')):
                    if dt: pg.evaluate("t=>__HK.tick(t)", dt)
                    cr, _ = shot(pg, fx, fy); label(cr, '%s  %s: %s (%s)' % (w[0], 'Torchlight' if mode == 'torch' else 'Classic', lab, st[1])); cells.append(cr)
                pg.close()
        grid(cells, 4, os.path.join(OUTD, 'r45_pool.png'))
        if 'nogif' not in a:
            for nm, w in (('r45_gust.gif', ('gust', 'peri', '', '', '', 0, 1)), ('r45_vine.gif', ('vine', 'perg', '', '', 'day', 0, 0))):
                pg = page(b, NEW, 'torch', 2); f = pg.evaluate(FIND, list(w[1:]) + [0])
                if not f: f = pg.evaluate(FIND, ['', '', '', '', 0, 1, 0]) if nm == 'r45_gust.gif' else None
                if not f: print('no scene for', nm); pg.close(); continue
                n, s, r, px, fx, fy = scene(f); pg.evaluate(SETUP, [n, s, r, px, 1]); frames = []
                for i in range(90):
                    cr, _ = shot(pg, fx, fy, zk=2, dsf=2); frames.append(cr.resize((int(cr.width * 0.7), int(cr.height * 0.7)), Image.LANCZOS).quantize(colors=128, method=Image.MEDIANCUT)); pg.evaluate("t=>__HK.tick(t)", 3)
                frames[0].save(os.path.join(OUTD, nm), save_all=True, append_images=frames[1:], duration=50, loop=0, optimize=True); print('wrote', nm, f); pg.close()
        b.close()
