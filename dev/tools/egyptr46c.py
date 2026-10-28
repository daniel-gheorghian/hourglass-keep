# egyptr46c.py old.html new.html [outdir] [torch|classic]: round 46c's pictures (owner: "as a rule, if you add contours or accents always use a
# darker shade of the pixels that are closer to the edge or lighter if light hits it - with some tinting of course"; "apply it everywhere").
# For each prop the round changed, three instances across themes and hours (floors FLOORS, seed 1, the first of the kind found on each, up to
# three), old | new, the prop's crop at 3x (a world box 80 x 84 round it, 3 px a world px):
#   r46c_props_<mode>.png   rows: the props; columns: three instances, each old | new
#   r46c_phone_<n>.png      whole views at phone size (852 x 393), old over new, both modes, on a few floors
# Run from dev/tools (HK_GPU=0: WebGL in SwiftShader).
import io, os, sys
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright
a = sys.argv[1:]
OLD, NEW = os.path.abspath(a[0]), os.path.abspath(a[1])
OUT = os.path.abspath(a[2]) if len(a) > 2 and a[2] not in ('torch', 'classic') else os.path.dirname(os.path.abspath(__file__))
MODES = [m for m in ('torch', 'classic') if m in a] or ['torch', 'classic']
GPU = [] if os.environ.get('HK_GPU') == '0' else ['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist', '--force_high_performance_gpu']
FLOORS = [5, 9, 13, 18, 22, 27, 30, 34, 41, 46]
KINDS = ['lamp', 'flask', 'plate', 'xplate', 'lplate', 'closer', 'block', 'gate', 'chomp', 'lift', 'bar', 'pend', 'clock', 'darter', 'saw', 'spikes',
         'banner', 'jamb', 'stone', 'loose', 'door']
PHONE = [(9, 1), (22, 1), (34, 1)]
DSF, BW, BH = 3, 80, 84

LIST = r'''([n,sd])=>{const H=__HK;window.__HKfreeze=true;const L=H.load(n,sd,false),TW=32,TH=64,S=r=>(r+1)*TH-4,out=[];
  const add=(k,x,y)=>out.push([k,x,y]);
  for(const o of L.dyn)add(o.f.t,o.f.t==='bar'&&o.f.x?o.f.x:o.c*TW+16,o.f.t==='bar'&&o.f.y?o.f.y+24:o.f.t==='gate'||o.f.t==='chomp'||o.f.t==='pend'?S(o.r)-14:S(o.r)); // (the bar at its own height)
  for(const t of L.torches)if(!t.broken)add('lamp',t.c*TW+16,S(t.r)-14);
  add('door',L.door.c*TW+16,S(L.door.r)-10);for(const q of L.cps)add('clock',q.x,S(q.r)-8);for(const b of L.ext.blocks)add('block',b.c*TW+16,S(b.r)-14);
  for(const it of L.items)if(!it.hidden)add('flask',it.x,S(it.r));for(const lf of L.lifts)add('lift',(lf.ca+lf.cb+1)*TW/2,S(lf.rB)-20);
  for(const k of L.courts||[])add('jamb',k.c0*TW,S(k.r)-20);return [out,H.themeName(n)];}'''
SHOW = r'''([n,sd,fx,fy,kind])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS)H.S.hints[id]=1;const L=H.L&&H.L.n===n&&H.L.seed===H.levelSeed(n)?H.L:H.load(n,sd,false);
  H.banner=null;const P=H.P;P.x=-999;P.y=-999;
  if(kind==='stone')for(const o of L.dyn)if(o.f.t==='stone'&&Math.abs(o.c*32+16-fx)<2){o.f.s=3;o.f.land=-99;L.rubble.add(o.r*L.cols+o.c);}
  H.setClock(()=>1e6);H.setGT(10);H.clearRooms();H.cam.x=fx-H.viewW/2;H.cam.y=fy-192*0.62;H.cam.gy=H.cam.y;if(H.GLP){H.GLP.pipe=false;H.GLP.rs=1;window.__HKnoauto=true;}for(let i=0;i<4;i++)H.render();
  const X=H.XF,cv=[...document.querySelectorAll('canvas')].find(c=>c.getBoundingClientRect().width>0),R=cv.getBoundingClientRect(),k=X.VZ/cv.width*R.width;
  return [R.left-X.camD/cv.width*R.width,R.top-X.camDY/cv.height*R.height,k];}'''


def label(im, t):
    d = ImageDraw.Draw(im); d.rectangle((0, 0, 6 + 6 * len(t), 12), fill=(0, 0, 0)); d.text((3, 0), t, fill=(250, 240, 215))


def shoot(pg, n, sd, kind, fx, fy, whole=False):
    q = pg.evaluate(SHOW, [n, sd, fx, fy, kind]); im = Image.open(io.BytesIO(pg.screenshot())).convert('RGB')
    if whole: return im.resize((852, 393), Image.LANCZOS)
    k = q[2] * DSF; x0, y0 = q[0] * DSF + (fx - BW / 2) * k, q[1] * DSF + (fy - BH + 20) * k
    return im.crop((int(x0), int(y0), int(x0 + BW * k), int(y0 + BH * k))).resize((BW * 3, BH * 3), Image.LANCZOS)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True); errs = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=GPU); pages = {}
        for src in (OLD, NEW):
            for mode in MODES:
                pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=DSF); pg.on('pageerror', lambda e: errs.append(str(e)))
                pg.goto('file://' + src); pg.wait_for_timeout(800)
                pg.evaluate("()=>{document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.body.classList.remove('panelOpen');const st=document.createElement('style');st.textContent='.ctl,#pause,#pauseBtn,#pad{display:none!important}';document.head.appendChild(st);}")
                pg.evaluate("m=>{__HK.S.set.lightMode=m;__HK.GLFX.sheen=false;}", mode); pages[(src, mode)] = pg
        pick = {k: [] for k in KINDS}  # (kind -> [(n, x, y, theme)], the first of the kind on each floor, three floors)
        for n in FLOORS:
            out, th = pages[(NEW, MODES[0])].evaluate(LIST, [n, 1]); seen = set()
            for k, x, y in out:
                if k in pick and k not in seen and len(pick[k]) < 3: pick[k].append((n, x, y, th)); seen.add(k)
        for mode in MODES:
            rows = [k for k in KINDS if pick[k]]; cw, ch = BW * 3, BH * 3
            sh = Image.new('RGB', (3 * (2 * cw + 10), len(rows) * (ch + 4)), (20, 16, 24))
            for i, k in enumerate(rows):
                for j, (n, x, y, th) in enumerate(pick[k]):
                    for s, src in enumerate((OLD, NEW)):
                        im = shoot(pages[(src, mode)], n, 1, k, x, y); label(im, '%s %s fl%d %s' % ('v87' if src == OLD else '46c', k, n, th[4:26])); sh.paste(im, (j * (2 * cw + 10) + s * cw, i * (ch + 4)))
                print(mode, k, flush=True)
            sh.save(os.path.join(OUT, 'r46c_props_%s.png' % mode)); print('wrote props', mode)
        for n, sd in PHONE:
            out, th = pages[(NEW, MODES[0])].evaluate(LIST, [n, sd]); g = next((q for q in out if q[0] in ('gate', 'lift', 'block')), out[0])
            ph = Image.new('RGB', (852 * len(MODES) + 6, 2 * 393 + 6), (20, 16, 24))
            for i, mode in enumerate(MODES):
                for j, src in enumerate((OLD, NEW)):
                    im = shoot(pages[(src, mode)], n, sd, g[0], g[1], g[2], True); label(im, '%s fl%d %s %s' % ('v87' if src == OLD else '46c', n, th, mode)); ph.paste(im, (i * 858, j * 399))
            ph.save(os.path.join(OUT, 'r46c_phone_%d.png' % n)); print('wrote phone', n)
        if errs: print('errors', errs[:3])
        b.close()
