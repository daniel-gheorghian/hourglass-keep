import json,sys
from playwright.sync_api import sync_playwright
cases=[(8,700776,508,5),(9,700899,647,3),(11,701080,151,8),(15,701455,92,7),(20,701966,14,5),(16,701552,650,3)]
JS=r'''([n,seed,gc,gr])=>{const L=__HK.load(n,seed,true);const o=L.dyn.find(q=>q.c===gc&&q.r===gr);if(!o)return {n,none:true,f:(L.dyn.filter(q=>q.r===gr&&Math.abs(q.c-gc)<3).map(q=>q.c+':'+q.f.t))};
 const pl=L.dyn.find(q=>q.f.t==='plate'&&q.f.g===o.f),cl=L.dyn.find(q=>q.f.t==='closer'&&q.f.g===o.f);
 const i=L.path.findIndex(a=>(a.c!==undefined&&a.c>=gc)||(a.to!==undefined&&a.to>=gc&&a.from<gc));
 return {n,t:o.f.t,dur:o.f.dur,latch:o.f.latch,far:!!o.f.far,block:!!o.f.blockGate,plate:pl&&[pl.c,pl.r],closer:cl&&cl.c,path:L.path.slice(Math.max(0,i-4),i+2)};}'''
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(300)
    for c in cases: print(json.dumps(pg.evaluate(JS,list(c))))
    b.close()
