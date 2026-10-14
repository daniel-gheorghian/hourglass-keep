from playwright.sync_api import sync_playwright
import json,sys
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':844,'height':390}); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(300); pg.add_script_tag(path='bot.js')
    stats=pg.evaluate('''()=>{let N=0,dbl=0,timed=0,det=0;for(let n=4;n<=40;n++)for(let s=0;s<5;s++){N++;const L=__HK.genLevel(n,s*101+n*3,false);for(const d of L.detours||[]){if(d.double)dbl++;else{det++;if(d.timed)timed++;}}}return {perFloor:{double:(dbl/N).toFixed(2),detour:(det/N).toFixed(2),timedDetour:(timed/N).toFixed(2)}};}''')
    print(json.dumps(stats))
    # find floors with a double gate / timed detour and play them
    cases=pg.evaluate('''()=>{const out=[];for(let n=7;n<=40&&out.length<10;n+=1)for(let s=0;s<40;s++){const L=__HK.genLevel(n,9000+s,true);const ds=L.detours||[];
        if(ds.some(d=>d.double)&&out.filter(o=>o[2]==='double').length<6){out.push([n,9000+s,'double']);break;}
        if(ds.some(d=>d.timed)&&out.filter(o=>o[2]==='timed').length<4){out.push([n,9000+s,'timed']);break;}}return out;}''')
    for n,s,kind in cases:
        r=pg.evaluate('''([n,s])=>{const use=[];const H=__HK;const seen=new Set();
          const res=runBot(n,s,{stop:H=>{for(const o of H.L.dyn){const f=o.f;if(f.t==='gate'&&f.far&&!f.latch&&!seen.has(o)&&H.P.x>o.c*32+24&&Math.floor((H.P.y-1)/64)===o.r){seen.add(o);
              const pl=H.L.dyn.find(q=>q.f.t==='plate'&&q.f.g===f);use.push({dur:f.dur,used:+(H.gameTime-pl.f.press).toFixed(1)});}}return false;}});
          const ds=(H.L.detours||[]).filter(d=>d.double||d.timed).map(d=>d.double?{double:true,timedSide:d.tg?'gallery':'cellar',dur:d.dur}:{timed:true,gal:d.gal,dur:d.dur});
          return {n,s,ok:res.ok,why:res.why,trace:res.trace,ds,use};}''',[n,s])
        print(kind,json.dumps(r)[:600])
    print('errors',errs); b.close()
