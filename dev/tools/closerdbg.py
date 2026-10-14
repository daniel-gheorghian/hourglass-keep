from playwright.sync_api import sync_playwright
JS=r'''()=>{const H=__HK;for(let s=0;s<12;s++){const n=4;const L=H.load(n,1000+n*97+s*7919,true);
  const o=L.dyn.find(o=>o.f.t==='gate'&&!o.f.far&&o.f.dur>0&&L.dyn.some(q=>q.f.t==='closer'&&q.f.g===o.f));if(!o)continue;
  const g=o.f,pl=L.dyn.find(q=>q.f.t==='plate'&&q.f.g===g),cl=L.dyn.find(q=>q.f.t==='closer'&&q.f.g===g);
  const P=H.P;P.x=pl.c*32+16;P.y=(o.r+1)*64-4;P.fallY=P.y;P.state='stand';P.face=1;H.tick(2);H.setKey('kb','r',true);
  const tr=[];let jumped=false;
  for(let f=0;f<200;f++){H.tick(1);if(!jumped&&P.state==='run'&&Math.abs(P.vx)>60){H.setKey('kb','j',true);H.tick(1);H.setKey('kb','j',false);jumped=true;tr.push('J@'+P.x.toFixed(0));}
   if(f%6==0)tr.push(P.state+':'+P.x.toFixed(0)+':'+g.open.toFixed(2));}
  H.setKey('kb','r',false);
  return {plate:pl.c,closer:cl.c,gate:o.c,gx:o.c*32+16,tr:tr.join(' ')};}}'''
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(300)
    print(pg.evaluate(JS)); b.close()
