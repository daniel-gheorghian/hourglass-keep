from playwright.sync_api import sync_playwright
import json,sys
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(400)
    print('load errors',errs[:3])
    r=pg.evaluate('''()=>{const H=__HK,out=[];for(const n of [1,2,5,9,14,20,26]){for(let s=0;s<3;s++){let L;try{const t=performance.now();L=H.genLevel(n,5000+s*31,true);const dt=performance.now()-t;
        out.push({n,s,ms:+dt.toFixed(1),cols:L.cols,rows:L.rows,runs:L.runsInfo?L.runsInfo.length:0,strip:!L.plan||L.plan.runs.length===1&&L.plan.turns.length===0,W:L.plan&&L.plan.W,H:L.plan&&L.plan.H});}catch(e){out.push({n,s,err:String(e),stack:e.stack.split('\\n').slice(0,4).join(' | ')});}}}return out;}''')
    for x in r: print(x)
    print('errors',errs[:3]); b.close()
