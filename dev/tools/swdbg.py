from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(300); pg.add_script_tag(path='bot.js')
    print(pg.evaluate('''()=>{const H=__HK;let log=[],on=false,last='';const r=runBot(6,503,{stop:H=>{const L=H.L;const i=L.path.findIndex(a=>a.a==='swing');
        const P=H.P;if(P.state==='swing')on=true;if(on){const st=P.state+' x'+Math.round(P.x-116*32)+' y'+Math.round(P.y);if(st!==last){log.push(st);last=st;}if(log.length>45)return true;}return false;}});
        return JSON.stringify({ok:r.ok,why:r.why,i:r.i})+'\\n'+log.join(' | ');}'''))
    b.close()
