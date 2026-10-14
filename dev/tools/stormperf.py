from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2); pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(500); pg.add_script_tag(path='bot.js')
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true)")
    out={}
    for atmo in (0,1):
        r=pg.evaluate(f'''()=>{{const H=__HK;H.S.set.gfx.atmo={'true' if atmo else 'false'};const g=document.getElementById('game').getContext('2d');const ts=[];
          runBot(11,788,{{fight:false,stop:H2=>{{const c=H.L.ext.chase;if(c&&c.on&&(c.fade||0)<1){{const t0=performance.now();H.render();g.getImageData(0,0,1,1);ts.push(performance.now()-t0);}}return false;}}}});
          ts.sort((a,b)=>a-b);return {{n:ts.length,p50:+ts[ts.length>>1].toFixed(1),p95:+ts[Math.floor(ts.length*0.95)].toFixed(1)}};}}''')
        out['atmo'+str(atmo)]=r
    print(json.dumps(out),errs); b.close()
