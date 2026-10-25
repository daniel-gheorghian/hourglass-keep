# doorscan.py [file.html] [lo hi] [out.png]: wall art over doorways (round 15, owner: "Wall decoration over door. Check all levels for this
# issue"). For every floor lo..hi (default 1..48: all twelve themes) it frames the exit door (open, lit) and the entry door, in Torchlight and in
# Classic, and compares the doorway's opening (inside its frame) with the same frame drawn with the room's back-wall art left out (EGP.noart:
# the stone courses, friezes, hangings and scars of the back wall not drawn) : any difference inside the opening is wall art showing through
# or over the door. Prints a count per mode and a contact sheet of the worst cases. Run from dev/tools.
import io, os, sys
from playwright.sync_api import sync_playwright
from PIL import Image, ImageChops, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
SRC = os.path.abspath(next((x for x in a if x.endswith('.html')), os.path.join(HERE, '..', 'hourglass-keep.html')))
NUM = [int(x) for x in a if x.isdigit()]
LO, HI = (NUM + [1, 48])[:2] if len(NUM) >= 2 else (1, 48)
OUT = next((x for x in a if x.endswith('.png')), os.path.join(HERE, 'doorscan.png'))
SHOW = r'''([n,exit,noart])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS)H.S.hints[id]=1;const L=H.load(n,4400+n,true);H.banner=null;H.EGP.noart=noart;H.EGP.nocut=window.__NOCUT||false;H.clearRooms();
  const d=exit?L.door:{x:H.startDoorX?H.startDoorX():(L.start.door===undefined?1:L.start.door)*32+16,r:L.start.r,c:L.start.door===undefined?1:L.start.door}; // (round 39: where the start door is drawn, clear of a face beside it)if(exit){d.opening=true;d.open=1;}
  const P=H.P;P.inv=1e9;P.x=-999;H.cam.x=d.x-H.viewW/2;H.cam.y=(d.r+1)*64-64*1.6;H.cam.gy=H.cam.y;H.mode='play';H.GLP&&(H.GLP.pipe=false);H.gameTime=10;
  H.render();H.render();H.render();const X=H.XF,cv=[...document.querySelectorAll('canvas')].find(c=>c.getBoundingClientRect().width>0),R=cv.getBoundingClientRect(),
  m=(x,y)=>[R.left+(x*X.VZ-X.camD)/cv.width*R.width,R.top+(y*X.VZ-X.camDY)/cv.height*R.height];
  const c=Math.floor(d.x/32),Yc=d.r*64,xc=d.x+8,x0=xc-12+2,x1=xc+12-2,yb=(d.r+1)*64-4-4-2,y0=Yc+5+6+8; // (the opening, inside its frame and arched head)
  return {a:m(x0,y0),b:m(x1,yb),th:H.themeName(n)};}'''


def page(b, mode):
    pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=2)
    pg.errs = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e)))
    pg.goto('file://' + SRC)
    pg.wait_for_timeout(700)
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.body.classList.remove('panelOpen')")
    pg.evaluate("m=>{__HK.S.set.lightMode=m;}", mode)
    if 'nocut' in a:
        pg.evaluate("()=>{window.__NOCUT=true;}")  # (the doorways not cut out: as before round 15)
    return pg


if __name__ == '__main__':
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
        bad, worst, errs, cases = {}, [], [], 0
        for mode in ('torch', 'classic'):
            pg = page(b, mode); bad[mode] = 0
            for n in range(LO, HI + 1):
                for ex in (True, False):
                    r1 = pg.evaluate(SHOW, [n, ex, False]); im1 = Image.open(io.BytesIO(pg.screenshot())).convert('RGB')
                    pg.evaluate(SHOW, [n, ex, True]); im0 = Image.open(io.BytesIO(pg.screenshot())).convert('RGB')
                    box = (int(r1['a'][0] * 2), int(r1['a'][1] * 2), int(r1['b'][0] * 2), int(r1['b'][1] * 2))
                    if box[2] <= box[0] or box[3] <= box[1]:
                        continue
                    cases += 1
                    df = ImageChops.difference(im1.crop(box), im0.crop(box)).convert('L')
                    hist = df.histogram(); nbad = sum(hist[24:])
                    if nbad > 6:
                        bad[mode] += 1
                        if len(worst) < 12:
                            cx, cy = (box[0] + box[2]) // 2, (box[1] + box[3]) // 2; c = im1.crop((cx - 120, cy - 110, cx + 120, cy + 110))
                            ImageDraw.Draw(c).text((4, 3), '%s %d %s %s (%d px)' % (mode, n, 'exit' if ex else 'entry', r1['th'][:18], nbad), fill=(255, 240, 160)); worst.append(c)
            errs += pg.errs; pg.close()
        print('doors with wall art over the opening: torch %d, classic %d (of %d door views)' % (bad['torch'], bad['classic'], cases), 'errors', errs[:3])
        if worst:
            sh = Image.new('RGB', (4 * 242, ((len(worst) + 3) // 4) * 222), (20, 16, 24))
            for i, c in enumerate(worst):
                sh.paste(c, ((i % 4) * 242, (i // 4) * 222))
            sh.save(OUT); print('wrote', OUT)
        b.close()
