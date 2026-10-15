# Torchlight effects: shadow by a torch, vent shimmer, sandstorm, one scene per theme.  python3 s2shots.py outdir [names...]
# Each scene is drawn Classic and Torchlight; the file names are s2_<name>_<mode>.png
from playwright.sync_api import sync_playwright
import sys, os
out = sys.argv[1] if len(sys.argv) > 1 else '.'
only = sys.argv[2:]
scenes = [('shadow', 5, 8001, 'torch'), ('shadow2', 5, 8001, 'torchR'), ('vent', 13, 8000, 'vent'), ('storm', 12, 900, 'storm')]
for i, n in enumerate((1, 5, 9, 13, 17)):
    scenes.append(('theme%d' % (i + 1), n, 8000 + i, 'torch'))
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 844, 'height': 390}, device_scale_factor=2)
    pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(500)
    pg.evaluate("window.__HKfreeze=true;window.__HKnoauto=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    for name, n, sd0, kind in scenes:
        if only and name not in only: continue
        pos = None
        for sd in range(sd0, sd0 + 120):
            pos = pg.evaluate('''([n,sd,kind])=>{const H=__HK;const L=H.load(n,sd,false);H.G.length=0;let x,r;
              if(kind==='torch'||kind==='torchR'){const t=L.torches.filter(t=>t.c>8)[1]||L.torches.find(t=>t.c>8);if(!t)return null;x=t.c*32+(kind==='torchR'?48:-48);r=t.r;}
              else if(kind==='vent'){const o=L.dyn.find(o=>o.f.t==='vent'&&o.c>8);if(!o)return null;x=o.c*32-70;r=o.r;}
              else if(kind==='storm'){const c=L.ext.chase;if(!c)return null;x=(c.c0+8)*32;r=c.rBot-1;}
              H.P.x=x;H.P.y=(r+1)*64-4;H.P.fallY=H.P.y;H.P.state='stand';H.P.face=1;H.P.inv=1e9;H.cam.snap=true;H.tick(2);H.P.x=x;H.cam.snap=true;H.mode='play';
              if(kind==='storm'){const c=L.ext.chase;c.on=true;c.t=0;c.wx=x-150;}
              for(let k=0;k<60*3;k++){H.P.x=x;H.P.state='stand';H.P.inv=1e9;if(kind==='storm')L.ext.chase.wx=x-150;H.tick(1);}
              if(kind==='vent'){const o=L.dyn.find(o=>o.f.t==='vent'&&o.c>8);for(let k=0;k<600;k++){const f=o.f,ph=(((H.gameTime+f.off)%f.per)+f.per)%f.per/f.per;if(ph>0.8)break;H.P.x=x;H.P.inv=1e9;H.tick(1);}}
              return [x,r];}''', [n, sd, kind])
            if pos: break
        for mode in ('classic', 'torch'):
            pg.evaluate("m=>{__HK.S.set.lightMode=m;__HK.render();}", mode)
            pg.wait_for_timeout(50)
            pg.screenshot(path=os.path.join(out, 's2_%s_%s.png' % (name, mode)))
        print(name, n, pos)
    print(errs); b.close()
