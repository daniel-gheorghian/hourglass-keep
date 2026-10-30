# egyptr48a.py old.html new.html [outdir]: round 48a's pictures (owner: "The red tiles that slam shut the doors: they shouldn't be red and have
# a different design. They should look the same and have no warning"; chose B, the closing plate drawn as the opening plate).
# On floors FLOORS (seed 1; three themes and hours, night among them) the first in-line gate with its opening plate and a closing plate in front
# of it on the same row, plus a slab closer (four closing plates under a gallery) where found: old | new.
#   r48a_closer_<mode>.png   rows: the cases; each row old | new, the stretch from the opening plate to the gate at 3x
#   r48a_phone.png           the same views whole at phone size (852 x 393), old | new, both modes
# Run from dev/tools (HK_GPU=0: WebGL in SwiftShader).
import io, os, sys
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright
a = sys.argv[1:]
OLD, NEW = os.path.abspath(a[0]), os.path.abspath(a[1])
OUT = os.path.abspath(a[2]) if len(a) > 2 else os.path.dirname(os.path.abspath(__file__))
MODES = ['torch', 'classic']
GPU = [] if os.environ.get('HK_GPU') == '0' else ['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist', '--force_high_performance_gpu']
FLOORS = list(range(4, 64))
DSF, BW, BH = 3, 230, 84

LIST = r'''([n,sd])=>{const H=__HK;window.__HKfreeze=true;const L=H.load(n,sd,false),TW=32,S=r=>(r+1)*64-4,out=[];
  for(const o of L.dyn){if(o.f.t!=='closer')continue;const g=L.dyn.find(q=>q.f===o.f.g);if(!g||g.r!==o.r)continue;
    const pl=L.dyn.find(q=>q.f.t==='plate'&&q.f.g===o.f.g&&q.r===o.r);if(!pl)continue;const c0=Math.min(pl.c,o.c,g.c),c1=Math.max(pl.c,o.c,g.c);if(c1-c0>6)continue;
    out.push([o.f.slabF?'slab':'inline',(c0+c1+1)*TW/2,S(o.r)]);}
  const p=H.progOf(n);return [out,H.themeName(n),p.tod];}'''
SHOW = r'''([n,sd,fx,fy])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS)H.S.hints[id]=1;const L=H.L&&H.L.n===n&&H.L.seed===H.levelSeed(n)?H.L:H.load(n,sd,false);
  H.banner=null;const P=H.P;P.x=-999;P.y=-999;
  H.setClock(()=>1e6);H.setGT(10);H.clearRooms();H.cam.x=fx-H.viewW/2;H.cam.y=fy-192*0.62;H.cam.gy=H.cam.y;if(H.GLP){H.GLP.pipe=false;H.GLP.rs=1;window.__HKnoauto=true;}for(let i=0;i<4;i++)H.render();
  const X=H.XF,cv=[...document.querySelectorAll('canvas')].find(c=>c.getBoundingClientRect().width>0),R=cv.getBoundingClientRect(),k=X.VZ/cv.width*R.width;
  return [R.left-X.camD/cv.width*R.width,R.top-X.camDY/cv.height*R.height,k];}'''


def label(im, t):
    d = ImageDraw.Draw(im); d.rectangle((0, 0, 6 + 6 * len(t), 12), fill=(0, 0, 0)); d.text((3, 0), t, fill=(250, 240, 215))


def shoot(pg, n, sd, fx, fy, whole=False):
    q = pg.evaluate(SHOW, [n, sd, fx, fy]); im = Image.open(io.BytesIO(pg.screenshot())).convert('RGB')
    if whole: return im.resize((852, 393), Image.LANCZOS)
    k = q[2] * DSF; x0, y0 = q[0] * DSF + (fx - BW / 2) * k, q[1] * DSF + (fy - BH + 20) * k
    return im.crop((int(x0), int(y0), int(x0 + BW * k), int(y0 + BH * k))).resize((BW * 3, BH * 3), Image.LANCZOS)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True); errs = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=GPU); pages = {}
        for src in (OLD, NEW):
            for mode in MODES:
                pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=DSF); pg.on('pageerror', lambda e: errs.append(str(e)))
                pg.goto('file://' + src); pg.wait_for_timeout(800)
                pg.evaluate("()=>{document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.body.classList.remove('panelOpen');const st=document.createElement('style');st.textContent='.ctl,#pause,#pauseBtn,#pad{display:none!important}';document.head.appendChild(st);}")
                pg.evaluate("m=>{__HK.S.set.lightMode=m;__HK.GLFX.sheen=false;}", mode); pages[(src, mode)] = pg
        cases, tods, themes, slab = [], set(), set(), None
        for n in FLOORS:
            out, th, tod = pages[(NEW, 'torch')].evaluate(LIST, [n, 1])
            for k, x, y in out:
                if k == 'slab' and slab is None: slab = (n, x, y, th, k)
                if k == 'inline' and tod not in tods and th.split(' by ')[0] not in themes and len(cases) < 3:
                    cases.append((n, x, y, th, k)); tods.add(tod); themes.add(th.split(' by ')[0])
        if slab: cases.append(slab)
        print('cases', cases, flush=True)
        cw, ch = BW * 3, BH * 3
        for mode in MODES:
            sh = Image.new('RGB', (2 * cw + 10, len(cases) * (ch + 4)), (20, 16, 24))
            for i, (n, x, y, th, k) in enumerate(cases):
                for s, src in enumerate((OLD, NEW)):
                    im = shoot(pages[(src, mode)], n, 1, x, y); label(im, '%s %s fl%d %s %s' % ('v89' if src == OLD else '48a', k, n, th, mode)); sh.paste(im, (s * (cw + 10), i * (ch + 4)))
            sh.save(os.path.join(OUT, 'r48a_closer_%s.png' % mode)); print('wrote', mode, flush=True)
        ph = Image.new('RGB', (2 * 858, len(cases) * len(MODES) * 399), (20, 16, 24)); row = 0
        for (n, x, y, th, k) in cases:
            for mode in MODES:
                for s, src in enumerate((OLD, NEW)):
                    im = shoot(pages[(src, mode)], n, 1, x, y, True); label(im, '%s fl%d %s %s' % ('v89' if src == OLD else '48a', n, th, mode)); ph.paste(im, (s * 858, row * 399))
                row += 1
        ph.save(os.path.join(OUT, 'r48a_phone.png')); print('wrote phone')
        if errs: print('errors', errs[:3])
        b.close()
