# egyptr46d.py old.html new.html [outdir] [torch|classic]: round 46d's pictures (the owner's contour rule on the figures: "as a rule, if you add
# contours or accents always use a darker shade of the pixels that are closer to the edge or lighter if light hits it - with some tinting of
# course"; "apply it everywhere"). On three floors (themes and hours: FLOORS), each figure stands on a stretch of plain floor away from the
# lamps (a dark wall behind him, the hard case for reading him at phone size) and, in a second set, beside a lamp:
#   r46d_figs_<mode>.png    rows: floor x {dark, lamp} x {old, new}; columns: the prince standing, running, hanging, crawling, on guard with the
#                           blade; the recruit, the soldier, the veteran, the captain (each on guard), the skeleton, a snake; 3x crops
#   r46d_lowdetail.png      the same columns with Graphics > Detail off (drawFigure, drawSnake), Classic, old | new
#   r46d_phone_<n>.png      whole views at phone size (852 x 393): the prince, a captain and a snake on the dark stretch, old over new, both modes
# Run from dev/tools (HK_GPU=0: WebGL in SwiftShader).
import io, os, sys
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright
a = sys.argv[1:]
OLD, NEW = os.path.abspath(a[0]), os.path.abspath(a[1])
OUT = os.path.abspath(a[2]) if len(a) > 2 and a[2] not in ('torch', 'classic') else os.path.dirname(os.path.abspath(__file__))
MODES = [m for m in ('torch', 'classic') if m in a] or ['torch', 'classic']
GPU = [] if os.environ.get('HK_GPU') == '0' else ['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist', '--force_high_performance_gpu']
FLOORS = [10, 22, 34]
FIGS = ['stand', 'run', 'hang', 'crawl', 'fight', 'recruit', 'soldier', 'veteran', 'captain', 'skeleton', 'snake']
DSF, BW, BH = 3, 56, 70

# a stretch of nine plain floor cells (no feature) on one row, kind 'dark': no lamp within six cells of it; 'lamp': a lamp at its middle
FIND = r'''([n,kind])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS)H.S.hints[id]=1;
  for(let sd=1;sd<60;sd++){const L=H.load(n,sd,false);H.banner=null;const C=L.cols,B=(c,r)=>L.base[r*C+c],F=(c,r)=>L.feat[r*C+c];
    for(let r=1;r<L.rows-1;r++)for(let c=8;c<C-8;c++){let ok=true;for(let d=-4;d<=4&&ok;d++)ok=B(c+d,r)===1&&!F(c+d,r);if(!ok)continue;
      const near=L.torches.filter(t=>!t.broken&&t.r===r&&Math.abs(t.c-c)<=6);
      if(kind==='dark'?near.length:!near.some(t=>t.c===c))continue;
      if(!H.G.length&&!H.SN.length)continue;return [sd,c*32+16+(kind==='lamp'?40:0),(r+1)*64-4,H.themeName(n)];}}
  return null;}'''
# one figure at (x, y) (the others out of view), a frozen clock and random numbers; returns where the canvas is on the page and its scale
SHOW = r'''([n,sd,x,y,fig,many])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS)H.S.hints[id]=1;
  const L=H.L&&H.L.n===n&&H.L.seed===H.levelSeed(n)&&H.L._r46d===sd?H.L:H.load(n,sd,false);L._r46d=sd;H.banner=null;
  let T=1e6;H.setClock(()=>T);let a=12345;Math.random=()=>{a=(a*16807)%2147483647;return a/2147483647;};
  const P=H.P,PS=H.PS;P.inv=1e9;P.x=-999;P.y=-999;P.sword=false;P.foe=null;P.hideMode=0;P.chm=null;P.rdx=0;P.rdy=0;P.yo=0;P.flash=0;
  for(const e of H.G){e.x=-9999;e.flash=0;}for(const s of H.SN)s.x=-9999;
  const g=H.G.find(e=>e.alive&&!e.gone)||H.G[0],sn=H.SN[0];
  const prince=(pose,st)=>{P.x=x;P.y=y;P.fallY=y;P.vx=P.vy=0;P.state=st||'stand';P.face=1;P.dF=0;P.pose=H.mk(pose);};
  const guard=(tier,cap,skel,gx)=>{if(!g)return;g.x=gx;g.y=y;g.face=-1;g.alive=true;g.gone=false;g.state='fight';g.tier=tier;g.cap=cap;g.skel=skel;g.t=0;g.pose=H.mk(PS.garde);g.rdx=0;};
  const snake=sx=>{if(!sn)return;sn.x=sx;sn.y=y;sn.dir=-1;sn.alive=true;sn.state='coil';sn.t=0.3;sn.ph=0.2;};
  if(many){prince(PS.stand);guard(3,true,false,x+70);snake(x+150);}
  else if(fig==='stand')prince(PS.stand);else if(fig==='run')prince(H.RP(0.25),'run');else if(fig==='hang')prince(PS.hang);
  else if(fig==='crawl')prince(H.crawlPose(0.3),'crawl');
  else if(fig==='fight'){prince(PS.garde,'fight');P.sword=true;P.foe=g||null;}
  else if(fig==='recruit')guard(0,false,false,x);else if(fig==='soldier')guard(1,false,false,x);else if(fig==='veteran')guard(2,false,false,x);
  else if(fig==='captain')guard(2,true,false,x);else if(fig==='skeleton')guard(1,false,true,x);else if(fig==='snake')snake(x);
  H.setGT(10);H.cam.x=x-H.viewW/2+(many?60:0);H.cam.y=y-192*0.62;H.cam.gy=H.cam.y;H.mode='play';if(H.GLP){H.GLP.pipe=false;H.GLP.rs=1;window.__HKnoauto=true;}
  for(let i=0;i<4;i++){a=12345;H.render();}
  const X=H.XF,cv=[...document.querySelectorAll('canvas')].find(c=>c.getBoundingClientRect().width>0),R=cv.getBoundingClientRect(),k=X.VZ/cv.width*R.width;
  return [R.left-X.camD/cv.width*R.width,R.top-X.camDY/cv.height*R.height,k,!!(fig==='snake'?sn:fig.length>5&&fig!=='stand'&&fig!=='crawl'?g:1)];}'''


def label(im, t):
    d = ImageDraw.Draw(im); d.rectangle((0, 0, 6 + 6 * len(t), 12), fill=(0, 0, 0)); d.text((3, 0), t, fill=(250, 240, 215))


def shoot(pg, n, sd, x, y, fig, whole=False):
    q = pg.evaluate(SHOW, [n, sd, x, y, fig, whole]); im = Image.open(io.BytesIO(pg.screenshot())).convert('RGB')
    if whole: return im.resize((852, 393), Image.LANCZOS)
    k = q[2] * DSF; x0, y0 = q[0] * DSF + (x - BW / 2) * k, q[1] * DSF + (y - BH + 8) * k
    return im.crop((int(x0), int(y0), int(x0 + BW * k), int(y0 + BH * k))).resize((BW * 3, BH * 3), Image.LANCZOS)


def page(b, src, mode, errs, hd=True):
    pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=DSF); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://' + src); pg.wait_for_timeout(800)
    pg.evaluate("()=>{document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.body.classList.remove('panelOpen');const st=document.createElement('style');st.textContent='.ctl,#pause,#pauseBtn,#pad,#hud{display:none!important}';document.head.appendChild(st);}")
    pg.evaluate("([m,hd])=>{__HK.S.set.lightMode=m;__HK.GLFX.sheen=false;const g=__HK.S.set.gfx||(__HK.S.set.gfx={});g.hd=hd;}", [mode, hd])
    return pg


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True); errs = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=GPU)
        pages = {(src, mode): page(b, src, mode, errs) for src in (OLD, NEW) for mode in MODES}
        spots = {}
        for n in FLOORS:
            for kind in ('dark', 'lamp'):
                spots[(n, kind)] = pages[(NEW, MODES[0])].evaluate(FIND, [n, kind])
                print('spot', n, kind, spots[(n, kind)], flush=True)
        cw, ch = BW * 3, BH * 3
        for mode in MODES:
            rows = [(n, kind, src) for n in FLOORS for kind in ('dark', 'lamp') if spots[(n, kind)] for src in (OLD, NEW)]
            sh = Image.new('RGB', (len(FIGS) * (cw + 4), len(rows) * (ch + 4) + 8 * (len(rows) // 2)), (20, 16, 24)); yy = 0
            for i, (n, kind, src) in enumerate(rows):
                sd, x, y, th = spots[(n, kind)]
                for j, f in enumerate(FIGS):
                    im = shoot(pages[(src, mode)], n, sd, x, y, f); label(im, '%s %s fl%d %s %s' % ('v87' if src == OLD else '46d', f, n, kind, th[4:20])); sh.paste(im, (j * (cw + 4), yy))
                yy += ch + 4 + (8 if src == NEW else 0)
                print(mode, n, kind, src == NEW, flush=True)
            sh.save(os.path.join(OUT, 'r46d_figs_%s.png' % mode)); print('wrote figs', mode, flush=True)
        lp = {src: page(b, src, 'classic', errs, False) for src in (OLD, NEW)}
        rows = [(n, src) for n in FLOORS[:2] for src in (OLD, NEW)]
        sh = Image.new('RGB', (len(FIGS) * (cw + 4), len(rows) * (ch + 4)), (20, 16, 24))
        for i, (n, src) in enumerate(rows):
            sd, x, y, th = spots[(n, 'dark')]
            for j, f in enumerate(FIGS):
                im = shoot(lp[src], n, sd, x, y, f); label(im, '%s low detail %s fl%d' % ('v87' if src == OLD else '46d', f, n)); sh.paste(im, (j * (cw + 4), i * (ch + 4)))
        sh.save(os.path.join(OUT, 'r46d_lowdetail.png')); print('wrote lowdetail', flush=True)
        for n in FLOORS:
            sd, x, y, th = spots[(n, 'dark')]
            ph = Image.new('RGB', (852 * len(MODES) + 6, 2 * 393 + 6), (20, 16, 24))
            for i, mode in enumerate(MODES):
                for j, src in enumerate((OLD, NEW)):
                    im = shoot(pages[(src, mode)], n, sd, x, y, 'all', True); label(im, '%s fl%d %s %s' % ('v87' if src == OLD else '46d', n, th, mode)); ph.paste(im, (i * 858, j * 399))
            ph.save(os.path.join(OUT, 'r46d_phone_%d.png' % n)); print('wrote phone', n, flush=True)
        if errs: print('errors', errs[:3])
        b.close()
