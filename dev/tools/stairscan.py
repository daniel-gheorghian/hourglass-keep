# stairscan.py [file.html] [lo hi] [out.png]: the prince's feet on the exit stairs (round 16c, owner: "check the step height in every theme").
# For every floor lo..hi (default 1..48: all twelve themes and the five drawing styles), seed 4400+n, Classic: the exit door open, the
# prince climbing (state 'exit') planted on treads 1..4 in turn. Measured from the render, at the canvas's own resolution: his lowest pixel
# inside the doorway (a frame with him against one without him, LIFT_DBG.rider) and, in the frame without him, the tread's front edge
# below that pixel (drawDoor's tread edge; the render's strongest change of colour going down that column within 1.5 px of it is printed as 'drawn',
# so the treads are checked too) and the edge behind it
# (the riser's top, one tread up). A foot lands on the tread when it lies between the tread's front edge and its back edge (SY above).
# Also measured: how far his lowest pixel moves sideways while he stands planted on a tread (a sliding foot). Prints a line per style,
# the worst floor, and ALL OK or FAILURES n. Run from dev/tools.
import io, os, sys
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
SRC = os.path.abspath(next((x for x in a if x.endswith('.html')), os.path.join(HERE, '..', 'hourglass-keep.html')))
NUM = [int(x) for x in a if x.isdigit()]
LO, HI = (NUM + [1, 48])[:2] if len(NUM) >= 2 else (1, 48)
OUT = next((x for x in a if x.endswith('.png')), None)
SHOW = r'''([n,tr,ff,hide])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS)H.S.hints[id]=1;
  if(window.__n!==n){H.load(n,4400+n,true);window.__n=n;}const L=H.L,d=L.door,P=H.P;H.banner=null;d.opening=true;d.open=1;H.levelCompleteHook=()=>{};
  P.inv=1e9;P.state='exit';P.face=1;P.x=d.x;P.y=(d.r+1)*64-4;P.vx=P.vy=0;
  for(let k=0;k<10;k++){P.t=0;P.exS=tr+ff;H.tick(1);}
  H.cam.x=d.x-H.viewW/2;H.cam.y=(d.r+1)*64-64*1.6;H.cam.gy=H.cam.y;H.mode='play';H.GLP&&(H.GLP.pipe=false);H.LIFT_DBG.rider=hide;
  H.render();H.render();H.LIFT_DBG.rider=false;const X=H.XF,cv=[...document.querySelectorAll('canvas')].find(c=>c.getBoundingClientRect().width>0),R=cv.getBoundingClientRect();
  const sx=R.width/cv.width,sy=R.height/cv.height;
  const xc=d.x+8,yb=(d.r+1)*64-4-4,rdy=8*0.45,SY=8*0.22,RS=6.2;
  return {VZ:X.VZ,camD:X.camD,camDY:X.camDY,sx,sy,left:R.left,top:R.top,x0:xc-12,x1:xc+12,yb,rdy,SY,RS,exY:P.exY,exS:P.exS,st:L.theme.style,th:H.themeName(n),look:L.theme.look};}'''


def page(b):
    pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=2)
    pg.errs = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e)))
    pg.goto('file://' + SRC)
    pg.wait_for_timeout(700)
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.body.classList.remove('panelOpen')")
    pg.evaluate("()=>{__HK.S.set.lightMode='classic';}")
    return pg


HIDE = "()=>{const H=__HK;H.LIFT_DBG.rider=true;H.render();H.render();H.LIFT_DBG.rider=false;}"


def grab(pg, n, tr, ff, hide):
    if hide:  # (the same moment without him: no tick between the two frames, so nothing else has moved)
        pg.evaluate(HIDE); return None, Image.open(io.BytesIO(pg.screenshot())).convert('RGB')
    r = pg.evaluate(SHOW, [n, tr, ff, False])
    return r, Image.open(io.BytesIO(pg.screenshot())).convert('RGB')


def lum(p):
    return 0.3 * p[0] + 0.59 * p[1] + 0.11 * p[2]


if __name__ == '__main__':
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
        pg = page(b)
        res, fails, tiles = {}, 0, []
        for n in range(LO, HI + 1):
            worst = 0
            for tr in (1, 2, 3, 4):
                foots = []
                for ff in (0.05, 0.3, 0.5):  # (planted: the climb's rise starts at 0.55 of a tread)
                    r, im = grab(pg, n, tr, ff, False); _, im0 = grab(pg, n, tr, ff, True)
                    A, B0 = im.load(), im0.load()
                    # screen px of world (x,y): canvas px = x*VZ-camD; screenshot px = (left + canvas*sx)*2
                    W = lambda x, y: (int((r['left'] + (x * r['VZ'] - r['camD']) * r['sx']) * 2), int((r['top'] + (y * r['VZ'] - r['camDY']) * r['sy']) * 2))
                    k = 2 * r['VZ'] * r['sy']  # screenshot px per world px
                    (X0, Y0), (X1, Y1) = W(r['x0'] + 1, r['yb'] - 60), W(r['x1'] - 1, r['yb'] + 8)
                    low = None
                    for y in range(Y1, Y0, -1):
                        for x in range(X0, X1):
                            u, v = A[x, y], B0[x, y]
                            if abs(u[0] - v[0]) + abs(u[1] - v[1]) + abs(u[2] - v[2]) > 40:
                                low = (x, y); break
                        if low: break
                    if not low:
                        continue
                    foots.append(low)
                    # the tread under him (tread tr-1): drawDoor's front edge, then the strongest edge within 6 px of it in the frame without him
                    kk = tr - 1; top = r['yb'] - r['rdy'] - kk * r['SY'] - (kk + 1) * r['RS']
                    _, ty = W(0, top); best, by = -1, ty
                    for y in range(int(ty - 1.5 * k), int(ty + 1.5 * k) + 1):
                        g = abs(lum(B0[low[0], y + 1]) - lum(B0[low[0], y - 1]))
                        if g > best: best, by = g, y
                    edge = ty / k; foot = low[1] / k  # (world px, relative: drawDoor's edge, checked against the render below)
                    res.setdefault('drawn', []).append((by - ty) / k)  # (the drawn edge's offset from drawDoor's formula, from the render)
                    gap = foot - edge  # >0: the foot below the tread's front edge (sunk into the riser); <-SY: floating over it
                    res.setdefault(r['st'], []).append(gap)
                    bad = gap > 0.5 or gap < -(r['SY'] + 0.5)
                    if bad:
                        fails += 1
                    worst = max(worst, abs(gap + r['SY'] / 2))
                    if OUT and n in (1, 5, 13, 17, 25) and ff == 0.3 and tr in (1, 3):
                        cx, cy = low; c = im.crop((cx - 90, cy - 150, cx + 90, cy + 40)); ImageDraw.Draw(c).line((0, by - cy + 150, 180, by - cy + 150), fill=(0, 255, 120))
                        ImageDraw.Draw(c).text((3, 3), '%d %s t%d gap %.1f' % (n, r['st'], tr, gap), fill=(255, 240, 160)); tiles.append(c)
                if len(foots) > 1:
                    sl = (max(f[0] for f in foots) - min(f[0] for f in foots)) / k
                    res.setdefault('slide', []).append(sl)
                    if sl > 1.5:
                        fails += 1; print('slide %d %s tread %d: %.1f px' % (n, r['st'], tr, sl))
            print('floor %2d %-7s %-24s worst off the tread middle %.1f px' % (n, r['st'], r['th'][:24], worst), flush=True)
        for st, v in sorted(res.items()):
            print('%-8s n %3d  mean %.2f  min %.2f  max %.2f' % (st, len(v), sum(v) / len(v), min(v), max(v)))
        print('(gap: foot minus the tread\'s front edge, world px; on the tread is between %.2f and 0)' % -(8 * 0.22))
        print('errors', pg.errs[:3])
        print('ALL OK' if not fails else 'FAILURES %d' % fails)
        if OUT and tiles:
            sh = Image.new('RGB', (5 * 182, ((len(tiles) + 4) // 5) * 192), (20, 16, 24))
            for i, c in enumerate(tiles):
                sh.paste(c, ((i % 5) * 182, (i // 5) * 192))
            sh.save(OUT); print('wrote', OUT)
        b.close()
