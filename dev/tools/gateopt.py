import json,sys
from playwright.sync_api import sync_playwright
# fastest honest run through each in-line timed gate: stand on the plate, hold right, tap Jump once if there's a pit or closer
JS=r'''([ns,seeds])=>{const H=__HK,rows=[];
 for(const n of ns)for(let s=0;s<seeds;s++){const L=H.load(n,1000+n*97+s*7919,true);
  const gates=L.dyn.filter(o=>o.f.t==='gate'&&!o.f.far&&!o.f.blockGate&&o.f.dur>0);
  for(const o of gates){H.load(n,1000+n*97+s*7919,true);const LL=H.L;const go=LL.dyn.find(q=>q.c===o.c&&q.r===o.r);const g=go.f;
   const pl=LL.dyn.find(q=>q.f.t==='plate'&&q.f.g===g);const cl=LL.dyn.find(q=>q.f.t==='closer'&&q.f.g===g);
   let pit=false,hc=-1;for(let c=pl.c+1;c<go.c;c++)if(H.L.base[go.r*LL.cols+c]!==1){pit=true;if(hc<0)hc=c;}if(cl)hc=cl.c;
   const P=H.P;P.x=pl.c*32+16;P.y=(go.r+1)*64-4;P.fallY=P.y;P.state='stand';P.face=1;P.vx=0;H.tick(2);
   H.setKey('kb','r',true);let f=0,jumped=false,ok=false;
   while(f<600){H.tick(1);f++;
    if(hc>=0&&!jumped&&P.state==='run'&&hc*32-P.x<70){H.setKey('kb','j',true);H.tick(1);f++;H.setKey('kb','j',false);jumped=true;}
    if(P.x>go.c*32+16+8&&Math.abs(P.y-((go.r+1)*64-4))<2){ok=true;break;}
    if(P.state==='dead')break;}
   H.setKey('kb','r',false);
   rows.push({n,m:go.c-pl.c-2,kind:cl?'closer':pit?'gap':'plain',dur:g.dur,used:ok?+(H.gameTime-pl.f.press).toFixed(3):null,ok,state:P.state});}}
 return rows;}'''
f=sys.argv[1]
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); pg.goto('file://'+f); pg.wait_for_timeout(300)
    rows=pg.evaluate(JS,[list(range(3,31)),12])
    b.close()
import collections
by=collections.defaultdict(list)
for r in rows: by[(r['kind'],r['m'])].append(r)
fails=[r for r in rows if not r['ok']]
print('gates',len(rows),'fails',len(fails),fails[:5])
for k in sorted(by):
    v=[r for r in by[k] if r['ok']]
    if not v: continue
    u=[r['used'] for r in v];d=[r['dur'] for r in v]
    print(k,'n=%d opt min %.2f avg %.2f max %.2f | dur avg %.2f | opt/dur avg %.2f max %.2f'%(len(v),min(u),sum(u)/len(u),max(u),sum(d)/len(d),sum(a/b for a,b in zip(u,d))/len(u),max(a/b for a,b in zip(u,d))))
