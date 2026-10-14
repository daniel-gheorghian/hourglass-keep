# flagroute.py: route length and trap count of floors forced to each rare flag, against the v39 floor's min and mean (fm40.json, from metrics40.py)
import json,statistics as S
from playwright.sync_api import sync_playwright
base=json.load(open('fm40.json'))['v39']
JS='''([flag,ns])=>{const out=[];window.__FEAT={flag};for(let n=4;n<=27;n++){if(flag==='longway'&&n<6)continue;for(let s=0;s<ns;s++){const L=__HK.genLevel(n,30000+s*101+n*7,true);let r=0;for(const ri of L.runsInfo)r+=Math.abs(ri.c1-ri.c0);const lr=L.runsInfo[L.runsInfo.length-1];r+=Math.abs(L.door.c-lr.c1);
  const MOV=new Set(['flat','up','down','drop2']);const tr=L.segs.filter(q=>!MOV.has(q.k)&&!/^(turn-|loop-|fork-)/.test(q.k)).length;
  let gm=99;{const t2=L.segs.filter(q=>!MOV.has(q.k)&&!/^(turn-|loop-|fork-)/.test(q.k));for(let i=1;i<t2.length;i++){const a=t2[i-1],b=t2[i],d=b.dir||1;if((a.dir||1)!==d||Math.abs(a.r1-b.r0)>1)continue;const g=(b.c0-a.c1)*d;if(g>=0&&g<60)gm=Math.min(gm,g);}}
  out.push({n,route:r,traps:tr,gm,forks:L.forks.length});}}return out;}'''
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(300)
    for flag in ['tower','rotten','barracks','longway','maze']:
        o=pg.evaluate(JS,[flag,4]); bad=[]
        for n in sorted(set(x['n'] for x in o)):
            xs=[x for x in o if x['n']==n]; v=base[str(n)]
            vm=S.mean(q['route'] for q in v); vmin=min(q['route'] for q in v)
            if S.mean(x['route'] for x in xs)<vm or min(x['route'] for x in xs)<vmin: bad.append((n,round(S.mean(x['route'] for x in xs)),round(vm),min(x['route'] for x in xs),vmin))
        print(flag,'floors',len(o),'mean traps %.1f (v39 same floors %.1f)'%(S.mean(x['traps'] for x in o),S.mean(S.mean(q['traps'] for q in base[str(n)]) for n in set(x['n'] for x in o))),'min gap',min(x['gm'] for x in o),'floors shorter than v39 (n,mean,v39mean,min,v39min):',bad)
    b.close()
