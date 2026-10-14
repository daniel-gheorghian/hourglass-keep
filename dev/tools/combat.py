import json
from playwright.sync_api import sync_playwright
JS = r'''([n,trials,react])=>{
 const H=__HK; let wins=0, hpLeft=0, times=[];
 for(let t=0;t<trials;t++){
  let L=H.load(n, 7000+n*13+t*101, false);
  let tries=0; while(!H.G.length && tries<20){ L=H.load(n, 7000+n*13+t*101+(++tries)*7, false); }
  const g=H.G[0]; for(const o of H.G) if(o!==g){o.alive=false;o.gone=true;}
  const P=H.P; P.x=g.x-80; P.y=g.y; P.state='stand'; P.hp=3; P.face=1;
  const set=(k,v)=>H.setKey('kb',k,v); let pulse=null;
  const press=k=>{set(k,true);pulse=k;};
  let f=0, sawWind=-1, cool=0;
  while(f<60*90){
   if(P.state==='dead'||H.mode==='dead') break;
   if(!g.alive) break;
   cool--;
   if(['garde'].includes(P.state) && cool<=0){
     if(g.state==='strike' && g.t>=react && g.t<g.windup-0.02){ press('u'); cool=12; }
     else if(g.state==='blocked' || g.state==='hurt'){ press('g'); cool=10; }
     else if(g.state!=='strike' && Math.abs(g.x-P.x)<34 && Math.random()<0.06){ press('g'); cool=14; }
     else if(Math.abs(g.x-P.x)>34){ set('r',true); }
   } else set('r',false);
   if(P.state!=='garde') set('r',false);
   if(['stand','run'].includes(P.state)) set('r',true);
   H.tick(1); if(pulse){set(pulse,false);pulse=null;} f++;
  }
  set('r',false);
  if(!g.alive && P.state!=='dead'){wins++;hpLeft+=P.hp;times.push(f/60);}
 }
 return {n,wins,trials,avgHp:wins?hpLeft/wins:0,avgT:times.length?times.reduce((a,b)=>a+b)/times.length:0};
}'''
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page()
    pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(300)
    for react in (0.15, 0.22):
        for n in (1,5,10,15,20,25,30):
            print('react',react, pg.evaluate(JS,[n,40,react]))
    b.close()
