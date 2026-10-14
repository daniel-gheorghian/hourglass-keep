from playwright.sync_api import sync_playwright
from PIL import Image
import sys
out=sys.argv[1] if len(sys.argv)>1 else 'skels.png'
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=3); pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(500)
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    ims=[]
    for i,(pose,old) in enumerate([('garde',1),('garde',0),('windup',0),('lunge',0),('hurt',0),('stand',0)]):
        clip=pg.evaluate('''([pose,old])=>{const H=__HK;H.S.set.gfx.hd=!old;let L,g=null;for(let s=0;s<200&&!g;s++){L=H.load(18,800+s,false);g=H.G.find(q=>q.skel);}
          for(const q of H.G)if(q!==g){q.alive=false;q.gone=true;}
          H.P.x=g.x-60;H.P.y=g.y;H.P.state='stand';H.P.face=1;H.cam.snap=true;H.tick(2);H.P.x=g.x-60;g.state=pose==='stand'?'idle':'garde';g.face=-1;g.pose=Object.assign({},H.PS[pose]);H.tick(1);g.pose=Object.assign({},H.PS[pose]);
          H.render();const cam=H.cam,rc=document.getElementById('game').getBoundingClientRect(),sc=rc.height/192;
          return {x:rc.left+(g.x-cam.x-38)*sc,y:rc.top+(g.y-cam.y-66)*sc,width:64*sc,height:72*sc};}''',[pose,old])
        pg.screenshot(path=f'skl{i}.png',clip=clip); ims.append(Image.open(f'skl{i}.png'))
    w,h=ims[0].size; sh=Image.new('RGB',(len(ims)*(w+6),h));[sh.paste(im,(i*(w+6),0)) for i,im in enumerate(ims)]
    sh.resize((sh.width*2//5,sh.height*2//5)).save(out); print(errs); b.close()
