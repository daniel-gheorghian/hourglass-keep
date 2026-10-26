# egyptr41.py [new.html] [outdir]: round 41's pictures (owner: "The sand lifts become a trap: the sand drains, the door opens, but he has to
# jump, because the slab keeps going. The shaft is bottomless; the sand drains off the screen and the slab falls off the screen").
# r41_sandfall.png: one row per moment, Classic | Torchlight, crops round the sand lift's foot at 3x (3 screen px a world px):
#   the slab sinking, the foot's mouth opening with him on it; stepping off through the mouth; the slab dropping away under the floor;
#   the empty bottomless shaft after; missed: he rides on under the floor into the dark; a far-side lift (the way on behind him).
# r41_sandfall.gif: a ride in real time (Classic, 2x): on, down, the mouth, the step off, the slab going down out of sight; then a miss.
# outdir defaults to dev/tools/egypt_themes. Run from dev/tools (Torchlight is software WebGL in headless Chromium: a few s a frame).
import io, os, sys
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
NEW = os.path.abspath(next((x for x in a if x.endswith('.html')), os.path.join(HERE, '..', 'hourglass-keep.html')))
OUTD = next((x for x in a if not x.endswith('.html')), os.path.join(HERE, 'egypt_themes'))
INK = (20, 16, 24)
BW, BH, ZK = 150, 150, 3  # the crop in world px round the foot (from 100 px over the floor to 50 under), and its scale

FIND = r'''(two)=>{const H=__HK;for(let n=6;n<=40;n++)for(let s=0;s<40;s++){const seed=90000+n*211+s*31,L=H.genLevel(n,seed,true);
  const f=L.lifts.find(f=>f.sand&&(f.ms.length>1)===two&&f.k===3);if(f)return [n,seed,f.sc];}return null;}'''
# set up the floor: the prince on the slab at the top, guards away, hints off; returns nothing
LOAD = r'''([n,seed,sc])=>{const H=__HK;for(const id in H.HINTS){H.S.hints[id]=1;H.S.learned[id]=1;}const L=H.load(n,seed,true);H.banner=null;
  const f=L.lifts.find(f=>f.sand&&f.sc===sc);window.__F=f;const P=H.P;P.inv=1e9;for(const e of H.G)e.x=-9999;
  P.x=f.sc*32+16;P.y=f.yT;P.fallY=P.y;P.vx=0;P.face=f.sB;P.state='stand';H.mode='play';
  let q=12345;Math.random=()=>{q=(q*16807)%2147483647;return q/2147483647;};return [f.yB,f.sB,f.ms,H.themeName(n)];}'''
# run the game until cond (a JS expression over f, P) holds, holding keys; at most lim frames
STEP = r'''([cond,keys,lim])=>{const H=__HK,f=window.__F,P=H.P;for(const k of ['l','r','u','j'])H.setKey('kb',k,keys.includes(k));
  const c=new Function('f','P','H','return '+cond);let i=0;while(i++<lim&&!c(f,P,H))H.tick(1);return [i,P.state,+(f.y-f.yB).toFixed(1),f.s];}'''
# draw the frame with the camera on the foot (held as play holds it there), frozen clock; returns the crop's placement
SHOW = r'''()=>{const H=__HK,f=window.__F;H.banner=null;let T=1e6+H.gameTime*1000;H.setClock(()=>T);
  const fx=f.sc*32+16,fy=f.yB;H.cam.x=fx-H.viewW/2;H.cam.y=fy-192*0.6;H.cam.gy=fy;if(H.GLP){H.GLP.pipe=false;H.GLP.rs=1;window.__HKnoauto=true;}
  window.__HKfreeze=true;for(let i=0;i<3;i++)H.render();const X=H.XF,cv=[...document.querySelectorAll('canvas')].find(c=>c.getBoundingClientRect().width>0),R=cv.getBoundingClientRect(),k=X.VZ/cv.width*R.width;
  return [R.left-X.camD/cv.width*R.width,R.top-X.camDY/cv.height*R.height,k,fx,fy];}'''
MODES = [('Classic', 'classic'), ('Torchlight', 'torch')]


def page(b, mode, dsf=2):
    pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=dsf)
    pg.errs = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e)))
    pg.goto('file://' + NEW)
    pg.wait_for_timeout(700)
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.body.classList.remove('panelOpen')")
    pg.evaluate("m=>{__HK.S.set.lightMode=m;}", mode)
    pg.dsf = dsf
    return pg


def shot(pg, zk=ZK):
    q = pg.evaluate(SHOW)
    im = Image.open(io.BytesIO(pg.screenshot())).convert('RGB')
    d = pg.dsf
    ox, oy, k, fx, fy = q[0] * d, q[1] * d, q[2] * d, q[3], q[4]
    x0, y0 = ox + (fx - BW / 2) * k, oy + (fy - 100) * k
    return im.crop((int(x0), int(y0), int(x0 + BW * k), int(y0 + BH * k))).resize((BW * zk, BH * zk), Image.LANCZOS)


def label(im, t):
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 8 + 6 * len(t), 13), fill=(0, 0, 0))
    d.text((4, 1), t, fill=(250, 240, 215))


def moments(pg, lift, two):
    # yields (title, image) for one lift, in order
    pg.evaluate(LOAD, lift)
    side = 'r' if pg.evaluate('__F.sB') > 0 else 'l'
    off = pg.evaluate('__F.ms.length>1') and ('l' if side == 'r' else 'r') or side
    pg.evaluate(STEP, ["P.state==='lift'", '', 60])
    pg.evaluate(STEP, ["f.y>=f.yB-24", '', 600])
    yield 'the slab 24 px over the foot\'s floor: the mouth slab%s rising, he rides on it' % ('s' if two else ''), shot(pg)
    pg.evaluate(STEP, ["P.state==='step'&&P.t>=0.12", off, 120])
    yield 'stepping off through the %s mouth (the way on)' % ('far' if two else 'exit'), shot(pg)
    pg.evaluate(STEP, ["f.y>=f.yB+44", '', 600])
    yield 'off, on the landing: the slab 44 px under the floor, going down into the dark', shot(pg)
    pg.evaluate(STEP, ["f.s>=3", '', 900])
    yield 'after: the empty bottomless shaft, both mouths open' if two else 'after: the empty bottomless shaft, the mouth open', shot(pg)


def miss(pg, lift):
    pg.evaluate(LOAD, lift)
    pg.evaluate(STEP, ["P.state==='lift'", '', 60])
    pg.evaluate(STEP, ["f.y>=f.yB+36", '', 900])
    yield 'missed: nothing pressed, he rides on under the floor (36 px down), fading into the dark', shot(pg)


if __name__ == '__main__':
    rows = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        pages = {m: page(b, m) for _, m in MODES}
        L1 = pages['classic'].evaluate(FIND, False)
        L2 = pages['classic'].evaluate(FIND, True)
        print('lifts', L1, L2, flush=True)
        seqs = [('Exit-side lift, floor %d seed %d' % (L1[0], L1[1]), lambda pg: moments(pg, L1, False)),
                ('', lambda pg: miss(pg, L1)),
                ('Far-side lift (the route runs on behind him), floor %d seed %d' % (L2[0], L2[1]), lambda pg: moments(pg, L2, True))]
        for head, fn in seqs:
            cols = {m: list(fn(pages[m])) for _, m in MODES}
            for i in range(len(cols['classic'])):
                t = cols['classic'][i][0]
                cw = BW * ZK
                row = Image.new('RGB', (2 * cw + 8, 20 + BH * ZK), INK)
                ImageDraw.Draw(row).text((6, 4), ((head + ': ') if head and i == 0 else '') + t, fill=(250, 240, 215))
                for j, (mt, m) in enumerate(MODES):
                    c = cols[m][i][1]
                    label(c, mt)
                    row.paste(c, (j * (cw + 8), 20))
                rows.append(row)
                print('row', t, flush=True)
        # the gif: Classic at 2x, every 3rd frame, a step-off ride and then a miss
        gp = page(b, 'classic', 1)
        frames = []
        def rec(cond, keys, lim, every=3):
            n = 0
            while n < lim:
                gp.evaluate(STEP, ['false', keys, every])
                im = shot(gp, 2)
                frames.append(im)
                n += every
                if gp.evaluate("(c)=>{const f=window.__F,P=__HK.P;return new Function('f','P','return '+c)(f,P)}", cond):
                    break
        for lift, two in ((L1, False),):
            gp.evaluate(LOAD, lift)
            side = 'r' if gp.evaluate('__F.sB') > 0 else 'l'
            rec("P.state==='lift'", '', 60)
            rec("f.y>=f.yB-40", '', 600)
            rec("P.state==='stand'&&P.y===f.yB", side, 120)
            rec("f.s>=3", '', 600)
            for _ in range(8):
                frames.append(frames[-1])
            gp.evaluate(LOAD, lift)
            rec("P.state==='lift'", '', 60)
            rec("P.state==='dead'", '', 900)
            for _ in range(12):
                gp.evaluate(STEP, ['false', '', 3]); frames.append(shot(gp, 2))
        os.makedirs(OUTD, exist_ok=True)
        gif = os.path.join(OUTD, 'r41_sandfall.gif')
        frames[0].save(gif, save_all=True, append_images=frames[1:], duration=50, loop=0, optimize=True)
        print('wrote', gif, len(frames), 'frames')
        for k, pg in list(pages.items()) + [('gif', gp)]:
            if pg.errs:
                print('errors', k, pg.errs[:3])
        b.close()
    W = max(r.width for r in rows)
    sheet = Image.new('RGB', (W, sum(r.height + 6 for r in rows)), INK)
    y = 0
    for r in rows:
        sheet.paste(r, (0, y)); y += r.height + 6
    out = os.path.join(OUTD, 'r41_sandfall.png')
    sheet.save(out, optimize=True)
    print('wrote', out, sheet.size)
