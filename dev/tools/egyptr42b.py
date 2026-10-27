# egyptr42b.py old.html new.html [outdir]: round 42b's pictures (owner: "Fix the drawing overlaps you choose are most noticeable").
# r42b_shadow.png: Torchlight, his lamp shadow on what stands before the back wall (shadowscan.py's scenes, the caster beyond him):
#   one row per kind (bar, rig, loop, lamp, sand: a well and a sand lift, debris, vent, dart), old | new at 3x, then old | new at phone size.
# r42b_bar.png: the swing bar's near pole and rope (drawn after him now), him swinging facing left and right at three angles, old | new in
#   Classic and Torchlight, 3x crops; a phone-size row.
# r42b_vent.png: him standing on a vent at the roar (0.86), the pilot (0.73) and the die-down (0.985), the back row of flames behind him now, old | new in both modes, 3x; a phone-size row.
# Run from dev/tools (Torchlight is software WebGL in headless Chromium unless HK_GPU=1).
import io, os, sys
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright
import shadowscan

HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
H = [os.path.abspath(x) for x in a if x.endswith('.html')]
OLD, NEW = (H + [os.path.join(HERE, '..', 'hourglass-keep.html')] * 2)[:2]
OUTD = next((x for x in a if not x.endswith('.html')), os.path.join(HERE, 'egypt_themes'))
os.makedirs(OUTD, exist_ok=True)
INK = (20, 16, 24)
GPU = ['--use-angle=metal', '--force_high_performance_gpu', '--enable-gpu', '--ignore-gpu-blocklist'] if os.environ.get('HK_GPU') else []
DSF = 3

# a world point -> css px on the page (after a render)
MAP = r'''(p)=>{const H=__HK,X=H.XF,cv=[...document.querySelectorAll('canvas')].find(q=>q.getBoundingClientRect().width>0),R=cv.getBoundingClientRect();
  return [R.left+(p[0]*X.VZ-X.camD)/cv.width*R.width,R.top+(p[1]*X.VZ-X.camDY)/cv.height*R.height,X.VZ/cv.width*R.width];}'''
# the swing: him on floor n's first bar at angle th facing face; the vent: him on floor n's first vent at its roar
SCENE = r'''([kind,n,sd,th,face,ph])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS){H.S.hints[id]=1;H.S.learned[id]=1;}
  const L=H.load(n,sd,true);H.banner=null;H.intro=0;H.mode='play';const P=H.P;P.inv=1e9;let fx,fy;
  if(kind==='bar'){const o=L.dyn.find(q=>q.f.t==='bar'),f=o.f;f.ps=0;f.pw=0;P.x=f.x;P.y=f.y+57;P.vx=P.vy=0;P.state='air';P.autoGrab=true;P.face=face;P.fallY=P.y;H.tick(1);
    P.swTh=th;P.swOm=0;for(let k=0;k<4;k++){P.swTh=th;P.swOm=0;H.tick(1);}fx=f.x;fy=f.y+16;}
  else{const o=L.dyn.find(q=>q.f.t==='vent'),f=o.f;f.off=(((ph||0.86)*f.per-H.gameTime)%f.per+f.per)%f.per;P.state='stand';P.face=face;P.x=o.c*32+16+th;P.y=(o.r+1)*64-4;P.fallY=P.y;P.vx=P.vy=0;fx=P.x;fy=P.y-26;}
  H.clearRooms();H.cam.x=fx-H.viewW/2;H.cam.y=fy-192*0.55;H.cam.gy=H.cam.y;H.GLP&&(H.GLP.pipe=false);H.render();H.render();H.render();return [fx,fy];}'''


def page(b, html, mode):
    pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=DSF)
    pg.errs = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e)))
    pg.goto('file://' + html); pg.wait_for_timeout(700)
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.body.classList.remove('panelOpen')")
    pg.evaluate("m=>{__HK.S.set.lightMode=m;__HK.GLFX.sheen=false;}", mode)
    pg.evaluate(shadowscan.JS)
    return pg


def grab(pg, cx, cy, hw, hh):
    q = pg.evaluate(MAP, [cx, cy])
    im = Image.open(io.BytesIO(pg.screenshot())).convert('RGB')
    k = q[2] * DSF
    x, y = q[0] * DSF, q[1] * DSF
    return im.crop((int(x - hw * k), int(y - hh * k), int(x + hw * k), int(y + hh * k))), im.resize((852, 393), Image.LANCZOS)


def label(im, t):
    d = ImageDraw.Draw(im); d.rectangle([0, 0, 8 + 6 * len(t), 13], fill=INK); d.text((4, 1), t, fill=(255, 240, 160)); return im


def sheet(rows, path):
    w = max(sum(c.width for c in r) + 6 * (len(r) - 1) for r in rows); h = sum(max(c.height for c in r) + 6 for r in rows)
    out = Image.new('RGB', (w, h), INK); y = 0
    for r in rows:
        x = 0
        for c in r: out.paste(c, (x, y)); x += c.width + 6
        y += max(c.height for c in r) + 6
    out.save(path); print('wrote', path)


SH = [('bar', 10, 1, 0), ('rig', 8, 1, 0), ('loop', 8, 1, 0), ('lamp', 9, 1, 0), ('lamp', 6, 1, 0), ('sand', 7, 1, 0), ('sand', 9, 1, 0),
      ('debris', 9, 1, 0), ('vent', 13, 1, 0), ('dart', 8, 1, 0)]

if __name__ == '__main__':
    with sync_playwright() as p:
        b = p.chromium.launch(args=GPU)
        pages = {(h, m): page(b, h, m) for h in (OLD, NEW) for m in ('classic', 'torch')}
        # the lamp shadow (Torchlight)
        rows, phone = [], {}
        for kind, n, sd, i in SH:
            row = []
            for h in (OLD, NEW):
                pg = pages[(h, 'torch')]
                r = pg.evaluate("([n,sd,k,i])=>SHS.show(n,sd,k,i,true,false)", [n, sd, kind, i])
                if not r: break
                q = pg.evaluate(MAP, [0, 0])
                if h == OLD or not r.get('shc'): cxy = r['mid']
                else:  # (the middle of the thing's carved outline near it, so the crop is on the thing; the old build takes the new one's)
                    pts = [pt for e in r['shc'] for rg in e['rings'] for pt in rg if abs(pt[0] - r['mid'][0]) < 60 * q[2] and abs(pt[1] - r['mid'][1]) < 70 * q[2]]
                    cxy = [(min(x for x, y in pts) + max(x for x, y in pts)) / 2, (min(y for x, y in pts) + max(y for x, y in pts)) / 2] if pts else r['mid']
                    row[-1] = None; row.pop()
                    po = pages[(OLD, 'torch')]; po.evaluate("([n,sd,k,i])=>SHS.show(n,sd,k,i,true,false)", [n, sd, kind, i])
                    mx = (cxy[0] - q[0]) / q[2]; my = (cxy[1] - q[1]) / q[2]
                    c0, f0 = grab(po, mx, my, 36, 28); row.append(label(c0, '%s %d/%d v86' % (kind, n, sd)))
                    if len(phone.get(kind, [])) == 1: phone[kind][-1] = label(f0, '%s v86 phone size' % kind)
                mx = (cxy[0] - q[0]) / q[2]; my = (cxy[1] - q[1]) / q[2]  # (back in world px)
                c, full = grab(pg, mx, my, 36, 28)
                row.append(label(c, '%s %d/%d %s' % (kind, n, sd, 'v86' if h == OLD else '42b')))
                if kind in ('lamp', 'sand') and len(phone.get(kind, [])) < 2: phone.setdefault(kind, []).append(label(full, '%s %s phone size' % (kind, 'v86' if h == OLD else '42b')))
            if row: rows.append(row)
        phone = list(phone.values())
        sheet(rows + phone, os.path.join(OUTD, 'r42b_shadow.png'))
        # the swing bar and the vent, both modes
        for kind, n, sd, cases, hw, hh, name in (('bar', 6, 502, [(t, f, 0) for f in (-1, 1) for t in (-0.6, 0.0, 0.6)], 34, 30, 'r42b_bar.png'),
                                                  ('vent', 13, 1, [(-2, 1, 0.86), (3, -1, 0.86), (-2, 1, 0.73), (3, -1, 0.985)], 30, 34, 'r42b_vent.png')):
            rows, phone = [], []
            for th, face, ph in cases:
                row = []
                for m in ('classic', 'torch'):
                    for h in (OLD, NEW):
                        pg = pages[(h, m)]
                        fx, fy = pg.evaluate(SCENE, [kind, n, sd, th, face, ph])
                        c, full = grab(pg, fx, fy, hw, hh)
                        row.append(label(c, '%s %s %s %+.1f %s' % (m[:5], 'v86' if h == OLD else '42b', 'L' if face < 0 else 'R', th, ('phase %.3f' % ph) if ph else '')))
                        if (th, face, ph) == cases[0]: phone.append(label(full, '%s %s' % (m, 'v86' if h == OLD else '42b')))
                rows.append(row)
            sheet(rows + [phone[:2], phone[2:]], os.path.join(OUTD, name))
        for pg in pages.values():
            if pg.errs: print('errors', pg.errs[:3])
        b.close()
