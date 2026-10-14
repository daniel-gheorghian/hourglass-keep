from playwright.sync_api import sync_playwright
import sys
f=sys.argv[1] if len(sys.argv)>1 else '/home/claude/hourglass-keep.html'
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':844,'height':390}); pg.goto('file://'+f); pg.wait_for_timeout(300); pg.add_script_tag(path='bot.js')
    for s in range(4):
        seed=700000+10*97+s*13
        r=pg.evaluate('([n,s])=>{window.__hurts=[];const r=runBot(n,s,{fight:false});return {ok:r.ok,hurt:r.hurt,h:window.__hurts}}',[10,seed])
        print(seed,r)
    b.close()
