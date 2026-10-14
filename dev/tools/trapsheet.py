from playwright.sync_api import sync_playwright
from PIL import Image
import sys
out=sys.argv[1] if len(sys.argv)>1 else 'trapsheet.png'
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=3)
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(500)
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    shots=[]
    jobs=[('chomp',9,0.5,False),('chomp',9,0.03,False),('chomp',9,0.10,False),('chomp',9,0.10,True),('chomp',13,0.5,False),('chomp',13,0.25,True),
          ('spikes',9,1,False),('spikes',9,0.5,False),('spikes',13,1,False)]
    for i,(kind,n,ph,blood) in enumerate(jobs):
        box=pg.evaluate('''([kind,n,ph,blood])=>{const H=__HK;let o=null;for(let s=0;s<80&&!o;s++){const L=H.load(n,300+s,true);o=L.dyn.find(q=>q.f.t===kind&&(kind!=='spikes'||q.c%2===s%2));}
          const f=o.f;H.P.x=o.c*32-60;H.P.y=(o.r+1)*64-4;H.P.fallY=H.P.y;H.P.state='stand';H.cam.snap=true;H.tick(1);H.P.x=o.c*32-60;
          if(kind==='chomp'){f.off=ph*f.per-H.gameTime;f.blood=blood;}else{f.ext=ph;}
          H.render();
          const cam=H.cam,r=document.getElementById('game').getBoundingClientRect(),sc=r.height/192;
          return {x:r.left+(o.c*32-cam.x-17)*sc,y:r.top+(o.r*64-cam.y-12)*sc,width:66*sc,height:80*sc};}''',[kind,n,ph,blood])
        pg.screenshot(path=f'tr{i}.png',clip=box); shots.append(f'tr{i}.png')
    ims=[Image.open(s) for s in shots];W=sum(i.width for i in ims)+8*len(ims);Hh=max(i.height for i in ims)
    sheet=Image.new('RGB',(W,Hh),(20,16,28));x=0
    for im in ims:sheet.paste(im,(x,0));x+=im.width+8
    sheet.save(out);print(errs)
    b.close()
