from playwright.sync_api import sync_playwright
from PIL import Image
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2)
    pg=ctx.new_page(); pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(500)
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    ims=[]
    for i,(n,rx) in enumerate([(3,2),(9,3),(15,4),(19,2)]):
        pg.evaluate('''([n,rx])=>{const H=__HK;const L=H.load(n,4242,true);H.P.x=rx*320;H.P.y=(L.start.r+1)*64-4;H.P.state='stand';H.cam.snap=true;H.tick(1);H.cam.x=rx*320-200;H.render();}''',[n,rx])
        pg.screenshot(path=f'se{i}.png'); ims.append(Image.open(f'se{i}.png'))
    w,h=ims[0].size; sheet=Image.new('RGB',(w*2+10,h*2+10),(20,16,28))
    for i,im in enumerate(ims): sheet.paste(im,((i%2)*(w+10),(i//2)*(h+10)))
    sheet.save('seams.png'); b.close()
