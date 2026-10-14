from playwright.sync_api import sync_playwright
from PIL import Image
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=3)
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(500)
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    shots=[]
    for i,(theme_n,phase,blood) in enumerate([(9,0.5,False),(9,0.03,False),(9,0.10,False),(9,0.10,True),(1+12,0.5,False),(13,0.10,True)]):
        box=pg.evaluate('''([n,ph,blood])=>{const H=__HK;let o=null;for(let s=0;s<60&&!o;s++){const L=H.load(n,300+s,true);o=L.dyn.find(q=>q.f.t==='chomp');}
          const f=o.f;f.off=ph*f.per-H.gameTime;f.blood=blood;H.P.x=o.c*32-60;H.P.y=(o.r+1)*64-4;H.P.fallY=H.P.y;H.P.state='stand';H.cam.snap=true;H.tick(1);f.off=ph*f.per-H.gameTime;f.blood=blood;H.P.x=o.c*32-60;H.render();
          const cam=H.cam,VS=document.getElementById('game').height/192,r=document.getElementById('game').getBoundingClientRect(),sc=r.height/192;
          return {x:r.left+(o.c*32-cam.x-10)*sc,y:r.top+(o.r*64-cam.y-6)*sc,width:52*sc,height:76*sc};}''',[theme_n,phase,blood])
        print(box);pg.screenshot(path=f'jaw{i}.png',clip=box); shots.append(f'jaw{i}.png')
    ims=[Image.open(s) for s in shots];W=sum(i.width for i in ims)+10*len(ims);Hh=max(i.height for i in ims)
    sheet=Image.new('RGB',(W,Hh),(20,16,28));x=0
    for im in ims:sheet.paste(im,(x,0));x+=im.width+10
    sheet.save('jawsheet.png');print(errs)
    b.close()
