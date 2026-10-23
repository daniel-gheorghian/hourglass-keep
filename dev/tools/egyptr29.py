# egyptr29.py [new.html] [old.html]: round 29's pictures (owner: "instead of a sandstorm I want a storm of darkness ... think of Anubis";
# "100% black opaque, like rips in the scene, and on that background the eyes, the jackal"; the granite plug dropped; "the shadow being
# pulled back is a great idea"), into egypt_themes/r29_dark.png: the chase on a few floors at 844x390 CSS px and DPR 3 (an iPhone in
# landscape), Torchlight and Classic: the rip opening from a crack as it wakes, the jackal coming out at the wake and when the dark is
# within two tiles, the eyes in the dark, his shadow pulled back toward it, dawn's tatters and the holes burning through it at the arch;
# and old.html's chase (the v75 plug) for comparison when it is given or hk_v75_release.html is here. Run from dev/tools.
import io, os, sys
from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
NEW = os.path.abspath(a[0] if a else os.path.join(HERE, '..', 'hourglass-keep.html'))
OLD = os.path.abspath(a[1] if len(a) > 1 else os.path.join(HERE, 'hk_v75_release.html'))
OUT = os.path.join(HERE, 'egypt_themes', 'r29_dark.png')
W, H, DPR, TW = 844, 390, 3, 562   # (each frame shown at TW px wide)
SETUP = '''([n,mode])=>{const H=__HK;window.__HKfreeze=true;window.__HKnoauto=true;H.S.set.lightMode=mode;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);
  document.getElementById('app').classList.add('overlay');for(const id in H.HINTS)H.S.hints[id]=1;for(const id of H.HINT_MOVE)H.S.learned[id]=1;
  for(let s=9100;s<9140;s++){const L=H.load(n,s,true);H.banner=null;const c=L.ext.chase;if(!c)continue;let sp=null;
    for(let cc=c.c0+8;cc<c.c1-4&&!sp;cc++)for(let r=c.rTop;r<=c.rBot;r++){let ok=true;for(let k=0;k<6;k++)ok=ok&&H.solidBelow(cc-k,r);if(ok){sp={x:cc*32+16,r};break;}}
    if(!sp)continue;window.__sp=sp;return {seed:s,theme:L.theme.name};}return null;}'''
# the prince standing on a chase row, the dark lead px behind him at chase time t; dt >= 0: dawn's burst dt s after he passes the arch;
# eyes: tick on until a pair of eyes is open on the screen
STEP = '''([lead,t,dt,eyes])=>{const H=__HK,P=H.P,c=H.L.ext.chase,sp=window.__sp,put=()=>{P.x=sp.x;P.y=(sp.r+1)*64-4;P.fallY=P.y;P.state='stand';P.inv=1e9;P.face=1;P.vx=P.vy=0;};
  put();H.mode='play';c.on=true;c.done=false;c.diss=null;c.fade=0;c.t=t;c.wx=P.x-lead;H.cam.snap=true;H.tick(1/60);put();c.wx=P.x-lead;c.t=t;
  if(eyes&&H.dkLook){for(let k=0;k<900;k++){const K=H.dkLook(c,c.wx);if(K.ey.some(e=>e[2]>0.9&&Math.abs(e[1]-P.y+40)<70))break;H.tick(1/60);put();c.wx=P.x-lead;c.t=t;}}
  if(dt>=0){c.done=true;c.diss={t:0,x0:c.wx,tx:P.x+40,bx:c.wx,ts:Math.max(0.45,Math.min(0.95,(P.x+40-c.wx)/460))};let k=0;while(c.diss.t<dt&&k<400){H.tick(1/60);k++;put();}}
  H.cam.snap=true;for(let i=0;i<3;i++)H.render();return true;}'''
SHOTS = [  # (label, floor, mode, lead, t, dt, eyes)
    ('wakes: the rip opens from a crack (t .12 s)', 12, 'torch', 128, 0.12, -1, 0),
    ('the jackal comes out as it wakes (t 1.2 s)', 12, 'torch', 128, 1.2, -1, 0),
    ('within two tiles: the jackal over his head', 16, 'torch', 60, 5, -1, 0),
    ('eyes open in the dark', 22, 'torch', 150, 5, -1, 1),
    ('his shadow pulled back toward it (120 px)', 22, 'torch', 120, 5, -1, 0),
    ('dawn at the arch: tatters part round him', 12, 'torch', 100, 5, 0.3, 0),
    ('dawn burns holes through it', 12, 'torch', 100, 5, 0.8, 0),
    ('Classic: the jackal, two tiles', 12, 'classic', 60, 5, -1, 0),
    ('Classic: the shadow (120 px)', 16, 'classic', 120, 5, -1, 0),
    ('Classic: dawn burns holes through it', 12, 'classic', 100, 5, 0.8, 0),
]

def font(sz):
    for f in ['/System/Library/Fonts/Supplemental/Arial.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']:
        if os.path.exists(f):
            return ImageFont.truetype(f, sz)
    return ImageFont.load_default()

def shoot(html, shots):
    out = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
        pg = b.new_page(viewport={'width': W, 'height': H}, device_scale_factor=DPR)
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto('file://' + html); pg.wait_for_timeout(600)
        for lab, n, mode, lead, t, dt, eyes in shots:
            info = pg.evaluate(SETUP, [n, mode])
            pg.evaluate(STEP, [lead, t, dt, eyes])
            im = Image.open(io.BytesIO(pg.screenshot())).convert('RGB')
            out.append((lab + ' — floor %d, %s' % (n, info['theme'] if info else '?'), im))
        b.close()
        if errs:
            print('page errors', errs[:3])
    return out

frames = shoot(NEW, SHOTS)
if os.path.exists(OLD):
    frames = shoot(OLD, [('before (v75): the granite plug', 16, 'torch', 60, 5, -1, 0)]) + frames
cols, f, pad, lh = 2, font(20), 12, 34
th = TW * H // W
rows = (len(frames) + cols - 1) // cols
sheet = Image.new('RGB', (cols * (TW + pad) + pad, rows * (th + lh + pad) + pad), (20, 16, 24))
d = ImageDraw.Draw(sheet)
for i, (lab, im) in enumerate(frames):
    x, y = pad + (i % cols) * (TW + pad), pad + (i // cols) * (th + lh + pad)
    d.text((x, y + 6), lab, fill=(250, 240, 215), font=f)
    sheet.paste(im.resize((TW, th), Image.LANCZOS), (x, y + lh))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
sheet.save(OUT)
print(OUT)
