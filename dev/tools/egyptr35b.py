# egyptr35b.py [new.html] [old.html]: round 35b's picture (owner after v80, Torchlight, floor 17, the Green Hall of Osiris: "light beam through
# sand" and "light beam in front of the saws"), into egypt_themes/r35b_beams.png. Frozen frames (clock fixed, GLP.pipe off, four renders),
# v80 | round 35b, Torchlight and Classic:
#   1. a sand well whose pit has a breach in its back wall (floor 17 seed 19): v80 laid the breach's lit rim, its haze and footprint on the
#      sand's face, halfway down the column (the owner's screenshot); now the sand's face takes no beam light, like a wall's front face;
#   2. a well with an open arch behind its pit (floor 17 seed 37): the arch's edge and sill lit on the sand;
#   3. a saw rising out of its slot in a footprint (floor 17 seed 35), 3x: the footprint was added over the blade and the slot; now it lands
#      only on the floor as the scene shows it (Torchlight: the scene's alpha, fpGate; Classic: the standing things cut out, ryStandCut).
# old.html defaults to v80 (git cd72a27), else hk_v80_release.html. Run from dev/tools.
import io, os, sys, subprocess, tempfile
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
NEW = os.path.abspath(a[0] if a else os.path.join(HERE, '..', 'hourglass-keep.html'))
OUT = os.path.join(HERE, 'egypt_themes', 'r35b_beams.png')
INK, TXT, HDR = (20, 16, 24), (250, 240, 215), (255, 210, 140)


def old_src():
    if len(a) > 1:
        return os.path.abspath(a[1])
    try:
        s = subprocess.run(['git', 'show', 'cd72a27:dev/hourglass-keep.html'], cwd=HERE, capture_output=True, check=True).stdout
        p = os.path.join(tempfile.mkdtemp(prefix='r35b_'), 'v80.html'); open(p, 'wb').write(s); return p
    except Exception:
        return os.path.join(HERE, 'hk_v80_release.html')


OLD = old_src()
# (floor, seed, camera centre x, y, world crop box, scale of the crop, title)
CASES = [(17, 19, 4790, 4395, (4655, 4300, 4925, 4490), 1, 'sand well, a breach in its pit\'s back wall (floor 17 seed 19)'),
         (17, 37, 7160, 3790, (7040, 3696, 7290, 3884), 1, 'sand well, an open arch behind its pit (floor 17 seed 37)'),
         (17, 35, 7296, 4092, (7238, 4068, 7352, 4100), 3, 'a saw in a footprint (floor 17 seed 35), 3x')]
SHOW = r'''([n,sd,x,y])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS)H.S.hints[id]=1;H.load(n,sd,true);H.banner=null;const P=H.P;P.inv=1e9;
  P.x=x+400;P.y=Math.floor(y/64)*64+60;P.state='stand';P.face=1;H.cam.x=x-H.viewW/2;H.cam.y=y-96;H.cam.gy=H.cam.y;
  H.mode='play';H.GLP.pipe=false;H.GLP.rs=1;H.GLP.inSession=true;window.__HKnoauto=true;for(let i=0;i<4;i++)H.render();const X=H.XF;return [X.VZ,X.camD,X.camDY];}'''


def shot(b, src, mode, c):
    pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=2)
    pg.set_default_timeout(300000)
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://' + src); pg.wait_for_timeout(500)
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.body.classList.remove('panelOpen')")
    pg.evaluate("m=>{__HK.S.set.lightMode=m;__HK.setClock(()=>12345.6);}", mode)
    VZ, cd, cdy = pg.evaluate(SHOW, list(c[:4]))
    im = Image.open(io.BytesIO(pg.screenshot())).convert('RGB')
    pg.close()
    x0, y0, x1, y1 = c[4]
    box = tuple(int(round(v)) for v in (x0 * VZ - cd, y0 * VZ - cdy, x1 * VZ - cd, y1 * VZ - cdy))
    cr = im.crop(box)
    k = c[5] * 0.5 if c[5] > 1 else 0.5
    cr = cr.resize((int(cr.width * k), int(cr.height * k)), Image.LANCZOS if c[5] == 1 else Image.NEAREST)
    return cr, errs


def label(im, t):
    d = ImageDraw.Draw(im); d.rectangle((0, 0, 6 * len(t) + 8, 13), fill=(0, 0, 0)); d.text((4, 1), t, fill=TXT); return im


if __name__ == '__main__':
    rows, errs = [], []
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
        for c in CASES:
            cells = []
            for mode in ('torch', 'classic'):
                for tag, src in (('v80', OLD), ('round 35b', NEW)):
                    im, e = shot(b, src, mode, c); errs += e
                    cells.append(label(im, '%s, %s' % (tag, 'Torchlight' if mode == 'torch' else 'Classic')))
            w = sum(x.width for x in cells) + 6 * (len(cells) - 1); h = max(x.height for x in cells) + 18
            r = Image.new('RGB', (w, h), INK); ImageDraw.Draw(r).text((4, 2), c[6], fill=HDR)
            x = 0
            for cl in cells:
                r.paste(cl, (x, 18)); x += cl.width + 6
            rows.append(r)
        b.close()
    W = max(r.width for r in rows) + 12
    notes = ['Round 35b (owner after v80): the sky beams. Sand (a well\'s body, a sand lift\'s column) stands in front of the room\'s depth like a',
             'wall\'s front face: no haze, rim, pane or footprint on it (sandSegs; Torchlight u_sd, Classic cut with the walls); the mist and wall looks keep off it too.',
             'The footprint is light on the floor\'s top face: things drawn live on it (a saw and its slot, stakes, a flask, a fallen block) are not lit by it.']
    hd = Image.new('RGB', (W, 14 * len(notes) + 8), INK)
    for i, t in enumerate(notes):
        ImageDraw.Draw(hd).text((6, 4 + 14 * i), t, fill=TXT)
    sheet = Image.new('RGB', (W, hd.height + sum(r.height + 8 for r in rows)), INK)
    sheet.paste(hd, (0, 0)); y = hd.height
    for r in rows:
        sheet.paste(r, (6, y)); y += r.height + 8
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    sheet.save(OUT)
    print('errors', errs[:3])
    print('wrote', OUT)
