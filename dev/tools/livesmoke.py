from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2)
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(800)
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay');const H=__HK;H.load(11,777,false);H.mode='play';H.setKey('kb','r',true);")
    pg.wait_for_timeout(4000)
    print(pg.evaluate("({x:__HK.P.x,st:__HK.P.state,builds:__HK.roomBuilds,draw:__HK.drawBuilds,pf:__HK.prefetched})"))
    pg.screenshot(path='live.png'); print('errors',errs); b.close()
