from playwright.sync_api import sync_playwright
import json,sys
lo,hi=int(sys.argv[1]),int(sys.argv[2])
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':844,'height':390}); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(300); pg.add_script_tag(path='bot.js')
    rows=[]
    for n in range(lo,hi+1):
        r=pg.evaluate('''(n)=>{const use=[];const seen=new Set();
          const res=runBot(n,5150+n,{fight:false,stop:H=>{for(const o of H.L.dyn){const f=o.f;if(f.t==='gate'&&!f.latch&&f.dur>0.3&&!seen.has(o)&&H.P.x>o.c*32+16&&Math.floor((H.P.y-1)/64)===o.r){seen.add(o);
              const pl=H.L.dyn.find(q=>q.f.t==='plate'&&q.f.g===f);if(pl)use.push({far:!!f.far,tiles:o.c-pl.c,dur:f.dur,used:+(H.gameTime-pl.f.press).toFixed(2)});}}return false;}});
          return {n,ok:res.ok,why:res.why,use};}''',n)
        rows.append(r)
    allu=[u for r in rows for u in r['use']]
    for r in rows: print(r['n'],r['ok'],r.get('why'),[(u['tiles'],u['dur'],u['used']) for u in r['use']])
    near=[u['used']/u['dur'] for u in allu if not u['far']]; far=[u['used']/u['dur'] for u in allu if u['far']]
    if near: print('in-line gates: n=%d used/dur min %.2f avg %.2f max %.2f'%(len(near),min(near),sum(near)/len(near),max(near)))
    if far: print('detour gates: n=%d used/dur min %.2f avg %.2f max %.2f'%(len(far),min(far),sum(far)/len(far),max(far)))
    print('errors',errs); b.close()
