from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(300); pg.add_script_tag(path='bot.js')
    for n in (3,6,10,14,18):
        r=pg.evaluate('([n])=>runBot(n,12345+n,{fight:true})',[n]); print(n, r.get('ok'), round(r.get('frames',0)/60), r.get('why'))
    print('drinks', [h for h in pg.evaluate('window.__hurts||[]') if 'drink' in h]); print('errors',errs[:3]); b.close()
