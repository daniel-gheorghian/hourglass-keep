# egyptr49a.py old.html new.html [outdir]: round 49a's pictures (owner: "drop all hint messages, rely only on subtle graphic hints ...
# I would keep the how to play screen that describes what the buttons do"). Phone size (852 x 393), Classic, old | new:
#   r49a_how.png      the How to play screen
#   r49a_death.png    the death card on spikes (old: with its tip)
#   r49a_glance.gif   a remote plate pressed with its gate out of view: old, the banner; new, the glance toward the gate and back
#   r49a_glance.png   four frames of it (the press, the look, the hold, back)
# Run from dev/tools.
import io, os, sys
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright
a = sys.argv[1:]
OLD, NEW = os.path.abspath(a[0]), os.path.abspath(a[1])
OUT = os.path.abspath(a[2]) if len(a) > 2 else os.path.dirname(os.path.abspath(__file__))
VW, VH = 852, 393
SEED = 5

PREP = r'''([seed])=>{const H=__HK;window.__HKfreeze=true;H.setGameSeed(seed);H.S.set.lightMode='classic';H.S.set.cross=false;for(const id in H.HINTS){H.S.hints[id]=1;if(H.S.learned)H.S.learned[id]=1;}
  document.querySelectorAll('.screen').forEach(e=>e.hidden=true);return 1;}'''
FIND = r'''([lo,hi])=>{const H=__HK,TW=32,S=r=>(r+1)*64-4;
  for(let n=lo;n<=hi;n++){H.startLevel(n,-1);H.mode='play';H.tick(2);const L=H.L;
    for(const o of L.dyn){if(o.f.t!=='plate'||!o.f.where)continue;const g=L.dyn.find(q=>q.f===o.f.g);if(!g)continue;
      if(Math.abs(g.r-o.r)>1||Math.abs(g.c-o.c)<9||Math.abs(g.c-o.c)>13)continue;
      for(const s of [-1,1]){const c=o.c+s;if(L.dyn.some(q=>q.c===c&&q.r===o.r))continue;const P=H.P;P.x=c*TW+16;P.y=S(o.r);P.fallY=P.y;P.state='stand';P.vx=P.vy=0;H.tick(6);
        if(P.state==='stand'&&P.y===S(o.r))return [n,o.c,o.r,s,g.c,g.r];}}}
  return null;}'''
SETUP = r'''([n,c,r,s])=>{const H=__HK,TW=32,S=r=>(r+1)*64-4;H.startLevel(n,-1);H.mode='play';H.intro=0;H.banner=null;for(const e of H.G)e.x=-9999;for(const e of H.SN)e.x=-9999;
  const P=H.P;P.x=(c+s)*TW+16;P.y=S(r);P.fallY=P.y;P.state='stand';P.vx=P.vy=0;P.face=-s;P.inv=1e9;H.cam.snap=true;H.tick(90);H.intro=0;H.banner=null;
  window.__go=c*TW+16;return 1;}'''
STEP = r'''([k])=>{const H=__HK,P=H.P;if(window.__go){P.x=window.__go;window.__go=0;} // onto the plate (one cell)
  H.tick(k);H.intro=0;H.render();return [P.x,H.cam.x,H.banner?H.banner.text:null,H.GLN?H.GLN.t:0,P.state];}'''


def shot(pg):
    return Image.open(io.BytesIO(pg.screenshot())).convert('RGB').resize((VW, VH), Image.LANCZOS)


def label(im, t):
    d = ImageDraw.Draw(im); d.rectangle((0, 0, 8 + 6 * len(t), 13), fill=(0, 0, 0)); d.text((4, 1), t, fill=(250, 240, 215)); return im


def pair(a, b, la, lb, k=1.0):
    w, h = int(VW * k), int(VH * k)
    im = Image.new('RGB', (2 * w + 6, h), (20, 16, 24))
    im.paste(label(a.resize((w, h), Image.LANCZOS), la), (0, 0)); im.paste(label(b.resize((w, h), Image.LANCZOS), lb), (w + 6, 0)); return im


with sync_playwright() as p:
    b = p.chromium.launch()
    pages = {}
    for nm, src in (('old', OLD), ('new', NEW)):
        pg = b.new_page(viewport={'width': VW, 'height': VH}, device_scale_factor=1); errs = []
        pg.on('pageerror', lambda e, errs=errs: errs.append(str(e)))
        pg.goto('file://' + src); pg.wait_for_timeout(600); pg.evaluate(PREP, [SEED]); pages[nm] = (pg, errs)
    # the glance
    case = pages['new'][0].evaluate(FIND, [6, 20]); print('case', case)
    fr = {'old': [], 'new': []}; info = {}
    for nm, (pg, _) in pages.items():
        pg.evaluate(SETUP, case[:4]); xs = []
        for i in range(70):
            q = pg.evaluate(STEP, [3]); xs.append(q); fr[nm].append(shot(pg))
        info[nm] = xs
    print('new cam.x, glance t, state', [(round(q[1]),round(q[3],2),q[4]) for q in info['new']][::4]); print('old banners', sorted(set(q[2] for q in info['old'] if q[2])))
    gif = [pair(o, n, 'v89: the banner', 'round 49a: heard and glanced at', 0.6) for o, n in zip(fr['old'], fr['new'])]
    gif[0].save(os.path.join(OUT, 'r49a_glance.gif'), save_all=True, append_images=gif[1:], duration=50, loop=0)
    picks = [8, 20, 34, 64]
    strip = Image.new('RGB', (gif[0].width, gif[0].height * len(picks)), (0, 0, 0))
    for i, k in enumerate(picks): strip.paste(gif[k], (0, i * gif[0].height))
    strip.save(os.path.join(OUT, 'r49a_glance.png'))
    # How to play
    hw = {}
    for nm, (pg, _) in pages.items():
        pg.evaluate("()=>{document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('how').hidden=false;}"); pg.wait_for_timeout(300); hw[nm] = shot(pg)
        pg.evaluate("()=>{document.getElementById('how').hidden=true;}")
    pair(hw['old'], hw['new'], 'v89 + 48a/48b', 'round 49a').save(os.path.join(OUT, 'r49a_how.png'))
    # the death card on spikes
    dc = {}
    for nm, (pg, _) in pages.items():
        dc[nm] = None
        pg.evaluate(r'''()=>{const H=__HK;H.startLevel(4,-1);H.mode='play';H.intro=0;H.tick(30);H.intro=0;H.banner=null;H.die('spikes');H.tick(110);H.render();}''')
        pg.wait_for_timeout(200); dc[nm] = shot(pg)
    pair(dc['old'], dc['new'], 'v89 + 48a/48b', 'round 49a').save(os.path.join(OUT, 'r49a_death.png'))
    for nm, (pg, errs) in pages.items(): print(nm, 'errors', errs[:3])
    b.close()
