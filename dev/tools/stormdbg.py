from playwright.sync_api import sync_playwright
import json,os
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':844,'height':390}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+os.path.abspath('dbg_storm.html')); pg.wait_for_timeout(400); pg.add_script_tag(path='bot.js')
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    r=pg.evaluate('''()=>{const tot=[];let after=0;runBot(11,788,{fight:false,stop:H=>{const c=H.L.ext.chase;if(!c||!c.on)return false;window.__sms=[];const t=performance.now();H.render();tot.push([+(performance.now()-t).toFixed(1),+((window.__sms[0]||0)).toFixed(1),c.done?1:0,Math.round(c.wx),Math.round(H.cam.y)]);if(c.done)after++;return after>60;}});
      const slow=tot.filter(x=>x[0]>40);return {n:tot.length,slow:slow.length,ex:slow.slice(0,12)};}''')
    print(json.dumps(r)); print(errs[:3]); b.close()
