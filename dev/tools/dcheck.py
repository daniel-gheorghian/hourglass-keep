from playwright.sync_api import sync_playwright
import json,sys
fight=len(sys.argv)>1 and sys.argv[1]=='fight'
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':844,'height':390}); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(300); pg.add_script_tag(path='bot.js')
    out=pg.evaluate('''(fight)=>{const res=[];for(const [n,seed] of [[5,11],[8,23],[11,7],[14,5],[18,9],[22,4],[27,3],[33,8]]){
      // stop as soon as the floor is done; record chain collapse margins via a stop hook
      let minGap=1e9;const H=__HK;
      const r=runBot(n,seed,{fight,stop:(H)=>{for(const o of H.L.dyn){const f=o.f;if(f.t==='loose'&&f.sturdy&&f.s===1&&f.tm>=0.5-1/60-1e-9&&!f.seen){f.seen=1;const pc=Math.floor(H.P.x/32);if(H.P.y>=0)minGap=Math.min(minGap,Math.abs(pc-o.c));}}return false;}});
      const L=H.L,ds=(L.detours||[]).map(d=>{const pl=L.dyn.find(o=>o.f.t==='plate'&&o.f.latch&&o.c===d.x0);return {gal:d.gal,len:d.len,kinds:d.kinds.join(','),chain:d.chain,amb:d.amb,opened:pl&&pl.f.g.tm===Infinity,fell:pl&&pl.f.chain?pl.f.chain.filter(t=>t.s===2).length:null};});
      res.push({n,seed,ok:r.ok,why:r.why,frames:r.frames,hurt:r.hurt,fights:r.fights,trace:r.trace,minTilesFromCollapse:minGap,ds});}
      return res;}''',fight)
    for r in out: print(json.dumps(r)[:900])
    print('errors',errs[:5]); b.close()
