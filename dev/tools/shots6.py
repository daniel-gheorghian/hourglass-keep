from playwright.sync_api import sync_playwright
scenes=[
 ('closer',  [5,6,7,9], "H=>H.P.state==='air'&&H.L.dyn.some(o=>o.f.t==='closer'&&Math.abs(o.c*32+16-H.P.x)<10)"),
 ('shutgate',[4,5,6,7], "H=>H.P.state==='stand'&&H.L.dyn.some(o=>o.f.t==='gate'&&o.f.latch&&o.f.open<0.1&&o.r===Math.floor((H.P.y-1)/64)&&o.c*32+16-H.P.x>40&&o.c*32+16-H.P.x<110)&&H.L.dyn.some(o=>o.f.t==='plate'&&o.f.latch&&o.r<Math.floor((H.P.y-1)/64)&&Math.abs(o.c*32-H.P.x)<300)"),
 ('gallery', [4,5,6,7], "H=>H.L.dyn.some(o=>o.f.t==='plate'&&o.f.latch&&H.P.state==='stand'&&Math.floor(H.P.x/32)===o.c&&Math.floor((H.P.y-1)/64)===o.r&&H.L.dyn.some(q=>q.f===o.f.g&&q.r>o.r))"),
 ('cellar',  [4,5,6,7], "H=>H.L.dyn.some(o=>o.f.t==='plate'&&o.f.latch&&H.P.state==='stand'&&Math.floor(H.P.x/32)===o.c&&Math.floor((H.P.y-1)/64)===o.r&&H.L.dyn.some(q=>q.f===o.f.g&&q.r<o.r))"),
]
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2)
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(500); pg.add_script_tag(path='bot.js')
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    for name,floors,stop in scenes:
        got=None
        for n in floors:
            for s in range(3):
                r=pg.evaluate(f"([n,s])=>{{const r=runBot(n,s,{{stop:{stop}}});window.__HK.tick(name==='gallery'?20:0);window.__HK.render();return r;}}".replace("name==='gallery'","'"+name+"'==='gallery'"),[n,7300+n*11+s])
                if r.get('ok')=='stopped': got=(n,s); break
            if got: break
        pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true)")
        pg.screenshot(path=f's6_{name}.png'); print(name,got)
    print(errs); b.close()
