from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':390,'height':844},device_scale_factor=2)
    pg=ctx.new_page(); pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(500)
    pg.evaluate('''()=>{window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);const H=__HK;H.S.maxHp=7;H.load(13,4242,false);
      const g=H.L.dyn.find(o=>o.f.t==='gate'&&o.f.dur>0);g.f.tm=g.f.dur*0.4;H.P.x=g.c*32-200;H.P.y=(g.r+1)*64-4;H.P.fallY=H.P.y;H.P.hp=5;
      const gd=H.G[0];H.P.foe=gd;H.P.state='garde';H.P.sword=true;H.cam.snap=true;H.layout();H.render();}''')
    pg.screenshot(path='p_hud.png',clip={'x':0,'y':0,'width':390,'height':300}); b.close()
