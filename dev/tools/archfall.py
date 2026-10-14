from playwright.sync_api import sync_playwright
from PIL import Image
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2)
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(400)
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    ims=[]
    for i,(n,phase) in enumerate([(7,0),(7,1),(11,0),(11,1)]):
        clip=pg.evaluate('''([n,phase])=>{const H=__HK;const L=H.load(n,6060,true);const lo=L.dyn.filter(o=>o.f.t==='loose'&&L.base[(o.r-1)*L.cols+o.c]===0&&o.c>6);const o=lo[0];
          H.P.x=o.c*32-70;H.P.y=(o.r+1)*64-4;H.P.state='stand';H.P.face=1;H.cam.snap=true;H.tick(2);H.P.x=o.c*32-70;
          const cx=H.cam.x,cy=H.cam.y;if(phase){o.f.s=1;o.f.tm=0;H.P.x=4*32;H.tick(60);H.cam.x=cx;H.cam.y=cy;for(let k=0;k<40;k++)H.roomWork();H.cam.x=cx;H.cam.y=cy;}
          H.render();const cam=H.cam,rc=document.getElementById('game').getBoundingClientRect(),sc=rc.height/192;
          let x=rc.left+(o.c*32-cam.x-80)*sc,y=rc.top+(o.r*64-cam.y-70)*sc;const w=190*sc,h=150*sc;x=Math.max(0,Math.min(innerWidth-w,x));y=Math.max(0,Math.min(innerHeight-h,y));return {x,y,width:w,height:h};}''',[n,phase])
        pg.screenshot(path=f'af{i}.png',clip=clip); ims.append(Image.open(f'af{i}.png'))
    w,h=ims[0].size; sheet=Image.new('RGB',(2*(w+8),2*(h+8)),(20,16,28))
    for i,im in enumerate(ims): sheet.paste(im,((i%2)*(w+8),(i//2)*(h+8)))
    sheet.resize((sheet.width//2,sheet.height//2)).save('archfall.png'); print(errs); b.close()
