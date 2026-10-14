from playwright.sync_api import sync_playwright
JS=r'''()=>{const H=__HK;let g=null;for(let k=0;k<200&&!g;k++){H.load(13,5000+k*13,false);g=H.G.find(q=>!q.skel&&!q.cap&&q.tier===2);}
 for(const o of H.G)if(o!==g){o.alive=false;o.gone=true;}
 const P=H.P;P.x=g.x-70;P.y=g.y;P.fallY=P.y;P.state='stand';P.hp=40;P.face=1;
 const set=(k,v)=>H.setKey('kb',k,v);let pulse=null;const press=k=>{set(k,true);pulse=k;};
 const log=[];let prevG='',prevP='';
 for(let f=0;f<60*8&&g.alive;f++){
   set('r',false);if(['stand','run'].includes(P.state))set('r',true);else if(P.state==='garde'){if(Math.abs(g.x-P.x)>34)set('r',true);else press('g');}
   H.tick(1);if(pulse){set(pulse,false);pulse=null;}
   const s='P:'+P.state+' G:'+g.state+(g.state==='strike'?'('+g.wu.toFixed(2)+')':'');
   if(P.state!==prevP||g.state!==prevG){log.push((f/60).toFixed(2)+' '+s+' hp'+P.hp+'/'+g.hp+' dx'+Math.round(g.x-P.x));prevP=P.state;prevG=g.state;}
 }return log.slice(0,60).join('\n');}'''
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page();pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html');pg.wait_for_timeout(300)
    print(pg.evaluate(JS));b.close()
