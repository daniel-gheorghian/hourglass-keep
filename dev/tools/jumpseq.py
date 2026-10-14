from playwright.sync_api import sync_playwright
from PIL import Image
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2)
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(400)
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    pg.evaluate('''()=>{const H=__HK;const L=H.load(7,1201,true);const q={c:301,r:4};window.__q=q;H.P.face=1;H.P.x=q.c*32-6.5;H.P.y=(q.r+1)*64-4;H.P.state='stand';H.cam.snap=true;H.tick(30);H.setKey('kb','u',true);}''')
    ims=[]
    for i,n in enumerate([0,4,4,4,4,4,4,8,20, 1,3,3,3,4,8]):
        clip=pg.evaluate('''([i,n])=>{const H=__HK,q=window.__q;if(i===1)H.setKey('kb','u',false);if(i===9){H.setKey('kb','d',true);}H.tick(n);if(i===10)H.setKey('kb','d',false);H.render();
          const xe=q.c*32,ys=q.r*64-4,cam=H.cam,rc=document.getElementById('game').getBoundingClientRect(),sc=rc.height/192;
          return {x:rc.left+(xe-40-cam.x)*sc,y:rc.top+(ys-40-cam.y)*sc,width:70*sc,height:120*sc,st:H.P.state};}''',[i,n])
        st=clip.pop('st');print(i,st,end='; ')
        pg.screenshot(path=f'js{i}.png',clip=clip); ims.append(Image.open(f'js{i}.png'))
    w,h=ims[0].size; sheet=Image.new('RGB',(len(ims)*(w+6),h),(20,16,28))
    for i,im in enumerate(ims): sheet.paste(im,(i*(w+6),0))
    sheet=sheet.resize((sheet.width//2,sheet.height//2)); sheet.save('jumpseq.png'); print(errs); b.close()
