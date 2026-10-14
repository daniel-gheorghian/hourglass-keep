from playwright.sync_api import sync_playwright
import json,statistics as S,sys
files=sys.argv[1:]
FL=[1,2,5,9,14,20,26]
def run(f):
    with sync_playwright() as p:
        b=p.chromium.launch(); pg=b.new_page(); pg.goto('file://'+f); pg.wait_for_timeout(300)
        r=pg.evaluate('''(FL)=>{const H=__HK,out={};const MOV=new Set(['flat','up','down','drop2']),VERT=new Set(['wallrun','shaft','banner']);
          for(const n of FL){const acc=[];for(let s=0;s<12;s++){const L=H.genLevel(n,5000+s*31,true);
            const segs=L.segs.filter(q=>!q.k.startsWith('turn-'));
            const tr=segs.filter(q=>!MOV.has(q.k)),trH=tr.filter(q=>!VERT.has(q.k));
            let gaps=[];for(let i=1;i<tr.length;i++){const a=tr[i-1],b=tr[i],d=b.dir||1;if((a.dir||1)!==d||Math.abs(a.r1-b.r0)>1)continue;const g=(b.c0-a.c1)*d;if(g>=0&&g<60)gaps.push(g);}
            let route;if(L.runsInfo){route=0;for(const ri of L.runsInfo)route+=Math.abs(ri.c1-ri.c0);const lr=L.runsInfo[L.runsInfo.length-1];route+=Math.abs(L.door.c-lr.c1);}else route=L.door.c-L.start.x/32;
            const turns=L.segs.filter(q=>q.k.startsWith('turn-'));
            acc.push({route,traps:tr.length,trapsH:trH.length,vert:tr.length-trH.length,gapMean:gaps.reduce((a,b)=>a+b,0)/Math.max(1,gaps.length),gapMin:gaps.length?Math.min(...gaps):99,gap2:gaps.filter(g=>g<2).length,
              guards:L.guards.length,cps:L.cps.length,det:(L.detours||[]).length+(L.secret?1:0),runs:L.runsInfo?L.runsInfo.length:1,W:L.cols/10,H:L.rows,turnMoves:turns.length});}
            out[n]=acc;}return out;}''',FL)
        b.close(); return r
res={f:run(f) for f in files}
keys=['route','traps','trapsH','vert','gapMean','gapMin','gap2','guards','cps','det','runs']
print('floor | '+' | '.join(keys))
for n in map(str,FL):
    for f in files:
        a=res[f][n]
        def m(k):
            v=[x[k] for x in a]
            if k=='gapMin': return min(v)
            if k in('route','traps','trapsH'): return f"{S.mean(v):.1f} (min {min(v)})"
            return round(S.mean(v),1)
        print(n,f.split('/')[-1][:14],' | '.join(str(m(k)) for k in keys))
