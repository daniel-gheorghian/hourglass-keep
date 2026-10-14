import json,sys
from playwright.sync_api import sync_playwright
# human-ish fencer vs a corridor skeleton: notices each incoming blow with probability `skill`, reacts after `react` s.
# 'mash' strikes whenever free; 'rhythm' strikes into a reeling/blocked skeleton or after a quiet spell
JS=r'''([trials,policy,skill,react])=>{
 const H=__HK; let wins=0,lost=0,times=[],strikes=0,landed=0;
 for(let t=0;t<trials;t++){
  let g=null;
  for(let k=0;k<400&&!g;k++){const n=17+(k%4);H.load(n,9000+t*977+k*13,false);g=H.G.find(q=>q.skel&&q.pit>0);}
  for(const o of H.G) if(o!==g){o.alive=false;o.gone=true;}
  const P=H.P; P.x=g.x-90; P.y=g.y; P.fallY=P.y; P.state='stand'; P.hp=4; P.face=1;
  const set=(k,v)=>H.setKey('kb',k,v); let pulse=null; const press=k=>{set(k,true);pulse=k;};
  let f=0,parryAt=-1,lastSwing=null,lastClang=-1,lastStrike=-9,hurtSeen=null,hp0=4,ns=0,nl=0,lastFlash=0;
  while(f<60*90){
   if(P.state==='dead'||H.mode==='dead'||g.gone||!g.alive) break;
   const now=f/60;
   if(g.state==='strike'&&g.t<1/50&&lastSwing!==g){lastSwing=g;if(Math.random()<skill)parryAt=now+Math.max(0.15,react+(Math.random()-0.5)*0.1);}
   if(g.state!=='strike')lastSwing=null;
   if(P.state==='blocked'&&P.t<1/50&&lastClang<now-0.1){lastClang=now;if(Math.random()<skill)parryAt=now+Math.max(0.15,react+(Math.random()-0.5)*0.1);}
   set('r',false);
   if(['stand','run'].includes(P.state)) set('r',true);
   else if(parryAt>0&&now>=parryAt&&(P.state==='garde'||P.state==='blocked')){press('u');parryAt=-1;}
   else if(P.state==='garde'&&parryAt<0){
     if(Math.abs(g.x-P.x)>34) set('r',true);
     else if(policy==='mash'){press('g');ns++;}
     else { if(g.state==='blocked'&&g.t>=react*0.8){press('g');ns++;lastStrike=now;}
       else if(g.state==='hurt'&&hurtSeen!==g.lastHit&&Math.random()<0.5){hurtSeen=g.lastHit;press('g');ns++;lastStrike=now;}
       else if(g.state!=='strike'&&now-lastStrike>1.2&&Math.random()<0.04){press('g');ns++;lastStrike=now;} }
   }
   if(g.flash>lastFlash+0.1)nl++; lastFlash=g.flash;
   H.tick(1); if(pulse){set(pulse,false);pulse=null;} f++;
  }
  set('r',false);
  if((g.gone||!g.alive)&&P.state!=='dead'){wins++;times.push(f/60);} lost+=4-Math.max(0,P.hp); strikes+=ns; landed+=nl;
 }
 return {policy,skill,react,winPct:Math.round(100*wins/trials),livesLost:+(lost/trials).toFixed(2),sec:times.length?+(times.reduce((a,b)=>a+b)/times.length).toFixed(1):null,hitsToWin:+(landed/trials).toFixed(1),strikes:+(strikes/trials).toFixed(1)};
}'''
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page()
    for f in sys.argv[1:]:
        pg.goto('file://'+f); pg.wait_for_timeout(300)
        for pol in ('mash','rhythm'):
            for skill,react in ((0.7,0.25),(0.9,0.2)):
                print(f.split('/')[-1],json.dumps(pg.evaluate(JS,[30,pol,skill,react])))
    b.close()
