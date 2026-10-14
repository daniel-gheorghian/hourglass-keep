from playwright.sync_api import sync_playwright
scenes=[('storm',12,900,"H=>{const c=H.L.ext.chase;return c&&c.on&&c.t>4&&H.P.state==='air';}"),
        ('arch',12,900,"H=>{const c=H.L.ext.chase;return c&&c.done&&(c.fade||0)<0.3;}"),
        ('secret',12,900,"H=>{const s=H.L.secret;return s&&Math.abs(s.c*32-H.P.x)<90&&Math.floor((H.P.y-1)/64)===s.r+(s.gal?1:0)&&H.P.state==='stand';}"),
        ('goldflask',12,900,"H=>H.L.items.some(i=>i.hidden&&!i.taken&&Math.abs(i.x-H.P.x)<70&&Math.floor((H.P.y-1)/64)===i.r)")]
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2)
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(500); pg.add_script_tag(path='bot.js')
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    for name,n,s,stop in scenes:
        r=pg.evaluate("([n,s])=>{const r=runBot(n,s,{stop:%s});__HK.render();return r.ok;}"%stop,[n,s])
        pg.screenshot(path=f'c_{name}.png'); print(name,r)
    print(errs); b.close()
