from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2)
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(500); pg.add_script_tag(path='bot.js')
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    # 1: standing before the double gates, both shut
    r=pg.evaluate('''()=>{const r=runBot(9,9000,{stop:H=>{const d=(H.L.detours||[]).find(q=>q.double);return d&&Math.floor((H.P.y-1)/64)===d.r&&H.P.x>(d.g1c-5)*32&&H.P.state==='stand';}});__HK.render();return r.ok;}''')
    pg.screenshot(path='g1_double.png'); print('double',r)
    # 2: after the latch plate, racing back with the timer running
    r=pg.evaluate('''()=>{const r=runBot(9,9000,{stop:H=>{const d=(H.L.detours||[]).find(q=>q.double);if(!d)return false;const g2=H.L.dyn.find(o=>o.c===d.g2c&&o.r===d.r);return g2&&g2.f.tm>0&&g2.f.tm<g2.f.dur*0.6&&H.P.state==='run';}});__HK.render();return r.ok;}''')
    pg.screenshot(path='g2_timer.png'); print('timer',r)
    print(errs); b.close()
