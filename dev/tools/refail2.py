from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':844,'height':390}); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(300); pg.add_script_tag(path='bot.js')
    for n,s,f in [(18,701746,True),(26,702522,True),(17,921662,False),(22,922134,False),(7,700,False),(7,703,False),(7,706,False),(7,707,False)]:
        r=pg.evaluate('([n,s,f])=>{const r=runBot(n,s,{fight:f});return {ok:r.ok,why:r.why,ins:r.ins,trace:r.trace,state:r.state};}',[n,s,f]); print(n,s,json.dumps(r)[:300])
    print(errs); b.close()
