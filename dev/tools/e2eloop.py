from playwright.sync_api import sync_playwright
import json,sys
f=sys.argv[1] if len(sys.argv)>1 else '/Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'
lo,hi,ns=(int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4])) if len(sys.argv)>4 else (6,27,2)
JS=r'''([n,seed])=>{const H=__HK;const L0=H.load(n,seed,true);if(!L0.loops.length)return null;
  // play the floor, but at the first loop take the hole: down the ledges to the shut gate, back up, then on the long way
  const q=L0.loops[0],h=q.rLow-q.rUp,dir=q.dir,col=j=>j%2?q.H:q.O;
  const path=L0.path.map(a=>Object.assign({},a));const i=path.findIndex(a=>a.a==='sjump'&&a.loop&&a.from===q.H-dir&&a.to===q.O);if(i<0)return {err:'no sjump'};
  const seq=[{a:'drop',from:q.H-dir,dir}];for(let j=1;j<h;j++){const a=col(j),b=col(j+1);seq.push({a:'drop',from:a,dir:Math.sign(b-a)});}
  seq.push({a:'look'});
  const X=col(h-1),Y=X===q.H?q.O:q.H;seq.push({a:'walk',c:Y},{a:'climb',from:Y,dir:Math.sign(X-Y)});for(let j=h-1;j>=1;j--){const a=col(j),b=j>1?col(j-1):q.O;seq.push({a:'climb',from:a,dir:Math.sign(b-a)});}
  path.splice(i,1,...seq);
  let sawShut=null;const gate=()=>H.L.dyn.find(o=>o.f.t==='gate'&&o.f.loop&&o.c===q.gate.c&&o.r===q.gate.r);
  const r=runBot(n,seed,{fight:false,path,stop:H=>{if(sawShut===null&&H.P.state==='stand'&&Math.floor((H.P.y-1)/64)===q.rLow&&Math.abs(H.P.x/32-q.H)<3)sawShut=gate().f.open<0.05;return false;}});
  return {ok:r.ok,why:r.why,hurt:r.hurt,sawShut,openAtEnd:gate().f.open>0.9,trace:r.trace?r.trace.slice(-4):null};}'''
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':844,'height':390}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+f); pg.wait_for_timeout(300); pg.add_script_tag(path='bot.js')
    pg.evaluate("()=>{const o=window.runBot;}")
    tot=ok=0
    for n in range(lo,hi+1):
        for s in range(ns):
            seed=700000+n*97+s*13
            r=pg.evaluate(JS,[n,seed])
            if r is None: continue
            tot+=1; good=r.get('ok') is True and r.get('sawShut') is True and r.get('openAtEnd') and not r.get('hurt')
            ok+=good
            if not good: print(n,seed,json.dumps(r)[:300])
    print('shortcut-first floors finished',ok,'/',tot,errs[:3]); b.close()
