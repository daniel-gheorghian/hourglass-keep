import json, sys
from playwright.sync_api import sync_playwright
src = sys.argv[1]
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width':844,'height':390})
    pg.goto('file://'+src); pg.wait_for_timeout(300); pg.add_script_tag(path='bot.js')
    rows=[]
    for n in [1,2,3,5,8,12,16,20,25,30]:
        ts=[];cols=[];fails=0
        for s in range(4):
            r=pg.evaluate('([n,s])=>{const r=runBot(n,s);r.cols=__HK.L.cols;r.rows=__HK.L.rows;r.cps=__HK.L.cps.length;return r;}',[n,7700+n*13+s*101])
            if r['ok'] is True: ts.append(r['frames']/60); cols.append(r['cols'])
            else: fails+=1
        rows.append((n, cols[0] if cols else None, round(sum(ts)/max(1,len(ts))), fails))
    for r in rows: print('floor %2d cols %s bot %ss fails %d'%r)
    b.close()
