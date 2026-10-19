# openscan.py [file.html] [lo hi] [out.png] [torch|classic|both]: wall art over openings other than doors (round 16c; doorscan.py does the doors).
# For every floor lo..hi (default 1..48: all twelve themes), seed 4400+n, in Torchlight and in Classic:
#  - windows (up to two a floor): the window's opening (its own path, 1 px in from its edge) against the same frame drawn with what is hung
#    on the back wall after the windows left out (EGP.noover: the hangings and the scars of fallen lamps);
#  - gate openings (up to two portcullises a floor, shut): the slab's faces against the frame drawn with the back wall's art left out
#    (EGP.noart): any difference is the wall's courses, friezes or bands showing on the slab (Torchlight's relief is taken from the room's
#    picture, so it embosses whatever lies behind a live object unless that object is rubbed back);
#  - lift mouths (each counterweight lift, its platform half way, both mouths shut): each mouth's slab, as for the gates.
# A view is bad when more than 6 pixels inside the opening differ by more than 24 (sum of channels). Prints the counts per kind and
# mode, and a contact sheet of the worst cases. Run from dev/tools.
import io, os, sys
from playwright.sync_api import sync_playwright
from PIL import Image, ImageChops, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
SRC = os.path.abspath(next((x for x in a if x.endswith('.html')), os.path.join(HERE, '..', 'hourglass-keep.html')))
NUM = [int(x) for x in a if x.isdigit()]
LO, HI = (NUM + [1, 48])[:2] if len(NUM) >= 2 else (1, 48)
OUT = next((x for x in a if x.endswith('.png')), os.path.join(HERE, 'openscan.png'))
MODES = ['torch', 'classic'] if 'both' in a or not ('torch' in a or 'classic' in a) else (['torch'] if 'torch' in a else ['classic'])
LIST = r'''(n)=>{const H=__HK;const L=H.load(n,4400+n,true),C=L.cols,out=[];
  L.windows.slice(0,2).forEach((w,i)=>out.push(['window',i]));
  L.dyn.filter(o=>o.f.t==='gate').slice(0,2).forEach((o,i)=>out.push(['gate',i]));
  L.lifts.forEach((f,i)=>{if(f.t==='lift'&&!f.sand)for(const e of [0,1])out.push(['lift',i,e]);});return out;}'''
# set the view; returns the opening's screen pixels (css px) as a list of [x,y] samples
SHOW = r'''([n,k,i,e,flag])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS)H.S.hints[id]=1;const L=H.load(n,4400+n,true),C=L.cols;H.banner=null;
  H.EGP.noart=flag==='noart';H.EGP.noover=flag==='noover';H.clearRooms();const P=H.P;P.inv=1e9;P.x=-999;
  let cx,cy,pts=[],th=L.theme.style;
  if(k==='window'){const w=L.windows[i],x=w.c*32+16,y=w.r*64+38;cx=x;cy=y;const c=document.createElement('canvas').getContext('2d'),p=H.windowPath(th,x,y);c.lineWidth=2;
    for(let yy=y-16;yy<=y+16;yy+=0.5)for(let xx=x-12;xx<=x+12;xx+=0.5)if(c.isPointInPath(p,xx,yy)&&!c.isPointInStroke(p,xx,yy))pts.push([xx,yy]);}
  else{let X,Y,ys,open;if(k==='gate'){const o=L.dyn.filter(o=>o.f.t==='gate')[i];o.f.open=0;o.f.tm=0;X=o.c*32;Y=o.r*64;ys=(o.r+1)*64-4;}
    else{const f=L.lifts[i];f.y=(f.yT+f.yB)/2;f.gT=0;f.gB=0;L.base[f.rT*C+f.sc]=0;const s=e?f.sB:f.sT,rr=e?f.rB:f.rT;X=(s<0?f.sc*32-3.5:(f.sc+1)*32+3.5)-16;Y=rr*64;ys=(rr+1)*64-4;}
    H.gateGeom(X,Y,ys,{open:0});const g=H.gateGeom(X,Y,ys,{open:0}),pl=g.pl,a=pl.L0,b=pl.R0,T=7;cx=X+16;cy=(pl.top+ys)/2;
    for(let yy=pl.top+20;yy<=ys;yy+=0.5){for(let xx=a-T/2+1.5;xx<=a+T/2-1.5;xx+=0.5)pts.push([xx,yy]); // the narrow face, below the ceiling's shade
      for(let xx=a+T/2+1.5;xx<=b+T/2-1.5;xx+=0.5){const y0=pl.ce(xx-T/2)-3+(xx-a-T/2)*0;if(yy>y0+20&&yy<pl.fl(xx-T/2)-1.5)pts.push([xx,yy]);}}}
  H.cam.x=cx-H.viewW/2;H.cam.y=cy-64*1.1;H.cam.gy=H.cam.y;H.mode='play';H.GLP&&(H.GLP.pipe=false);
  H.render();H.render();H.render();const X=H.XF,cv=[...document.querySelectorAll('canvas')].find(c=>c.getBoundingClientRect().width>0),R=cv.getBoundingClientRect();
  const m=([x,y])=>[R.left+(x*X.VZ-X.camD)/cv.width*R.width,R.top+(y*X.VZ-X.camDY)/cv.height*R.height];
  return {pts:pts.map(m),c:m([cx,cy]),th:H.themeName(n)};}'''


def page(b, mode):
    pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=2)
    pg.errs = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e)))
    pg.goto('file://' + SRC)
    pg.wait_for_timeout(700)
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.body.classList.remove('panelOpen')")
    pg.evaluate("m=>{__HK.S.set.lightMode=m;}", mode)
    return pg


if __name__ == '__main__':
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
        bad, tot, worst, errs = {}, {}, [], []
        for mode in MODES:
            pg = page(b, mode)
            for n in range(LO, HI + 1):
                for it in pg.evaluate(LIST, n):
                    k, i, e = it[0], it[1], (it[2] if len(it) > 2 else 0)
                    flag = 'noover' if k == 'window' else 'noart'
                    r1 = pg.evaluate(SHOW, [n, k, i, e, '']); im1 = Image.open(io.BytesIO(pg.screenshot())).convert('RGB')
                    pg.evaluate(SHOW, [n, k, i, e, flag]); im0 = Image.open(io.BytesIO(pg.screenshot())).convert('RGB')
                    px = {(int(x * 2), int(y * 2)) for x, y in r1['pts'] if 0 <= x * 2 < im1.width and 0 <= y * 2 < im1.height}
                    if len(px) < 20:
                        continue
                    key = (k, mode); tot[key] = tot.get(key, 0) + 1
                    A, B0 = im1.load(), im0.load(); nb = 0
                    for q in px:
                        u, v = A[q], B0[q]
                        if abs(u[0] - v[0]) + abs(u[1] - v[1]) + abs(u[2] - v[2]) > 24: nb += 1
                    if nb > 6:
                        bad[key] = bad.get(key, 0) + 1
                        if len(worst) < 16:
                            cx, cy = int(r1['c'][0] * 2), int(r1['c'][1] * 2); c = im1.crop((cx - 120, cy - 110, cx + 120, cy + 110))
                            ImageDraw.Draw(c).text((4, 3), '%s %d %s %d.%d %s (%d px)' % (mode, n, k, i, e, r1['th'][:14], nb), fill=(255, 240, 160)); worst.append(c)
            errs += pg.errs; pg.close()
        for k in ('window', 'gate', 'lift'):
            print('%-7s with wall art over the opening: %s' % (k, ', '.join('%s %d of %d' % (m, bad.get((k, m), 0), tot.get((k, m), 0)) for m in MODES)))
        print('errors', errs[:3])
        if worst:
            sh = Image.new('RGB', (4 * 242, ((len(worst) + 3) // 4) * 222), (20, 16, 24))
            for i, c in enumerate(worst):
                sh.paste(c, ((i % 4) * 242, (i // 4) * 222))
            sh.save(OUT); print('wrote', OUT)
        b.close()
