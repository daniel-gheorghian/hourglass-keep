# gratepeek.py [lo hi seeds [shot.png]]: crouching on a fork-4 grating looks down the shaft: the camera must come to rest with the
# flask and its violet gate both in view (the prince out of it), and letting go must bring him back into view. Floors lo..hi
# (default 6..27), `seeds` seeds each. With a fourth argument the first peek is saved as a screenshot of the page.
from playwright.sync_api import sync_playwright
import sys
lo,hi,ns=(int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3])) if len(sys.argv)>3 else (6,27,6)
shot=sys.argv[4] if len(sys.argv)>4 else None
f='/Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'
JS='''([lo,hi,ns,shot])=>{const H=__HK,bad=[];let tested=0,first=null;
  for(let n=lo;n<=hi;n++)for(let s=0;s<ns;s++){const seed=700000+n*97+s*13,L=H.load(n,seed,true);
    for(const fk of L.forks){if(!fk.grate)continue;const o=L.dyn.find(q=>q.f.t==='grate'&&q.r===fk.rUp),it=L.items.find(i=>i.fork);
      if(!o||!it){bad.push([n,seed,'no grate or flask']);continue;}
      tested++;const P=H.P;P.x=o.c*32+16;P.y=(fk.rUp+1)*64-4;P.fallY=P.y;P.state='stand';P.vx=0;P.vy=0;H.cam.snap=true;H.tick(2);
      H.setKey('kb','d',true);H.tick(240);
      const cam=H.cam,vw=H.viewW,sy=it.r*64+60,gx=fk.gate.c*32+16,seen=(x,y)=>x>cam.x&&x<cam.x+vw&&y>cam.y&&y<cam.y+192;
      if(!seen(it.x,sy-20))bad.push([n,seed,'flask not in view',Math.round(cam.x),Math.round(cam.y),it.x,sy]);
      if(!seen(gx,sy-20))bad.push([n,seed,'gate not in view']);
      if(shot){H.render();return {tested,bad};}
      H.setKey('kb','d',false);H.tick(240);
      if(!(P.y>cam.y&&P.y<cam.y+192&&P.x>cam.x&&P.x<cam.x+vw))bad.push([n,seed,'prince not back in view',P.state]);
    }}
  return {tested,bad:bad.slice(0,8)};}'''
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':844,'height':390}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+f); pg.wait_for_timeout(300); pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    r=pg.evaluate(JS,[lo,hi,ns,shot])
    if shot: pg.screenshot(path=shot)
    b.close()
print('gratepeek',lo,hi,'tested',r['tested'],'bad',len(r['bad']),r['bad'],errs[:2])
if r['bad'] or errs or not r['tested']: sys.exit(1)
