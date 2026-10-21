# egyptr25d.py [new.html] [old.html]: round 25d's pictures (owner: "lift slab with no ceiling above it"), into egypt_themes/r25d_slab.png.
# The open-hall pass gave every counterweight lift's top landing a row of headroom, the mouth and the shaft's top included, so the
# mouth's stone slab, shut while the platform is away, stood free against the hall (and the sky through its openings) with nothing to
# slide up into. Now the lintel stays over the mouth and the shaft's top, as over every portcullis. Each row is one lift, the platform
# at the bottom and the top mouth shut, the prince on the landing two cells out: Torchlight and Classic, before | after, at the phone's
# resolution (852x393 CSS px at 2x, crops of the 1704 px canvas at 1:1), and under each a 2x crop of the slab's top.
# old.html defaults to round 25c's source (git show c021d32:dev/hourglass-keep.html). Run from dev/tools.
import io, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
NEW = os.path.abspath(a[0] if a else os.path.join(HERE, '..', 'hourglass-keep.html'))
OLD = a[1] if len(a) > 1 else None
OUT = os.path.join(HERE, 'egypt_themes', 'r25d_slab.png')
INK = (20, 16, 24)
SPOTS = [  # (title, floor, seed, shaft column)
    ('Floor 7, The Halls of the West: the owner\'s case, a left mouth by the hall\'s windows', 7, 4601, 79),
    ('Floor 10, The Blue Chambers: a right mouth', 10, 701, 140),
    ('Floor 26, The Deffufa of Kerma by Moonlight: a left mouth', 26, 701, 399),
    ('Floor 41, The Ruined Labyrinth of Hawara at Dawn: a right mouth', 41, 701, 470),
]
SHOW = r'''([n,seed,sc,rs])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS)H.S.hints[id]=1;const L=H.load(n,seed,true);H.banner=null;
  const f=L.lifts.find(f=>f.sc===sc&&f.t==='lift');if(!f)return null;let T=1e6;H.setClock(()=>T);let q=12345;Math.random=()=>{q=(q*16807)%2147483647;return q/2147483647;};
  f.y=f.yB;f.tgt=null;L.base[f.rT*L.cols+f.sc]=0;f.gT=0;f.gB=1;
  const P=H.P;P.inv=1e9;P.x=(f.sc+2*f.sT)*32+16;P.y=f.yT;P.state='stand';P.face=-f.sT;for(const e of H.G)e.x=-9999;
  H.cam.x=f.sc*32+16-H.viewW/2;H.cam.y=f.yT-64*2.0;H.cam.gy=H.cam.y;H.mode='play';if(H.GLP){H.GLP.pipe=false;H.GLP.rs=rs;}
  for(let i=0;i<4;i++){q=12345;H.render();}const X=H.XF,cv=[...document.querySelectorAll('canvas')].find(c=>c.getBoundingClientRect().width>0),R=cv.getBoundingClientRect();
  const sx=(f.sc+(f.sT>0?1:0))*32;
  return [R.left+(sx*X.VZ-X.camD)/cv.width*R.width,R.top+((f.rT*64)*X.VZ-X.camDY)/cv.height*R.height,H.themeName(n)];}'''
MODES = [('Torchlight', 'torch'), ('Classic', 'classic')]
CW, CH = 420, 330   # crop of the canvas at 1:1, round the slab's top
ZW, ZH = 210, 120   # the 2x crop


def old_src(tmp):
    if OLD:
        return os.path.abspath(OLD)
    fn = os.path.join(tmp, '_r25c.html')
    open(fn, 'w', encoding='utf-8').write(subprocess.run(['git', 'show', 'c021d32:dev/hourglass-keep.html'], cwd=HERE, capture_output=True, text=True, check=True).stdout)
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


def shot(pg, spot, rs=1):
    _, n, seed, sc = spot
    q = pg.evaluate(SHOW, [n, seed, sc, rs])
    if not q:
        return None
    im = Image.open(io.BytesIO(pg.screenshot())).convert('RGB')
    cx, cy = q[0] * 2, q[1] * 2
    x0 = int(min(max(0, cx - CW / 2), im.width - CW)); y0 = int(min(max(0, cy - CH * 0.4), im.height - CH))
    full = im.crop((x0, y0, x0 + CW, y0 + CH))
    zx = int(cx - ZW / 2); zy = int(cy - ZH * 0.45)
    zoom = im.crop((zx, zy, zx + ZW, zy + ZH)).resize((ZW * 2, ZH * 2), Image.LANCZOS)
    return q, full, zoom


def label(im, t):
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 8 + 6 * len(t), 13), fill=(0, 0, 0))
    d.text((4, 1), t, fill=(250, 240, 215))


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
                    r = shot(pages[(t, m)], spot)
                    if not r:
                        print('no case', spot); break
                    q, full, zoom = r
                    label(full, '%s, %s' % (mt, t)); label(zoom, '%s, %s, 2x' % (mt, t))
                    cells.append((full, zoom))
            if len(cells) != 4:
                continue
            print('spot', spot[0], flush=True)
            W = 4 * CW + 2 * 4 + 12
            row = Image.new('RGB', (W, 22 + CH + 4 + ZH * 2), INK)
            ImageDraw.Draw(row).text((6, 5), '%s (seed %d, shaft column %d; platform at the bottom, top mouth shut)' % (spot[0], spot[2], spot[3]), fill=(250, 240, 215))
            x = 0
            for i, (full, zoom) in enumerate(cells):
                row.paste(full, (x, 22)); row.paste(zoom, (x + (CW - ZW * 2) // 2, 22 + CH + 4))
                x += CW + (4 if i % 2 == 0 else 12)
            rows.append(row)
        for k, pg in pages.items():
            if pg.errs:
                print('errors', k, pg.errs[:3])
        b.close()
    W = max(r.width for r in rows)
    sheet = Image.new('RGB', (W, sum(r.height + 8 for r in rows)), INK)
    y = 0
    for r in rows:
        sheet.paste(r, (0, y)); y += r.height + 8
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    sheet.save(OUT, optimize=True)
    print('wrote', OUT, sheet.size)
