from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':844,'height':390}); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(300); pg.add_script_tag(path='bot.js')
    for n,s,f in [(39,933783,True),(26,922535,False),(9,920000+9*97+13,False),(30,920000+30*97,False)]:
        r=pg.evaluate('([n,s,f])=>runBot(n,s,{fight:f})',[n,s,f]); print(json.dumps(r)[:300])
    print(errs); b.close()
