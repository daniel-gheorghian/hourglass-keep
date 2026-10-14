from playwright.sync_api import sync_playwright
import json,statistics as S
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(300)
    r=pg.evaluate('''()=>{const H=__HK,out={};const MOV=new Set(['flat','up','down','drop2']);
      for(const n of [1,2,5,9,14,20,26]){const acc=[];for(let s=0;s<12;s++){const L=H.genLevel(n,5000+s*31,true);
        const tr=L.segs.filter(q=>!MOV.has(q.k));let gaps=[];for(let i=1;i<tr.length;i++)gaps.push(tr[i].c0-tr[i-1].c1);
        acc.push({route:L.door.c-L.start.x/32,traps:tr.length,gapMean:gaps.reduce((a,b)=>a+b,0)/gaps.length,gapMin:Math.min(...gaps),gap2:gaps.filter(g=>g<2).length,guards:L.guards.length,cps:L.cps.length,det:(L.detours||[]).length});}
        out[n]=acc;}return out;}''')
    for n,a in r.items():
        f=lambda k:round(S.mean(x[k] for x in a),1)
        print(n,'route tiles',f('route'),'traps',f('traps'),'gap mean',f('gapMean'),'gap min',min(x['gapMin'] for x in a),'gaps<2',f('gap2'),'guards',f('guards'),'cps',f('cps'),'side passages',f('det'))
    b.close()
