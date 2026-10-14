from playwright.sync_api import sync_playwright
import json,sys
# Run at a guard from 150px and take a running jump just before the 64px engage range; also a standing jump from 50px after sheathing.
JS=r'''([kind])=>{const H=__HK;let res=[];
 for(let t=0;t<30;t++){let g=null;
  for(let k=0;k<300&&!g;k++){H.load(9,8800+t*131+k*7,false);
    g=H.G.find(q=>!q.skel&&!q.cap&&[...Array(12).keys()].every(i=>{const c=Math.floor((q.x-200)/32)+i;return H.L.base[q.r*H.L.cols+c]===1&&!H.L.feat[q.r*H.L.cols+c];}));}
  if(!g){res.push('noguard');continue;}
  for(const o of H.G)if(o!==g){o.alive=false;o.gone=true;}
  g.state='garde';g.x=Math.floor(g.x/32)*32+16;g.lo=g.x-6;g.hi=g.x+6; // pinned so the test is about the jump, not footwork
  const P=H.P;P.y=g.y;P.fallY=P.y;P.state='stand';P.face=1;P.hp=9;
  const set=(k,v)=>H.setKey('kb',k,v);let pulse=null;const press=k=>{set(k,true);pulse=k;};
  if(kind==='run'){P.x=g.x-170;set('r',true);}else{P.x=g.x-50;P.peace=3;}
  let jumped=false,maxX=P.x;
  for(let f=0;f<180;f++){
    if(kind==='run'&&!jumped&&P.state==='run'&&g.x-P.x<100){press('j');jumped=true;}
    if(kind==='stand'&&!jumped&&f===2){press('j');jumped=true;}
    H.tick(1);if(pulse){set(pulse,false);pulse=null;}
    maxX=Math.max(maxX,P.x);if(P.state!=='air'&&P.state!=='jumpPrep'&&f>40)set('r',false);
  }
  set('r',false);res.push(maxX>g.x?'PAST':'blocked');}
 const c={};for(const r of res)c[r]=(c[r]||0)+1;return c;}'''
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page()
    pg.goto('file://'+sys.argv[1]);pg.wait_for_timeout(300)
    for k in ('run','stand'):print(k,json.dumps(pg.evaluate(JS,[k])))
    b.close()
