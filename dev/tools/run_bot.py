import json, sys
from playwright.sync_api import sync_playwright
levels = range(1, int(sys.argv[1]) if len(sys.argv)>1 else 31)
seeds = int(sys.argv[2]) if len(sys.argv)>2 else 4
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width':844,'height':390})
    errs=[]
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.on('console', lambda m: errs.append('console:'+m.text) if m.type=='error' else None)
    pg.goto('file:///home/claude/hourglass-keep.html')
    pg.wait_for_timeout(500)
    pg.add_script_tag(path='bot.js')
    res=[]; fails=[]
    for n in levels:
        for s in range(seeds):
            seed = 520000+n*223+s*61
            r = pg.evaluate('([n,s])=>runBot(n,s)', [n, seed])
            res.append(r)
            if not r['ok']: fails.append(r)
    print('passed', sum(1 for r in res if r['ok']), '/', len(res))
    for f in fails[:25]: print(json.dumps(f))
    print('errors', errs[:10])
    b.close()
