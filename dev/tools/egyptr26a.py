# egyptr26a.py [new.html] [old.html]: round 26a's pictures (owner, five phone screenshots of v72's lifts), into egypt_themes/r26a_lifts.png.
# One row per fault, each the owner's kind of case: (1) a paternoster at the foot of whose shaft an open arch looked out at the sky: the
# arch's posts and the opening's edges embossed on the slabs by Torchlight's relief, its sky light over them; (2) a paternoster with an arch
# recess at its foot: the posts and the back wall's courses embossed on the slabs; (3) a slab at the top of the column beside the right
# landing: its right side face over that landing's floor and the wall's top; (4) a slab on the bottom run: its lip over the foot floor's lip
# (sunk into the tile); (5) a counterweight lift's left mouth slab, shut: where it rises past the ceiling's edge, a bright wedge over the
# ceiling's dark shade. Torchlight before | after, Classic before | after, at the phone's resolution (852x393 CSS px at 2x, crops of the canvas
# at 1:1), and under each a 2x crop of the fault. old.html defaults to v72's source (git show de2c63c:dev/hourglass-keep.html). Run from
# dev/tools.
import io, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
NEW = os.path.abspath(a[0] if a else os.path.join(HERE, '..', 'hourglass-keep.html'))
OLD = a[1] if len(a) > 1 else None
OUT = os.path.join(HERE, 'egypt_themes', 'r26a_lifts.png')
INK = (20, 16, 24)
# (title, floor, seed, lift kind, its first column, clock ticks (paternoster; 'top': until a slab stands at the top of the column beside the
# right landing, 'bot': until one stands on the bottom run under a column) or the platform's place (0 top, 1 bottom), focus x, y (world))
SPOTS = [
    ('1. Floor 8, The Halls of the West: a paternoster with an open arch at its foot (the owner\'s first and second shots)', 8, 701, 'chain', 165, 180, 5296, 2958),
    ('2. Floor 8, The Halls of the West: an arch recess at a paternoster\'s foot, its posts and the courses embossed on the slabs', 8, 41048, 'chain', 189, 121, 6080, 962),
    ('3. The top of the column beside the right landing: the slab\'s right side face over the landing (third shot)', 8, 701, 'chain', 165, 'top', 5338, 2880),
    ('4. The bottom run: the slab\'s lip over the foot floor\'s lip, sunk into the tile (fourth shot)', 8, 701, 'chain', 165, 'bot', 5300, 3006),
    ('5. Floor 8: a counterweight lift\'s left mouth slab, shut, where it rises past the ceiling\'s edge (fifth shot)', 8, 701, 'lift', 140, 0, 4474, 1534),
]
SHOW = r'''([n,seed,kind,col,tk,fx,fy,rs])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS)H.S.hints[id]=1;const L=H.load(n,seed,true);H.banner=null;
  const f=L.lifts.find(f=>f.t===kind&&f.ca===col);if(!f)return null;const P=H.P;P.inv=1e9;for(const e of H.G)e.x=-9999;
  if(kind==='chain'){let si=0;if(typeof tk==='number')H.tick(tk);else for(let k=0;k<1200;k++){H.tick(1);let hit=-1;for(let j=0;j<f.n;j++){const q=H.chainPos(f,j,H.gameTime);
      if(tk==='bot'?Math.abs(q.y-f.yB)<0.5&&(Math.abs(q.x-(f.ca*32+16))<1.5||Math.abs(q.x-(f.cb*32+16))<1.5):Math.abs(q.y-f.yT)<0.5&&Math.abs(q.x-(f.cb*32+16))<1.5)hit=j;}if(hit>=0){si=hit;break;}}
    const q=H.chainPos(f,si,H.gameTime);P.x=q.x;P.y=q.y;P.fallY=P.y;P.state='lift';P.lift=f;P.slab=si;P.bx=q.x;P.by=q.y;P.bt=-9;P.face=f.dx;}
  else{f.y=tk?f.yB:f.yT;f.tgt=null;L.base[f.rT*L.cols+f.sc]=tk?0:1;f.gT=tk?0:1;f.gB=tk?1:0;const e=tk?0:1,rr=e?f.rB:f.rT;P.x=(f.sc+2*(e?f.sB:f.sT))*32+16;P.y=(rr+1)*64-4;P.state='stand';P.face=-(e?f.sB:f.sT);}
  let T=1e6;H.setClock(()=>T);let q=12345;Math.random=()=>{q=(q*16807)%2147483647;return q/2147483647;};
  H.cam.x=fx-H.viewW/2;H.cam.y=fy-64*1.6;H.cam.gy=H.cam.y;H.mode='play';if(H.GLP){H.GLP.pipe=false;H.GLP.rs=rs;window.__HKnoauto=true;}
  for(let i=0;i<4;i++){q=12345;H.render();}const X=H.XF,cv=[...document.querySelectorAll('canvas')].find(c=>c.getBoundingClientRect().width>0),R=cv.getBoundingClientRect();
  return [R.left+(fx*X.VZ-X.camD)/cv.width*R.width,R.top+(fy*X.VZ-X.camDY)/cv.height*R.height,H.themeName(n)];}'''
MODES = [('Torchlight', 'torch'), ('Classic', 'classic')]
CW, CH = 420, 330   # crop of the canvas at 1:1, round the fault
ZW, ZH = 200, 110   # the 2x crop


def old_src(tmp):
    if OLD:
        return os.path.abspath(OLD)
    fn = os.path.join(tmp, '_v72.html')
    open(fn, 'w', encoding='utf-8').write(subprocess.run(['git', 'show', 'de2c63c:dev/hourglass-keep.html'], cwd=HERE, capture_output=True, text=True, check=True).stdout)
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
    q = pg.evaluate(SHOW, list(spot[1:]) + [rs])
    if not q:
        return None
    im = Image.open(io.BytesIO(pg.screenshot())).convert('RGB')
    cx, cy = q[0] * 2, q[1] * 2
    x0 = int(min(max(0, cx - CW / 2), im.width - CW)); y0 = int(min(max(0, cy - CH * 0.55), im.height - CH))
    full = im.crop((x0, y0, x0 + CW, y0 + CH))
    d = ImageDraw.Draw(full); zx = int(cx - ZW / 2); zy = int(cy - ZH / 2)
    zoom = im.crop((zx, zy, zx + ZW, zy + ZH)).resize((ZW * 2, ZH * 2), Image.LANCZOS)
    d.rectangle((zx - x0, zy - y0, zx - x0 + ZW, zy - y0 + ZH), outline=(255, 70, 60))
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
            ImageDraw.Draw(row).text((6, 5), '%s  (seed %d)' % (spot[0], spot[2]), fill=(250, 240, 215))
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
