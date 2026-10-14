from playwright.sync_api import sync_playwright
from PIL import Image
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2)
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(400)
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    found=pg.evaluate('''()=>{const H=__HK;for(let s=0;s<300;s++){const n=6+(s%14);const L=H.load(n,1200+s,true);const bl=L.ext.blocks.find(b=>b.c>4&&L.base[b.r*L.cols+b.c-1]!==2&&L.base[(b.r-1)*L.cols+b.c-1]!==2);if(bl){window.__bl={n,s:1200+s,c:bl.c,r:bl.r};return window.__bl;}}return null;}''')
    print(found)
    ims=[]
    for i,mode in enumerate(['stand','hang','climb1','climb2','climb3']):
        clip=pg.evaluate('''(mode)=>{const H=__HK,q=window.__bl;const L=H.load(q.n,q.s,true);const xe=q.c*32,ys=(q.r)*64-4;
          H.P.face=1;
          if(mode==='stand'){H.P.x=xe-6.5;H.P.y=(q.r+1)*64-4;H.P.state='stand';H.cam.snap=true;H.tick(30);}
          else{H.P.x=xe-7;H.P.y=ys+57;H.P.state='hang';H.P.t=0;H.P.ledge={c:q.c,r:q.r-1,s:-1,xe,ys};H.P.vx=0;H.P.vy=0;H.cam.snap=true;H.tick(30);
            if(mode!=='hang'){H.setKey('kb','u',true);H.tick(1);H.setKey('kb','u',false);H.tick(mode==='climb1'?8:mode==='climb2'?17:24);}}
          H.render();const cam=H.cam,rc=document.getElementById('game').getBoundingClientRect(),sc=rc.height/192;
          return {x:rc.left+(xe-50-cam.x)*sc,y:rc.top+(ys-50-cam.y)*sc,width:100*sc,height:130*sc,st:H.P.state};}''',mode)
        st=clip.pop('st');print(mode,st)
        pg.screenshot(path=f'bk{i}.png',clip=clip); ims.append(Image.open(f'bk{i}.png'))
    w,h=ims[0].size; sheet=Image.new('RGB',(len(ims)*(w+8),h),(20,16,28))
    for i,im in enumerate(ims): sheet.paste(im,(i*(w+8),0))
    sheet=sheet.resize((sheet.width//2,sheet.height//2)); sheet.save('blockcheck.png'); print(errs); b.close()
