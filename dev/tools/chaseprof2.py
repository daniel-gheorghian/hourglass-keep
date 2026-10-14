from playwright.sync_api import sync_playwright
import json,sys
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2)
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+__import__('os').getcwd()+'/prof.html'); pg.wait_for_timeout(500); pg.add_script_tag(path='bot.js')
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    r=pg.evaluate('''()=>{const H=__HK;const fr=[];let chaseOn=0;window.__rb=[];
      const res=runBot(11,788,{fight:false,stop:H=>{const ch=H.L.ext.chase,on=!!(ch&&ch.on&&(ch.fade||0)<1);const nb=window.__rb.length;
        const t0=performance.now();H.render();const ctx=document.getElementById('game').getContext('2d');ctx.getImageData(0,0,1,1);const dt=performance.now()-t0;
        fr.push({on,dt,builds:window.__rb.length-nb,bt:window.__rb.slice(nb).reduce((a,b)=>a+b,0)});return false;}});
      const ch=fr.filter(f=>f.on),no=fr.filter(f=>!f.on);
      const sum=a=>{const d=a.map(f=>f.dt).sort((x,y)=>x-y);const nob=a.filter(f=>!f.builds).map(f=>f.dt).sort((x,y)=>x-y);const q=(s,p)=>s.length?+s[Math.min(s.length-1,Math.floor(p*s.length))].toFixed(2):0;
        return {frames:a.length,median:q(d,.5),p90:q(d,.9),p99:q(d,.99),max:q(d,1),framesWithBuild:a.filter(f=>f.builds).length,avgBuildMs:+(a.reduce((s,f)=>s+f.bt,0)/Math.max(1,a.reduce((s,f)=>s+f.builds,0))).toFixed(1),medianNoBuild:q(nob,.5),p99NoBuild:q(nob,.99)};};
      const st=window.__st||[];return {ok:res.ok,chase:sum(ch),normal:sum(no),stormMs:st.length?+(st.reduce((a,b)=>a+b,0)/st.length).toFixed(2):0};}''')
    print(json.dumps(r,indent=0)); print('errors',errs); b.close()
