from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':844,'height':390}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(400); pg.add_script_tag(path='bot.js')
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    for atmo in (True,False):
        r=pg.evaluate('''(atmo)=>{__HK.S.set.gfx.atmo=atmo;const m={chase:[],diss:[],calm:[]};let after=0;
          const res=runBot(11,788,{fight:false,stop:H=>{const c=H.L.ext.chase;if(!c||!c.on)return false;const t=performance.now();H.render();const ms=performance.now()-t;
            if(!c.done)m.chase.push(ms);else if(c.diss&&!c.diss.over)m.diss.push(ms);else{m.calm.push(ms);after++;}return after>120;}});
          const av=a=>a.length?+(a.reduce((x,y)=>x+y,0)/a.length).toFixed(2):null,p95=a=>a.length?+a.slice().sort((x,y)=>x-y)[Math.floor(a.length*0.95)].toFixed(2):null;
          return {atmo,res:res.ok,chase:[av(m.chase),p95(m.chase)],diss:[av(m.diss),p95(m.diss)],calm:[av(m.calm),p95(m.calm)],grains:null};}''',atmo)
        print(json.dumps(r))
    print('errors',errs[:3]); b.close()
