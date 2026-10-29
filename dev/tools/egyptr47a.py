# egyptr47a.py old.html new.html [outdir] [nogif] [classic]: round 47a's pictures: the checked leap and PoP's test foot at a heap and a drift
# (owner: "you shouldn't be able to jump over them, only way is to walk at the pace they let you"; at the foot "PoP's stop with the test foot").
# Each case is played with the game's own input (the arrow held, Jump pressed d px before the hill's foot) in both builds:
#   heap_leap   running, Jump 40 px before a heap: v88 clears it; 47a's leap is cut to land short of its foot, then the test foot
#   heap_brake  running, Jump 12 px before it: no room for a leap: the braking stop (runstop) and the test foot
#   heap_stand  standing 20 px before it, Jump: the careful step up to it and the test foot
#   drift_leap  running, Jump 36 px before a drift: v88 lands in it; 47a lands short and tests the sand
#   drift_brake running, Jump 12 px before a drift
# r47a_<case>_<mode>.png: frames every 0.083 s from the press, old over new, 3x crops (3 screen px a world px), Classic and Torchlight;
# r47a_<case>_phone.png: phone size (852 x 393), new, both modes, at the toe's contact; r47a_<case>.gif: new, Classic, 2x, real time.
# Run from dev/tools (HK_GPU=1: Torchlight on the GPU).
import io, os, sys
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
HT = [os.path.abspath(x) for x in a if x.endswith('.html')]
OLD, NEW = (HT + [None, None])[:2] if len(HT) >= 2 else (None, HT[0] if HT else os.path.join(HERE, '..', 'hourglass-keep.html'))
OUTD = next((x for x in a if not x.endswith('.html') and x not in ('nogif', 'classic')), os.path.join(HERE, 'egypt_themes'))
MODES = ['classic'] if 'classic' in a else ['classic', 'torch']
INK = (20, 16, 24)
BW, BH, ZK = 230, 100, 3
GPU = ['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist', '--force_high_performance_gpu'] if os.environ.get('HK_GPU') else []
FIND = r'''([v,need])=>{const H=__HK;for(let n=3;n<=48;n++)for(const s of [1,2]){const L=H.genLevel(n,s,true);for(const h of L.hills||[]){if(v==='C2'?h.v!=='C2':h.v==='C2')continue;if(v!=='C2'&&v!=='any'&&h.v!==v)continue;
  const C=L.cols,ok=c=>L.base[h.r*C+c]===1&&!L.feat[h.r*C+c]&&L.base[(h.r-1)*C+c]===0;let k=0,c=h.dir>0?h.c-1:h.c+h.n;while(k<5&&ok(c)){k++;c-=h.dir;}if(k>=need)return [n,s,h.c,h.r,h.n,h.dir,h.v];}}return null;}'''
# the prince d px before the hill's foot: running in from 70 px further back with the arrow held (run) or standing (stand); Jump pressed there
SETUP = r'''([n,sd,c,r,nn,dir,d,run])=>{const H=__HK;for(const id in H.HINTS){H.S.hints[id]=1;H.S.learned[id]=1;}const L=H.load(n,sd,true);H.banner=null;const P=H.P;P.inv=1e9;for(const e of H.G)e.x=-9999;
  const xa=dir>0?c*32:(c+nn)*32;let q=12345;Math.random=()=>{q=(q*16807)%2147483647;return q/2147483647;};for(const k of ['l','r','u','d','j','g'])H.setKey('kb',k,false);
  P.x=xa-dir*(d+(run?70:0));P.y=(r+1)*64-4;P.fallY=P.y;P.vx=0;P.face=dir;P.state='stand';H.mode='play';H.tick(20);
  H.setKey('kb',dir>0?'r':'l',true);if(run)for(let i=0;i<300&&(P.x-(xa-dir*d))*dir<0;i++)H.tick(1);
  H.setKey('kb','j',true);H.tick(1);H.setKey('kb','j',false);return [P.x,P.state];}'''
SHOW = r'''([fx,fy])=>{const H=__HK;H.banner=null;let T=1e6+H.gameTime*1000;H.setClock(()=>T);
  H.cam.x=fx-H.viewW/2;H.cam.y=fy-192*0.62;H.cam.gy=fy;if(H.GLP){H.GLP.pipe=false;H.GLP.rs=1;window.__HKnoauto=true;}
  window.__HKfreeze=true;for(let i=0;i<3;i++)H.render();const X=H.XF,cv=[...document.querySelectorAll('canvas')].find(c=>c.getBoundingClientRect().width>0),R=cv.getBoundingClientRect(),k=X.VZ/cv.width*R.width;
  return [R.left-X.camD/cv.width*R.width,R.top-X.camDY/cv.height*R.height,k,H.P.x,H.P.state];}'''
CASES = [('heap_leap', 'heap', 40, 1, 'running, Jump 40 px before a heap'), ('heap_brake', 'heap', 12, 1, 'running, Jump 12 px before a heap'),
         ('heap_stand', 'heap', 20, 0, 'standing 20 px before a heap, Jump'), ('drift_leap', 'C2', 36, 1, 'running, Jump 36 px before a drift'),
         ('drift_brake', 'C2', 12, 1, 'running, Jump 12 px before a drift')]
STEPS = 5  # ticks between frames (0.083 s)


def page(b, mode, html, dsf=3):
    pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=dsf)
    pg.errs = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e)))
    pg.goto('file://' + html)
    pg.wait_for_timeout(800)
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.body.classList.remove('panelOpen')")
    pg.evaluate("m=>{__HK.S.set.lightMode=m;}", mode)
    pg.dsf = dsf
    return pg


def shot(pg, fx, fy, zk=ZK):
    q = pg.evaluate(SHOW, [fx, fy])
    im = Image.open(io.BytesIO(pg.screenshot())).convert('RGB')
    d = pg.dsf
    ox, oy, k = q[0] * d, q[1] * d, q[2] * d
    x0, y0 = ox + (fx - BW / 2) * k, oy + (fy - 78) * k
    return im.crop((int(x0), int(y0), int(x0 + BW * k), int(y0 + BH * k))).resize((BW * zk, BH * zk), Image.LANCZOS), im.resize((852, 393), Image.LANCZOS), q


def label(im, t):
    dr = ImageDraw.Draw(im)
    dr.rectangle((0, 0, 8 + 6 * len(t), 13), fill=(0, 0, 0))
    dr.text((4, 1), t, fill=(250, 240, 215))


def play(b, mode, html, spot, d, run, nf, dsf=3, every=1):
    n, sd, c, r, nn, dr, v = spot
    pg = page(b, mode, html, dsf)
    pg.evaluate(SETUP, [n, sd, c, r, nn, dr, d, run])
    xa = c * 32 if dr > 0 else (c + nn) * 32
    fx, fy = xa - dr * 20, (r + 1) * 64 - 4
    out = []
    for i in range(nf):
        if i % every == 0: out.append(shot(pg, fx, fy))
        pg.evaluate("k=>{__HK.tick(k);}", STEPS)
    errs = pg.errs
    pg.close()
    return out, errs


if __name__ == '__main__':
    os.makedirs(OUTD, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(args=GPU)
        f0 = page(b, 'classic', NEW, 1)
        spots = {'heap': f0.evaluate(FIND, ['B1', 4]), 'C2': f0.evaluate(FIND, ['C2', 4])}
        f0.close()
        print('spots', spots)
        errs = []
        for tag, kind, d, run, title in CASES:
            spot = spots[kind]
            for mode in MODES:
                rows = []
                for nm, html in (('v88', OLD), ('47a', NEW)):
                    if not html: continue
                    fr, e = play(b, mode, html, spot, d, run, 16)
                    errs += e
                    rows.append((nm, fr))
                cols = 8
                sheet = Image.new('RGB', (cols * (BW * ZK + 2) + 4, len(rows) * (BH * ZK + 2) + 28), INK)
                for ri, (nm, fr) in enumerate(rows):
                    for ci in range(cols):
                        cr, ph, q = fr[ci * 2]
                        cr = cr.copy(); label(cr, '%s  t+%.2fs  %s' % (nm, ci * 2 * STEPS / 60, q[4])); sheet.paste(cr, (2 + ci * (BW * ZK + 2), 26 + ri * (BH * ZK + 2)))
                label(sheet, '%s  floor %d seed %d, %s %d tiles, %s, 3x, every %.2f s from the press: v88 (top) | round 47a' % (title, spot[0], spot[1], spot[6], spot[4], 'Torchlight' if mode == 'torch' else 'Classic', 2 * STEPS / 60))
                fn = os.path.join(OUTD, 'r47a_%s_%s.png' % (tag, mode)); sheet.save(fn, optimize=True); print('wrote', fn)
            # phone size, new, both modes: the toe on the hill (about 0.75 s after the press for a leap, 0.45 s for a brake)
            ph = []
            for mode in MODES:
                fr, e = play(b, mode, NEW, spot, d, run, 12 if 'leap' in tag else 8, dsf=2)
                errs += e
                im = fr[-1][1].copy(); label(im, '47a  %s  %s  phone size' % (title, 'Torchlight' if mode == 'torch' else 'Classic')); ph.append(im)
            sheet = Image.new('RGB', (858 * len(ph), 399), INK)
            for i, im in enumerate(ph): sheet.paste(im, (i * 858, 0))
            fn = os.path.join(OUTD, 'r47a_%s_phone.png' % tag); sheet.save(fn, optimize=True); print('wrote', fn)
            if 'nogif' not in a:
                n, sd, c, r, nn, dr, v = spot
                pg = page(b, 'classic', NEW, 2); pg.evaluate(SETUP, [n, sd, c, r, nn, dr, d, run])
                xa = c * 32 if dr > 0 else (c + nn) * 32; fx, fy = xa - dr * 20, (r + 1) * 64 - 4; gf = []
                for i in range(int(2.4 * 60 / 3)):
                    cr, _, q = shot(pg, fx, fy, 2); gf.append(cr); pg.evaluate("()=>{__HK.tick(3);}")
                errs += pg.errs; pg.close()
                fn = os.path.join(OUTD, 'r47a_%s.gif' % tag); gf[0].save(fn, save_all=True, append_images=gf[1:], duration=50, loop=0, optimize=True); print('wrote', fn)
        b.close()
    print('errors', errs[:5])
