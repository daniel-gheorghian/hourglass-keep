import json, sys
from playwright.sync_api import sync_playwright
src = sys.argv[1]
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width':844,'height':390})
    errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+src); pg.wait_for_timeout(300); pg.add_script_tag(path='bot.js')
    for n in [1,5,8,12,16,20,25,30]:
        ts=[];info=None;fails=[]
        for s in range(3):
            r=pg.evaluate('([n,s])=>{const r=runBot(n,s);const L=__HK.L;r.cols=L.cols;r.rows=L.rows;r.cps=L.cps.length;r.items=L.items.map(i=>i.type).join(",");return r;}',[n,7700+n*13+s*101])
            if r['ok'] is True: ts.append(r['frames']/60); info=r
            else: fails.append(r)
        print('floor %2d cols %3s cps %s bot %4ss fails %d  items[%s]'%(n,info and info['cols'],info and info['cps'],round(sum(ts)/max(1,len(ts))),len(fails),info and info['items']))
        for f in fails[:2]: print('   ',json.dumps(f)[:300])
    print('errors',errs[:5]); b.close()
