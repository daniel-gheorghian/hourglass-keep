from playwright.sync_api import sync_playwright
from PIL import Image
import base64,io
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2); pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(500)
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    r=pg.evaluate('''()=>{const H=__HK;let floors=0,withBig=0;for(let n=4;n<=30;n++)for(let s=0;s<10;s++){const L=H.genLevel(n,7000+n*31+s,true);floors++;if(L.items.some(i=>i.type==='big'))withBig++;}
      for(let n=6;n<=30;n++)for(let s=0;s<10;s++){const L=H.load(n,7000+n*31+s,true);const it=L.items.find(i=>i.type==='big');if(!it)continue;
        // a small red flask beside it for scale
        L.items.push({c:it.c+1,r:it.r,x:(it.c+1)*32+14,type:'heal',taken:false});
        const P=H.P;P.x=it.x-60;P.y=(it.r+1)*64-4;P.fallY=P.y;P.state='stand';P.face=1;H.cam.snap=true;H.tick(2);P.x=it.x-60;H.cam.snap=true;H.tick(10);H.render();
        const X=H.XF,cx=it.x*X.VZ-X.camD,cy=((it.r+1)*64-20)*X.VZ-X.camDY,c=document.getElementById('game'),o=document.createElement('canvas');o.width=420;o.height=220;
        o.getContext('2d').drawImage(c,cx-180,cy-120,420,220,0,0,420,220);return {u:o.toDataURL(),n,floors,withBig};}return {floors,withBig};}''')
    print(r.get('n'),'floors with a large flask',r['withBig'],'/',r['floors'],errs[:2])
    if 'u' in r: Image.open(io.BytesIO(base64.b64decode(r['u'].split(',')[1]))).save('flask_big.png')
    b.close()
