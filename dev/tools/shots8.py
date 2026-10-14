from playwright.sync_api import sync_playwright
scenes=[
 ('soldier',13,"H=>H.P.foe&&H.P.foe.alive&&H.P.foe.tier===1&&!H.P.foe.cap&&H.P.foe.state==='strike'&&H.P.foe.t>0.1"),
 ('veteran',13,"H=>H.P.foe&&H.P.foe.alive&&H.P.foe.tier===2&&!H.P.foe.cap&&H.P.foe.state==='strike'&&H.P.foe.t>0.1"),
 ('riposte',21,"H=>H.P.foe&&H.P.foe.alive&&H.P.state==='blocked'&&H.P.t>0.05"),
 ('lowsword',13,"H=>H.P.state==='crouch'&&H.P.lowSword&&H.SN.some(s=>s.alive&&s.r===Math.floor((H.P.y-1)/64)&&Math.abs(s.x-H.P.x)<70)"),
 ('poke',13,"H=>H.P.state==='poke'&&H.P.t>0.09&&H.P.t<0.14"),
]
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2)
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(500); pg.add_script_tag(path='bot.js')
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    for name,n,stop in scenes:
        got=None
        for s in range(6):
            r=pg.evaluate("([n,s])=>{const r=runBot(n,s,{fight:true,stop:%s});window.__HK.render();return r;}"%stop,[n,s+5])
            if r.get('ok')=='stopped': got=(n,s+5); break
        pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true)")
        pg.screenshot(path=f's8_{name}.png'); print(name,got)
    print(errs); b.close()
