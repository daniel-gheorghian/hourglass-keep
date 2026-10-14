from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=3)
    pg=ctx.new_page(); pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(500)
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    pg.evaluate('''()=>{const H=__HK;let o=null,sp=null;for(let s=0;s<200&&!(o&&sp);s++){const L=H.load(12,500+s,true);o=L.dyn.find(q=>q.f.t==='chomp');sp=o&&L.dyn.find(q=>q.f.t==='spikes'&&q.r===o.r&&Math.abs(q.c-o.c)<7);}
      H.P.x=o.c*32-40;H.P.y=(o.r+1)*64-4;H.P.fallY=H.P.y;H.P.state='stand';H.cam.snap=true;H.tick(1);sp.f.ext=1;o.f.off=0.03*o.f.per-H.gameTime;H.render();}''')
    pg.screenshot(path='fullview.png'); b.close()
