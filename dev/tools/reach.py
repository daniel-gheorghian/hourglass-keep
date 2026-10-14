from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(300)
    r=pg.evaluate('''()=>{const H=__HK;const L=H.genLevel(10,700983,true);const o=L.dyn.find(o=>o.f.t==='pend');let maxx=-1e9,minx=1e9;
      for(let t=0;t<5;t+=0.005){const f=o.f;const px=o.c*32+16,py=(()=>{let rr=o.r-1;while(rr>=0&&L.base[rr*L.cols+o.c]!==2)rr--;return (rr+1)*64;})();const Lp=(o.r+1)*64-4-40-py;const th=f.amp*Math.sin(6.2832*(t+f.off)/f.per);
        const bx=px+Lp*Math.sin(th),by=py+Lp*Math.cos(th);const P_y=(o.r+1)*64-4;if(by>P_y-50){maxx=Math.max(maxx,bx-px);minx=Math.min(minx,bx-px);}}
      return {hitZoneFromPivot:[+minx.toFixed(1),+maxx.toFixed(1)],plusBody:11};}''')
    print(json.dumps(r)); b.close()
