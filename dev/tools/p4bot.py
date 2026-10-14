# p4bot.py [lo hi [seeds]]: the bot on floors forced to the timed-remote-plate puzzle (P4, window.__PZ='P4'); counts the P4 gates on them
# and the runs that pass with 0 damage (unit G1: the gate timers carry no extra factor, so the estimate must hold for the bot).
import sys,json
from playwright.sync_api import sync_playwright
lo,hi=(int(sys.argv[1]),int(sys.argv[2])) if len(sys.argv)>2 else (6,27)
ns=int(sys.argv[3]) if len(sys.argv)>3 else 4
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':844,'height':390}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(300); pg.add_script_tag(path='bot.js')
    tot=ok=dmg=p4=0; fails=[]
    for n in range(lo,hi+1):
        for s in range(ns):
            sd=920000+n*97+s*13
            r=pg.evaluate('([n,sd])=>{window.__PZ="P4";window.__FEAT={puzzle:"timed"};const L=__HK.genLevel(n,sd,true);const k=L.puzzles.filter(q=>/^P4/.test(q.puz)).length;const r=runBot(n,sd,{});return {r,k}}',[n,sd])
            tot+=1;p4+=r['k']
            if r['r'].get('ok') is True:
                ok+=1
                if r['r'].get('hurt'): dmg+=1
            else: fails.append((n,sd,json.dumps(r['r'])[:200]))
    print('P4 gates',p4,'runs passed',ok,'/',tot,'with damage',dmg)
    for f in fails[:10]: print(f)
    print('errors',errs[:3]); b.close()
sys.exit(0 if ok==tot and not dmg and not errs else 1)
