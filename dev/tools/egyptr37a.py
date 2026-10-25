# egyptr37a.py [new.html] [old.html] [out.png]: round 37a's pictures (owner after v81: "The lift shafts, at the very bottom the floor tile
# should be missing because the moving tile of the lift will replace it"), into egypt_themes/r37a_liftfoot.png. One row per case: a counterweight
# lift (its bottom landing on the left, then one on the right) with the platform resting at the foot, just off it and at the top; a sand lift with
# its slab at the top (the sand standing in the shaft), sinking and at rest at the foot; a paternoster's foot (unchanged: a floor he walks on).
# Columns: v81 | round 37a, Classic then Torchlight, crops of the foot at 3x (3 screen px a world px). old.html defaults to origin/main's source
# (git show origin/main:dev/hourglass-keep.html; v81). Run from dev/tools (Torchlight is software WebGL in headless Chromium: a few s a frame).
import io, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
htm = [x for x in a if x.endswith('.html')]
NEW = os.path.abspath(htm[0] if htm else os.path.join(HERE, '..', 'hourglass-keep.html'))
OLD = os.path.abspath(htm[1]) if len(htm) > 1 else None
OUT = next((x for x in a if x.endswith('.png')), os.path.join(HERE, 'egypt_themes', 'r37a_liftfoot.png'))
INK = (20, 16, 24)
# (title, floor, seed, kind ('lift', 'sand', 'chain'), its first column, state)
CASES = [
    ('Counterweight lift, floor 8: the platform at rest at the foot', 8, 41048, 'lift', 89, 'foot'),
    ('... the platform 14 px up, leaving the foot', 8, 41048, 'lift', 89, 'off'),
    ('... the platform at the top: the foot (the mouth slab shut on its left)', 8, 41048, 'lift', 89, 'top'),
    ('Counterweight lift, floor 3, landing on the right: the platform at rest at the foot', 3, 40393, 'lift', 99, 'foot'),
    ('... the platform at the top: the foot (the mouth slab shut on its right)', 3, 40393, 'lift', 99, 'top'),
    ('Sand lift, floor 10: the slab at the top, the sand standing in the shaft', 10, 41310, 'sand', 30, 'top'),
    ('... sinking, a storey above the foot', 10, 41310, 'sand', 30, 'mid'),
    ('... at rest at the foot, for good', 10, 41310, 'sand', 30, 'foot'),
    ('Paternoster, floor 8: a slab on the bottom run (unchanged: the foot is a floor he walks and lands on)', 8, 41048, 'chain', 189, 'bot'),
]
SHOW = r'''([n,seed,kind,col,st])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS)H.S.hints[id]=1;const L=H.load(n,seed,true);H.banner=null;
  const sand=kind==='sand',kk=sand?'lift':kind,f=L.lifts.find(f=>f.t===kk&&f.ca===col&&!!f.sand===sand);if(!f)return null;const P=H.P;P.inv=1e9;for(const e of H.G)e.x=-9999;
  if(kind==='chain'){for(let k=0;k<2400;k++){H.tick(1);let hit=0;for(let j=0;j<f.n;j++){const q=H.chainPos(f,j,H.gameTime);if(Math.abs(q.y-f.yB)<0.5&&Math.abs(q.x-(f.ca*32+32))<1.5)hit=1;}if(hit)break;}}
  else if(sand){if(st!=='top'){f.s=st==='foot'?2:1;f.tm=1;f.y=st==='foot'?f.yB:f.yB-64;}L.base[f.rT*L.cols+f.sc]=f.y===f.yT?1:0;f.gT=f.y===f.yT?1:0;f.gB=f.y===f.yB?1:0;}
  else{f.y=st==='foot'?f.yB:st==='top'?f.yT:f.yB-14;f.tgt=null;L.base[f.rT*L.cols+f.sc]=st==='top'?1:0;f.gT=st==='top'?1:0;f.gB=st==='foot'?1:0;}
  P.x=L.start.x;P.y=(L.start.r+1)*64-4;P.state='stand';
  let T=1e6;H.setClock(()=>T);let q=12345;Math.random=()=>{q=(q*16807)%2147483647;return q/2147483647;};
  const fx=(f.ca+f.cb+1)*16,fy=(f.rB+1)*64-4;
  H.cam.x=fx-H.viewW/2;H.cam.y=fy-64*1.5;H.cam.gy=H.cam.y;H.mode='play';if(H.GLP){H.GLP.pipe=false;H.GLP.rs=1;window.__HKnoauto=true;}
  for(let i=0;i<3;i++){q=12345;H.render();}const X=H.XF,cv=[...document.querySelectorAll('canvas')].find(c=>c.getBoundingClientRect().width>0),R=cv.getBoundingClientRect(),k=X.VZ/cv.width*R.width;
  return [R.left-X.camD/cv.width*R.width,R.top-X.camDY/cv.height*R.height,k,fx,fy,H.themeName(n)];}'''
MODES = [('Classic', 'classic'), ('Torchlight', 'torch')]
BW, BH, ZK = 112, 64, 3   # the crop in world px round the foot, and its scale


def old_src(tmp):
    if OLD:
        return OLD
    fn = os.path.join(tmp, '_v81.html')
    open(fn, 'w', encoding='utf-8').write(subprocess.run(['git', 'show', 'origin/main:dev/hourglass-keep.html'], cwd=HERE, capture_output=True, text=True, check=True).stdout)
    return fn


def page(b, src, mode):
    pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=2)
    pg.errs = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e)))
    pg.goto('file://' + src)
    pg.wait_for_timeout(700)
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.body.classList.remove('panelOpen')")
    pg.evaluate("m=>{__HK.S.set.lightMode=m;}", mode)
    return pg


def shot(pg, case):
    q = pg.evaluate(SHOW, list(case[1:]))
    if not q:
        return None
    im = Image.open(io.BytesIO(pg.screenshot())).convert('RGB')
    ox, oy, k, fx, fy = q[0] * 2, q[1] * 2, q[2] * 2, q[3], q[4]
    x0, y0 = ox + (fx - BW / 2) * k, oy + (fy - BH * 0.7) * k
    return im.crop((int(x0), int(y0), int(x0 + BW * k), int(y0 + BH * k))).resize((BW * ZK, BH * ZK), Image.LANCZOS)


def label(im, t):
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 8 + 6 * len(t), 13), fill=(0, 0, 0))
    d.text((4, 1), t, fill=(250, 240, 215))


if __name__ == '__main__':
    tmp = tempfile.mkdtemp()
    srcs = [('v81', old_src(tmp)), ('37a', NEW)]
    rows = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        pages = {(t, m): page(b, s, m) for t, s in srcs for _, m in MODES}
        for case in CASES:
            cells = []
            for mt, m in MODES:
                for t, _ in srcs:
                    c = shot(pages[(t, m)], case)
                    if c is None:
                        print('no case', case); break
                    label(c, '%s, %s' % (t, mt)); cells.append(c)
            if len(cells) != 4:
                continue
            print('case', case[0], flush=True)
            cw = BW * ZK
            row = Image.new('RGB', (4 * cw + 2 * 4 + 12, 20 + BH * ZK), INK)
            ImageDraw.Draw(row).text((6, 4), '%s  (seed %d)' % (case[0], case[2]), fill=(250, 240, 215))
            x = 0
            for i, c in enumerate(cells):
                row.paste(c, (x, 20)); x += cw + (4 if i % 2 == 0 else 12)
            rows.append(row)
        for k, pg in pages.items():
            if pg.errs:
                print('errors', k, pg.errs[:3])
        b.close()
    W = max(r.width for r in rows)
    sheet = Image.new('RGB', (W, sum(r.height + 6 for r in rows)), INK)
    y = 0
    for r in rows:
        sheet.paste(r, (0, y)); y += r.height + 6
    os.makedirs(os.path.dirname(os.path.abspath(OUT)), exist_ok=True)
    sheet.save(OUT, optimize=True)
    print('wrote', OUT, sheet.size)
