from playwright.sync_api import sync_playwright
import os,sys,json
f=sys.argv[1]; n=int(sys.argv[2]); idx=int(sys.argv[3]); out=sys.argv[4]; mark=len(sys.argv)>5
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2); pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+os.path.abspath(f)); pg.wait_for_timeout(500)
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    r=pg.evaluate('''([n,idx,mark])=>{const H=__HK;const all=[];for(let s=0;s<16;s++){const L=H.load(n,5555+s*11,true);const hs=H.breaches().filter(Boolean);for(const h of hs)all.push([s,h]);}
      const [s,h0]=all[idx%all.length];const L=H.load(n,5555+s*11,true);const h=H.breaches().filter(Boolean).find(q=>q.c0===h0.c0&&q.r===h0.r);
      const mc=Math.round((h.c0+h.c1)/2);const P=H.P;P.x=(h.c1+1)*32+40;P.y=(h.r+1)*64-4;P.fallY=P.y;P.state='stand';P.face=-1;H.cam.snap=true;H.tick(2);H.cam.snap=true;H.tick(10);H.render();
      return {s,c0:h.c0,c1:h.c1,r:h.r,style:L.theme.style,n:all.length,x0:h.x0,x1:h.x1,y0:h.y0,y1:h.y1,pieces:h.pieces.length};}''',[n,idx,mark])
    print(r)
    pg.locator('#game').screenshot(path=out); print(errs[:3]); b.close()
