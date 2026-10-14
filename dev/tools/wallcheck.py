from playwright.sync_api import sync_playwright
from PIL import Image
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2)
    pg=ctx.new_page(); pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(500)
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    ims=[]
    for i,(n,side) in enumerate([(7,1),(7,-1),(15,1),(18,-1)]):
        r=pg.evaluate('''([n,side])=>{const H=__HK;const L=H.load(n,555,true);let c0=-1,r0=-1;
          for(let r=0;r<L.rows&&c0<0;r++)for(let c=4;c<L.cols-4;c++){const b=(cc,rr)=>H.L.base[rr*L.cols+cc];if(b(c,r)!==2&&(b(c,r)===1||b(c,r+1)===2)&&b(c+side,r)===2&&b(c,r-1)!==2){c0=c;r0=r;break;}}
          H.P.x=side>0?(c0+1)*32-6.5:c0*32+6.5;H.P.y=(r0+1)*64-4;H.P.state='stand';H.P.face=side;H.cam.snap=true;H.tick(1);H.P.x=side>0?(c0+1)*32-6.5:c0*32+6.5;H.tick(25);H.render();
          const cam=H.cam,rc=document.getElementById('game').getBoundingClientRect(),sc=rc.height/192;let x=rc.left+(H.P.x-cam.x-50)*sc,y=rc.top+(H.P.y-cam.y-80)*sc;const w=100*sc,h=100*sc;x=Math.max(0,Math.min(innerWidth-w,x));y=Math.max(0,Math.min(innerHeight-h,y));return {x,y,width:w,height:h};}''',[n,side])
        pg.screenshot(path=f'wc{i}.png',clip=r); ims.append(Image.open(f'wc{i}.png'))
    w,h=ims[0].size; sheet=Image.new('RGB',(4*(w+8),h),(20,16,28))
    for i,im in enumerate(ims): sheet.paste(im,(i*(w+8),0))
    sheet=sheet.resize((sheet.width//2,sheet.height//2)); sheet.save('wallcheck.png'); b.close()
