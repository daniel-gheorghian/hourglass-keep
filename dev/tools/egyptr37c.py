# egyptr37c.py [new.html] [old.html]: round 37c's picture (owner after v81, iPhone screenshot: "The timer checkpoint over the front wall"), into
# egypt_themes/r37c_checkpoint.png. The water clock (the checkpoint) in the cell before a wall stood with its right half over the wall's front face,
# which stands HX nearer and HX to the left of its cell; one after a wall spilled its halo on that wall's face. Scenes: one like the owner's (a warm palace
# theme, a wall on the right), others with the wall on the right, one with a wall on the left. Rows: per scene, Torchlight and Classic; columns:
# v81 | round 37c, each a 3x crop round the clock (lit, its halo on). old.html defaults to v81's source (git: the commit 'v81: ...'). Run from dev/tools.
import io, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
NEW = os.path.abspath(a[0] if a else os.path.join(HERE, '..', 'hourglass-keep.html'))
OLD = a[1] if len(a) > 1 else None
OUT = os.path.join(HERE, 'egypt_themes', 'r37c_checkpoint.png')
INK, TXT = (20, 16, 24), (250, 240, 215)
# (floor, seed, checkpoint index, what)
SCENES = [(5, 3, 6, "a wall on the right, as in the owner's screenshot"), (2, 1, 0, 'a wall on the right'), (12, 2, 7, 'a wall on the right'),
          (9, 2, 5, 'a wall on the left (its halo)')]
SHOW = r'''([n,seed,i])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS)H.S.hints[id]=1;const L=H.load(n,seed,true);H.banner=null;
  H.clearRooms();const P=H.P;P.inv=1e9;P.x=-999;const q=L.cps[i];for(const o of L.cps)o.on=false;q.on=true;q.onAt=-100;
  H.cam.x=q.x-H.viewW/2;H.cam.y=(q.r+1)*64-64*1.6;H.cam.gy=H.cam.y;H.mode='play';H.GLP&&(H.GLP.pipe=false);H.gameTime=10;
  H.render();H.render();H.render();const X=H.XF,cv=[...document.querySelectorAll('canvas')].find(c=>c.getBoundingClientRect().width>0),R=cv.getBoundingClientRect();
  const wx=q.c*32+16,wy=(q.r+1)*64-30;
  return [R.left+(wx*X.VZ-X.camD)/cv.width*R.width,R.top+(wy*X.VZ-X.camDY)/cv.height*R.height,H.themeName(n),q.c,q.r,X.VZ*R.width/cv.width];}'''


def old_src(tmp):
    if OLD:
        return os.path.abspath(OLD)
    h = subprocess.run(['git', 'log', '--all', '--grep', '^v81:', '-1', '--format=%H'], cwd=HERE, capture_output=True, text=True, check=True).stdout.strip()
    fn = os.path.join(tmp, '_v81.html')
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
    for n, seed, i, _ in SCENES:
        x, y, th, c, r, z = pg.evaluate(SHOW, [n, seed, i])
        im = Image.open(io.BytesIO(pg.screenshot())).convert('RGB'); x, y = x * 2, y * 2
        crop = im.crop((int(x - 34 * z * 2), int(y - 26 * z * 2), int(x + 34 * z * 2), int(y + 18 * z * 2))).resize((68 * 3 * 2, 44 * 3 * 2), Image.LANCZOS)
        out.append((crop, th, c, r))
    if errs:
        print(src, mode, 'errors', errs[:3])
    pg.close()
    return out


if __name__ == '__main__':
    with tempfile.TemporaryDirectory() as tmp, sync_playwright() as p:
        b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
        srcs = [('v81', old_src(tmp)), ('round 37c', NEW)]
        res = {(nm, mode): shots(b, s, mode) for mode in ('torch', 'classic') for nm, s in srcs}
        b.close()
    W, H = 68 * 6, 44 * 6
    sheet = Image.new('RGB', (2 * (W + 8) + 8, len(SCENES) * 2 * (H + 8) + 8 + 22), INK)
    ImageDraw.Draw(sheet).text((8, 6), "round 37c: the water clock keeps clear of the walls' front faces (moved along its cell, cut by them). v81 | round 37c, 3x", fill=TXT)
    y = 30
    for si, sc in enumerate(SCENES):
        for mode in ('torch', 'classic'):
            for col, nm in enumerate(('v81', 'round 37c')):
                crop, th, c, r = res[(nm, mode)][si]
                crop = crop.copy()
                label(crop, '%s, %s: floor %d seed %d %s c%d,%d: %s' % (nm, 'Torchlight' if mode == 'torch' else 'Classic', sc[0], sc[1], th[4:22], c, r, sc[3]))
                sheet.paste(crop, (8 + col * (W + 8), y))
            y += H + 8
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    sheet.save(OUT); print('wrote', OUT)
