# tilescan.py [file.html] [lo hi] [out.png] [torch|classic|both] [views=K] [sheen]: wall art over the floor's tiles (round 35c, owner after v80:
# "wall decorations over the tiles"; openscan.py and doorscan.py do the openings and the doors). For every floor lo..hi (default 1..48: all twelve
# themes), seed 4400+n, in Torchlight and in Classic, the camera is set on up to K (default 4) of the floor's tiles that are drawn live (a cracked
# slab over a corridor or a well, a plank, a plate, a closer, a grating: drawRoomStatic leaves their cells to drawDynamic), and every floor
# tile in the view (live, plain, or the top of a pushed block: drawBlock) is compared with the same frame drawn with the room's back-wall art
# left out and its openings left open (EGP.noart 'atop': courses, friezes, posts, bands, frames, hangings, scars flattened to the wall's tone;
# the sky's light unchanged): its top face and lip (1.3 px in from their edges) must not change. Torchlight's relief reads the room's picture,
# which has the wall's art and no slab under a live tile or block, so it embossed the posts and friezes behind on it until round 35c
# (glRelFloors). Torchlight's wet sheen (round 31, crypt and
# dungeon floors) is off unless 'sheen' is given: it mirrors the lit things over the floor on purpose (a pale post in a sky beam among them),
# a reflection, not art drawn on the tile; with it on, those tiles count too.
# A tile is bad when more than 6 of its pixels differ by more than 24 (sum of channels). Prints the counts per kind and mode, and a contact
# sheet of the worst cases. Run from dev/tools.
import io, os, sys
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
SRC = os.path.abspath(next((x for x in a if x.endswith('.html')), os.path.join(HERE, '..', 'hourglass-keep.html')))
NUM = [int(x) for x in a if x.isdigit()]
LO, HI = (NUM + [1, 48])[:2] if len(NUM) >= 2 else (1, 48)
OUT = next((x for x in a if x.endswith('.png')), os.path.join(HERE, 'tilescan.png'))
MODES = ['torch', 'classic'] if 'both' in a or not ('torch' in a or 'classic' in a) else (['torch'] if 'torch' in a else ['classic'])
VIEWS = int(next((x[6:] for x in a if x.startswith('views=')), '4'))
LIVE = "['plate','xplate','lplate','closer','grate']"
# the floor's live tiles, spread along it (every k-th, so the views sample the whole floor)
LIST = r'''([n,K])=>{const H=__HK;const L=H.load(n,4400+n,true),out=[];
  for(const o of L.dyn){const t=o.f.t;if((t==='loose'&&o.f.s<2)||%s.includes(t))out.push([o.c,o.r]);}
  if(out.length<=K)return out;const s=[];for(let i=0;i<K;i++)s.push(out[Math.floor((i+0.5)*out.length/K)]);return s;}''' % LIVE
# frame the tile (c,r); with the art (or without); returns every floor tile in view: [c, r, kind, top polygon, lip polygon] in css px
SHOW = r'''([n,c,r,noart])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS)H.S.hints[id]=1;const L=H.load(n,4400+n,true),C=L.cols;H.banner=null;
  H.EGP.noart=noart&&'atop';H.clearRooms();const P=H.P;P.inv=1e9;P.x=-999;H.cam.x=c*32+16-H.viewW/2;H.cam.y=(r+1)*64-64*1.6;H.cam.gy=H.cam.y;H.mode='play';H.GLP&&(H.GLP.pipe=false);H.gameTime=10;
  H.render();H.render();H.render();const X=H.XF,cv=[...document.querySelectorAll('canvas')].find(c=>c.getBoundingClientRect().width>0),R=cv.getBoundingClientRect();
  const m=([x,y])=>[R.left+(x*X.VZ-X.camD)/cv.width*R.width,R.top+(y*X.VZ-X.camDY)/cv.height*R.height];
  const B=(cc,rr)=>cc<0||rr<0||cc>=C||rr>=L.rows?2:L.base[rr*C+cc],x0=X.camD/X.VZ,y0=X.camDY/X.VZ,x1=x0+cv.width/X.VZ,y1=y0+cv.height/X.VZ,out=[];
  for(let rr=Math.max(0,Math.floor(y0/64));rr<=Math.min(L.rows-1,Math.floor(y1/64));rr++)for(let cc=Math.max(0,Math.floor(x0/32));cc<=Math.min(C-1,Math.floor(x1/32));cc++){
    const b=B(cc,rr);if(b===2||!(b===1||B(cc,rr+1)===2))continue;const f=L.feat[rr*C+cc];let kind=L.blockAt&&L.blockAt.get((rr+1)*C+cc)?'block':'plain'; // (the top of a pushed block, drawBlock)
    if(f){const t=f.t;if(t==='loose'){if(f.s>=2)continue;kind=f.plank?'plank':f.wl?'well':'loose';}else if(%s.includes(t))kind=t;}
    const X0=cc*32,ys=(rr+1)*64-4,fx=X0-8,fr=fx+32,ft=ys+4,yb=ys-4,wr=B(cc+1,rr)===2,lx=y=>fx+(ft-y)*2+2.6,rx=y=>wr?fr-1.5:fr+(ft-y)*2-2.6;
    if(fx<x0+4||fr+16>x1-4||yb<y0+4||ft+8>y1-4)continue;
    const ya=ft-1.3,yc=yb+1.3,top=[[lx(ya),ya],[rx(ya),ya],[rx(yc),yc],[lx(yc),yc]].map(m),la=kind==='plank'?ft+0.5:ft+1.2,lb=kind==='plank'?ft+1.9:ft+3.8,lip=[[fx+1.5,la],[fr-1.5,la],[fr-1.5,lb],[fx+1.5,lb]].map(m); // (a plank's front edge is 2.4 px, drawPlank)
    out.push([cc,rr,kind,top,lip]);}
  return {tiles:out,th:H.themeName(n)};}''' % LIVE


def page(b, mode):
    pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=2)
    pg.errs = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e)))
    pg.goto('file://' + SRC)
    pg.wait_for_timeout(700)
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.body.classList.remove('panelOpen')")
    pg.evaluate("m=>{__HK.S.set.lightMode=m;}", mode)
    if 'sheen' not in a:
        pg.evaluate("()=>{__HK.GLFX.sheen=false;}")  # (the wet floor's reflection of the lit wall: see above)
    return pg


def pixels(polys, w, h):  # the device pixels inside the polygons (css px, device scale 2)
    pts = [(x * 2, y * 2) for p in polys for x, y in p]
    x0, y0 = max(0, int(min(x for x, y in pts))), max(0, int(min(y for x, y in pts)))
    x1, y1 = min(w, int(max(x for x, y in pts)) + 2), min(h, int(max(y for x, y in pts)) + 2)
    if x1 <= x0 or y1 <= y0:
        return []
    mk = Image.new('L', (x1 - x0, y1 - y0), 0); d = ImageDraw.Draw(mk)
    for p in polys:
        d.polygon([(x * 2 - x0, y * 2 - y0) for x, y in p], fill=255)
    W = x1 - x0
    return [(x0 + i % W, y0 + i // W) for i, v in enumerate(mk.tobytes()) if v]


if __name__ == '__main__':
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
        bad, tot, worst, errs, where = {}, {}, [], [], []
        for mode in MODES:
            pg = page(b, mode)
            for n in range(LO, HI + 1):
                seen = set()
                for c, r in pg.evaluate(LIST, [n, VIEWS]):
                    if (c, r) in seen:
                        continue
                    r1 = pg.evaluate(SHOW, [n, c, r, False]); im1 = Image.open(io.BytesIO(pg.screenshot())).convert('RGB')
                    pg.evaluate(SHOW, [n, c, r, True]); im0 = Image.open(io.BytesIO(pg.screenshot())).convert('RGB')
                    A, B0 = im1.load(), im0.load()
                    for cc, rr, kind, top, lip in r1['tiles']:
                        if (cc, rr) in seen:
                            continue
                        seen.add((cc, rr))
                        px = pixels([top, lip], im1.width, im1.height)
                        if len(px) < 20:
                            continue
                        key = (kind, mode); tot[key] = tot.get(key, 0) + 1; nb = 0
                        for q in px:
                            u, v = A[q], B0[q]
                            if abs(u[0] - v[0]) + abs(u[1] - v[1]) + abs(u[2] - v[2]) > 24: nb += 1
                        if nb > 6:
                            bad[key] = bad.get(key, 0) + 1; where.append("%s %d %s %d,%d (%d px)" % (mode, n, kind, cc, rr, nb))
                            if len(worst) < 16:
                                xs = [x for x, y in px]; ys = [y for x, y in px]; cx, cy = (min(xs) + max(xs)) // 2, (min(ys) + max(ys)) // 2
                                cr = im1.crop((cx - 120, cy - 110, cx + 120, cy + 110))
                                ImageDraw.Draw(cr).text((4, 3), '%s %d %s %d,%d %s (%d px)' % (mode, n, kind, cc, rr, r1['th'][:14], nb), fill=(255, 240, 160)); worst.append(cr)
            errs += pg.errs; pg.close()
        kinds = sorted({k for k, m in tot})
        for k in kinds:
            print('%-7s tiles with wall art over the tile: %s' % (k, ', '.join('%s %d of %d' % (m, bad.get((k, m), 0), tot.get((k, m), 0)) for m in MODES)))
        nbad = sum(bad.values())
        if where:
            print("bad:", "; ".join(where[:24]))
        print('tilescan: %s (%d bad of %d tiles, floors %d-%d)' % ('ok' if nbad == 0 else 'FAIL', nbad, sum(tot.values()), LO, HI), 'errors', errs[:3])
        if worst:
            sh = Image.new('RGB', (4 * 242, ((len(worst) + 3) // 4) * 222), (20, 16, 24))
            for i, c in enumerate(worst):
                sh.paste(c, ((i % 4) * 242, (i // 4) * 222))
            sh.save(OUT); print('wrote', OUT)
        b.close()
