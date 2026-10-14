from playwright.sync_api import sync_playwright
from PIL import Image
import io,base64
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=1)
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(400); pg.add_script_tag(path='bot.js')
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    frames=[]
    for n,seed,start,count in [(6,4106,"H.P.state==='run'&&H.P.t>0.5",110),(6,4106,"H.P.state==='garde'",110)]:
        pg.evaluate('''([n,seed,start])=>{const f=new Function('H','return '+start);window.__rec=[];let on=false,k=0;window.__bstop=null;
          window.__run=()=>runBot(n,seed,{fight:true,stop:H=>{if(!on&&f(H))on=true;if(on){k++;if(k%2===0){H.render();window.__rec.push(document.getElementById('game').toDataURL('image/jpeg',0.8));}if(window.__rec.length>=window.__max)return true;}return false;}});}''',[n,seed,start])
        pg.evaluate(f"window.__max={count};__run()")
        data=pg.evaluate("window.__rec")
        for d in data:
            im=Image.open(io.BytesIO(base64.b64decode(d.split(',')[1]))).convert('RGB')
            frames.append(im.resize((im.width*2//3,im.height*2//3)))
    frames[0].save('gameplay.gif',save_all=True,append_images=frames[1:],duration=33,loop=0,optimize=True)
    print(len(frames),frames[0].size,errs); b.close()
