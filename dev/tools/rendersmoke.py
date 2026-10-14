from playwright.sync_api import sync_playwright
import sys, time
lo,hi=int(sys.argv[1]),int(sys.argv[2])
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':844,'height':390}); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(300); pg.add_script_tag(path='bot.js')
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    res=[];tot=0;t0=time.time()
    for n in range(lo,hi+1):
        r=pg.evaluate('''(n)=>{let k=0,ms=0,cnt=0;const r=runBot(n,31337+n,{fight:true,stop:H=>{if(++k%20===0){const t=performance.now();H.render();ms+=performance.now()-t;cnt++;}return false;}});return {ok:r.ok,why:r.why,ms:ms/Math.max(1,cnt)};}''',n)
        res.append((n,r['ok'],r.get('why'),round(r['ms'],2)))
    print(res); print('errors',errs[:5]); b.close()
