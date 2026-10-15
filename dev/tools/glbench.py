# ms per frame, Classic vs Torchlight (headless Chromium = software GL, so only the ratio means anything).
# render() time includes the texture upload and the draw calls; gl.finish() after it makes the GPU work count too.
from playwright.sync_api import sync_playwright
import sys
floors=[int(x) for x in sys.argv[1:]] or [2,5,13]
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':844,'height':390}); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(300)
    pg.evaluate("window.__HKfreeze=true;window.__HKnoauto=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    for n in floors:
        r=pg.evaluate('''(n)=>{const H=__HK,L=H.load(n,9000+n,false);H.G.length=0;const t=L.torches.find(t=>t.c>8)||L.torches[0];const x=t.c*32-40;
          H.P.x=x;H.P.y=(t.r+1)*64-4;H.P.fallY=H.P.y;H.P.state='stand';H.P.inv=1e9;H.cam.snap=true;H.tick(2);H.mode='play';
          for(let k=0;k<120;k++){H.P.x=x;H.P.inv=1e9;H.tick(1);}
          const out={};for(const m of ['classic','torch','classic','torch']){H.S.set.lightMode=m;for(let k=0;k<20;k++)H.render();
            const t0=performance.now();for(let k=0;k<120;k++){H.tick(1);H.render();if(H.GLP.gl&&m==='torch')H.GLP.gl.finish();}out[m]=(performance.now()-t0)/120;}
          return out;}''',n)
        print('floor',n,{k:round(v,2) for k,v in r.items()})
    print('errors',errs); b.close()
