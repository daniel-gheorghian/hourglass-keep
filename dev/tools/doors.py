from playwright.sync_api import sync_playwright
from PIL import Image
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=3)
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(400)
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    ims=[]
    for i,(n,which,op) in enumerate([(6,'start',0),(6,'exit',0),(6,'exit',0.4),(6,'exit',1),(14,'exit',1),(18,'start',0)]):
        r=pg.evaluate('''([n,which,op])=>{const H=__HK;const L=H.load(n,4321,true);const c=which==='start'?1:L.door.c,rr=which==='start'?L.start.r:L.door.r;
          H.P.x=c*32+16-50;H.P.y=(rr+1)*64-4;H.P.state='stand';H.P.face=1;H.cam.snap=true;H.tick(1);H.P.x=c*32+16-50;L.door.open=op;L.door.opening=false;H.render();
          const cam=H.cam,rc=document.getElementById('game').getBoundingClientRect(),sc=rc.height/192;let x=rc.left+(c*32-cam.x-30)*sc,y=rc.top+(rr*64-cam.y-10)*sc;const w=100*sc,h=84*sc;x=Math.max(0,Math.min(innerWidth-w,x));y=Math.max(0,Math.min(innerHeight-h,y));return {x,y,width:w,height:h};}''',[n,which,op])
        pg.screenshot(path=f'dr{i}.png',clip=r); ims.append(Image.open(f'dr{i}.png'))
    w,h=ims[0].size; sheet=Image.new('RGB',(3*(w+8),2*(h+8)),(20,16,28))
    for i,im in enumerate(ims): sheet.paste(im,((i%3)*(w+8),(i//3)*(h+8)))
    sheet=sheet.resize((sheet.width*2//5,sheet.height*2//5)); sheet.save('doors.png'); print(errs)
    b.close()
