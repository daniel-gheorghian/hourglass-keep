import json,sys
from playwright.sync_api import sync_playwright
JS = r'''([n,trials,tier,policy,react])=>{
 const H=__HK; let wins=0, lost=0, times=[], hits=0, parried=0;
 for(let t=0;t<trials;t++){
  let g=null;
  for(let k=0;k<200&&!g;k++){H.load(n,5000+n*31+t*977+k*13,false);g=H.G.find(q=>!q.skel&&!q.cap&&(tier<0||q.tier===tier));}
  if(!g) return {err:'no guard'};
  for(const o of H.G) if(o!==g){o.alive=false;o.gone=true;}
  const P=H.P; P.x=g.x-70; P.y=g.y; P.fallY=P.y; P.state='stand'; P.hp=4; P.face=1;
  const set=(k,v)=>H.setKey('kb',k,v); let pulse=null; const press=k=>{set(k,true);pulse=k;};
  let f=0,cool=0,hp0=g.hp;
  while(f<60*120){
   if(P.state==='dead'||H.mode==='dead'||!g.alive) break;
   cool--;
   const wu=g.wu||g.windup, incoming=g.state==='strike'&&g.t>=react&&g.t<wu-0.02;
   const ready=P.state==='garde'||P.state==='blocked';
   set('r',false);
   if(['stand','run'].includes(P.state)) set('r',true);
   else if(ready&&cool<=0){
     if(policy!=='mash'&&incoming){press('u');cool=12;}
     else if(P.state==='garde'){
       if(Math.abs(g.x-P.x)>34) set('r',true);
       else if(policy==='mash'||policy==='mashparry'){press('g');cool=2;}
       else if(g.state==='blocked'){press('g');cool=10;}
       else if(g.state!=='strike'&&Math.random()<0.02){press('g');cool=14;}
     }
   }
   const before=g.state; H.tick(1); if(pulse){set(pulse,false);pulse=null;} f++;
   if(P.state==='blocked'&&P.t<1/59)parried++;
  }
  set('r',false);
  if(!g.alive&&P.state!=='dead'){wins++;times.push(f/60);} lost+=4-Math.max(0,P.hp);
 }
 return {n,tier,policy,winPct:Math.round(100*wins/trials),avgLivesLost:+(lost/trials).toFixed(2),avgSec:times.length?+(times.reduce((a,b)=>a+b)/times.length).toFixed(1):null,parriedPerDuel:+(parried/trials).toFixed(1)};
}'''
file=sys.argv[1]; tiers=[int(x) for x in sys.argv[2].split(',')]
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page()
    pg.goto('file://'+file); pg.wait_for_timeout(300)
    for n in (13,25):
        for tier in tiers:
            for pol in ('mash','mashparry','rhythm'):
                print(json.dumps(pg.evaluate(JS,[n,40,tier,pol,0.15])))
    b.close()
