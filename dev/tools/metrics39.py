from playwright.sync_api import sync_playwright
import json,statistics as S,sys
out={}
for tag,f in [('v38','/tmp/claude-0/-home-claude-hourglass-keep/f01bc65f-8e08-5e8f-8f80-4fcb704e8720/scratchpad/hk_v38_release.html'),('v39','/home/claude/hourglass-keep.html')]:
  with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); pg.goto('file://'+f); pg.wait_for_timeout(300)
    out[tag]=pg.evaluate('''()=>{const H=__HK,out={};const MOV=new Set(['flat','up','down','drop2']),VERT=new Set(['wallrun','shaft','banner']);
      for(let n=1;n<=27;n++){const acc=[];for(let s=0;s<20;s++){const L=H.genLevel(n,30000+s*101+n*7,true);
        const segs=L.segs.filter(q=>!q.k.startsWith('turn-')&&!q.k.startsWith('loop-'));const tr=segs.filter(q=>!MOV.has(q.k));
        const turnsV=L.segs.filter(q=>/turn-(banner|shaft|wallrun)/.test(q.k)).length;
        let gaps=[];for(let i=1;i<tr.length;i++){const a=tr[i-1],b2=tr[i],d=b2.dir||1;if((a.dir||1)!==d||Math.abs(a.r1-b2.r0)>1)continue;const g=(b2.c0-a.c1)*d;if(g>=0&&g<60)gaps.push(g);}
        let route;if(L.runsInfo){route=0;for(const ri of L.runsInfo)route+=Math.abs(ri.c1-ri.c0);const lr=L.runsInfo[L.runsInfo.length-1];route+=Math.abs(L.door.c-lr.c1);}else route=L.door.c-L.start.x/32;
        acc.push({route,traps:tr.length,vert:tr.filter(q=>VERT.has(q.k)).length+turnsV,gapMin:gaps.length?Math.min(...gaps):99,gapMean:gaps.reduce((a,b)=>a+b,0)/Math.max(1,gaps.length),
          guards:L.guards.length,cps:L.cps.length,det:(L.detours||[]).length+(L.secret?1:0),runs:L.runsInfo?L.runsInfo.length:1,turns:L.plan?L.plan.turns.length:0,rev:L.plan?L.plan.turns.filter(t=>t.rev).length:0,
          loops:(L.loops||[]).length,ups:L.plan?L.plan.turns.filter(t=>!t.down).length:0,W:L.cols/10,H:Math.round(L.rows/3)});}
        out[n]=acc;}return out;}''')
    b.close()
json.dump(out,open('fm39.json','w'))
def agg(a,k,fn='mean'):
    v=[x[k] for x in a]
    return round(S.mean(v),1) if fn=='mean' else min(v)
rows=[]
for n in range(1,28):
    A=out['v38'][str(n)];B=out['v39'][str(n)]
    rows.append([n,agg(A,'route'),agg(B,'route'),agg(A,'route','min'),agg(B,'route','min'),agg(A,'traps'),agg(B,'traps'),agg(A,'traps','min'),agg(B,'traps','min'),agg(A,'gapMin','min'),agg(B,'gapMin','min'),agg(A,'gapMean'),agg(B,'gapMean'),agg(A,'guards'),agg(B,'guards'),agg(A,'cps'),agg(B,'cps'),agg(A,'det'),agg(B,'det'),agg(B,'loops'),agg(B,'turns'),agg(B,'rev'),agg(B,'ups'),agg(B,'W'),agg(B,'H')])
hdr='n route38 route39 rmin38 rmin39 traps38 traps39 tmin38 tmin39 gmin38 gmin39 gmean38 gmean39 guards38 guards39 cps38 cps39 side38 side39 loops39 turns rev ups W H'.split()
print(' '.join(hdr))
for r in rows: print(' '.join(str(x) for x in r))
json.dump({'hdr':hdr,'rows':rows},open('fm39_table.json','w'))
