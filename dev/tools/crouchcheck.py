from playwright.sync_api import sync_playwright
from PIL import Image
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2)
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(400)
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    ims=[]
    for i,(n,sword) in enumerate([(7,False),(7,True),(15,True),(18,False)]):
        clip=pg.evaluate('''([n,sword])=>{const H=__HK;const L=H.load(n,555,true);let c0=-1,r0=-1;
          for(let r=1;r<L.rows&&c0<0;r++)for(let c=4;c<L.cols-4;c++){const b=(cc,rr)=>L.base[rr*L.cols+cc];if(b(c,r)!==2&&(b(c,r)===1||b(c,r+1)===2)&&b(c+1,r)===2&&b(c,r-1)!==2&&!L.feat[r*L.cols+c]){c0=c;r0=r;break;}}
          H.P.x=(c0+1)*32-6.5;H.P.y=(r0+1)*64-4;H.P.state='stand';H.P.face=1;H.cam.snap=true;H.tick(2);H.P.x=(c0+1)*32-6.5;
          H.setKey('kb','d',true);H.tick(20);if(sword){H.P.lowSword=true;H.P.sword=true;}H.tick(30);
          H.render();const cam=H.cam,rc=document.getElementById('game').getBoundingClientRect(),sc=rc.height/192;
          let x=rc.left+(H.P.x-cam.x-50)*sc,y=rc.top+(H.P.y-cam.y-70)*sc;const w=100*sc,h=84*sc;x=Math.max(0,Math.min(innerWidth-w,x));y=Math.max(0,Math.min(innerHeight-h,y));
          H.setKey('kb','d',false);return {x,y,width:w,height:h,st:H.P.state};}''',[n,sword])
        st=clip.pop('st');print(n,sword,st)
        pg.screenshot(path=f'cc{i}.png',clip=clip); ims.append(Image.open(f'cc{i}.png'))
    w,h=ims[0].size; sheet=Image.new('RGB',(4*(w+8),h),(20,16,28))
    for i,im in enumerate(ims): sheet.paste(im,(i*(w+8),0))
    sheet.resize((sheet.width//2,sheet.height//2)).save('crouchcheck.png'); print(errs); b.close()
