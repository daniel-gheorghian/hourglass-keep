from playwright.sync_api import sync_playwright
from PIL import Image
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2)
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(400); pg.add_script_tag(path='bot.js')
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    ims=[]
    for i,(n,st) in enumerate([(5,'hang'),(6,'climb'),(9,'hang'),(10,'climb'),(13,'hang'),(17,'climb'),(7,'crawl'),(11,'push')]):
        r=pg.evaluate('''([n,st])=>{let k=0;const r=runBot(n,777+n,{fight:false,stop:H=>{const p=H.P;if(p.state===st){k++;return k>(st==='climb'?(window.__ck||14):st==='crawl'?20:6);}return false;}});
          const H=__HK;H.render();const cam=H.cam,rc=document.getElementById('game').getBoundingClientRect(),sc=rc.height/192;
          let x=rc.left+(H.P.x-cam.x-60)*sc,y=rc.top+(H.P.y-cam.y-110)*sc;const w=120*sc,h=140*sc;x=Math.max(0,Math.min(innerWidth-w,x));y=Math.max(0,Math.min(innerHeight-h,y));return {ok:r.ok,clip:{x,y,width:w,height:h}};}''',[n,st])
        if r['ok']!='stopped': print('no',n,st,r['ok']); continue
        pg.screenshot(path=f'hs{i}.png',clip=r['clip']); ims.append(Image.open(f'hs{i}.png'))
    w,h=ims[0].size; cols=4; rows=(len(ims)+cols-1)//cols
    sheet=Image.new('RGB',(cols*(w+8),rows*(h+8)),(20,16,28))
    for i,im in enumerate(ims): sheet.paste(im,((i%cols)*(w+8),(i//cols)*(h+8)))
    sheet=sheet.resize((sheet.width//2,sheet.height//2)); sheet.save('hangshots.png'); print(errs)
    b.close()
