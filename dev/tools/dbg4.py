from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(300)
    r=pg.evaluate('''()=>{const L=__HK.genLevel(10,700983,true);const near=L.dyn.filter(o=>o.c>=212&&o.c<=226).map(o=>[o.c,o.r,o.f.t,o.f.dur?+o.f.dur.toFixed(2):'']);
      const i=L.path.findIndex(a=>a.a==='sjump'&&a.from===221);return {near,path:L.path.slice(i-3,i+2)};}''')
    print(json.dumps(r)); b.close()
