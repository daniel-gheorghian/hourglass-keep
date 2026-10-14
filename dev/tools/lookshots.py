from playwright.sync_api import sync_playwright
from PIL import Image
import sys
out=sys.argv[1] if len(sys.argv)>1 else 'look.png'
scenes=[(2,8003,None),(7,8000,(249,6)),(10,8000,(120,5)),(14,8001,None),(18,8000,(51,3)),(6,8001,(89,6))]
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2)
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(500)
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    ims=[]
    for i,(n,sd,tp) in enumerate(scenes):
        pg.evaluate('''([n,sd,tp])=>{const H=__HK;const L=H.load(n,sd,false);let x,r;if(tp){x=tp[0]*32-30;r=tp[1];}else{const t=L.torches.find(t=>t.c>8);x=t.c*32-30;r=t.r;}
          H.P.x=x;H.P.y=(r+1)*64-4;H.P.fallY=H.P.y;H.P.state='stand';H.P.face=1;H.cam.snap=true;H.tick(2);H.P.x=x;H.cam.snap=true;H.tick(30);H.render();}''',[n,sd,tp])
        pg.screenshot(path=f'lk{i}.png'); ims.append(Image.open(f'lk{i}.png'))
    w,h=ims[0].size; sheet=Image.new('RGB',(2*w+10,3*h+20),(0,0,0))
    for i,im in enumerate(ims): sheet.paste(im,((i%2)*(w+10),(i//2)*(h+10)))
    sheet.resize((sheet.width//2,sheet.height//2)).save(out); print(errs); b.close()
