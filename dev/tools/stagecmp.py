from playwright.sync_api import sync_playwright
from PIL import Image, ImageChops
def shot(staged,path):
  with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2)
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(500)
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    n=pg.evaluate('''(staged)=>{const H=__HK;H.load(14,4242,true);H.P.x=40*32;H.cam.snap=true;H.tick(2);let n=0;if(staged){for(let i=0;i<200;i++)if(H.roomWork())n++;}H.render();return [n,H.roomBuilds,H.drawBuilds];}''',staged)
    pg.screenshot(path=path); b.close(); return n,errs
print(shot(True,'st_a.png')); print(shot(False,'st_b.png'))
a=Image.open('st_a.png').convert('RGB');b=Image.open('st_b.png').convert('RGB');d=ImageChops.difference(a,b);print('bbox of differences',d.getbbox(),'max',max(px for band in d.split() for px in [band.getextrema()[1]]))
