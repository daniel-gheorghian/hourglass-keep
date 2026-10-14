from playwright.sync_api import sync_playwright
PRE="const d=(H.L.detours||[]).find(D);const row=Math.floor((H.P.y-1)/64),col=Math.floor(H.P.x/32);const pl=d&&H.L.dyn.find(o=>o.f.t==='plate'&&o.c===d.x0&&o.r===d.b);const pressed=pl&&pl.f.g.tm===Infinity;"
scenes0=[
 ('gallery',27,3,"d=>d.gal&&d.chain&&d.amb","d&&H.P.state==='stand'&&row===d.b&&col<d.bend-14&&!pressed"),
 ('chain',  27,3,"d=>d.gal&&d.chain&&d.amb","d&&pressed&&pl.f.chain.some(t=>t.s===2)&&pl.f.chain.some(t=>t.s===1)"),
 ('ambush', 27,3,"d=>d.gal&&d.chain&&d.amb","d&&pressed&&H.G.length>H.L.guards.length&&H.G[H.G.length-1].state==='garde'&&Math.abs(H.G[H.G.length-1].x-H.P.x)<90"),
 ('cellar', 22,4,"d=>!d.gal","d&&H.P.state==='stand'&&row===d.b&&col<d.bend-10&&!pressed"),
 ('retjump',22,4,"d=>!d.gal","d&&pressed&&row===d.b&&H.P.state==='air'&&H.P.face===1"),
 ('corridor',33,8,"d=>d.gal","d&&H.P.state==='stand'&&row===d.r&&col>d.c+8&&col<d.e-6&&!pressed"),
]
scenes=[
 ('gallery',27,3,"d=>d.gal&&d.chain&&d.amb","d&&H.P.state==='stand'&&row===d.b&&col>=d.x0&&col<d.bend-14&&!pressed"),
 ('cellar', 22,4,"d=>!d.gal","d&&H.P.state==='stand'&&row===d.b&&col>=d.x0&&col<d.bend-10&&!pressed"),
 ('entrance',33,8,"d=>d.gal","d&&row===d.r&&H.P.state==='climb'&&col>=d.e-1&&!pressed"),
 ('cellarin',22,4,"d=>!d.gal","d&&row===d.r&&H.P.state==='hang'&&!pressed"),
]
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2)
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(500); pg.add_script_tag(path='bot.js')
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    for name,n,s,D,cond in scenes:
        js="([n,s])=>{const D=%s;const r=runBot(n,s,{fight:true,stop:H=>{%s return !!(%s);}});window.__HK.render();return r;}"%(D,PRE,cond)
        r=pg.evaluate(js,[n,s])
        pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true)")
        pg.screenshot(path=f's7_{name}.png'); print(name,r.get('ok'),r.get('why'))
    print(errs); b.close()
