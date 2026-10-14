from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(300); pg.add_script_tag(path='bot.js')
    r=pg.evaluate('''()=>{const H=__HK;const out=[];
      for(const n of [17,18,19,20,37]){const res=runBot(n,4242+n,{fight:true});const L=H.L;
        out.push({n,ok:res.ok,secs:Math.round((res.frames||0)/60),skeletons:L.guards.filter(g=>g.skel).length,skeletonsInPit:H.G.filter(g=>g.skel&&g.gone).length,
          replacements:H.G.length-L.guards.length,snakesKilled:H.SN.filter(s=>!s.alive).length+'/'+H.SN.length,why:res.why});}
      for(const n of [8,12,15,26]){const res=runBot(n,5151+n,{fight:true});const L=H.L;out.push({n,ok:res.ok,guards:L.guards.length,withReplacement:L.guards.filter(g=>g.reinf).length,replacementsSpawned:H.G.length-L.guards.length,why:res.why});}
      return out;}''')
    for x in r: print(json.dumps(x))
    b.close()
