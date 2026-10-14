# A latching plate pressed before a checkpoint keeps its gate open after the respawn; one pressed after it does not.
from playwright.sync_api import sync_playwright
import json,sys
f=sys.argv[1] if len(sys.argv)>1 else '/Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'
JS=r'''([n,gseed])=>{const H=__HK,S=H.S,out=[];S.seed=gseed;
  const SURF=r=>(r+1)*64-4;
  const go=(c,r,k)=>{const P=H.P;P.x=c*32+16;P.y=SURF(r);P.fallY=P.y;P.vx=P.vy=0;P.state='stand';P.t=0;H.tick(k||6);};
  H.startLevel(n,-1);H.mode='play';
  const L0=H.L;if(!L0.cps.length)return out;
  const plates=L0.dyn.filter(o=>o.f.t==='plate'&&o.f.latch&&o.f.g.far).map(o=>({c:o.c,r:o.r,loop:!!o.f.loop,key:o.c+','+o.r}));
  const gateOf=(L,pl)=>{const o=L.dyn.find(o=>o.c===pl.c&&o.r===pl.r);return o.f.g;};
  for(const pl of plates.slice(0,3)){
    for(const mode of ['before','after']){
      H.startLevel(n,-1);H.mode='play';let L=H.L;
      const cp=L.cps[L.cps.length-1],cpi=L.cps.length-1;
      const order=mode==='before'?[[pl.c,pl.r],[Math.floor(cp.x/32),cp.r]]:[[Math.floor(cp.x/32),cp.r],[pl.c,pl.r]];
      for(const [c,r] of order){go(c,r,8);H.P.hp=H.P.hp;}
      const pressed=gateOf(H.L,pl).tm===Infinity,cpOn=H.L.cpIndex===cpi;
      // die and rise at the checkpoint (what respawn() does)
      H.startLevel(H.S.level,H.L.cpIndex);
      const g=gateOf(H.L,pl);
      out.push({n,seed:gseed,plate:pl.key,loop:pl.loop,mode,pressed,cpOn,openAfter:g.tm===Infinity&&g.open>=1});
    }
  }
  return out;}'''
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':844,'height':390}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+f); pg.wait_for_timeout(300)
    rows=[]
    for n in (4,6,8,10,13,17,22):
        for gs in (101,202,303,404):
            rows+=pg.evaluate(JS,[n,gs])
    bad=[];nb=na=0
    for r in rows:
        if not(r['pressed'] and r['cpOn']): bad.append(('setup',r));continue
        if r['mode']=='before':
            nb+=1
            if not r['openAfter']: bad.append(('closed after respawn',r))
        else:
            na+=1
            if r['openAfter']: bad.append(('stayed open though pressed after cp',r))
    print('cases before-cp',nb,'after-cp',na,'bad',len(bad),'loops covered',sum(1 for r in rows if r['loop'] and r['mode']=='before'))
    for x in bad[:8]: print(json.dumps(x)[:300])
    print(errs[:3]); b.close()
    sys.exit(1 if bad or not nb else 0)
