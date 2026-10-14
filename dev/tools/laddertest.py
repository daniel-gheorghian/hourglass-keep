from playwright.sync_api import sync_playwright
import json,sys
f=sys.argv[1] if len(sys.argv)>1 else '/home/claude/hourglass-keep.html'
lo,hi,ns=(int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4])) if len(sys.argv)>4 else (6,27,4)
JS=r'''([n,seed])=>{const H=__HK;const L0=H.load(n,seed,true);const out=[];
  for(let li=0;li<L0.loops.length;li++){const q=JSON.parse(JSON.stringify(L0.loops[li]));const h=q.rLow-q.rUp,dir=q.dir,col=j=>j%2?q.H:q.O;
    const gateOf=L=>L.dyn.find(o=>o.f.t==='gate'&&o.f.loop&&o.c===q.gate.c&&o.r===q.gate.r);
    // down: from the floor before the hole, drop through it and down the ledges to the lower run
    const down=[{a:'drop',from:q.H-dir,dir}];for(let j=1;j<h;j++){const a=col(j),b=col(j+1);down.push({a:'drop',from:a,dir:Math.sign(b-a)});}
    const rd=runBot(n,seed,{fight:false,at:{c:q.H-2*dir,r:q.rUp,face:dir},path:down,done:H=>H.P.state==='stand'&&Math.floor((H.P.y-1)/64)===q.rLow});
    const g=gateOf(H.L),downOk=rd.ok===true&&!rd.hurt,shut=g&&g.f.open<0.05;
    // up: from the lower run under the ladder, climb ledge by ledge to the upper run
    const X=col(h-1),Y=X===q.H?q.O:q.H,up=[{a:'climb',from:Y,dir:Math.sign(X-Y)}];for(let j=h-1;j>=1;j--){const a=col(j),b=j>1?col(j-1):q.O;up.push({a:'climb',from:a,dir:Math.sign(b-a)});}
    const ru=runBot(n,seed,{fight:false,at:{c:Y,r:q.rLow,face:Math.sign(X-Y)},path:up,done:H=>H.P.state==='stand'&&Math.floor((H.P.y-1)/64)===q.rUp});
    out.push({li,h,down:downOk,downWhy:rd.why||rd.ok,shut,up:ru.ok===true&&!ru.hurt,upWhy:ru.why||ru.ok,upAt:ru.trace?ru.trace.slice(-3):''});}
  return out;}'''
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':844,'height':390}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+f); pg.wait_for_timeout(300); pg.add_script_tag(path='bot.js')
    tot=ok=0;bad=[]
    for n in range(lo,hi+1):
        for s in range(ns):
            seed=700000+n*97+s*13
            for r in pg.evaluate(JS,[n,seed]):
                tot+=1
                if r['down'] and r['up'] and r['shut']: ok+=1
                else: bad.append((n,seed,r))
    print('ladders ok',ok,'/',tot)
    for x in bad[:10]: print(json.dumps(x)[:400])
    print(errs[:3]); b.close()
