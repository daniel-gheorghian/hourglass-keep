import json,sys
from playwright.sync_api import sync_playwright
# A) passage ambush: press the plate, then sprint for the way out (also: teleport well past the ambush ground first)
# B) reinforcement: kill a guard that calls one, then sprint on immediately
# pass = the dropped guard lands ahead of the prince and he never gets past it while it lives
JS=r'''([mode,file])=>{const H=__HK,res=[];const ch=c=>c*32+16;
 for(let n=6;n<=30&&res.length<60;n++)for(let s=0;s<6&&res.length<60;s++){const seed=3000+n*131+s*17;let L=H.load(n,seed,false);
  if(mode==='amb'||mode==='ambfast'){
   const pls=L.dyn.filter(o=>o.f.amb);
   for(const o of pls){L=H.load(n,seed,false);for(const g of H.G){g.alive=false;g.gone=true;}
    const pl=L.dyn.find(q=>q.c===o.c&&q.r===o.r),sp=pl.f.amb,P=H.P;
    if(pl.f.chain)for(const t of pl.f.chain){t.sturdy=true;} // keep the chain up so the sprint is about the guard
    P.x=ch(o.c);P.y=(o.r+1)*64-4;P.fallY=P.y;P.state='stand';P.face=1;H.tick(2);
    if(pl.f.chain)for(const t of pl.f.chain){t.s=0;t.tm=0;}
    if(mode==='ambfast'){P.x=sp.x-20;H.tick(1);} // already past where the old ambush landed
    H.setKey('kb','r',true);let g0=H.G.length,spawnP=null,g=null,passed=false,f=0;
    while(f<60*6){H.tick(1);f++;if(!g&&H.G.length>g0){g=H.G[H.G.length-1];spawnP=P.x;}
     if(g&&g.alive&&g.state!=='drop'&&P.x>g.x+4)passed=true;if(P.state==='dead')break;}
    H.setKey('kb','r',false);
    res.push({n,seed,c:o.c,spawned:!!g,ahead:g?+(g.x-spawnP).toFixed(0):null,passed,foe:!!(P.foe),pstate:P.state});}
  }else{
   const gs=H.G.filter(g=>g.reinf>0);
   for(const g0 of gs.slice(0,2)){L=H.load(n,seed,false);const i=H.G.findIndex(q=>q.x===g0.x&&q.r===g0.r);const g=H.G[i];
    for(const q of H.G)if(q!==g){q.alive=false;q.gone=true;}
    const P=H.P;P.x=g.x-28;P.y=g.y;P.fallY=P.y;P.state='stand';P.face=1;g.face=-1;g.hp=1;H.tick(1);
    H.resolveStrike(P,g);P.foe=null;P.sword=false;P.state='stand';
    H.setKey('kb','r',true);let ng=null,spawnP=null,passed=false,f=0;const n0=H.G.length;
    while(f<60*8){H.tick(1);f++;if(!ng&&H.G.length>n0){ng=H.G[H.G.length-1];spawnP=P.x;}
     if(ng&&ng.alive&&ng.state!=='drop'&&Math.abs(P.y-ng.y)<8&&P.x>ng.x+4)passed=true;if(P.state==='dead')break;
     if(['air','hang'].includes(P.state))H.setKey('kb','r',false);}
    H.setKey('kb','r',false);
    res.push({n,seed,spawned:!!ng,ahead:ng?+(ng.x-spawnP).toFixed(0):null,passed,pstate:P.state,row:ng?ng.r===g.r:null});}
  }}
 return res;}'''
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    f=sys.argv[1]; pg.goto('file://'+f); pg.wait_for_timeout(300)
    for mode in sys.argv[2].split(','):
        r=pg.evaluate(JS,[mode,f])
        bad=[x for x in r if (not x['spawned']) or x['passed'] or (x['ahead'] is not None and x['ahead']<30)]
        ah=[x['ahead'] for x in r if x['ahead'] is not None]
        print(mode,'cases',len(r),'spawned',sum(1 for x in r if x['spawned']),'behind/too close',sum(1 for x in ah if x<30),'passed',sum(1 for x in r if x['passed']),'ahead px min/avg',min(ah) if ah else None,round(sum(ah)/len(ah)) if ah else None)
        for x in bad[:6]: print('  ',x)
    print('errors',errs[:3]); b.close()
