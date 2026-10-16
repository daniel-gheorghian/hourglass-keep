# featbot.py [seeds [fight [flags [floors [kind:value]]]]] (floors: comma list, e.g. 9,18, '-' for the default; kind:value, e.g. flag:maze or puzzle:slab, plays just that one; both so suite.py can split it into small jobs): the bot on floors forced to each rare flag and to each featured family (window.__FEAT),
# so every flag and every family is played through, not just the ones the seeds happen to draw. 0 damage on the safe way.
import json, sys
from slowguard import SlowGuard
from playwright.sync_api import sync_playwright
ns=int(sys.argv[1]) if len(sys.argv)>1 else 2
fight=len(sys.argv)>2 and sys.argv[2]=='fight'
FL=[('tower',3),('rotten',4),('barracks',4),('longway',6),('maze',4)]
FAM=[('move',v,3) for v in ['plain','collapse','jumps','banners','lifts']]+[('puzzle',v,4) for v in ['slab','side','alcove','timed','double']]+[('obstacle',v,4) for v in ['spikes','loose','chomp','saw','tunnel']]
FLOORS=[4,6,9,13,18,24,27]
ONLY=len(sys.argv)>3 and sys.argv[3]=='flags' # (just the flags, on the deep floors)
if ONLY: FLOORS=[9,18,24,25,27]; FAM=[]
if len(sys.argv)>4 and sys.argv[4]!='-': FLOORS=[int(x) for x in sys.argv[4].split(',')]
WANT=sys.argv[5] if len(sys.argv)>5 else None
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':844,'height':390}); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(300); pg.add_script_tag(path='bot.js')
    tot=ok=dmg=0; fails=[]; guard=SlowGuard('featbot')
    for kind,val,mn in [('flag',f,m) for f,m in FL]+FAM:
        if WANT and WANT!=kind+':'+val: continue
        o=pe=pd=0
        for n in FLOORS:
            if n<mn: continue
            if kind=='puzzle' and val=='timed' and n<6: continue
            for s in range(ns):
                pg.evaluate('([k,v])=>{window.__FEAT={};window.__FEAT[k]=v}',[kind,val])
                r=guard.run(pg,'([n,s,f])=>runBot(n,s,{fight:f})',[n,910000+n*97+s*13,fight],'%s %s floor %d seed %d'%(kind,val,n,910000+n*97+s*13))
                tot+=1;pe+=1
                if r.get('ok') is True:
                    ok+=1;o+=1
                    if r.get('hurt'): dmg+=1;pd+=1
                else: fails.append((kind,val,n,s,json.dumps(r)[:300]))
        print(kind,val,'passed',o,'/',pe,'damage',pd,flush=True)
    print('TOTAL passed',ok,'/',tot,'with damage',dmg)
    for f in fails[:15]: print(f)
    print('errors',errs[:5]); b.close()
sys.exit(guard.finish(True))
