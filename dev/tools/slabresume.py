# (for the closers the gate is still shut at that moment: its own plate comes later)
# A floor saved after a slab has fallen on its plate (or closers) comes back with the slab fallen, the plate jammed and the gate open.
from playwright.sync_api import sync_playwright
JS='''([n,sd,kind])=>{const H=__HK;let L=H.load(n,sd,true);const d=L.detours.find(q=>q.puz===kind);if(!d)return {err:'none'};
  const pf=()=>H.L.dyn.find(o=>o.f.slabF&&(kind==='P2G1'?o.f.t==='plate':o.f.t==='closer')&&o.r===d.r&&o.c>=d.c0&&o.c<=d.c1);
  let saved=false,snap=null;
  const r=runBot(n,sd,{stop:H=>{const o=pf();if(o&&o.f.jam&&!snap&&['stand','run'].includes(H.P.state)){H.snapshotResume();snap=JSON.parse(JSON.stringify(H.S.resume));return true;}return false;}});
  if(!snap)return {err:'no snapshot',r:r.ok};
  L=H.load(n,sd,true);const o0=pf();const before=!!o0.f.jam;
  const ok=H.applyResume(snap);const o=pf();const gate=H.L.dyn.find(q=>q.f===o.f.g);
  return {ok,before,jam:!!o.f.jam,gateOpen:kind==='P3G1'?true:gate.f.tm===Infinity&&gate.f.open>0.9,slabFell:o.f.slabF.s===2};}'''
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(300); pg.add_script_tag(path='bot.js')
    fl={'P2G1':[],'P3G1':[]}
    for n in range(5,16):
        for s in range(6):
            sd=30000+s*101+n*7
            for k in fl:
                if len(fl[k])<3 and pg.evaluate("([n,sd,k])=>!!__HK.genLevel(n,sd,true).detours.find(q=>q.puz===k)",[n,sd,k]): fl[k].append((n,sd))
    bad=0
    for k,lst in fl.items():
        for n,sd in lst:
            r=pg.evaluate(JS,[n,sd,k]); good=r.get('ok') and not r.get('before') and r.get('jam') and r.get('gateOpen') and r.get('slabFell'); bad+=0 if good else 1
            print(k,n,sd,r,'OK' if good else 'BAD')
    print('bad',bad,errs[:3]); b.close()
