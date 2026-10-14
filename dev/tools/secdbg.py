from playwright.sync_api import sync_playwright
import json,os
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':844,'height':390}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+os.path.abspath('dbg_sec.html')); pg.wait_for_timeout(400); pg.add_script_tag(path='bot.js')
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    r=pg.evaluate('''()=>{const out=[];let k=0;runBot(11,788,{fight:false,stop:H=>{const c=H.L.ext.chase;if(!c||!c.on)return false;window.__sec={};window.__lt=0;window.__sms=[];H.render();if((window.__sms[0]||0)>40)out.push({tot:+window.__sms[0].toFixed(0),sec:Object.fromEntries(Object.entries(window.__sec).map(([a,b])=>[a,+b.toFixed(1)])),top:0});return ++k>120;}});return out.slice(0,6);}''')
    for x in r: print(json.dumps(x))
    print(errs[:3]); b.close()
