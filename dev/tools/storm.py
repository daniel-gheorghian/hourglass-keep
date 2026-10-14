from playwright.sync_api import sync_playwright
from PIL import Image
import sys
out=sys.argv[1] if len(sys.argv)>1 else 'storm.png'
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2); pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(500); pg.add_script_tag(path='bot.js')
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    ims=[]
    for i,(n,atmo,k) in enumerate([(11,0,200),(11,1,200),(8,1,140),(14,1,260)]):
        pg.evaluate(f'''()=>{{__HK.S.set.gfx.atmo={'true' if atmo else 'false'};let k=0;return runBot({n},777+{n},{{fight:false,stop:H=>{{const c=H.L.ext.chase;if(c&&c.on&&(c.fade||0)<1){{k++;return k>{k};}}return false;}}}});}}''')
        pg.evaluate("__HK.render()"); pg.screenshot(path=f'stm{i}.png'); ims.append(Image.open(f'stm{i}.png'))
    w,h=ims[0].size; sh=Image.new('RGB',(2*w+10,2*h+10));[sh.paste(im,((i%2)*(w+10),(i//2)*(h+10))) for i,im in enumerate(ims)]
    sh.resize((sh.width//2,sh.height//2)).save(out); print(errs); b.close()
