from playwright.sync_api import sync_playwright
import sys,json
lo,hi,seeds=int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3]);fight=len(sys.argv)>4 and sys.argv[4]=='fight';base=int(sys.argv[5]) if len(sys.argv)>5 else 700000
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':844,'height':390}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(300); pg.add_script_tag(path='bot.js')
    ok=0;tot=0;fails=[]
    for n in range(lo,hi+1):
        for s in range(seeds):
            r=pg.evaluate('([n,s,f])=>runBot(n,s,{fight:f})',[n,base+n*97+s*13,fight]);tot+=1
            if r.get('ok') is True: ok+=1
            else: fails.append({k:r.get(k) for k in ('n','seed','why','i','ins','col','row','trace')})
    print('passed',ok,'/',tot); 
    for f in fails: print(json.dumps(f)[:600])
    print('errors',errs[:3]); b.close()
