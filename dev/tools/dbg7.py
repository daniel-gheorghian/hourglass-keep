from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(300)
    r=pg.evaluate('''()=>{const H=__HK;const L=H.load(16,701565,true);const P=H.P;P.x=4520;P.y=8*64-4;P.state='crouch';P.face=1;for(const s of H.SN)if(s.r===7&&s.lo<4500&&s.lo>4000){s.alive=false;s.gone=true;}
      H.setKey('kb','r',true);const out=[];for(let i=0;i<200;i++){H.tick(1);if(i%10===0)out.push(P.state+':'+P.x.toFixed(1)+':hp'+P.hp+' sn:'+H.SN.filter(s=>s.lo>4500&&s.lo<4700).map(s=>s.x.toFixed(0)+s.state).join());}return out;}''')
    print(json.dumps(r)); b.close()
