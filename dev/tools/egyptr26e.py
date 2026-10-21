# egyptr26e.py [new.html] [old.html]: round 26e's picture (owner: "sand lifts must always work within a shaft otherwise they don't make
# sense"), into egypt_themes/r26e_sandshaft.png. Four typical sand lifts, each one row: Torchlight before | after, Classic before | after, crops
# of the phone's canvas (852x393 CSS px at 2x) round the shaft, the slab at the ride's given share. (1) three storeys, the exit on the right
# and a corridor running on past the foot on the left: before, the storey over the foot open on both sides (the hall pass's headroom) and
# the foot open both ways, the sand a free pillar in a hall two storeys high; after, walls beside the sand and a mouth slab on each side of
# the foot. (2) three storeys, exit on the left, a wall past the foot: one mouth slab. (3) four storeys, near the bottom: the mouth slabs
# rising over the ride's last 28 px. (4) one of the 16 in 322 (floors 1-48, 3 seeds) with a side opened or a drop beside its foot: built as the banner
# slide instead. Under the rows, sandshaft.py's counts before and after. old.html defaults to the source before round 26e (git show
# 3b92b01:dev/hourglass-keep.html). Run from dev/tools.
import io, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sandshaft

a = sys.argv[1:]
NEW = os.path.abspath(a[0] if a else os.path.join(HERE, '..', 'hourglass-keep.html'))
OLD = a[1] if len(a) > 1 else None
OUT = os.path.join(HERE, 'egypt_themes', 'r26e_sandshaft.png')
INK = (20, 16, 24)
# (title, floor, seed, shaft column, top row, share of the ride 0..100)
SPOTS = [
    ('1. Floor 5, The Halls of the West: three storeys, exit right, a corridor past the foot on the left (the slab 40% down)', 5, 56493, 124, 33, 40),
    ('2. Floor 4, The Waters of Nun: three storeys, exit left, a wall past the foot (40% down)', 4, 48443, 170, 33, 40),
    ('3. Floor 6, The Halls of the West: four storeys, near the foot: the mouth slabs rising as the slab comes down (96% down)', 6, 56624, 134, 20, 96),
    ('4. Floor 15, The Forges of Meroe: a drop beside the foot, so no shaft: now the banner slide (30% down before)', 15, 57803, 77, 9, 30),
]
SHOW = r'''([n,seed,sc,rT,fr,mode])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS)H.S.hints[id]=1;H.S.set.lightMode=mode;const L=H.load(n,seed,true);H.banner=null;
  const P=H.P;P.inv=1e9;for(const e of H.G)e.x=-9999;const f=L.lifts.find(f=>f.sand&&f.sc===sc&&f.rT===rT);let yT=(rT+1)*64-4,yB=yT;
  if(f){yB=f.yB;f.y=f.yT+(f.yB-f.yT)*fr/100;if(fr>0){f.s=fr>=100?2:1;f.tm=1;L.base[f.rT*L.cols+f.sc]=0;}f.gT=f.y===f.yT?1:0;f.gB=f.y===f.yB?1:0;
    P.x=f.sc*32+16;P.y=f.y;P.state=fr>0&&fr<100?'lift':'stand';P.lift=f;}
  else{let r=rT+1;while(L.base[r*L.cols+sc]===0)r++;yB=(r+1)*64-4;const s=L.base[rT*L.cols+sc-1]===1?-1:1;P.x=(sc+s)*32+16;P.y=yT;P.state='stand';}
  P.face=1;let T=1e6;H.setClock(()=>T);let q=12345;Math.random=()=>{q=(q*16807)%2147483647;return q/2147483647;};
  const fx=sc*32+16,fy=yB-62;H.cam.x=fx-H.viewW/2;H.cam.y=fy-H.viewW*393/852/2;H.cam.gy=H.cam.y;H.mode='play';if(H.GLP){H.GLP.pipe=false;H.GLP.rs=1;window.__HKnoauto=true;}
  for(let i=0;i<4;i++){q=12345;H.render();}const X=H.XF,cv=[...document.querySelectorAll('canvas')].find(c=>c.getBoundingClientRect().width>0),R=cv.getBoundingClientRect(),k=R.width/cv.width*X.VZ;
  return [R.left+(fx*X.VZ-X.camD)/cv.width*R.width,R.top+(fy*X.VZ-X.camDY)/cv.height*R.height,k,yB-yT];}'''
MODES = [('Torchlight', 'torch'), ('Classic', 'classic')]
CW = 400


def old_src(tmp):
    if OLD:
        return os.path.abspath(OLD)
    fn = os.path.join(tmp, '_r26d.html')
    open(fn, 'w', encoding='utf-8').write(subprocess.run(['git', 'show', '3b92b01:dev/hourglass-keep.html'], cwd=HERE, capture_output=True, text=True, check=True).stdout)
    return fn


def page(b, src, mode):
    pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=2)
    pg.errs = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e)))
    pg.goto('file://' + src)
    pg.wait_for_timeout(700)
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.body.classList.remove('panelOpen')")
    return pg


def shot(pg, spot, mode):
    q = pg.evaluate(SHOW, list(spot[1:]) + [mode])
    im = Image.open(io.BytesIO(pg.screenshot())).convert('RGB')
    cx, cy, k, hh = q[0] * 2, q[1] * 2, q[2] * 2, q[3]
    ch = im.height
    x0 = int(min(max(0, cx - CW / 2), im.width - CW)); y0 = int(min(max(0, cy - ch / 2), im.height - ch))
    return im.crop((x0, y0, x0 + CW, y0 + ch))


def label(im, t):
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 8 + 6 * len(t), 13), fill=(0, 0, 0))
    d.text((4, 1), t, fill=(250, 240, 215))


def counts(src):
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(); pg.goto('file://' + src); pg.wait_for_timeout(300)
        res = pg.evaluate(sandshaft.SCAN, [1, 48, 3]); b.close()
    bad = [x for x in res if x['bad']]
    st = {}
    for x in bad:
        for k, s, sd in x['bad']:
            key = '%s storey %d' % (k, s); st[key] = st.get(key, 0) + 1
    return len(res), len(bad), sum(x['mo'] for x in res), st


if __name__ == '__main__':
    tmp = tempfile.mkdtemp()
    srcs = {'before': old_src(tmp), 'after': NEW}
    rows = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
        pages = {(t, m): page(b, s, m) for t, s in srcs.items() for _, m in MODES}
        for spot in SPOTS:
            cells = []
            for mt, m in MODES:
                for t in ('before', 'after'):
                    im = shot(pages[(t, m)], spot, m); label(im, '%s, %s' % (mt, t)); cells.append(im)
            H = max(c.height for c in cells)
            row = Image.new('RGB', (4 * CW + 4 + 12 + 4, 22 + H), INK)
            ImageDraw.Draw(row).text((6, 5), '%s  (seed %d)' % (spot[0], spot[2]), fill=(250, 240, 215))
            x = 0
            for i, c in enumerate(cells):
                row.paste(c, (x, 22)); x += CW + (4 if i % 2 == 0 else 12)
            rows.append(row); print('spot', spot[0], flush=True)
        for k, pg in pages.items():
            if pg.errs:
                print('errors', k, pg.errs[:3])
        b.close()
    cb, ca = counts(srcs['before']), counts(NEW)
    lines = ['sandshaft.py, floors 1-48, 3 seeds (sand lifts on the tiles: wall beside the sand on every storey, the foot shut by a mouth slab where open):',
             'before: %d sand lifts, %d not in a shaft (all); open cells by storey under the top: %s' % (cb[0], cb[1], ', '.join('%s %d' % kv for kv in sorted(cb[3].items()))),
             'after: %d sand lifts (16 with a side opened by a later run or a drop beside the foot now built as the banner slide), %d not in a shaft; %d foot mouth slabs' % (ca[0], ca[1], ca[2])]
    W = max(r.width for r in rows)
    foot = Image.new('RGB', (W, 16 * len(lines) + 10), INK)
    for i, t in enumerate(lines):
        ImageDraw.Draw(foot).text((6, 5 + 16 * i), t, fill=(250, 240, 215))
    sheet = Image.new('RGB', (W, sum(r.height + 8 for r in rows) + foot.height), INK)
    y = 0
    for r in rows:
        sheet.paste(r, (0, y)); y += r.height + 8
    sheet.paste(foot, (0, y))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    sheet.save(OUT, optimize=True)
    print('wrote', OUT, sheet.size)
    print('\n'.join(lines))
