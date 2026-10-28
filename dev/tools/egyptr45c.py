# egyptr45c.py [new.html] [old=FILE] [outdir] [nogif]: round 45c's pictures.
# r45c_jambs.png: each theme's threshold (the near jamb on the front plane he passes behind): its court's left and right ends (the two forms by hash),
#   him half behind the jamb, Classic and Torchlight, by day and by night where the theme has both, 3x; worn and broken jambs (beside worn walls and
#   breaches) in their own rows. r45c_jambs_phone.png: the same scenes at the phone's size (852 x 393), Torchlight by night or Classic by day.
# r45c_meroe.png: a Meroe court by day and by night, before (old=FILE) | after (its own sky and pyramids, its own grade), Classic and Torchlight,
#   phone size. r45c_aksum.png: an Aksum court before | after (S1: depth in layers), Classic and Torchlight, 3x.
# r45c_gust.gif: a gust coming in through a court's open side (Torchlight, 2x).
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
GPU = ['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist', '--force_high_performance_gpu'] if os.environ.get('HK_GPU') else []
# (label, look, hour, worn: 0 any, 1 a worn jamb, 2 a broken one)
JAMBS = [('colonnade (papyrus anta)', 'west', 'day', 0), ('colonnade (papyrus anta)', 'osiris', 'night', 0), ('Kushite pylon edge', 'meroe', 'day', 0), ('Kushite pylon edge', 'napata', 'day', 0),
         ('mudbrick (Shali)', 'shali', 'day', 0), ('mudbrick (Kerma)', 'deffufa', 'night', 0), ('mudbrick (Garama)', 'foggara', 'night', 0), ('Aksum monkey-head frame', 'aksum', '', 0),
         ('rock-cut jamb', 'wells', '', 0), ('Nun light well', 'nun', '', 0), ('worn: chips and cracks', '', '', 1), ('broken beside a breach', '', '', 2)]
FIND = r'''([look,hr,worn,skip])=>{const H=__HK;let i=0;for(let n=3;n<=60;n++){for(let s=1;s<=6;s++){const L=H.genLevel(n,s,true),tod=L.prog.tod;
  if(look&&L.theme.look!==look)break;if(hr==='day'&&tod===1||hr==='night'&&tod!==1)break;
  for(const q of L.courts){if(q.pits.length||L.guards.some(g=>g.r===q.r&&g.hi/32>q.c0-6&&g.lo/32<q.c1+6))continue;
    if(q.k!=='well'&&(L.base[q.r*L.cols+q.c0-1]!==1||L.base[(q.r-1)*L.cols+q.c0-1]!==0))continue;
    const jj=H.ctJambsOf(q);if(worn===1&&!(jj[0].wear>=2&&!jj[0].cut))continue;if(worn===2&&!jj[0].cut)continue;if(i++<skip)continue;
    return [n,s,q.k,q.r,q.c0,q.c1,H.themeName(n),tod];}}}return null;}'''
SETUP = r'''([n,seed,r,px,face])=>{const H=__HK;for(const id in H.HINTS){H.S.hints[id]=1;H.S.learned[id]=1;}H.S.windDeaths={};const L=H.load(n,seed,true);H.banner=null;
  const P=H.P;P.inv=1e9;for(const e of H.G)e.x=-9999;for(const s of H.SN)s.x=-9999;P.x=px;P.y=(r+1)*64-4;P.fallY=P.y;P.vx=0;P.face=face;P.state='stand';H.mode='play';
  let q=12345;Math.random=()=>{q=(q*16807)%2147483647;return q/2147483647;};for(const kk of ['l','r','u','d','j','g'])H.setKey('kb',kk,false);H.tick(20);P.x=px;return [P.x,P.state];}'''
SHOW = r'''([fx,fy])=>{const H=__HK;H.banner=null;let T=1e6+H.gameTime*1000;H.setClock(()=>T);
  H.cam.x=fx-H.viewW/2;H.cam.y=fy-160;H.cam.gy=fy;if(H.GLP){H.GLP.pipe=false;H.GLP.rs=1;window.__HKnoauto=true;}
  window.__HKfreeze=true;document.body.classList.add('panelOpen');const pd=document.getElementById('pad');if(pd)pd.style.display='none';
  for(let i=0;i<3;i++)H.render();const X=H.XF,cv=[...document.querySelectorAll('canvas')].find(c=>c.getBoundingClientRect().width>0),R=cv.getBoundingClientRect(),k=X.VZ/cv.width*R.width;
  return [R.left-X.camD/cv.width*R.width,R.top-X.camDY/cv.height*R.height,k];}'''


def page(b, html, mode, dsf=3):
    pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=dsf); pg.errs = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e))); pg.goto('file://' + html); pg.wait_for_timeout(800)
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.body.classList.remove('panelOpen')")
    pg.evaluate("m=>{__HK.S.set.lightMode=m;}", mode); return pg


def shot(pg, fx, fy, bw, bh=182, up=160, dsf=3, zk=3):
    q = pg.evaluate(SHOW, [fx, fy]); im = Image.open(io.BytesIO(pg.screenshot())).convert('RGB')
    ox, oy, k = q[0] * dsf, q[1] * dsf, q[2] * dsf; x0, y0 = ox + (fx - bw / 2) * k, oy + (fy - up) * k
    return im.crop((int(x0), int(y0), int(x0 + bw * k), int(y0 + bh * k))).resize((int(bw * zk), int(bh * zk)), Image.LANCZOS), im.resize((852, 393), Image.LANCZOS)


def label(im, t):
    d = ImageDraw.Draw(im); d.rectangle((0, 0, 8 + 6 * len(t), 13), fill=(0, 0, 0)); d.text((4, 1), t, fill=(250, 240, 215))


def grid(cells, cols, fn):
    w, h = cells[0].size; S = Image.new('RGB', (cols * (w + 6), ((len(cells) + cols - 1) // cols) * (h + 6)), INK)
    for i, c in enumerate(cells): S.paste(c, ((i % cols) * (w + 6), (i // cols) * (h + 6)))
    S.save(fn, optimize=True); print('wrote', fn, S.size)


MT = {'classic': 'Classic', 'torch': 'Torchlight'}
if __name__ == '__main__':
    os.makedirs(OUTD, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(args=GPU)
        pg = page(b, NEW, 'classic'); found = [(w, pg.evaluate(FIND, [w[1], w[2], w[3], 0])) for w in JAMBS]; pg.close()
        cells, phones = [], []
        for w, f in found:
            if not f: print('none for', w); continue
            n, s, k, r, c0, c1, th, tod = f; fy = (r + 1) * 64 - 4; hr = 'night' if tod == 1 else 'dawn' if tod == 2 else 'dusk'
            for end, fx, px, face in (('left end', c0 * 32 + 10, c0 * 32 - 11, 1), ('right end', (c1 + 1) * 32 - 18, (c1 + 1) * 32 - 5, -1)):
                for mode in ('classic', 'torch'):
                    pg = page(b, NEW, mode); pg.evaluate(SETUP, [n, s, r, px, face]); cr, ph = shot(pg, fx, fy, 160)
                    label(cr, '%s %s | %s %s fl %d | %s' % (w[0], end, th, hr, n, MT[mode])); cells.append(cr)
                    if end == 'left end' and mode == ('torch' if tod == 1 else 'classic'): label(ph, '%s | %s %s | %s' % (w[0], th, hr, MT[mode])); phones.append(ph)
                    if pg.errs: print('ERR', pg.errs[:2])
                    pg.close()
        grid(cells, 4, os.path.join(OUTD, 'r45c_jambs.png')); grid(phones, 2, os.path.join(OUTD, 'r45c_jambs_phone.png'))
        # Meroe's courts and Aksum's
        for nm, look, hrs, phone in (('meroe', 'meroe', ('day', 'night'), True), ('aksum', 'aksum', ('',), False)):
            cells = []
            for hr in hrs:
                pg = page(b, NEW, 'classic'); f = pg.evaluate(FIND, [look, hr, 0, 0]); pg.close()
                if not f: continue
                n, s, k, r, c0, c1, th, tod = f; fy = (r + 1) * 64 - 4; fx = (c0 + c1 + 1) / 2 * 32
                for mode in ('classic', 'torch'):
                    for tag, html in (('before', OLD), ('after', NEW)):
                        if not html: continue
                        pg = page(b, html, mode); pg.evaluate(SETUP, [n, s, r, c0 * 32 + 40, 1]); cr, ph = shot(pg, fx, fy, 330)
                        im = ph if phone else cr; label(im, '%s court %s | %s fl %d | %s | %s' % (th, hr, MT[mode], n, tag, 'own sky and grade' if nm == 'meroe' else 'S1 layered')); cells.append(im); pg.close()
            grid(cells, 4 if OLD else 2, os.path.join(OUTD, 'r45c_%s.png' % nm))
        if 'nogif' not in a:
            pg = page(b, NEW, 'torch', 2)
            f = pg.evaluate(r'''()=>{const H=__HK;for(let n=13;n<=48;n++)for(let s=1;s<=3;s++){const L=H.genLevel(n,s,true);const z=L.winds.find(z=>z.k==='g'&&z.o==='court');if(z)return [n,s,z.r,z.c,z.n];}return null;}''')
            if f:
                n, s, r, c, nn = f; fy = (r + 1) * 64 - 4; fx = (c + nn / 2) * 32; pg.evaluate(SETUP, [n, s, r, fx, 1]); frames = []
                for i in range(110):
                    cr, _ = shot(pg, fx, fy, 300, dsf=2, zk=2); frames.append(cr.resize((int(cr.width * 0.7), int(cr.height * 0.7)), Image.LANCZOS).quantize(colors=128, method=Image.MEDIANCUT)); pg.evaluate("t=>__HK.tick(t)", 3)
                frames[0].save(os.path.join(OUTD, 'r45c_gust.gif'), save_all=True, append_images=frames[1:], duration=50, loop=0, optimize=True); print('wrote r45c_gust.gif', f)
            pg.close()
        b.close()
