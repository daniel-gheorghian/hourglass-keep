# the shader drops back to Classic by itself after ~2 s of slow frames (once past the compile window), with a notice once
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':844,'height':390}); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(300)
    r=pg.evaluate('''()=>{const H=__HK;H.S.set.lightMode='torch';H.render();const o={};
      for(let i=0;i<150;i++)H.glTime(16);o.fastStill=H.S.set.lightMode;       // 2.4 s at 16 ms: stays on
      for(let i=0;i<150;i++)H.glTime(40);o.slow=H.S.set.lightMode;            // 6 s at 40 ms: off
      H.render();o.shaderOn=H.shaderOn();o.glHidden=H.GLP.cv.style.display;return o;}''')
    print(r,errs, 'FAILURES',0 if r=={'fastStill':'torch','slow':'classic','shaderOn':False,'glHidden':'none'} and not errs else 1); b.close()
