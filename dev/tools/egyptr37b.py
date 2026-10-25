# egyptr37b.py [new.html] [old.html]: round 37b's pictures (owner after v81, iPhone screenshot, The Blue Chambers in Torchlight: "The shadow of
# the prince over the guillotine jaws. Also the guillotine jaws needs to look more metallic"), into egypt_themes/r37b_jaws.png and r37b_jaws.gif.
# The owner's case: floor 9 seed 2, the slicer at cell 22,15 with a lamp two columns left of it and the prince between them, so his lamp shadow
# (glShadow) is cast to his right across the jaws. Top: that view at the phone's resolution (852x393 CSS px at 2x), v81 | round 37b, Torchlight
# and Classic, each with a 3x crop of the jaws. Below, one row a theme and hour (and one with EGP.traps off, the v61 looks: steel), 3x crops:
# v81 shut | 37b shut, closing, open, in Torchlight, then the same in Classic. The gif: one slice cycle in the owner's case, Torchlight, 37b.
# old.html defaults to v81's source (git: the commit 'v81: ...'). Run from dev/tools (software WebGL: a few minutes).
import io, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
NEW = os.path.abspath(a[0] if a else os.path.join(HERE, '..', 'hourglass-keep.html'))
OLD = a[1] if len(a) > 1 else None
OUTP = os.path.join(HERE, 'egypt_themes', 'r37b_jaws.png')
OUTG = os.path.join(HERE, 'egypt_themes', 'r37b_jaws.gif')
INK, TXT = (20, 16, 24), (250, 240, 215)
OWNER = (9, 2, 22, 15, 21)  # floor, seed, slicer cell c, r, the prince's column
CASES = [(9, 2, 22, 15, 21, 1, 'Blue Chambers (owner)'), (5, 1, 201, 8, 202, 1, 'Halls of the West'), (36, 3, 203, 69, 202, 1, 'Forges of Meroe'),
         (24, 3, 282, 66, 281, 1, 'Foggaras of Garama'), (29, 1, 48, 17, 47, 1, 'Well Corridors'), (40, 3, 275, 66, 276, 1, 'Green Hall of Osiris'),
         (9, 2, 22, 15, 21, 0, 'Blue Chambers, EGP.traps off')]
SETUP = r'''([n,seed,c,r,pc,egp])=>{const H=__HK;window.__HKfreeze=true;window.__HKnoauto=true;for(const id in H.HINTS)H.S.hints[id]=1;for(const id of H.HINT_MOVE)H.S.learned[id]=1;
  let a=seed;Math.random=()=>{a=(a*16807)%2147483647;return a/2147483647;};H.EGP.traps=!!egp;
  const L=H.load(n,seed,true);H.banner=null;const P=H.P,x=pc*32+16,y=(r+1)*64-4;P.inv=1e9;H.cam.snap=true;H.mode='play';
  for(let i=0;i<40;i++){P.x=x;P.y=y;P.fallY=y;P.state='stand';P.vx=0;P.vy=0;P.face=x<c*32+16?1:-1;H.tick(1);}
  window.__JO=L.dyn.find(o=>o.f.t==='chomp'&&o.c===c&&o.r===r);H.GLP&&(H.GLP.pipe=false);
  H.cam.x=c*32+16-H.viewW/2;H.cam.y=(r+1)*64-64*1.6;H.cam.gy=H.cam.y;return H.themeName(n);}'''
# p: the phase of the slicer's cycle (closing over 0..0.07, shut to 0.15, opening to 0.3, open after)
FRAME = r'''([p,mode,warm])=>{const H=__HK,f=__JO.f,c=__JO.c,r=__JO.r;f.off=((p*f.per-H.gameTime)%f.per+f.per)%f.per;H.S.set.lightMode=mode;
  for(let i=0;i<warm;i++)H.render();const X=H.XF,cv=[...document.querySelectorAll('canvas')].find(c=>c.getBoundingClientRect().width>0),R=cv.getBoundingClientRect();
  return [R.left+((c*32+16)*X.VZ-X.camD)/cv.width*R.width,R.top+((r*64+32)*X.VZ-X.camDY)/cv.height*R.height];}'''
STATES = [(0.1, 'shut'), (0.035, 'closing'), (0.5, 'open')]


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
    return im


class Page:
    def __init__(self, b, src):
        self.pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=2)
        self.errs = []; self.pg.on('pageerror', lambda e: self.errs.append(str(e)))
        self.pg.goto('file://' + src); self.pg.wait_for_timeout(700)
        self.pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.body.classList.remove('panelOpen')")

    def setup(self, case):
        return self.pg.evaluate(SETUP, list(case[:6]))

    def shot(self, p, mode, warm=14):
        x, y = self.pg.evaluate(FRAME, [p, mode, warm])
        return Image.open(io.BytesIO(self.pg.screenshot())).convert('RGB'), int(x * 2), int(y * 2)


def crop3(im, x, y):  # the jaws at 3x CSS px (the screenshot is 2x)
    return im.crop((x - 60, y - 80, x + 60, y + 72)).resize((180, 228), Image.LANCZOS)


if __name__ == '__main__':
    with tempfile.TemporaryDirectory() as tmp, sync_playwright() as pw:
        b = pw.chromium.launch()
        pages = [('v81', Page(b, old_src(tmp))), ('round 37b', Page(b, NEW))]
        top, rows, gif = [], [], []
        for mode in ('torch', 'classic'):
            for nm, pg in pages:
                pg.setup(CASES[0]); im, x, y = pg.shot(0.1, mode)
                top.append((nm, mode, im.crop((x - 420, y - 200, x + 180, y + 140)), crop3(im, x, y)))
        for case in CASES:
            row = []
            for mode in ('torch', 'classic'):
                for nm, pg in pages:
                    th = pg.setup(case)
                    for i, (p, sn) in enumerate(STATES if nm != 'v81' else STATES[:1]):
                        im, x, y = pg.shot(p, mode, 14 if i == 0 else 4)
                        row.append(label(crop3(im, x, y), '%s %s %s' % ('v81' if nm == 'v81' else '37b', 'T' if mode == 'torch' else 'C', sn)))
            rows.append((case[6] + ' (' + th + ')', row))
        pg = pages[1][1]; pg.setup(CASES[0]); pg.shot(0.5, 'torch')
        for i in range(30):
            im, x, y = pg.shot(i / 30, 'torch', 2)
            gif.append(im.crop((x - 300, y - 170, x + 150, y + 120)).resize((450, 290), Image.LANCZOS))
        for nm, p in pages:
            if p.errs:
                print(nm, 'errors', p.errs[:3])
        per = pg.pg.evaluate('__JO.f.per')
        b.close()
    W = 600 + 8 + 180
    sheet = Image.new('RGB', (max(2 * (W + 8) + 8, 8 + 8 * 188), 30 + 2 * 348 + 8 + len(rows) * 252 + 8), INK)
    ImageDraw.Draw(sheet).text((8, 8), "round 37b: the slicer's jaws (no lamp shadow on them; bronze, opaque, a honed bevel, riveted spine). v81 | round 37b; T Torchlight, C Classic; crops 3x", fill=TXT)
    y = 30
    for i, (nm, mode, wide, z) in enumerate(top):
        col = i % 2; yy = y + (i // 2) * 348
        sheet.paste(label(wide.copy(), '%s, %s: floor 9 seed 2, the Blue Chambers (the owner\'s case)' % (nm, 'Torchlight' if mode == 'torch' else 'Classic')), (8 + col * (W + 8), yy))
        sheet.paste(label(z.copy(), nm + ' 3x'), (8 + col * (W + 8) + 608, yy + 40))
    y += 2 * 348 + 8
    for nm, row in rows:
        ImageDraw.Draw(sheet).text((8, y), nm, fill=TXT)
        for j, im in enumerate(row):
            sheet.paste(im, (8 + j * 188, y + 16))
        y += 252
    os.makedirs(os.path.dirname(OUTP), exist_ok=True)
    sheet.save(OUTP); print('wrote', OUTP)
    gif[0].save(OUTG, save_all=True, append_images=gif[1:], duration=int(per / 30 * 1000), loop=0)
    print('wrote', OUTG)
