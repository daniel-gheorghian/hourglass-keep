from playwright.sync_api import sync_playwright
scenes=[('saw',7,700,"H=>H.P.state==='air'&&H.L.dyn.some(o=>o.f.t==='saw'&&o.r===Math.floor((H.P.y-1)/64)&&Math.abs(H.sawX(o.f,H.gameTime)-H.P.x)<30)"),
        ('darts',7,701,"H=>H.P.state==='crouch'&&H.L.ext.darts.some(d=>Math.abs(d.x-H.P.x)<40)"),
        ('push',7,707,"H=>H.P.state==='push'&&H.P.t>0.3"),
        ('blockplate',7,700,"H=>H.L.ext.blocks.some(b=>!b.mv&&H.L.feat[b.r*H.L.cols+b.c]&&H.L.feat[b.r*H.L.cols+b.c].t==='plate')&&H.P.state==='stand'")]
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2)
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(500); pg.add_script_tag(path='bot.js')
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    for name,n,s,stop in scenes:
        r=pg.evaluate("([n,s])=>{const r=runBot(n,s,{stop:%s});__HK.render();return r.ok;}"%stop,[n,s])
        pg.screenshot(path=f't_{name}.png'); print(name,r)
    print(errs); b.close()
