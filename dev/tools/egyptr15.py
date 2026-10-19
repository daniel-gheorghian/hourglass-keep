# egyptr15.py [new.html] [old.html] [outdir]: round 15's pictures for egypt_themes.html: the sky beams no longer reaching wall faces (r15_beams.png,
# made by beamwall.py), the doorways cut out of the back wall's relief (r15_door.png: round 14 and round 15, Torchlight, exit doors in three
# themes), and the prince climbing the exit stairs (r15_exit.gif: round 14 above, round 15 below, at 2x of the 1:1 canvas). Run from dev/tools.
import io, os, sys
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw
import beamwall as BW
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
NEW = os.path.abspath(a[0] if len(a) > 0 else os.path.join(HERE, '..', 'hourglass-keep.html'))
OLD = os.path.abspath(a[1] if len(a) > 1 else os.path.join(HERE, '..', '_r14.html'))
OUT = a[2] if len(a) > 2 else os.path.join(HERE, 'egypt_themes')
DOOR = r'''([n])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS)H.S.hints[id]=1;const L=H.load(n,4400+n,true);H.banner=null;H.clearRooms();const d=L.door;d.opening=true;d.open=1;
  const P=H.P;P.inv=1e9;P.x=-999;H.cam.x=d.x-H.viewW/2;H.cam.y=(d.r+1)*64-64*1.6;H.cam.gy=H.cam.y;H.mode='play';H.GLP&&(H.GLP.pipe=false);H.gameTime=10;H.render();H.render();H.render();
  const X=H.XF,cv=[...document.querySelectorAll('canvas')].find(c=>c.getBoundingClientRect().width>0),R=cv.getBoundingClientRect();return [R.left+((d.x+8)*X.VZ-X.camD)/cv.width*R.width,R.top+(((d.r+1)*64-36)*X.VZ-X.camDY)/cv.height*R.height];}'''
EXIT0 = r'''([n])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS)H.S.hints[id]=1;const L=H.load(n,4400+n,false);H.banner=null;const d=L.door;d.opening=true;d.open=1;
  const P=H.P;P.inv=1e9;P.x=d.x-40;P.y=(d.r+1)*64-4;P.fallY=P.y;P.face=1;P.state='stand';H.cam.snap=true;H.mode='play';H.tick(2);P.x=d.x-40;H.levelCompleteHook=()=>{};return 1;}'''
EXITN = r'''([n,go])=>{const H=__HK,L=H.L,d=L.door,P=H.P;if(go&&P.state!=='exit'){H.setKey('kb','r',P.x<d.x-6);if(P.x>=d.x-6){H.setKey('kb','r',false);if(P.state==='stand'){P.state='exit';P.t=0;P.sword=false;}}}
  H.tick(3);H.banner=null;H.GLP&&(H.GLP.pipe=false);H.render();const X=H.XF,cv=[...document.querySelectorAll('canvas')].find(c=>c.getBoundingClientRect().width>0),R=cv.getBoundingClientRect();
  return [R.left+((d.x+8)*X.VZ-X.camD)/cv.width*R.width,R.top+(((d.r+1)*64-40)*X.VZ-X.camDY)/cv.height*R.height,P.state];}'''


def lab(im, t):
    ImageDraw.Draw(im).text((4, 3), t, fill=(240, 230, 210)); return im


if __name__ == '__main__':
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
        P = {t: BW.page(b, s, 'torch') for t, s in (('round 14', OLD), ('round 15', NEW))}
        tl = []
        for n in (5, 9, 11):
            for t in ('round 14', 'round 15'):
                pg = P[t]; xy = pg.evaluate(DOOR, [n]); tl.append(lab(BW.crop(pg, xy, 220, 200), '%s, floor %d' % (t, n)))
        w, h = tl[0].size; sh = Image.new('RGB', (6 * (w + 2), h), (20, 16, 24))
        for i, im in enumerate(tl):
            sh.paste(im, (i * (w + 2), 0))
        sh.save(os.path.join(OUT, 'r15_door.png'))
        fr = [[], []]
        for j, t in enumerate(('round 14', 'round 15')):
            pg = P[t]; pg.evaluate(EXIT0, [5])
            for k in range(44):
                r = pg.evaluate(EXITN, [5, True]); fr[j].append(lab(BW.crop(pg, [r[0], r[1] - 20], 240, 260), t))
        frames = []
        for a1, a2 in zip(*fr):
            im = Image.new('RGB', (a1.width, a1.height * 2 + 2), (20, 16, 24)); im.paste(a1, (0, 0)); im.paste(a2, (0, a1.height + 2)); frames.append(im)
        frames[0].save(os.path.join(OUT, 'r15_exit.gif'), save_all=True, append_images=frames[1:], duration=60, loop=0, optimize=True)
        print('errors', P['round 14'].errs[:2], P['round 15'].errs[:2]); b.close()
