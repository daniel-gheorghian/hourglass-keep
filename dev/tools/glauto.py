# when frames run slow the shader first copies a smaller scene (scale 1 -> .75 -> .5, one 2 s window each), then drops back to
# Classic (once past the compile window), with a notice once; the scale found is kept for the session (a new floor keeps it) and starts at full size when Torchlight is switched on again
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':844,'height':390}); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(300)
    r=pg.evaluate('''()=>{const H=__HK;H.S.set.lightMode='torch';H.render();const o={};
      for(let i=0;i<150;i++)H.glTime(16);o.fastStill=H.S.set.lightMode;o.rsFast=H.GLP.rs;   // 2.4 s at 16 ms: stays on, full scale
      for(let i=0;i<60;i++)H.glTime(40);o.rsSlow=H.GLP.rs;o.stillTorch=H.S.set.lightMode;  // one slow window: a smaller scene, still Torchlight
      for(let i=0;i<300;i++)H.glTime(40);o.slow=H.S.set.lightMode;o.rsLow=H.GLP.rs;        // 12 s at 40 ms: down to .5, then off
      H.startLevel(2,-1);o.rsNew=H.GLP.rs;
      H.render();o.shaderOn=H.shaderOn();o.glHidden=H.GLP.cv.style.display;H.S.set.lightMode='torch';H.render();o.rsOn=H.GLP.rs;return o;}''')
    print(r,errs, 'FAILURES',0 if r=={'fastStill':'torch','rsFast':1,'rsSlow':0.75,'stillTorch':'torch','slow':'classic','rsLow':0.5,'rsNew':0.5,'rsOn':1,'shaderOn':False,'glHidden':'none'} and not errs else 1); b.close()
