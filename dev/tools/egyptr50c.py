# egyptr50c.py old.html new.html [outdir]: round 50c's death card at phone size (852x393), both modes: old (v90) | new (round 50c, D2 "ash"),
# floors 7, 22 and 38 seed 1, the prince dead after a fall, 0.6 s (the fade) and 2.4 s (the control line shown) after the death.
# Writes r50c_death.png. Run: source .venv/bin/activate; python3 egyptr50c.py hk_v90_release.html ../hourglass-keep.html [outdir]
import io, os, sys
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
OLD = os.path.abspath(a[0] if len(a) > 0 else os.path.join(HERE, 'hk_v90_release.html'))
NEW = os.path.abspath(a[1] if len(a) > 1 else os.path.join(HERE, '..', 'hourglass-keep.html'))
OUT = a[2] if len(a) > 2 else HERE
GPU = [] if os.environ.get('HK_GPU') == '0' else ['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist', '--force_high_performance_gpu']
SCENES = [(7, 1), (22, 1), (38, 1)]
W, H = 852, 393

SETUP = r'''([n,sd,mode])=>{const H=__HK;window.__HKfreeze=true;H.S.set.lightMode=mode;H.load(n,sd,false);H.banner=null;const P=H.P;
  H.cam.x=P.x-H.viewW/2;H.cam.y=P.y-192*0.62;if(H.GLP){H.GLP.pipe=false;H.GLP.rs=1;window.__HKnoauto=true;}
  H.die('fall');return H.themeName(n);}'''
STEP = r'''(n)=>{const H=__HK;H.tick(n);H.cam.x=H.P.x-H.viewW/2;for(let i=0;i<3;i++){if(H.GLP)H.GLP.hudK='r50c'+Math.random();H.render();}return 1;}'''


def label(im, t):
    d = ImageDraw.Draw(im); d.rectangle((0, H - 13, 6 + 6 * len(t), H), fill=(0, 0, 0)); d.text((3, H - 13), t, fill=(250, 240, 215))


if __name__ == '__main__':
    errs = []; rows = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=GPU)
        pages = {}
        for tag, src in (('v90', OLD), ('50c', NEW)):
            pg = b.new_page(viewport={'width': W, 'height': H}, device_scale_factor=2); pg.on('pageerror', lambda e: errs.append(str(e)))
            pg.goto('file://' + src); pg.wait_for_timeout(1200)
            pg.evaluate("()=>{document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.body.classList.remove('panelOpen');const st=document.createElement('style');st.textContent='.ctl,#pad{opacity:0!important}';document.head.appendChild(st);}")
            pages[tag] = pg
        for n, sd in SCENES:
            for mode in ('torch', 'classic'):
                for dt in (0.6, 2.4):
                    row = []
                    for tag in ('v90', '50c'):
                        pg = pages[tag]; th = pg.evaluate(SETUP, [n, sd, mode]); pg.evaluate(STEP, int(round(dt * 60)))
                        im = Image.open(io.BytesIO(pg.screenshot())).convert('RGB').resize((W, H), Image.LANCZOS)
                        label(im, '%s  floor %d %s  %s  %.1f s after' % (tag, n, th, mode, dt)); row.append(im)
                    rows.append(row)
        b.close()
    sh = Image.new('RGB', (2 * (W + 6), len(rows) * (H + 6)), (20, 16, 24))
    for i, r in enumerate(rows):
        for j, im in enumerate(r): sh.paste(im, (j * (W + 6), i * (H + 6)))
    sh.save(os.path.join(OUT, 'r50c_death.png')); print('wrote', os.path.join(OUT, 'r50c_death.png'))
    if errs: print('page errors', errs[:4])
