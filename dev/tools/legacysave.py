from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch()
    # find a chase floor for this seed using the live build, and the cols it had there
    pg=b.new_page();pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/tools/hk_v16_release.html');pg.wait_for_timeout(300)
    seed=123456
    info=pg.evaluate('''(seed)=>{const hash2=(a,b)=>{let h=(Math.imul(a|0,374761393)+Math.imul(b|0,668265263))|0;h=Math.imul(h^(h>>>13),1274126177);return (h^(h>>>16))>>>0;};
      for(let n=8;n<40;n++){const L=__HK.genLevel(n,hash2(seed,n*7919+13),false);if(L.ext.chase)return {n,cols:L.cols};}}''',seed)
    print('live build: floor',info['n'],'has a chase, cols',info['cols'])
    save={"v":1,"gen":7,"lifeTaken":[],"level":info['n'],"maxHp":5,"deaths":3,"time":4000,"floorTime":120,"floorDeaths":0,"seed":seed,"cp":-1,"started":True,
          "hints":{},"set":{"sound":False,"saver":False,"lefty":False},"resume":{"n":info['n'],"x":200,"y":0,"face":1,"hp":5}}
    ctx=b.new_context();ctx.add_init_script("localStorage.setItem('hourglass-keep-v1',%s)"%json.dumps(json.dumps(save)))
    pg2=ctx.new_page();pg2.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html');pg2.wait_for_timeout(500)
    pg2.click('#bContinue');pg2.wait_for_timeout(300)
    r=pg2.evaluate('()=>({level:__HK.L.n,cols:__HK.L.cols,legacy:__HK.S.legacyFloor,floorTime:Math.round(__HK.S.floorTime)})')
    print('after update, continuing:',r,'(same cols as live:',r['cols']==info['cols'],')')
    nxt=pg2.evaluate('''(n)=>{const H=__HK;const hash2=(a,b)=>{let h=(Math.imul(a|0,374761393)+Math.imul(b|0,668265263))|0;h=Math.imul(h^(h>>>13),1274126177);return (h^(h>>>16))>>>0;};
      H.S.level=n+1;H.S.legacyFloor=0;const L=H.genLevel(n,hash2(H.S.seed,n*7919+13),false,false);return {sameFloorFresh:L.cols};}''',info['n'])
    print('the same floor once finished and replayed fresh:',nxt)
    b.close()
