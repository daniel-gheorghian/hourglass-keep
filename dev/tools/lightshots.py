# Torchlight vs Classic: the same spots drawn both ways. python3 lightshots.py outdir
from playwright.sync_api import sync_playwright
import sys, os
out=sys.argv[1] if len(sys.argv)>1 else '.'
scenes=[('hall',5,8001,'torch'),('dark',2,8003,'dark'),('vent',7,8000,'vent'),('flask',3,8000,'flask'),('forge',13,8001,'torch')]
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2)
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(500)
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    for name,n,sd0,kind in scenes:
      for sd in range(sd0,sd0+40):
        pos=pg.evaluate('''([n,sd,kind])=>{const H=__HK;const L=H.load(n,sd,false);H.G.length=0;let x,r;
          if(kind==='torch'){const t=L.torches.find(t=>t.c>8);x=t.c*32-40;r=t.r;}
          else if(kind==='vent'){const o=L.dyn.find(o=>o.f.t==='vent');if(!o)return null;x=o.c*32-60;r=o.r;}
          else if(kind==='flask'){const it=L.items.find(i=>!i.taken&&i.c>6);if(!it)return null;x=it.x-50;r=it.r;}
          else{let bd=-1;for(const it of L.items){if(it.taken||it.c<8)continue;let d=1e9;for(const t of L.torches)d=Math.min(d,Math.abs(t.c-it.c)+Math.abs(t.r-it.r)*6);if(d>bd){bd=d;x=it.x-40;r=it.r;}}}
          H.P.x=x;H.P.y=(r+1)*64-4;H.P.fallY=H.P.y;H.P.state='stand';H.P.face=1;H.P.inv=1e9;H.cam.snap=true;H.tick(2);H.P.x=x;H.cam.snap=true;H.mode='play';
          for(let k=0;k<60*3;k++){H.P.x=x;H.P.state='stand';H.P.inv=1e9;H.tick(1);}return [x,r];}''',[n,sd,kind])
        if pos:break
      if 1:
        for mode in ('classic','torch'):
            pg.evaluate("m=>{__HK.S.set.lightMode=m;__HK.render();}",mode)
            pg.screenshot(path=os.path.join(out,f's_{name}_{mode}.png'))
        print(name,pos)
    print(errs); b.close()
