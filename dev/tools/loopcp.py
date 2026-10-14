from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
  b=p.chromium.launch(); pg=b.new_page(); pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(300)
  r=pg.evaluate('''()=>{const H=__HK;let loops=0,between=0,ex=[];
    for(let n=6;n<=27;n++)for(let s=0;s<20;s++){const seed=50000+s*131+n*7,L=H.genLevel(n,seed,true);
      for(const lp of (L.loops||[])){loops++;
        // walk the bot path: index where the plate is reached and where the gate is passed
        const path=L.path;let iP=-1,iG=-1;
        for(let i=0;i<path.length;i++){const a=path[i];const cc=a.c!==undefined?a.c:a.to;if(cc===undefined)continue;
          if(iP<0&&cc===lp.plate.c+lp.dir)iP=i; }
        // checkpoints by ord vs plate/gate: use x positions along each run
        const cpsB=L.cps.filter(cp=>{
          const onUp=(cp.r===lp.rUp||cp.r===lp.rUp-1)&&(cp.c-lp.plate.c)*lp.dir>0;
          const onLow=(cp.r===lp.rLow||cp.r===lp.rLow-1)&&(lp.gate.c-cp.c)*(-lp.dir)>0&&Math.abs(cp.c-lp.gate.c)<80;
          return onUp||onLow;});
        if(cpsB.length){between++;if(ex.length<5)ex.push({n,seed,plate:lp.plate,gate:lp.gate,cps:cpsB.map(c=>[c.c,c.r])});}
      }}
    return {loops,between,ex};}''')
  print(json.dumps(r,indent=1)); b.close()
