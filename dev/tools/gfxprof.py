from playwright.sync_api import sync_playwright
import json,os
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2)
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+os.getcwd()+'/prof3.html'); pg.wait_for_timeout(500); pg.add_script_tag(path='bot.js')
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    r=pg.evaluate('''()=>{const H=__HK;const g=document.getElementById('game').getContext('2d');let n=0,tot=0,fr=0;window.__pt={};
        runBot(11,788,{fight:true,stop:H2=>{if(++n%3)return false;const t0=performance.now();H.render();g.getImageData(0,0,1,1);tot+=performance.now()-t0;fr++;return n>9000;}});
        const o={frames:fr,total:+(tot/fr).toFixed(2)};for(const k in window.__pt)o[k]=+(window.__pt[k]/fr).toFixed(2);return o;}''')
    print(json.dumps(r),errs); b.close()
