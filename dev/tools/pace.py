import json,sys
from playwright.sync_api import sync_playwright
# pacing stats: hazards per floor, plain-floor tiles between consecutive hazards
JS=r'''([ns,seeds])=>{const H=__HK,out=[];const MOVE=new Set(['flat','up','down','drop2']);
 for(const n of ns){let cols=0,haz=0,moves=0,gaps=[],kinds={},guards=0,cps=0,len=0,dets=0,timed=0;
  for(let s=0;s<seeds;s++){const L=H.load(n,1000+n*97+s*7919,true);cols+=L.cols;guards+=L.guards.length;cps+=L.cps.length;
   let prev=null;for(const g of L.segs){if(g.k==='flat')continue;if(MOVE.has(g.k)){moves++;continue;}haz++;kinds[g.k]=(kinds[g.k]||0)+1;if(prev)gaps.push(g.c0-prev.c1);prev=g;}
   for(const o of L.dyn)if(o.f.t==='gate'&&!o.f.latch&&o.f.dur>0&&!o.f.blockGate)timed++;}
  gaps.sort((a,b)=>a-b);const q=p=>gaps[Math.floor(p*(gaps.length-1))];
  out.push({n,cols:Math.round(cols/seeds),haz:+(haz/seeds).toFixed(1),moves:+(moves/seeds).toFixed(1),guards:+(guards/seeds).toFixed(1),cps:+(cps/seeds).toFixed(1),timed:+(timed/seeds).toFixed(1),
   gapMean:+(gaps.reduce((a,b)=>a+b,0)/gaps.length).toFixed(2),le1:Math.round(100*gaps.filter(x=>x<=1).length/gaps.length),p50:q(0.5),p90:q(0.9),hazPerRoom:+(haz/(cols/10)).toFixed(2),kinds:Object.fromEntries(Object.entries(kinds).map(([k,v])=>[k,+(v/seeds).toFixed(1)]))});}
 return out;}'''
f=sys.argv[1]; ns=[int(x) for x in sys.argv[2].split(',')]; seeds=int(sys.argv[3]) if len(sys.argv)>3 else 6
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); pg.goto('file://'+f); pg.wait_for_timeout(300)
    for row in pg.evaluate(JS,[ns,seeds]): print(json.dumps(row))
    b.close()
