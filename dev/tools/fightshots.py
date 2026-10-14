from playwright.sync_api import sync_playwright
from PIL import Image
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2)
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(400); pg.add_script_tag(path='bot.js')
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    ims=[]
    for i,(n,cond) in enumerate([(6,"H.P.state==='strike'&&H.P.t>0.17&&H.P.t<0.24"),(9,"H.P.state==='strike'&&H.P.t>0.2&&H.P.t<0.26"),(12,"H.G.some(g=>g.state==='strike'&&g.trail&&g.trail.length>4)"),(15,"H.P.state==='blocked'&&H.P.t<0.05")]):
        r=pg.evaluate('''([n,cond])=>{let k=0;const f=new Function('H','return '+cond);const res=runBot(n,4100+n,{fight:true,stop:H=>{if(f(H)){k++;return k>1;}return false;}});__HK.render();return [res.ok,__HK.P.state];}''',[n,cond])
        print(n,r); pg.screenshot(path=f'fs{i}.png'); ims.append(Image.open(f'fs{i}.png'))
    w,h=ims[0].size; sheet=Image.new('RGB',(2*w+10,2*h+10),(0,0,0))
    for i,im in enumerate(ims): sheet.paste(im,((i%2)*(w+10),(i//2)*(h+10)))
    sheet.resize((sheet.width//2,sheet.height//2)).save('fights.png'); print(errs); b.close()
