from playwright.sync_api import sync_playwright
from PIL import Image
import sys
out=sys.argv[1] if len(sys.argv)>1 else 'snakes.png'
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=3); pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(500)
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    ims=[]
    for i,(st,t,old) in enumerate([('slither',0.3,1),('slither',0.3,0),('slither',0.65,0),('coil',0.3,0),('strike',0.12,0),('dead',0.3,0)]):
        clip=pg.evaluate('''([st,t,old])=>{const H=__HK;H.S.set.gfx.hd=!old;let L;for(let s=0;s<80;s++){L=H.load(11,700+s,false);if(H.SN.length)break;}const sn=H.SN[0];H.G.length=0;
          H.P.x=sn.x-70;H.P.y=sn.y;H.P.state='stand';H.P.face=1;H.cam.snap=true;H.tick(2);H.P.x=sn.x-70;
          sn.state=st==='dead'?'dead':st;sn.t=t;sn.dir=-1;if(st==='strike')sn.lunge=Math.sin(Math.PI*Math.min(1,t/0.22))*16;else sn.lunge=0;if(st==='dead'){sn.alive=false;}sn.ph=1.7+t;
          H.render();const cam=H.cam,rc=document.getElementById('game').getBoundingClientRect(),sc=rc.height/192;
          return {x:rc.left+(sn.x-cam.x-36)*sc,y:rc.top+(sn.y-cam.y-28)*sc,width:64*sc,height:34*sc};}''',[st,t,old])
        pg.screenshot(path=f'sk{i}.png',clip=clip); ims.append(Image.open(f'sk{i}.png'))
    w,h=ims[0].size; sh=Image.new('RGB',(3*(w+6),2*(h+6)));[sh.paste(im,((i%3)*(w+6),(i//3)*(h+6))) for i,im in enumerate(ims)]
    sh.resize((sh.width*3//5,sh.height*3//5)).save(out); print(errs); b.close()
