# egyptr35c.py [new.html] [old.html]: round 35c's picture (owner after v80, iPhone screenshot: "wall decorations over the tiles"), into
# egypt_themes/r35c_wallart.png. The owner's place: The Green Hall of Osiris, a cracked slab at the end of a ledge over a lower corridor (floor 18,
# seed 4418, cell 201,11), and a closer and a plate on the same floor (119,30 and 122,30). Rows: Torchlight, Classic; columns: old | new, each the
# view at the phone's resolution (852x393 CSS px at 2x, a 1:1 crop of the canvas) and a 4x crop of the tile. Torchlight's relief read the room's
# picture, which has the wall's posts, bands and frieze and no slab under a tile drawn live, and embossed them on its top and lip; the cracked
# slab's own lip crack was a lone '>' that read as one of the wall's chevrons. old.html defaults to v80's source (git: the commit 'v80: ...').
# Run from dev/tools.
import io, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
NEW = os.path.abspath(a[0] if a else os.path.join(HERE, '..', 'hourglass-keep.html'))
OLD = a[1] if len(a) > 1 else None
OUT = os.path.join(HERE, 'egypt_themes', 'r35c_wallart.png')
INK, TXT = (20, 16, 24), (250, 240, 215)
SCENES = [(18, 4418, 201, 11, 4, 66, 'cracked slab at a ledge (the owner\'s)'), (18, 4418, 119, 30, 10, 64, 'a closer, a plate beyond')]
SHOW = r'''([n,seed,c,r,wx,wy])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS)H.S.hints[id]=1;const L=H.load(n,seed,true);H.banner=null;
  H.clearRooms();const P=H.P;P.inv=1e9;P.x=-999;H.cam.x=c*32+16-H.viewW/2;H.cam.y=(r+1)*64-64*1.6;H.cam.gy=H.cam.y;H.mode='play';H.GLP&&(H.GLP.pipe=false);H.gameTime=10;
  H.render();H.render();H.render();const X=H.XF,cv=[...document.querySelectorAll('canvas')].find(c=>c.getBoundingClientRect().width>0),R=cv.getBoundingClientRect();
  return [R.left+((c*32+wx)*X.VZ-X.camD)/cv.width*R.width,R.top+((r*64+wy)*X.VZ-X.camDY)/cv.height*R.height,H.themeName(n)];}'''


def old_src(tmp):
    if OLD:
        return os.path.abspath(OLD)
    h = subprocess.run(['git', 'log', '--all', '--grep', '^v80:', '-1', '--format=%H'], cwd=HERE, capture_output=True, text=True, check=True).stdout.strip()
    fn = os.path.join(tmp, '_v80.html')
    open(fn, 'w', encoding='utf-8').write(subprocess.run(['git', 'show', h + ':dev/hourglass-keep.html'], cwd=HERE, capture_output=True, text=True, check=True).stdout)
    return fn


def label(im, t):
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 8 + 6 * len(t), 13), fill=(0, 0, 0))
    d.text((4, 1), t, fill=TXT)


def shots(b, src, mode):
    pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=2)
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://' + src); pg.wait_for_timeout(700)
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.body.classList.remove('panelOpen')")
    pg.evaluate("m=>{__HK.S.set.lightMode=m;}", mode)
    out = []
    for n, seed, c, r, wx, wy, _ in SCENES:
        x, y, th = pg.evaluate(SHOW, [n, seed, c, r, wx, wy])
        im = Image.open(io.BytesIO(pg.screenshot())).convert('RGB'); x, y = int(x * 2), int(y * 2)
        wide = im.crop((x - 260, y - 190, x + 260, y + 130))
        zoom = im.crop((x - 50, y - 40, x + 80, y + 40)).resize((520, 320), Image.LANCZOS)
        out.append((wide, zoom, th))
    if errs:
        print(src, mode, 'errors', errs[:3])
    pg.close()
    return out


if __name__ == '__main__':
    with tempfile.TemporaryDirectory() as tmp, sync_playwright() as p:
        b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
        srcs = [('v80', old_src(tmp)), ('round 35c', NEW)]
        rows = []
        for mode in ('torch', 'classic'):
            rows.append([(nm, mode, shots(b, s, mode)) for nm, s in srcs])
        b.close()
    W, H = 520, 320
    sheet = Image.new('RGB', (2 * (W + 8) + 8, len(SCENES) * 2 * (2 * H + 8) + 8 + 22), INK)
    ImageDraw.Draw(sheet).text((8, 6), 'round 35c: wall art over the floor tiles (Torchlight relief over live tiles; the cracked slab\'s lip crack). v80 | round 35c', fill=TXT)
    y = 30
    for si, sc in enumerate(SCENES):
        for row in rows:
            for col, (nm, mode, out) in enumerate(row):
                wide, zoom, th = out[si]
                wide = wide.copy(); zoom = zoom.copy()
                label(wide, '%s, %s: floor %d %s, %s' % (nm, 'Torchlight' if mode == 'torch' else 'Classic', sc[0], th[:26], sc[6]))
                label(zoom, '%s %s, 4x' % (nm, mode))
                sheet.paste(wide, (8 + col * (W + 8), y)); sheet.paste(zoom, (8 + col * (W + 8), y + H + 4))
            y += 2 * H + 8
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    sheet.save(OUT); print('wrote', OUT)
