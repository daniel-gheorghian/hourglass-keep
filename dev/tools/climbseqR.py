from playwright.sync_api import sync_playwright
from PIL import Image
import sys
out=sys.argv[1] if len(sys.argv)>1 else 'climbseq.png'
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=3)
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(400); pg.add_script_tag(path='bot.js')
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    # stop at the first hang on a wall's near face
    r=pg.evaluate('''()=>{window.__fl=9;return runBot(window.__fl||7,782,{fight:false,stop:H=>{const p=H.P;if(p.state==='hang'&&p.ledge&&p.ledge.s>0){const b=H.L.base[(p.ledge.r+1)*H.L.cols+p.ledge.c];return true;}return false;}});}''')
    print(r.get('ok'))
    ims=[]
    for i in range(12):
        clip=pg.evaluate('''(i)=>{const H=__HK;
          if(i===1){H.setKey('kb','u',true);}
          if(i>0)H.tick(i===1?1:5); if(i===1)H.setKey('kb','u',false);
          H.render();const lg=H.P.ledge,cam=H.cam,rc=document.getElementById('game').getBoundingClientRect(),sc=rc.height/192;
          return {x:rc.left+(lg.xe-30-cam.x)*sc,y:rc.top+(lg.ys-50-cam.y)*sc,width:70*sc,height:110*sc,st:H.P.state};}''',i)
        st=clip.pop('st'); pg.screenshot(path=f'cs{i}.png',clip=clip); ims.append(Image.open(f'cs{i}.png')); print(i,st)
    w,h=ims[0].size; sheet=Image.new('RGB',(len(ims)*(w+6),h),(20,16,28))
    for i,im in enumerate(ims): sheet.paste(im,(i*(w+6),0))
    sheet=sheet.resize((sheet.width//2,sheet.height//2)); sheet.save(out); print(errs)
    b.close()
