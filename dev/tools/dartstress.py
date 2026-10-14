from playwright.sync_api import sync_playwright
import json,sys
JS=r'''([n,seed])=>{const H=__HK;const L0=H.load(n,seed,true);const out=[];
  const acts=L0.path.filter(a=>a.a==='darts').map(a=>Object.assign({},a));
  for(const a of acts){const dir=a.dir||1,sg=L0.segs.find(q=>q.k==='darts'&&Math.min(q.c0,q.c1)<=a.from&&Math.max(q.c0,q.c1)>=a.from);if(!sg)continue;
    for(let k=0;k<130;k+=9){window.__hurts=[];const r=runBot(n,seed,{fight:false,at:{c:a.from-dir,r:sg.r0,face:dir},path:[{a:'look',f:k},Object.assign({},a)],done:H=>H.P.state==='stand'&&Math.floor((H.P.y-1)/64)<sg.r0});
      out.push({c:a.from,k,ok:r.ok,hurt:r.hurt||0,why:r.why||''});}}
  return out;}'''
f=sys.argv[1]
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':844,'height':390}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+f); pg.wait_for_timeout(300); pg.add_script_tag(path='bot.js')
    tot=hurt=fail=0;ex=[]
    for n in range(6,28):
        for s in range(2):
            for r in pg.evaluate(JS,[n,700000+n*97+s*13]):
                tot+=1;hurt+=r['hurt']>0;fail+=r['ok'] is not True
                if (r['hurt'] or r['ok'] is not True) and len(ex)<8: ex.append((n,r))
    print('darts runs',tot,'hurt',hurt,'failed',fail,ex,errs[:2]);b.close()
