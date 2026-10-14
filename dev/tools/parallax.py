from playwright.sync_api import sync_playwright
from PIL import Image
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2); pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(500)
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    ims=[]
    for i,dx in enumerate([0,90,180]):
        pg.evaluate(f'''()=>{{const H=__HK;H.load(7,8000,true);H.P.x=249*32-30+{dx};H.P.y=7*64-4;H.P.state='stand';H.P.face=1;H.cam.snap=true;H.tick(2);H.P.x=249*32-30+{dx};H.cam.snap=true;H.tick(1);H.render();}}''')
        pg.screenshot(path=f'px{i}.png'); ims.append(Image.open(f'px{i}.png').crop((0,0,1688,560)).resize((844,280)))
    sh=Image.new('RGB',(844,3*290));[sh.paste(im,(0,k*290)) for k,im in enumerate(ims)];sh.save('parallax.png');print(errs);b.close()
