from playwright.sync_api import sync_playwright
import json,sys
for src in sys.argv[1:]:
  with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2)
    pg=ctx.new_page(); pg.goto('file://'+src); pg.wait_for_timeout(500)
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    r=pg.evaluate('''()=>{const H=__HK,out={};const sink=document.createElement('canvas');sink.width=sink.height=1;const sc=sink.getContext('2d');
      for(const n of [2,6,10,14,18]){const L=H.load(n,999,true);H.render();const times=[];
        // force fresh builds of a strip of rooms by moving the camera far and rendering
        for(let k=0;k<12;k++){H.P.x=(k*1.0+2)*320;H.cam.snap=true;H.tick(1);const t0=performance.now();H.render();const g=document.getElementById('game').getContext('2d');g.getImageData(0,0,1,1);times.push(performance.now()-t0);}
        times.sort((a,b)=>a-b);out[n]={median:+times[6].toFixed(1),max:+times[11].toFixed(1)};}
      return out;}''')
    print(src.split('/')[-1],json.dumps(r)); b.close()
