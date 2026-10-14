import json,sys
from playwright.sync_api import sync_playwright
# A human-ish duellist: notices each threat (guard swing, or own blow blocked) with probability `skill`,
# reacts `react` seconds after the cue. 'mash' strikes whenever free; 'rhythm' strikes only into a reeling
# guard (blocked/hurt once) or after a quiet spell.
JS = r'''([n,trials,tier,policy,skill,react])=>{
 const H=__HK; let wins=0, lost=0, times=[];
 for(let t=0;t<trials;t++){
  let g=null;
  for(let k=0;k<200&&!g;k++){H.load(n,5000+n*31+t*977+k*13,false);g=H.G.find(q=>!q.skel&&!q.cap&&(tier<0||q.tier===tier));}
  for(const o of H.G) if(o!==g){o.alive=false;o.gone=true;}
  const P=H.P; P.x=g.x-70; P.y=g.y; P.fallY=P.y; P.state='stand'; P.hp=4; P.face=1;
  const set=(k,v)=>H.setKey('kb',k,v); let pulse=null; const press=k=>{set(k,true);pulse=k;};
  let f=0,parryAt=-1,lastSwing=null,lastClang=-1,lastStrike=-9,hurtSeen=null;
  while(f<60*120){
   if(P.state==='dead'||H.mode==='dead'||!g.alive) break;
   const now=f/60;
   if(g.state==='strike'&&g.t<1/50&&lastSwing!==g){lastSwing=g;if(Math.random()<skill)parryAt=now+Math.max(0.15,react+(Math.random()-0.5)*0.1);}
   if(g.state!=='strike')lastSwing=null;
   if(P.state==='blocked'&&P.t<1/50&&lastClang<now-0.1){lastClang=now;if(Math.random()<skill)parryAt=now+Math.max(0.15,react+(Math.random()-0.5)*0.1);}
   set('r',false);
   if(['stand','run'].includes(P.state)) set('r',true);
   else if(parryAt>0&&now>=parryAt&&(P.state==='garde'||P.state==='blocked')){press('u');parryAt=-1;}
   else if(P.state==='garde'&&parryAt<0){
     if(Math.abs(g.x-P.x)>34) set('r',true);
     else if(policy==='mash') press('g');
     else if(policy==='turtle'){ if(g.state==='blocked'){press('g');} else press('u'); }
     else { // rhythm
       if(g.state==='blocked'&&g.t>=react*0.8){press('g');lastStrike=now;}
       else if(g.state==='hurt'&&hurtSeen!==g.lastHit&&Math.random()<0.5){hurtSeen=g.lastHit;press('g');lastStrike=now;}
       else if(g.state!=='strike'&&now-lastStrike>1.6&&Math.random()<0.03){press('g');lastStrike=now;}
     }
   }
   H.tick(1); if(pulse){set(pulse,false);pulse=null;} f++;
  }
  set('r',false);
  if(!g.alive&&P.state!=='dead'){wins++;times.push(f/60);} lost+=4-Math.max(0,P.hp);
 }
 return {n,tier,policy,winPct:Math.round(100*wins/trials),livesLost:+(lost/trials).toFixed(2),sec:times.length?+(times.reduce((a,b)=>a+b)/times.length).toFixed(1):null};
}'''
NS=[int(x) for x in sys.argv[6].split(',')] if len(sys.argv)>6 else [5,13,25]
POLS=sys.argv[5].split(',') if len(sys.argv)>5 else ['mash','rhythm']
file=sys.argv[1]; tiers=[int(x) for x in sys.argv[2].split(',')]; skill=float(sys.argv[3]); react=float(sys.argv[4])
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page()
    pg.goto('file://'+file); pg.wait_for_timeout(300)
    for n in NS:
        for tier in tiers:
            for pol in POLS:
                print(json.dumps(pg.evaluate(JS,[n,40,tier,pol,skill,react])))
    b.close()
