from playwright.sync_api import sync_playwright
from PIL import Image
import io,sys
out=sys.argv[1]; n=int(sys.argv[2]); state=int(sys.argv[3])
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2); pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(500)
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    r=pg.evaluate('''([n,state])=>{const H=__HK;for(let s=0;s<40;s++){const L=H.load(n,900+s*11,true);const hs=(L.hangings||[]).filter(h=>state<0?true:h.state===state);
        // pick one with another hanging or lamp close by
        const hg=hs.find(h=>(L.hangings||[]).some(o=>o!==h&&o.r===h.r&&Math.abs(o.c-h.c)<9))||hs[0];if(!hg)continue;
        const P=H.P;P.x=hg.x+70;P.y=(hg.r+1)*64-4;P.fallY=P.y;P.state='stand';P.face=-1;H.cam.snap=true;H.tick(2);P.x=hg.x+70;H.cam.snap=true;H.tick(30);H.render();return [s,hg.c,hg.r];}return null;}''',[n,state])
    print(r); pg.locator('#game').screenshot(path=out); print(errs[:3]); b.close()
