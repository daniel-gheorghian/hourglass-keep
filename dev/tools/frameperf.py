from playwright.sync_api import sync_playwright
import sys,json
f=sys.argv[1]; bj=sys.argv[2]
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':844,'height':390}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+f); pg.wait_for_timeout(300); pg.add_script_tag(path=bj)
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    for n in [9,20]:
        r=pg.evaluate('''(n)=>{const ts=[];let k=0;const r=runBot(n,4242+n,{fight:false,stop:H=>{if(++k%2===0){const t=performance.now();H.roomWork();H.render();ts.push(performance.now()-t);}return k>60*240;}});
          ts.sort((a,b)=>a-b);return {ok:r.ok,frames:ts.length,p50:+ts[Math.floor(ts.length/2)].toFixed(2),p99:+ts[Math.floor(ts.length*0.99)].toFixed(2),max:+ts[ts.length-1].toFixed(2),over16:ts.filter(t=>t>16).length,builds:__HK.roomBuilds};}''',n)
        print(f.split('/')[-1][:12],n,r)
    print(errs[:3]); b.close()
