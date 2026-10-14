import json, sys
from playwright.sync_api import sync_playwright
lo,hi,seeds,fight=int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3]),(sys.argv[4]=='fight' if len(sys.argv)>4 else False)
base=int(sys.argv[5]) if len(sys.argv)>5 else 700000
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':844,'height':390}); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(300); pg.add_script_tag(path='bot.js')
    res=[];fails=[]
    for n in range(lo,hi+1):
        for s in range(seeds):
            r=pg.evaluate('([n,s,f])=>runBot(n,s,{fight:f})',[n,base+n*97+s*13,fight])
            res.append(r)
            if r.get('ok') is not True: fails.append(r)
    ok=[r for r in res if r.get('ok') is True]
    print('passed',len(ok),'/',len(res),' avg bot time %.0fs'%(sum(r['frames'] for r in ok)/max(1,len(ok))/60), ' runs with damage',sum(1 for r in ok if r.get('hurt')))
    for f in fails[:12]: print(json.dumps(f)[:420])
    print('hurts',pg.evaluate('window.__hurts||[]')[:20]); print('errors',errs[:5]); b.close()
