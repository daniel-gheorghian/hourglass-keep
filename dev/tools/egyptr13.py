# egyptr13.py [new.html] [old.html] [outdir]: round 13's pictures for egypt_themes.html, round 12 (old.html, default ../_r12.html, made
# with git show 04a1b37:dev/hourglass-keep.html) against round 13, in the game at the phone's resolution (crops of the 1704 px canvas,
# 1:1, both modes): the two kinds of lift (r13_lifts.png); the prince's head at 1:1 and 4x in several poses, both facings
# (r13_head.png); the prince standing against a fallen roof block (r13_block.png). Run from dev/tools.
import io, os, sys
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw
import egyptr10 as R10
import egyptr12 as R12
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
NEW = os.path.abspath(a[0] if len(a) > 0 else os.path.join(HERE, '..', 'hourglass-keep.html'))
OLD = os.path.abspath(a[1] if len(a) > 1 else os.path.join(HERE, '..', '_r12.html'))
OUT = a[2] if len(a) > 2 else os.path.join(HERE, 'egypt_themes')
# a lift of kind t ('lift': counterweight, 'chain': the paternoster), the prince riding it; the crop's centre
LIFT = r"""([t,frac])=>{const H=__HK;for(let n=4;n<=40;n++)for(let sd=701;sd<=704;sd++){const L=__P.load(n,sd);const lf=L.lifts.find(q=>q.t===t);if(!lf)continue;const P=H.P;
  if(t==='lift'){lf.y=lf.yT+(lf.yB-lf.yT)*frac;P.x=lf.sc*32+16;P.y=lf.y;P.state='stand';P.face=1;L.base[lf.rT*L.cols+lf.sc]=frac===0?1:0;lf.gT=frac===0?1:0;lf.gB=frac===1?1:0;}
  else{const q=H.chainPos(lf,0,H.gameTime);P.x=q.x;P.y=q.y;P.state='lift';P.lift=lf;P.slab=0;P.bx=q.x;P.by=q.y;P.bt=0;}
  P.inv=1e9;H.cam.snap=true;const px=P.x,py=P.y,st=P.state;H.tick(1);P.x=px;P.y=py;P.state=st;H.render();H.render();H.render();return {xy:__P.scr((lf.ca+lf.cb+1)*16,P.y-40),n,sd};}return null;}"""
HEAD = r"""([pose,face])=>{const H=__HK,L=__P.load(9,951);H.setHero&&H.setHero('P');__P.stand(Math.floor(L.start.x/32)+4,L.start.r,face);const P=H.P;
  if(pose==='crouch'){P.state='crouch';P.t=1;}H.tick(1);P.face=face;H.render();H.render();return __P.scr(P.x,P.y-44);}"""
BLOCK = r"""([q])=>{const H=__HK;H.EGP.traps=true;__P.load(q.n,q.seed);const L=H.L,C=L.cols,o=L.dyn.find(o=>o.c===q.c&&o.r===q.r);o.f.s=3;L.rubble.add(q.r*C+q.c);H.clearRooms();
  const P=H.P;__P.stand(q.c-2,q.r,1);P.x=q.c*32+16-11-6-0.01;P.state='stand';P.face=1;H.tick(1);P.x=q.c*32+16-11-6-0.01;H.render();H.render();return __P.scr(q.c*32+8,(q.r+1)*64-16);}"""
WHITE = (240, 230, 210)


def lab(im, t):
    ImageDraw.Draw(im).text((4, 3), t, fill=WHITE)
    return im


if __name__ == '__main__':
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
        errs = []
        P = {(t, m): R10.page(b, s, m) for t, s in (('round 12', OLD), ('round 13', NEW)) for m in ('torch', 'classic')}
        # the lifts
        tl = []
        for kind, frac, nm in (('lift', 0.5, 'counterweight lift'), ('chain', 0, 'paternoster')):
            for m in ('torch', 'classic'):
                for t in ('round 12', 'round 13'):
                    pg = P[(t, m)]; r = pg.evaluate(LIFT, [kind, frac])
                    if not r:
                        print('no lift', kind); continue
                    tl.append(lab(R10.crop(pg, r['xy'], 300, 420), '%s, %s %s' % (nm, t, m)))
        R12.grid(tl, 8).save(os.path.join(OUT, 'r13_lifts.png'))
        # the head: 1:1 and 4x, standing and crouching, both facings (Classic: the drawing's own colours)
        tl = []
        for pose in ('stand', 'crouch'):
            for face in (1, -1):
                for t in ('round 12', 'round 13'):
                    pg = P[(t, 'classic')]; xy = pg.evaluate(HEAD, [pose, face]); im = R10.crop(pg, xy, 120, 120)
                    tl.append(lab(im.resize((240, 240), Image.NEAREST), '%s %s %s 2x' % (t, pose, 'right' if face > 0 else 'left')))
        for t in ('round 12', 'round 13'):
            pg = P[(t, 'torch')]; xy = pg.evaluate(HEAD, ['stand', 1]); tl.append(lab(R10.crop(pg, xy, 60, 60).resize((240, 240), Image.NEAREST), '%s torch 4x' % t))
        R12.grid(tl, 10).save(os.path.join(OUT, 'r13_head.png'))
        # the prince against a fallen block
        pn = P[('round 13', 'torch')]
        sq = pn.evaluate(R12.PC['FINDF'], [R12.F([3, 2, 4]), ['stone'], 1, 3])[0]
        tl = []
        for m in ('torch', 'classic'):
            for t in ('round 12', 'round 13'):
                pg = P[(t, m)]; xy = pg.evaluate(BLOCK, [sq]); im = R10.crop(pg, xy, 220, 200)
                tl.append(lab(im.resize((440, 400), Image.LANCZOS), '%s %s 2x' % (t, m)))
        R12.grid(tl, 4).save(os.path.join(OUT, 'r13_block.png'))
        for pg in P.values():
            errs += pg.errs
        print('errors', errs[:4])
        b.close()
