from playwright.sync_api import sync_playwright
import json
scenes=[
 ('crawl',  [3,4,6,7],   False, "H=>H.P.state==='crouch'&&H.P.crawling&&H.P.t>0.5&&(()=>{const L=H.L,c=Math.floor(H.P.x/32),r=Math.floor((H.P.y-1)/64),f=L.feat[r*L.cols+c];return f&&f.t==='low';})()"),
 ('snake',  [5,6,7,8],   False, "H=>H.SN.some(s=>s.alive&&s.state==='coil'&&Math.abs(s.x-H.P.x)<40)"),
 ('skel',   [17,18,19],  True,  "H=>H.P.foe&&H.P.foe.skel&&H.P.foe.alive&&H.P.state==='strike'&&H.P.t>0.18"),
 ('skelfall',[17,18,19], True,  "H=>H.G.some(g=>g.skel&&g.state==='fall'&&g.t>0.12)"),
 ('reinf',  [26,27,28],  True,  "H=>H.G.some(g=>g.state==='drop'&&g.y>(g.r+1)*64-4-40)"),
 ('stones', [2,3,4,21],  False, "H=>H.L.debris.some(d=>d.kind==='rock'&&d.vy>120)"),
 ('bridge', [5,6,7,8],   False, "H=>H.L.dyn.some(o=>o.f.plank&&o.f.s===2)&&H.L.dyn.some(o=>o.f.plank&&o.f.s<2&&Math.abs(o.c*32+16-H.P.x)<20)"),
 ('pend',   [9,10,11,12],False, "H=>H.P.state==='crouch'&&H.L.dyn.some(o=>o.f.t==='pend'&&Math.abs(o.c*32+16-H.P.x)<14)&&H.L.dyn.some(o=>o.f.t==='pend'&&Math.abs(H.pendTip(o,o.f).th)<0.15)"),
 ('vent',   [13,14,15,16],False,"H=>H.L.dyn.some(o=>o.f.t==='vent'&&H.danger(o.f,H.gameTime)&&Math.abs(o.c*32+16-H.P.x)<70&&Math.abs(o.c*32+16-H.P.x)>30)"),
]
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2)
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(500); pg.add_script_tag(path='bot.js')
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    for name,floors,fight,stop in scenes:
        got=None
        for n in floors:
            for s in range(3):
                r=pg.evaluate(f"([n,s,f])=>{{const r=runBot(n,s,{{fight:f,stop:{stop}}});window.__HK.render();return r;}}",[n,9100+n*7+s,fight])
                if r.get('ok')=='stopped': got=(n,s); break
            if got: break
        pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true)")
        pg.screenshot(path=f's5_{name}.png'); print(name,got)
    print(errs); b.close()
