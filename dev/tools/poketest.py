from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':844,'height':390}); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(300); pg.add_script_tag(path='bot.js')
    # floors with snakes in tunnels; count snakes killed by pokes
    out=pg.evaluate('''()=>{const res=[];for(const [n,s] of [[9,3],[13,5],[17,2],[21,7],[30,4],[34,6]]){window.__pokes=0;const r=runBot(n,s,{});
      const killed=__HK.SN.filter(x=>!x.alive).length;res.push({n,s,ok:r.ok,why:r.why,trace:r.trace,hurt:r.hurt,snakes:__HK.SN.length,killed,pokeFrames:window.__pokes,sec:Math.round((r.frames||0)/60)});}return res;}''')
    for r in out: print(json.dumps(r)[:400])
    print('errors',errs); b.close()
