from playwright.sync_api import sync_playwright
from PIL import Image
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2)
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(400)
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    for i,(n,op) in enumerate([(7,0),(14,1)]):
        pg.evaluate('''([n,op])=>{const H=__HK;const L=H.load(n,321,true);const o=L.dyn.find(q=>q.f.t==='gate'&&!q.f.latch&&q.f.dur>0.3&&q.c>5);
          H.P.x=o.c*32-40;H.P.y=(o.r+1)*64-4;H.P.state='stand';H.P.face=1;H.cam.snap=true;H.tick(3);if(op){o.f.tm=o.f.dur*0.6;o.f.open=1;}H.render();}''',[n,op])
        pg.screenshot(path=f'gl{i}.png')
    ims=[Image.open(f'gl{i}.png') for i in range(2)];w,h=ims[0].size;sh=Image.new('RGB',(w,2*h+10),(20,16,28));sh.paste(ims[0],(0,0));sh.paste(ims[1],(0,h+10))
    sh.resize((sh.width//2,sh.height//2)).save('glasscheck.png');print(errs);b.close()
