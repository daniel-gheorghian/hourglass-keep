# egyptr30.py [new.html] [old.html]: round 30's pictures (owner: "whenever an upper corridor uses sand tiles this happens. Add a rule that a
# corridor above another corridor doesn't use sand tiles, but instead regular tiles"), into egypt_themes/r30_sandcorr.png at 844x390 CSS px
# and DPR 3 (an iPhone in landscape), Torchlight and Classic: the prince on a lower corridor's floor under a run of five cracked slabs (floor 9,
# seed 802, the Blue Chambers, slabs 139-143 on row 16, the corridor on row 18), before (old.html: v76, default hk_v76_release.html here, or
# `git show d11123a:dev/hourglass-keep.html > /tmp/hk_v76.html`) with the
# three inner slabs drawn as a column of sand through his corridor, and after with all five in the corridor look; and a true well (a row of two
# over a walled pit) that stays sand, also before and after. Run from dev/tools.
import io, os, sys
from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
NEW = os.path.abspath(a[0] if a else os.path.join(HERE, '..', 'hourglass-keep.html'))
OLD = os.path.abspath(a[1] if len(a) > 1 else os.path.join(HERE, 'hk_v76_release.html'))
OUT = os.path.join(HERE, 'egypt_themes', 'r30_sandcorr.png')
W, H, DPR, TW = 844, 390, 3, 562
# kind 'corr': the prince at column c on row r's floor; kind 'well': the first row of two over a walled pit on the floor, the prince on the
# slabs' floor two tiles beside it
SHOT = '''([n,sd,mode,kind,c,r])=>{const H=__HK;window.__HKfreeze=true;window.__HKnoauto=true;H.S.set.lightMode=mode;H.EGP.traps=true;
  document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay');
  for(const id in H.HINTS)H.S.hints[id]=1;for(const id of H.HINT_MOVE)H.S.learned[id]=1;const L=H.load(n,sd,true);H.banner=null;let info='';
  if(kind==='well'){let g=null;for(const o of L.dyn){if(o.f.t!=='loose'||o.f.plank)continue;const q=H.wellGroup(o);if(q&&q.n===2){g=q;break;}}
    if(!g)return null;r=g.r;c=g.c0-2;if(!H.solidBelow(c,r))c=g.c0+3;info='well at column '+g.c0+', row '+g.r;}
  const P=H.P,put=()=>{P.x=c*32+16;P.y=(r+1)*64-4;P.fallY=P.y;P.state='stand';P.inv=1e9;P.face=1;P.vx=P.vy=0;};
  put();H.mode='play';H.cam.snap=true;H.tick(1/60);put();H.cam.snap=true;for(let i=0;i<3;i++)H.render();
  let w=0;for(const o of L.dyn)if(o.f.t==='loose'&&!o.f.plank&&H.looseWell(o))w++;return {theme:L.theme.name,info,wells:w};}'''
SHOTS = [  # (label, html, floor, seed, mode, kind, c, r)
    ('before (v76): sand through his corridor', 'old', 9, 802, 'torch', 'corr', 141, 18),
    ('after: the corridor look (regular tiles)', 'new', 9, 802, 'torch', 'corr', 141, 18),
    ('before (v76), Classic', 'old', 9, 802, 'classic', 'corr', 141, 18),
    ('after, Classic', 'new', 9, 802, 'classic', 'corr', 141, 18),
    ('before (v76): the slabs above, on row 16', 'old', 9, 802, 'torch', 'corr', 137, 16),
    ('after: the slabs above, on row 16', 'new', 9, 802, 'torch', 'corr', 137, 16),
    ('a true well before (v76)', 'old', 9, 802, 'torch', 'well', 0, 0),
    ('a true well after: unchanged', 'new', 9, 802, 'torch', 'well', 0, 0),
]

def font(sz):
    for f in ['/System/Library/Fonts/Supplemental/Arial.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']:
        if os.path.exists(f):
            return ImageFont.truetype(f, sz)
    return ImageFont.load_default()

def shoot(which, html):
    out = {}
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
        pg = b.new_page(viewport={'width': W, 'height': H}, device_scale_factor=DPR)
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto('file://' + html); pg.wait_for_timeout(600)
        for i, (lab, h, n, sd, mode, kind, c, r) in enumerate(SHOTS):
            if h != which: continue
            info = pg.evaluate(SHOT, [n, sd, mode, kind, c, r])
            im = Image.open(io.BytesIO(pg.screenshot())).convert('RGB')
            sub = 'floor %d seed %d, %s, %s%s' % (n, sd, info['theme'] if info else '?', 'Torchlight' if mode == 'torch' else 'Classic',
                                                  (', ' + info['info']) if info and info['info'] else '')
            out[i] = (lab, sub, im)
        b.close()
        if errs:
            print('page errors', errs[:3])
    return out

frames = shoot('new', NEW)
if os.path.exists(OLD):
    frames.update(shoot('old', OLD))
frames = [frames[i] for i in sorted(frames)]
cols, f, f2, pad, lh = 2, font(19), font(14), 12, 50
th = TW * H // W
rows = (len(frames) + cols - 1) // cols
sheet = Image.new('RGB', (cols * (TW + pad) + pad, rows * (th + lh + pad) + pad), (20, 16, 24))
d = ImageDraw.Draw(sheet)
for i, (lab, sub, im) in enumerate(frames):
    x, y = pad + (i % cols) * (TW + pad), pad + (i // cols) * (th + lh + pad)
    d.text((x, y + 4), lab, fill=(250, 240, 215), font=f)
    d.text((x, y + 28), sub, fill=(190, 180, 160), font=f2)
    sheet.paste(im.resize((TW, th), Image.LANCZOS), (x, y + lh))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
sheet.save(OUT)
print('wrote', OUT)
