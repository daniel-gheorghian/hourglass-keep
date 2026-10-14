import json,sys
from playwright.sync_api import sync_playwright
cases=json.loads(sys.argv[1]); fight=len(sys.argv)>2 and sys.argv[2]=='fight'
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(300); pg.add_script_tag(path='bot.js')
    for n,s in cases:
        r=pg.evaluate('([n,s,f])=>runBot(n,s,{fight:f})',[n,s,fight]); print(json.dumps(r)[:300])
    print('errors',errs[:3]); b.close()
