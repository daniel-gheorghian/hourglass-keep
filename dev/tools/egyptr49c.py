# egyptr49c.py old.html new.html [outdir] [cases]: round 49c's pictures (owner after the round 49 research: "rely only on subtle graphic
# hints"; the wear marks and the bones of earlier thieves).
#   r49c_<case>_3x.png     old | new, Torchlight over Classic, a 3x crop: scuff (a wall the route runs up), groove (a block's track, the block
#                          at its start and again pushed one cell), pit, banner, slicer, sand (the bones of each kind; the sand lift's while
#                          its slab rides down above them)
#   r49c_<case>_phone.png  the same at phone size (852 x 393), old | new, Torchlight over Classic
#   r49c_all_3x.png        every case, new, Torchlight | Classic
# Cases: the first floor from 1 (seeds 700000+97n+13s, s 1-3) that has each (the new build's wearList). Run from dev/tools (any copy of
# dev/). GPU flags for Torchlight (HK_GPU=0 for software).
import io, os, sys
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright
a = sys.argv[1:]
OLD, NEW = os.path.abspath(a[0]), os.path.abspath(a[1])
OUT = os.path.abspath(a[2]) if len(a) > 2 and not a[2].startswith('cases=') else os.path.dirname(os.path.abspath(__file__))
WANT = next((x[6:].split(',') for x in a if x.startswith('cases=')), ['scuff', 'groove', 'pit', 'banner', 'slicer', 'sand'])
GPU = [] if os.environ.get('HK_GPU') == '0' else ['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist', '--force_high_performance_gpu']
VW, VH, DSF = 852, 393, 3
os.makedirs(OUT, exist_ok=True)

PREP = r'''(mode)=>{const H=__HK;window.__HKfreeze=true;window.__HKnoauto=true;H.S.set.lightMode=mode;H.S.set.cross=false;if(H.GLFX)H.GLFX.sheen=false;
  for(const id in H.HINTS){H.S.hints[id]=1;if(H.S.learned)H.S.learned[id]=1;}
  document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.body.classList.remove('panelOpen');
  const st=document.createElement('style');st.textContent='.ctl,#pause,#pauseBtn,#pad{display:none!important}';document.head.appendChild(st);return 1;}'''
# a place for each case: [n, seed, focus x, focus y, extra]
FIND = r'''(want)=>{const H=__HK,TW=32,S=r=>(r+1)*64-4,out={};
 for(let n=1;n<=48;n++)for(let s=1;s<=3;s++){const sd=700000+97*n+13*s;let need=false;for(const k of want)if(!out[k])need=true;if(!need)return out;
  H.load(n,sd,false);const W=H.wearList();
  if(!out.scuff&&W.scuff.length){const q=W.scuff[0];out.scuff=[n,sd,q.c*TW+16-q.s*24,S(q.r)-32,null];}
  if(!out.groove&&W.groove.length){const q=W.groove[0];out.groove=[n,sd,(q.lo+q.hi+1)/2*TW,S(q.r)-16,null];}
  for(const b of W.bones){if(out[b.k])continue;if(b.k==='sand'){const f=b.lf;out.sand=[n,sd,f.sc*TW+16,S(f.rD)-22,null];}else out[b.k]=[n,sd,b.c*TW+16,S(b.r)-(b.k==='pit'?18:16),null];}}
 return out;}'''
# the floor drawn still, nobody in view; groove 1: the block pushed one cell; sand: its slab 70 px over the pit's floor
SETUP = r'''([k,n,sd,x])=>{const H=__HK;const L=H.load(n,sd,false);H.banner=null;H.mode='play';H.intro=0;const P=H.P;P.x=-999;P.y=-999;P.state='dead';
  for(const e of H.G)e.x=-9999;for(const e of H.SN)e.x=-9999;
  if(k==='groove'&&x===1){const b=L.ext.blocks[0];const dir=b.c<=b.lo?1:-1;const nc=b.c+dir;L.base[b.r*L.cols+b.c]=b.under;b.under=L.base[b.r*L.cols+nc];L.base[b.r*L.cols+nc]=2;b.c=nc;H.rebuildBlocks&&H.rebuildBlocks();}
  if(k==='sand'){for(const f of L.lifts)if(f.sand&&f.rD!==undefined){const sb=f.yP||((f.rB+1)*64-4);f.s=1;f.tm=5;f.y=sb-70;}}
  return 1;}'''
CAM = r'''([fx,fy,gt])=>{const H=__HK;H.setClock(()=>1e6);H.setGT(gt);H.clearRooms();H.cam.x=fx-H.viewW/2;H.cam.y=fy-192*0.55;H.cam.gy=H.cam.y;
  if(H.GLP){H.GLP.pipe=false;H.GLP.rs=1;}for(let i=0;i<3;i++)H.render();
  const XF=H.XF,cv=[...document.querySelectorAll('canvas')].find(c=>c.getBoundingClientRect().width>0),R=cv.getBoundingClientRect(),k=XF.VZ/cv.width*R.width;
  return [R.left-XF.camD/cv.width*R.width,R.top-XF.camDY/cv.height*R.height,k];}'''


def label(im, t):
    d = ImageDraw.Draw(im); d.rectangle((0, 0, 8 + 6 * len(t), 13), fill=(0, 0, 0)); d.text((4, 1), t, fill=(250, 240, 215)); return im


def crop(pg, fx, fy, bw, bh, whole=False):
    q = pg.evaluate(CAM, [fx, fy, 10.37]); im = Image.open(io.BytesIO(pg.screenshot())).convert('RGB')
    if whole: return im.resize((VW, VH), Image.LANCZOS)
    k = q[2] * DSF; x0, y0 = q[0] * DSF + (fx - bw / 2) * k, q[1] * DSF + (fy - bh / 2) * k
    return im.crop((int(x0), int(y0), int(x0 + bw * k), int(y0 + bh * k))).resize((bw * 3, bh * 3), Image.LANCZOS)


def grid(rows, gap=8, bg=(20, 16, 24)):
    w = sum(i.width for i in rows[0]) + gap * (len(rows[0]) - 1); h = sum(r[0].height for r in rows) + gap * (len(rows) - 1)
    im = Image.new('RGB', (w, h), bg); y = 0
    for r in rows:
        x = 0
        for c in r: im.paste(c, (x, y)); x += c.width + gap
        y += r[0].height + gap
    return im


if __name__ == '__main__':
    with sync_playwright() as p:
        b = p.chromium.launch(args=GPU); pages = {}; errs = []
        for nm, src in (('old', OLD), ('new', NEW)):
            for mode in ('torch', 'classic'):
                pg = b.new_page(viewport={'width': VW, 'height': VH}, device_scale_factor=DSF); pg.on('pageerror', lambda e: errs.append(str(e)))
                pg.goto('file://' + src); pg.wait_for_timeout(700); pg.evaluate(PREP, mode); pages[(nm, mode)] = pg
        cases = pages[('new', 'torch')].evaluate(FIND, WANT); print('cases', cases, flush=True)
        BW, BH = 120, 76; allrows = []
        for k in WANT:
            if k not in cases: print('no case', k); continue
            n, sd, fx, fy, _ = cases[k]
            variants = [0, 1] if k == 'groove' else [0]
            rows, prow, arow = [], [], []
            for v in variants:
                for mode in ('torch', 'classic'):
                    row = []
                    for nm in ('old', 'new'):
                        pg = pages[(nm, mode)]; pg.evaluate(SETUP, [k, n, sd, v])
                        row.append(label(crop(pg, fx, fy, BW, BH), '%s %s fl%d %s%s' % (k, nm, n, mode, ' pushed' if v else '')))
                        if v == 0: prow.append(label(crop(pg, fx, fy, BW, BH, True), '%s %s fl%d %s' % (k, nm, n, mode)))
                        if v == 0 and nm == 'new': arow.append(row[-1])
                    rows.append(row)
            grid(rows).save(os.path.join(OUT, 'r49c_%s_3x.png' % k))
            grid([prow[0:2], prow[2:4]]).save(os.path.join(OUT, 'r49c_%s_phone.png' % k)); allrows.append(arow); print('wrote', k, flush=True)
        if allrows: grid(allrows).save(os.path.join(OUT, 'r49c_all_3x.png'))
        if errs: print('errors', errs[:5])
        b.close()
