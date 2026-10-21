# egyptr25c.py [new.html] [old.html]: round 25c's pictures (owner: "what is that haze around the prince?"), into egypt_themes/r25c_haze.png.
# The haze was the fill light every figure carries (gatherLights, kind 'fill') landing on the sky seen through an opening: a pale halo
# that went with him and stopped at the sill. Each row is one spot, the figure standing in front of an opening at the phone's resolution
# (852x393 CSS px at 2x, crops of the 1704 px canvas at 1:1): Torchlight at GLP.rs 1, Torchlight at GLP.rs .5, Classic, before | after;
# under it the same at 3x round the figure. Spots: floor 7 (the owner's, an open arch beside a raised block), floor 7 with a guard in
# front of the arch, floor 23 (another theme, at night) and floor 14 (another, at dusk), each before an open arch.
# old.html defaults to round 25f's source (git show 7de72e9:dev/hourglass-keep.html). Run from dev/tools.
import io, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
NEW = os.path.abspath(a[0] if a else os.path.join(HERE, '..', 'hourglass-keep.html'))
OLD = a[1] if len(a) > 1 else None
OUT = os.path.join(HERE, 'egypt_themes', 'r25c_haze.png')
INK = (20, 16, 24)

# a standing place beside an opening (kind): the cell under the opening's foot that is not wall, with floor under it; side 'block': the
# next cell to the right is a wall block one storey high (the owner's photo); returns where the figure stands
FIND = r'''([n,skip,kind,side,who])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS)H.S.hints[id]=1;let k=0;
  for(let sd=1;sd<80;sd++){const L=who==='G'?H.load(n,700+sd):H.load(n,700+sd,true);H.banner=null;const C=L.cols,B=(c,r)=>L.base[r*C+c];
    for(const o of H.ryOps()){if(o.kind!==kind||o.sh.own||o.x0<12*32||o.x1>(L.cols-12)*32)continue;const r=Math.floor((o.y1-2)/64);let c=-1;
      for(let cc=Math.floor(o.x0/32);cc<=Math.floor(o.x1/32)+1;cc++){if(B(cc,r)===2||!(B(cc,r+1)===2||B(cc,r+1)===1))continue;
        if(side==='block'?(B(cc+1,r)===2&&B(cc+1,r-1)!==2):(B(cc-1,r)!==2&&B(cc+1,r)!==2&&cc*32+16>o.x0-6&&cc*32+16<o.x1+6)){c=cc;break;}}
      if(c<0)continue;if(k++<skip)continue;window.__O={x:side==='block'?c*32+10:c*32+16,y:(r+1)*64-4};return [n,700+sd,H.themeName(n),o.kind];}}
  return null;}'''
# who stands there ('P' the prince; 'G' a guard there and the prince 3 cells to the left), a frozen clock and random numbers; returns
# the figure's place on the page
SHOW = r'''([who,rs])=>{const H=__HK,o=window.__O,P=H.P;let T=1e6;H.setClock(()=>T);let a=12345;Math.random=()=>{a=(a*16807)%2147483647;return a/2147483647;};
  P.inv=1e9;P.state='stand';P.face=1;P.x=o.x;P.y=o.y;
  if(who==='G'){const g=H.G.find(e=>e.alive&&!e.gone);if(!g)return null;P.x=o.x-96;g.x=o.x;g.y=o.y;g.face=-1;g.state='idle';for(const e of H.G)if(e!==g)e.x=-9999;}
  else for(const e of H.G)e.x=-9999;
  H.cam.x=o.x-H.viewW/2;H.cam.y=o.y-64*2.2;H.cam.gy=H.cam.y;H.mode='play';if(H.GLP){H.GLP.pipe=false;H.GLP.rs=rs;}
  for(let i=0;i<4;i++){a=12345;H.render();}const X=H.XF,cv=[...document.querySelectorAll('canvas')].find(c=>c.getBoundingClientRect().width>0),R=cv.getBoundingClientRect();
  return [R.left+(o.x*X.VZ-X.camD)/cv.width*R.width,R.top+((o.y-34)*X.VZ-X.camDY)/cv.height*R.height];}'''
SPOTS = [  # (title, floor, skip, kind, side, who)
    ('Floor 7, an open arch beside a raised block (the owner\'s photo)', 7, 1, 'arch', 'block', 'P'),
    ('Floor 7, a guard in front of an open arch (the prince to the left)', 7, 0, 'arch', 'open', 'G'),
    ('Floor 23 at night, an open arch', 23, 0, 'arch', 'open', 'P'),
    ('Floor 14 at dusk, an open arch', 14, 0, 'arch', 'open', 'P'),
]
MODES = [('Torchlight', 'torch', 1), ('Torchlight GLP.rs .5', 'torch', 0.5), ('Classic', 'classic', 1)]
CW, CH = 360, 300   # crop of the canvas at 1:1
ZW, ZH = 120, 100   # the 3x crop


def old_src(tmp):
    if OLD:
        return os.path.abspath(OLD)
    fn = os.path.join(tmp, '_r25f.html')
    open(fn, 'w', encoding='utf-8').write(subprocess.run(['git', 'show', '7de72e9:dev/hourglass-keep.html'], cwd=HERE, capture_output=True, text=True, check=True).stdout)
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


def shot(pg, spot, rs):
    _, n, skip, kind, side, who = spot
    q = pg.evaluate(FIND, [n, skip, kind, side, who])
    if not q:
        return None, None
    xy = pg.evaluate(SHOW, [who, rs])
    if not xy:
        return None, None
    im = Image.open(io.BytesIO(pg.screenshot())).convert('RGB')
    cx, cy = xy[0] * 2, xy[1] * 2
    x0 = int(min(max(0, cx - CW / 2), im.width - CW)); y0 = int(min(max(0, cy - CH * 0.55), im.height - CH))
    full = im.crop((x0, y0, x0 + CW, y0 + CH))
    zx = int(cx - ZW / 2); zy = int(cy - ZH * 0.5)
    zoom = im.crop((zx, zy, zx + ZW, zy + ZH)).resize((ZW * 3, ZH * 3), Image.NEAREST)
    return q, (full, zoom)


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
        pages = {(t, m): page(b, s, m) for t, s in srcs.items() for m in ('torch', 'classic')}
        for spot in SPOTS:
            cells = []
            for (mt, m, rs) in MODES:
                for t in ('before', 'after'):
                    q, r = shot(pages[(t, m)], spot, rs)
                    if not r:
                        print('no case', spot); break
                    label(r[0], '%s, %s' % (mt, t)); label(r[1], '%s, %s, 3x' % (mt, t))
                    cells.append(r)
            if len(cells) != 6:
                continue
            print('spot', spot[0], q, flush=True)
            W = 6 * CW + 5 * 4 + 3 * 8
            row = Image.new('RGB', (W, 22 + CH + 4 + ZH * 3), INK)
            ImageDraw.Draw(row).text((6, 5), '%s (floor %d, seed %d, %s)' % (spot[0], q[0], q[1], q[2]), fill=(250, 240, 215))
            x = 0
            for i, (full, zoom) in enumerate(cells):
                row.paste(full, (x, 22)); row.paste(zoom.crop((0, 0, CW, ZH * 3)) if ZW * 3 > CW else zoom, (x, 22 + CH + 4))
                x += CW + (4 if i % 2 == 0 else 12)
            rows.append(row)
        for k, pg in pages.items():
            if pg.errs:
                print('errors', k, pg.errs[:3])
        b.close()
    H = sum(r.height for r in rows) + 8 * (len(rows) - 1)
    sheet = Image.new('RGB', (max(r.width for r in rows), H), (250, 246, 238))
    y = 0
    for r in rows:
        sheet.paste(r, (0, y)); y += r.height + 8
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    sheet.save(OUT)
    print('wrote', OUT, sheet.size)
