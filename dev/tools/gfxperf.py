from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2)
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.add_init_script("""(()=>{window.__q=[];window.requestAnimationFrame=cb=>{window.__q.push(cb);return 1;};})();""")
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(500); pg.add_script_tag(path='bot.js')
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    for cfg in [dict(light=1,atmo=1,grade=1,hero=1,fx=1,hd=1,bg=1)]:
      r=pg.evaluate('''(cfg)=>{const H=__HK;H.S.set.gfx=Object.assign({},cfg);let ts=1000;const g=document.getElementById('game').getContext('2d');const all=[];let n=0;
        const res=runBot(11,788,{fight:true,stop:H2=>{if(++n%3)return false;const q=window.__q;window.__q=[];const t0=performance.now();for(const cb of q)cb(ts);g.getImageData(0,0,1,1);all.push(performance.now()-t0);return n>9000;}});
        all.sort((a,b)=>a-b);const q=p=>+all[Math.floor(p*(all.length-1))].toFixed(1);return {cfg:Object.values(cfg).join(''),frames:all.length,p50:q(.5),p95:q(.95),p99:q(.99)};}''',cfg)
      print(json.dumps(r))
    print(errs); b.close()
