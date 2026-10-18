# egyptr14.py [new.html] [old.html] [outdir]: round 14's pictures for egypt_themes.html, round 13 (old.html, default ../_r13.html, made
# with git show f716737:dev/hourglass-keep.html) against round 14, in the game at the phone's resolution (crops of the 1704 px canvas, shown
# at 2x, both modes): the portcullis where the ceiling's block ends beside it, half-way and closed (r14_gate.png); a counterweight lift's two
# mouths, the platform between them (r14_lift.png). Run from dev/tools.
import os, sys
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw
import egyptr10 as R10
import egyptr12 as R12
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
NEW = os.path.abspath(a[0] if len(a) > 0 else os.path.join(HERE, '..', 'hourglass-keep.html'))
OLD = os.path.abspath(a[1] if len(a) > 1 else os.path.join(HERE, '..', '_r13.html'))
OUT = a[2] if len(a) > 2 else os.path.join(HERE, 'egypt_themes')
PICK = r"""qs=>{const H=__HK;for(const q of qs){const L=__P.load(q.n,q.seed),C=L.cols;if(L.base[(q.r-1)*C+q.c]===2&&L.base[(q.r-1)*C+q.c+1]!==2)return q;}return qs[0];}"""
LIFT = r"""([n,sd,frac])=>{const H=__HK,L=__P.load(n,sd),lf=L.lifts.find(q=>q.t==='lift'),P=H.P;lf.y=lf.yT+(lf.yB-lf.yT)*frac;P.x=lf.sc*32+16;P.y=lf.y;P.state='stand';P.face=1;
  L.base[lf.rT*L.cols+lf.sc]=frac===0?1:0;lf.gT=frac===0?1:0;lf.gB=frac===1?1:0;P.inv=1e9;H.cam.snap=true;const px=P.x,py=P.y;H.tick(1);P.x=px;P.y=py;P.state='stand';
  lf.y=lf.yT+(lf.yB-lf.yT)*frac;H.render();H.render();const gx=s=>s<0?lf.sc*32:(lf.sc+1)*32;return [__P.scr(gx(lf.sT),(lf.rT+1)*64-34),__P.scr(gx(lf.sB),(lf.rB+1)*64-34)];}"""
WHITE = (240, 230, 210)


def lab(im, t):
    ImageDraw.Draw(im).text((4, 3), t, fill=WHITE)
    return im


if __name__ == '__main__':
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
        errs = []
        P = {(t, m): R12.page(b, s, m) for t, s in (('round 13', OLD), ('round 14', NEW)) for m in ('torch', 'classic')}
        pn = P[('round 14', 'torch')]
        fl = pn.evaluate("lk=>__HK.floorsOf(lk,180)", 'nun')
        qs = pn.evaluate(R12.PC['FINDF'], [R12.F([f + i for f in fl[:4] for i in range(4)]), ['gate'], 6, 2])
        q = pn.evaluate(PICK, qs)
        tl = []
        for m in ('torch', 'classic'):
            for t in ('round 13', 'round 14'):
                pg = P[(t, m)]
                for op, nm in ((0.4, 'part open'), (0, 'closed')):
                    xy = pg.evaluate(R12.GATE, [q, op]); tl.append(lab(R12.crop(R12.shot(pg), [xy[0] + 6, xy[1] - 22], 150, 230).resize((300, 460), Image.LANCZOS), '%s %s %s' % (t, m, nm)))
        R12.grid(tl, 8).save(os.path.join(OUT, 'r14_gate.png'))
        tl = []
        for m in ('torch', 'classic'):
            for t in ('round 13', 'round 14'):
                pg = P[(t, m)]; xs = pg.evaluate(LIFT, [3, 70182, 0.5])
                for k, xy in enumerate(xs):
                    tl.append(lab(R12.crop(R12.shot(pg), xy, 150, 200).resize((300, 400), Image.LANCZOS), '%s %s, %s mouth' % (t, m, 'top' if k == 0 else 'bottom')))
        R12.grid(tl, 8).save(os.path.join(OUT, 'r14_lift.png'))
        for pg in P.values():
            errs += pg.errs
        print('errors', errs[:4])
        b.close()
