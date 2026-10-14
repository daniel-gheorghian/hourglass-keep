from playwright.sync_api import sync_playwright
import sys
JS=r'''([start,kind])=>{const H=__HK;let g=null;
  for(let k=0;k<300&&!g;k++){H.load(9,8800+k*7,false);
    g=H.G.find(q=>!q.skel&&!q.cap&&[...Array(12).keys()].every(i=>{const c=Math.floor((q.x-200)/32)+i;return H.L.base[q.r*H.L.cols+c]===1&&!H.L.feat[q.r*H.L.cols+c];}));}
  for(const o of H.G)if(o!==g){o.alive=false;o.gone=true;}
  g.state='garde';g.x=Math.floor(g.x/32)*32+16;g.lo=g.x-6;g.hi=g.x+6;
  const P=H.P;P.y=g.y;P.fallY=P.y;P.state='stand';P.face=1;P.hp=9;P.x=g.x-start;P.peace=kind==='stand'?3:0;
  const set=(k,v)=>H.setKey('kb',k,v);let pulse=null;const press=k=>{set(k,true);pulse=k;};
  const log=[];if(kind==='run')set('r',true);let j=false;
  for(let f=0;f<90;f++){if(kind==='stand'&&f===2){press('j');} if(kind==='run'&&!j&&P.state==='run'&&g.x-P.x<kind_d){press('j');j=true;}
    H.tick(1);if(pulse){set(pulse,false);pulse=null;}
    if(f%4===0)log.push(P.state+' dx'+Math.round(P.x-g.x)+' h'+Math.round(g.y-P.y)+' g:'+g.state);}
  set('r',false);return log.join(' | ');}'''
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page();pg.goto('file://'+sys.argv[1]);pg.wait_for_timeout(300)
    print('STAND 50:',pg.evaluate(JS.replace('kind_d','80'),[50,'stand'])[:900]);print()
    print('RUN, jump at 80:',pg.evaluate(JS.replace('kind_d','80'),[170,'run'])[:900])
    b.close()
