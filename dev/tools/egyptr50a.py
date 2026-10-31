# egyptr50a.py new.html [outdir]: round 50a's pictures (owner after v90: "Yes, strengthen the grit, grooves and scuffs"; stage 1: the levels
# to choose from). One build, CUE's levels switched at runtime: 0 is v90's look, A mild, B clear, C strong.
#   r50a_<cue>_phone.png  the real game view (852 x 393), v90 | A | B | C, Torchlight over Classic
#   r50a_<cue>_3x.png     a 3x crop round the cue, v90 | A | B | C, Torchlight over Classic (the grit at two moments: grains, a trickle)
#   r50a_grit_B.gif       6 s of the grit at B (Torchlight, 3x crop), real time
# Spots: egyptr49b.py's grit (the first floor 3-20 with a slab over a plate), egyptr49c.py's scuff and groove (the first floor from 1).
# Run from dev/tools (any copy of dev/). GPU flags for Torchlight (HK_GPU=0 for software).
import io, os, sys
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright
a = sys.argv[1:]
NEW = os.path.abspath(a[0])
OUT = os.path.abspath(a[1]) if len(a) > 1 else os.path.dirname(os.path.abspath(__file__))
GPU = [] if os.environ.get('HK_GPU') == '0' else ['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist', '--force_high_performance_gpu']
VW, VH, DSF = 852, 393, 3
os.makedirs(OUT, exist_ok=True)
LV = [('v90', 0), ('A', 1), ('B', 2), ('C', 3)]

PREP = r'''(mode)=>{const H=__HK;window.__HKfreeze=true;window.__HKnoauto=true;H.S.set.lightMode=mode;H.S.set.cross=false;if(H.GLFX)H.GLFX.sheen=false;
  for(const id in H.HINTS){H.S.hints[id]=1;if(H.S.learned)H.S.learned[id]=1;}
  document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.body.classList.remove('panelOpen');
  const st=document.createElement('style');st.textContent='.ctl,#pause,#pauseBtn,#pad{display:none!important}';document.head.appendChild(st);return 1;}'''
GRITF = r'''([lo,hi])=>{const H=__HK;for(let n=lo;n<=hi;n++)for(const sd of [700000+97*n+13,4400+n]){H.load(n,sd,false);const g=H.gritList();if(g.length)return [n,sd,g[0].c,g[0].r0,g[0].r1];}return null;}'''
FIND = r'''(want)=>{const H=__HK,TW=32,S=r=>(r+1)*64-4,out={};
 for(let n=1;n<=48;n++)for(let s=1;s<=3;s++){const sd=700000+97*n+13*s;let need=false;for(const k of want)if(!out[k])need=true;if(!need)return out;
  H.load(n,sd,false);const W=H.wearList();
  if(!out.scuff&&W.scuff.length){const q=W.scuff[0];out.scuff=[n,sd,q.c*TW+16-q.s*24,S(q.r)-32];}
  if(!out.groove&&W.groove.length){const q=W.groove[0];out.groove=[n,sd,(q.lo+q.hi+1)/2*TW,S(q.r)-16];}}
 return out;}'''
SETUP = r'''([n,sd])=>{const H=__HK;H.load(n,sd,false);H.banner=null;H.mode='play';H.intro=0;const P=H.P;P.x=-999;P.y=-999;P.state='dead';
  for(const e of H.G)e.x=-9999;for(const e of H.SN)e.x=-9999;return 1;}'''
LEVEL = r'''([k,v])=>{const C=__HK.CUE;C.grit=C.groove=C.scuff=0;C[k]=v;return 1;}'''
CAM = r'''([fx,fy,gt,clr])=>{const H=__HK;H.setClock(()=>1e6);H.setGT(gt);if(clr)H.clearRooms();H.cam.x=fx-H.viewW/2;H.cam.y=fy-192*0.55;H.cam.gy=H.cam.y;
  if(H.GLP){H.GLP.pipe=false;H.GLP.rs=1;}for(let i=0;i<(clr?3:1);i++)H.render();
  const XF=H.XF,cv=[...document.querySelectorAll('canvas')].find(c=>c.getBoundingClientRect().width>0),R=cv.getBoundingClientRect(),k=XF.VZ/cv.width*R.width;
  return [R.left-XF.camD/cv.width*R.width,R.top-XF.camDY/cv.height*R.height,k];}'''


def h2(a, b):  # the game's hash2
    M = 0xffffffff
    def imul(x, y): return ((x & M) * (y & M)) & M
    h = (imul(a, 374761393) + imul(b, 668265263)) & M
    h = imul(h ^ (h >> 13), 1274126177)
    return (h ^ (h >> 16)) & M


def gh(a, b): return h2(a, b) / 4294967296


def trickle_time(sd, lv, t0=10.0):  # a gameTime with B's (or lv's) trickle half way through its run
    P = [None, ([6, 9], 0.55), ([4.5, 7], 0.8), ([3.5, 5.5], 1.1)][lv]
    P0 = P[0][0] + (P[0][1] - P[0][0]) * gh(sd, 600); ph = gh(sd, 601) * P0
    k = int((t0 + ph) // P0) + 1
    while gh(sd + 3, k * 7 + 600) < 0.25: k += 1
    return k * P0 - ph + P[1] * 0.5 + 0.55


def label(im, t):
    d = ImageDraw.Draw(im); d.rectangle((0, 0, 8 + 6 * len(t), 13), fill=(0, 0, 0)); d.text((4, 1), t, fill=(250, 240, 215)); return im


def shot(pg, fx, fy, bw, bh, gt, whole=False, clr=True):
    q = pg.evaluate(CAM, [fx, fy, gt, clr]); im = Image.open(io.BytesIO(pg.screenshot())).convert('RGB')
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
        for mode in ('torch', 'classic'):
            pg = b.new_page(viewport={'width': VW, 'height': VH}, device_scale_factor=DSF); pg.on('pageerror', lambda e: errs.append(str(e)))
            pg.goto('file://' + NEW); pg.wait_for_timeout(700); pg.evaluate(PREP, mode); pages[mode] = pg
        T = pages['torch']
        g = T.evaluate(GRITF, [3, 20]); cs = T.evaluate(FIND, ['scuff', 'groove']); print('grit', g, 'wear', cs, flush=True)
        cases = {}
        if g:
            n, sd, c, r0, r1 = g; cases['grit'] = [n, sd, c * 32 + 16, (r0 + r1 + 2) / 2 * 64 - 4, c * 131 + r0 * 977]
        for k in ('scuff', 'groove'):
            if k in cs: cases[k] = cs[k] + [None]
        for k in ('grit', 'scuff', 'groove'):
            if k not in cases: print('no case', k); continue
            n, sd, fx, fy, gsd = cases[k]
            times = [11.1, trickle_time(gsd, 2)] if k == 'grit' else [10.37]
            bw, bh = (90, 190) if k == 'grit' else (110, 46) if k == 'groove' else (120, 76)
            if k == 'groove': fy += 12
            rows3, rowsP = [], []
            for mode in ('torch', 'classic'):
                pg = pages[mode]; pg.evaluate(SETUP, [n, sd]); pr = []
                for gt in times:
                    row = []
                    for nm, v in LV:
                        pg.evaluate(LEVEL, [k, v]); row.append(label(shot(pg, fx, fy, bw, bh, gt), '%s %s fl%d %s t%.1f' % (k, nm, n, mode, gt)))
                    rows3.append(row)
                for nm, v in LV:
                    pg.evaluate(LEVEL, [k, v]); pr.append(label(shot(pg, fx, fy, 0, 0, times[-1], whole=True), '%s %s fl%d %s' % (k, nm, n, mode)))
                rowsP.append(pr)
            grid(rows3).save(os.path.join(OUT, 'r50a_%s_3x.png' % k))
            grid(rowsP, 6).save(os.path.join(OUT, 'r50a_%s_phone.png' % k)); print('wrote', k, flush=True)
        if 'grit' in cases:
            n, sd, fx, fy, gsd = cases['grit']; pg = T; pg.evaluate(SETUP, [n, sd]); pg.evaluate(LEVEL, ['grit', 2]); t0 = trickle_time(gsd, 2) - 2.5
            shot(pg, fx, fy, 70, 180, t0); fr = []
            for i in range(180):
                fr.append(label(shot(pg, fx, fy, 70, 180, t0 + i / 30, clr=False), 'grit B t%.2f' % (t0 + i / 30)).resize((140, 360), Image.LANCZOS))
            fr[0].save(os.path.join(OUT, 'r50a_grit_B.gif'), save_all=True, append_images=fr[1:], duration=33, loop=0)
        for pg in pages.values(): pg.evaluate(LEVEL, ['grit', 0])
        if errs: print('errors', errs[:5])
        b.close()
