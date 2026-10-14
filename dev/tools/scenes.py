from playwright.sync_api import sync_playwright
from PIL import Image
import sys
out=sys.argv[1]; src=sys.argv[2] if len(sys.argv)>2 else '/Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2)
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+src); pg.wait_for_timeout(500)
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    ims=[]
    for i,(n,kind,dx) in enumerate([(2,'stone',-50),(6,'gate',-40),(10,'chomp',-30),(14,'gate',-40),(18,'spikes',-60),(7,'start',0)]):
        pg.evaluate('''([n,kind,dx])=>{const H=__HK;let o=null,L;for(let s=0;s<80&&!o;s++){L=H.load(n,700+s,true);o=kind==='start'?{c:L.start.x/32|0,r:L.start.r,f:{}}:L.dyn.find(q=>q.f.t===kind&&q.c>6);}
          H.P.x=o.c*32+16+dx;H.P.y=(o.r+1)*64-4;H.P.fallY=H.P.y;H.P.state='stand';H.P.face=1;H.cam.snap=true;H.tick(1);H.P.x=o.c*32+16+dx;
          if(o.f.t==='gate'){o.f.open=0;o.f.tm=0;} if(o.f.t==='spikes')o.f.ext=1; H.cam.snap=true;H.tick(1);H.render();}''',[n,kind,dx])
        pg.screenshot(path=f'sc{i}.png'); ims.append(Image.open(f'sc{i}.png'))
    w,h=ims[0].size; sheet=Image.new('RGB',(w*2+10,h*3+20),(20,16,28))
    for i,im in enumerate(ims): sheet.paste(im,((i%2)*(w+10),(i//2)*(h+10)))
    sheet=sheet.resize((sheet.width//2,sheet.height//2)); sheet.save(out); print(errs)
    b.close()
