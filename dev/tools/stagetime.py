from playwright.sync_api import sync_playwright
import sys,json,os
for f in sys.argv[1:]:
  with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2); pg=ctx.new_page()
    pg.goto('file://'+os.path.abspath(f)); pg.wait_for_timeout(500)
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    r=pg.evaluate('''()=>{const H=__HK,out={};for(const n of [3,7,11,15,19]){H.load(n,4242,true);H.P.x=40*32;H.cam.snap=true;H.tick(2);H.render();const ts=[];
        // walk the camera along and time every staged build step it does on its own
        for(let k=0;k<40;k++){H.P.x=(40+k*4)*32;H.cam.snap=true;H.tick(1);for(let i=0;i<6;i++){const t=performance.now();const did=H.roomWork();const dt=performance.now()-t;if(did)ts.push(dt);}}
        ts.sort((a,b)=>a-b);out[n]={steps:ts.length,median:+ts[Math.floor(ts.length/2)].toFixed(2),p90:+ts[Math.floor(ts.length*0.9)].toFixed(2),max:+ts[ts.length-1].toFixed(2)};}return out;}''')
    print(f.split('/')[-1],json.dumps(r)); b.close()
