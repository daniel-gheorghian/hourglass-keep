# beamshot.py [file.html] [out.png] [i,j,..]: a contact sheet of the sky beams in Torchlight (frames sent at once, GLP.pipe=false):
# a fixed set of floors and times of day (the Forge by Moonlight with its arches and breaches, dusk, dawn and other themes),
# each framed on an opening (window, open arch or breach), some with the prince standing in its beam where it lands.
# Run it on the old release (hk_v57_release.html) and on the source for a before/after. Run from dev/tools.
import os, sys
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
SRC = next((x for x in a if x.endswith('.html')), os.path.join(HERE, '..', 'hourglass-keep.html'))
OUT = next((x for x in a if x.endswith('.png')), os.path.join(HERE, 'beamshot.png'))
ONLY = next((x for x in a if x[:1] in '0123456789'), None)  # (a list of shot indices, e.g. 0,6: only those, at full size)
# (floor, kind wanted: arch, br, win or any; the prince in the beam; which match to take)
SHOTS = [(34, 'arch', True, 0), (34, 'br', False, 0), (34, 'arch', False, 1), (34, 'win', True, 0),
         (31, 'arch', True, 0), (38, 'win', False, 0), (7, 'arch', True, 0), (3, 'win', False, 0),
         (45, 'arch', True, 0), (53, 'win', False, 0), (42, 'br', True, 0), (27, 'br', True, 0)]
FIND = r'''([n,kind,skip])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS)H.S.hints[id]=1;let k=0;
  for(let sd=1;sd<60;sd++){const L=H.load(n,700+sd,true);H.banner=null;const sb=H.skyBeam();
    for(const o of H.ryOps()){if(kind!=='any'&&o.kind!==kind)continue;if(o.x0<12*32||o.x1>(L.cols-12)*32)continue;
      const r=Math.round((o.fl+4)/64)-1,cy=(o.y0+o.y1)/2,lx=(o.x0+o.x1)/2+sb.dx/sb.dy*(o.fl-cy),c=Math.floor(lx/32);
      if(r<0||r>=L.rows||!H.solidBelow(c,r)||!H.solidBelow(c-1,r)||!H.solidBelow(c+1,r))continue;
      if(k++<skip)continue;window.__O={x:(o.x0+o.x1)/2,y:cy,lx,r,fl:o.fl,kind:o.kind};return [n,700+sd,H.themeName(n),o.kind];}}
  return null;}'''
PLACE = r'''(inb)=>{const H=__HK,o=window.__O,P=H.P;P.inv=1e9;P.x=inb?o.lx:o.lx+(o.lx<o.x?-70:70);P.y=(o.r+1)*64-4;P.fallY=P.y;P.state='stand';P.face=o.lx<o.x?1:-1;
  H.cam.snap=true;H.tick(2);P.x=inb?o.lx:P.x;H.GLP&&(H.GLP.pipe=false);H.render();H.render();H.render();const X=H.XF,cv=document.querySelector('canvas'),R=cv.getBoundingClientRect();
  const m=(x,y)=>[R.left+(x*X.VZ-X.camD)/cv.width*R.width,R.top+(y*X.VZ-X.camDY)/cv.height*R.height];
  return {o:m(o.x,o.y),f:m(o.lx,o.fl)};}'''
TW_, TH_ = 900, 640  # (device px cropped, then halved)
tiles = []
with sync_playwright() as p:
    b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
    for i_, (n, kind, inb, skip) in enumerate(SHOTS):
        if ONLY and str(i_) not in ONLY.split(','):
            continue
        pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=2)
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto('file://' + os.path.abspath(SRC))
        pg.wait_for_timeout(400)
        pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true)")
        pg.evaluate("()=>{__HK.S.set.lightMode='torch'}")
        f = pg.evaluate(FIND, [n, kind, skip])
        if not f:
            print('none', n, kind); pg.close(); continue
        r = pg.evaluate(PLACE, inb)
        tmp = os.path.join(HERE, '_beamshot_tmp.png')
        pg.screenshot(path=tmp)
        im = Image.open(tmp).convert('RGB')
        cx = (r['o'][0] + r['f'][0])
        cy = (r['o'][1] + r['f'][1])
        x0 = int(min(max(0, cx - TW_ / 2), im.width - TW_)); y0 = int(min(max(0, cy - TH_ / 2), im.height - TH_))
        t = im.crop((x0, y0, x0 + TW_, y0 + TH_)).resize((TW_ // (1 if ONLY else 2), TH_ // (1 if ONLY else 2)), Image.LANCZOS)
        ImageDraw.Draw(t).text((6, 4), '%d s%d %s %s%s' % (f[0], f[1], f[2], f[3], ' +P' if inb else ''), fill=(255, 255, 0))
        tiles.append(t)
        print(f, r, 'errors', errs[:2])
        pg.close()
        os.remove(tmp)
    b.close()
cols, w2, h2 = (min(2, len(tiles)), TW_, TH_) if ONLY else (3, TW_ // 2, TH_ // 2)
sheet = Image.new('RGB', (w2 * cols, h2 * ((len(tiles) + cols - 1) // cols)))
for i, t in enumerate(tiles):
    sheet.paste(t, ((i % cols) * w2, (i // cols) * h2))
sheet.save(OUT)
print('wrote', OUT)
