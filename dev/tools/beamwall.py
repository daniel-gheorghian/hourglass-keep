# beamwall.py [new.html] [old.html] [out.png]: sky beams that cross a solid wall's front face (round 15, owner: "the light beams are producing
# light around corners"). Finds openings whose beam, on its way down to its floor, passes over the front face of a wall block (one beside a
# window, a shaft beside a wall, a pit under an opening), frames each, and draws it in Torchlight and Classic for both builds, at the
# phone's canvas 1:1 (crops of the 1704 px canvas shown at 1x). Also prints, per shot, how much beam light lands on wall front faces in
# Torchlight (the S target read back over the wall cells: should be 0 after). Run from dev/tools.
import io, os, sys
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
NEW = os.path.abspath(next((x for x in a if x.endswith('.html')), os.path.join(HERE, '..', 'hourglass-keep.html')))
OLD = os.path.abspath(next((x for x in a[1:] if x.endswith('.html')), os.path.join(HERE, '..', '_r14.html')))
OUT = next((x for x in a if x.endswith('.png')), os.path.join(HERE, 'egypt_themes', 'r15_beams.png'))
# (floor, which match): floor 4 is the owner's palace window
SHOTS = [(4, 0), (4, 1), (3, 0), (7, 0), (9, 0), (23, 0)]
FIND = r'''([n,skip])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS)H.S.hints[id]=1;let k=0;
  for(let sd=1;sd<40;sd++){const L=H.load(n,700+sd,true);H.banner=null;const sb=H.skyBeam(),C=L.cols,B=(c,r)=>L.base[r*C+c];
    for(const o of H.ryOps()){if(o.sh.own||o.x0<12*32||o.x1>(L.cols-12)*32)continue;const cx=(o.x0+o.x1)/2,cy=(o.y0+o.y1)/2;let hit=null;
      for(let t=4;t<(o.fl-cy)/sb.dy;t+=3){const x=cx+sb.dx*t,y=cy+sb.dy*t,c=Math.floor((x+8)/32),r=Math.floor(y/64);if(r>=0&&r<L.rows&&B(c,r)===2){hit=[x,y];break;}} // (the front face of cell c covers x from c*32-8)
      if(!hit)continue;if(k++<skip)continue;window.__O={x:cx,y:cy,hx:hit[0],hy:hit[1]};return [n,700+sd,H.themeName(n),o.kind];}}
  return null;}'''
SHOW = r'''()=>{const H=__HK,o=window.__O,P=H.P;P.inv=1e9;P.x=-999;P.y=(Math.floor(o.hy/64)+1)*64-4;P.state='stand';H.cam.x=o.hx-H.viewW/2;H.cam.y=o.hy-64*1.2;H.cam.gy=H.cam.y;
  H.mode='play';H.GLP&&(H.GLP.pipe=false);H.render();H.render();H.render();const X=H.XF,cv=[...document.querySelectorAll('canvas')].find(c=>c.getBoundingClientRect().width>0),R=cv.getBoundingClientRect();
  return [R.left+((o.x+o.hx)/2*X.VZ-X.camD)/cv.width*R.width,R.top+((o.y+o.hy)/2*X.VZ-X.camDY)/cv.height*R.height];}'''


def page(b, src, mode):
    pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=2)
    pg.errs = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e)))
    pg.goto('file://' + src)
    pg.wait_for_timeout(700)
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.body.classList.remove('panelOpen')")
    pg.evaluate("m=>{__HK.S.set.lightMode=m;}", mode)
    return pg


def crop(pg, xy, cw, ch):
    im = Image.open(io.BytesIO(pg.screenshot())).convert('RGB')
    x0 = int(min(max(0, xy[0] * 2 - cw / 2), im.width - cw)); y0 = int(min(max(0, xy[1] * 2 - ch / 2), im.height - ch))
    return im.crop((x0, y0, x0 + cw, y0 + ch))


if __name__ == '__main__':
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
        P = {(t, m): page(b, s, m) for t, s in (('before', OLD), ('after', NEW)) for m in ('torch', 'classic')}
        rows, errs = [], []
        for n, k in SHOTS:
            q = P[('after', 'torch')].evaluate(FIND, [n, k])
            if not q:
                print('no case', n, k); continue
            print('case', q, flush=True)
            tl = []
            for m in ('torch', 'classic'):
                for t in ('before', 'after'):
                    pg = P[(t, m)]; pg.evaluate(FIND, [n, k]); xy = pg.evaluate(SHOW); im = crop(pg, xy, 420, 340)
                    ImageDraw.Draw(im).text((4, 3), '%s %s, floor %d %s' % (t, m, q[0], q[3]), fill=(240, 230, 210)); tl.append(im)
            w, h = tl[0].size; row = Image.new('RGB', (4 * w + 6, h), (20, 16, 24))
            for i, im in enumerate(tl):
                row.paste(im, (i * (w + 2), 0))
            rows.append(row)
        W = rows[0].width; sh = Image.new('RGB', (W, sum(r.height + 4 for r in rows)), (20, 16, 24)); y = 0
        for r in rows:
            sh.paste(r, (0, y)); y += r.height + 4
        sh.save(OUT)
        for pg in P.values():
            errs += pg.errs
        print('errors', errs[:4]); b.close()
