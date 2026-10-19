# egyptr16c.py [new.html] [old.html] [outdir]: round 16c's pictures for egypt_themes.html, round 16b (old.html, made with
# git show 5699dc4:dev/hourglass-keep.html) against round 16c, in the game at the phone's resolution (crops of the 1704 px canvas):
#  r16c_lift.png   a counterweight lift's mouths (one opening on the shaft's left, one on its right), platform half way, before and after,
#                  Torchlight and Classic, at 2x; under them the mouths at 1:1 in three more themes with the platform at the top, half way
#                  and at the bottom, the sand lift and the paternoster (after only)
#  r16c_gate.png   the portcullis closed in all twelve themes at 1:1, before (upper) and after (lower), Torchlight then Classic; then four at 2x
#  r16c_stairs.png the prince planted on the exit stairs' first and third treads in the five drawing styles, before and after, at 2x
# Run from dev/tools.
import os, sys
from playwright.sync_api import sync_playwright
from PIL import Image
import egyptr12 as R12
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
NEW = os.path.abspath(a[0] if len(a) > 0 else os.path.join(HERE, '..', 'hourglass-keep.html'))
OLD = os.path.abspath(a[1] if len(a) > 1 else os.path.join(HERE, '..', '_r16b.html'))
OUT = a[2] if len(a) > 2 else os.path.join(HERE, 'egypt_themes')
R12.OUT = OUT
FINDLIFT = r"""([n,kind])=>{for(const sd of [801,802,803,804,805,806]){const L=__P.load(n,sd);const i=L.lifts.findIndex(q=>kind==='sand'?q.sand:kind==='chain'?q.t==='chain':q.t==='lift'&&!q.sand);if(i>=0)return [sd,i];}return null;}"""
LIFT = r"""([n,sd,frac,i,e,oy])=>{const H=__HK;H.EGP.traps=true;const L=__P.load(n,sd),lf=L.lifts[i],P=H.P;
  if(lf.t==='lift'&&!lf.sand){lf.y=lf.yT+(lf.yB-lf.yT)*frac;L.base[lf.rT*L.cols+lf.sc]=frac===0?1:0;lf.gT=frac===0?1:0;lf.gB=frac===1?1:0;}
  if(lf.sand){lf.y=lf.yT+(lf.yB-lf.yT)*frac;if(frac>0){lf.s=1;lf.tm=5;}}
  const s=(e?lf.sB:lf.sT)||(e?1:-1),r=e?lf.rB:lf.rT,gx=s<0?lf.ca*32:(lf.cb+1)*32;
  P.x=gx+s*60;P.y=(r+1)*64-4;P.state='stand';P.face=-s;P.inv=1e9;H.cam.snap=true;const px=P.x,py=P.y;H.tick(1);P.x=px;P.y=py;P.state='stand';H.banner=null;
  if(lf.t==='lift')lf.y=lf.yT+(lf.yB-lf.yT)*frac;if(H.GLP)H.GLP.pipe=false;H.render();H.render();return [__P.scr(gx-s*4,(r+1)*64-oy),L.theme.look,s];}"""
GATE = r"""([q])=>{const H=__HK;H.EGP.traps=true;__P.load(q.n,q.seed);const L=H.L;__P.stand(q.pc,q.r,q.face);
  const o=L.dyn.find(o=>o.c===q.c&&o.r===q.r);o.f.open=0;o.f.tm=0;o.f.heldAt=-9;if(H.GLP)H.GLP.pipe=false;__P.draw();__P.draw();return __P.scr(q.c*32+16,(q.r+1)*64-34);}"""
STAIR = r"""([n,tr])=>{const H=__HK;window.__HKfreeze=true;H.load(n,4400+n,true);const L=H.L,d=L.door,P=H.P;H.banner=null;d.opening=true;d.open=1;H.levelCompleteHook=()=>{};
  P.inv=1e9;P.state='exit';P.face=1;P.x=d.x;P.y=(d.r+1)*64-4;P.vx=P.vy=0;for(let k=0;k<10;k++){P.t=0;P.exS=tr+0.3;H.tick(1);}
  H.cam.x=d.x-H.viewW/2;H.cam.y=(d.r+1)*64-64*1.6;H.cam.gy=H.cam.y;H.mode='play';H.GLP&&(H.GLP.pipe=false);H.render();H.render();
  const X=H.XF,cv=[...document.querySelectorAll('canvas')].find(c=>c.getBoundingClientRect().width>0),R=cv.getBoundingClientRect();
  return [R.left+((d.x+8)*X.VZ-X.camD)/cv.width*R.width,R.top+((P.y+(P.exY||0)-6)*X.VZ-X.camDY)/cv.height*R.height,L.theme.style];}"""


def up(im, k=2):
    return im.resize((im.width * k, im.height * k), Image.LANCZOS)


def row(ims, pad=2):
    g = Image.new('RGB', (sum(i.width for i in ims) + pad * (len(ims) - 1), max(i.height for i in ims)), (20, 16, 24)); x = 0
    for i in ims:
        g.paste(i, (x, 0)); x += i.width + pad
    return g


if __name__ == '__main__':
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
        P = {(t, m): R12.page(b, s, m) for t, s in (('before', OLD), ('after', NEW)) for m in ('torch', 'classic')}
        errs = []
        # --- lifts
        pn = P[('after', 'torch')]
        q3 = pn.evaluate(FINDLIFT, [3, 'lift'])
        top = []
        for m in ('torch', 'classic'):
            for t in ('before', 'after'):
                pg = P[(t, m)]
                for e in (0, 1):
                    r = pg.evaluate(LIFT, [3, q3[0], 0.5, q3[1], e, 16])
                    top.append(R12.label(up(R12.crop(R12.shot(pg), r[0], 250, 270)), '%s, %s, %s mouth (%s side), 2x' % (t, m, 'top' if e == 0 else 'bottom', 'left' if r[2] < 0 else 'right')))
        rows = [R12.grid(top[:4], 4), R12.grid(top[4:], 4)]
        tl = []
        for n, kind in ((9, 'lift'), (17, 'lift'), (13, 'lift')):
            q = pn.evaluate(FINDLIFT, [n, kind])
            if not q: continue
            for fr in (0, 0.5, 1):
                for e in (0, 1):
                    r = pn.evaluate(LIFT, [n, q[0], fr, q[1], e, 14]); tl.append(R12.label(R12.crop(R12.shot(pn), r[0], 200, 250), '%d %s %s %s' % (n, r[1], ['top', 'half', 'bottom'][int(fr * 2)], 'top' if e == 0 else 'bot')))
        for n, kind in ((5, 'sand'), (25, 'sand'), (14, 'chain')):
            q = pn.evaluate(FINDLIFT, [n, kind])
            if not q: continue
            for fr in ((0, 0.5) if kind == 'sand' else (0,)):
                for e in (0, 1):
                    r = pn.evaluate(LIFT, [n, q[0], fr, q[1], e, 14]); tl.append(R12.label(R12.crop(R12.shot(pn), r[0], 200, 250), '%d %s %s %s' % (n, kind, 'half' if fr else 'top', 'top' if e == 0 else 'bot')))
        rows.append(R12.grid(tl, 10))
        R12.stack(rows).save(os.path.join(OUT, 'r16c_lift.png'))
        # --- gates: one per theme
        looks = pn.evaluate("__HK.THEMES.map(t=>t.look)")
        Q = []
        for lk in looks:
            fl = pn.evaluate("lk=>__HK.floorsOf(lk,180)", lk)
            qs = pn.evaluate(R12.PC['FINDF'], [R12.F([f + i for f in fl[:3] for i in range(4)]), ['gate'], 1, 2])
            Q.append((lk, qs[0] if qs else None))
        rows, big = [], []
        for m in ('torch', 'classic'):
            for t in ('before', 'after'):
                pg = P[(t, m)]; tl = []
                for lk, q in Q:
                    if not q: continue
                    xy = pg.evaluate(GATE, [q]); c = R12.crop(R12.shot(pg), [xy[0] + 6, xy[1] - 22], 140, 230)
                    if lk in ('nun', 'osiris', 'wells', 'shali'): big.append(R12.label(up(c), '%s %s %s, 2x' % (t, m, lk)))
                    tl.append(R12.label(c, lk))
                rows.append(R12.label(R12.grid(tl, 12), '', (0, 0)))
        bigrows = [row(big[0:4] + big[4:8]), row(big[8:12] + big[12:16])]
        R12.stack(rows + bigrows).save(os.path.join(OUT, 'r16c_gate.png'))
        # --- stairs: one floor per drawing style
        tl = []
        for t in ('before', 'after'):
            pg = P[(t, 'classic')]
            for n in (1, 5, 9, 13, 17):
                for tr in (1, 3):
                    x, y, st = pg.evaluate(STAIR, [n, tr]); tl.append(R12.label(up(R12.crop(R12.shot(pg), [x, y], 150, 220)), '%s %s tread %d' % (t, st, tr)))
        R12.grid(tl, 10).save(os.path.join(OUT, 'r16c_stairs.png'))
        for pg in P.values():
            errs += pg.errs
        print('errors', errs[:4])
        b.close()
