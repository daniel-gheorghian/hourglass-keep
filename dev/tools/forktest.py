# forktest.py: the forks (switchbacks with a hole in the upper run's floor, floor 6 on). Four kinds:
#   1 a guard on the shortcut against the traps of the long way   2 a damaging descent (a broken lip, one life)
#   3 a short dense shortcut against a long easy way             4 a one-way hole (damaging); one in five is a grating
# For every fork in the sample this plays the SHORTCUT branch from the hole to the door (the regression bot only ever takes the
# long way, run2.py): kind 1 fighting the guard, kinds 2 and 4 stepping off the broken lip (must cost exactly one life), kind 3
# through its traps. A grating cannot be entered: it must be solid floor, its violet gate must stand open once the bot has gone the
# long way past the plate, and the flask must lie behind the gate. Usage: forktest.py [lo hi seeds]. Run from dev/tools.
from playwright.sync_api import sync_playwright
import json,sys
lo,hi,ns=(int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3])) if len(sys.argv)>3 else (6,27,2)
F='/Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'
FIND='''([n,seed])=>{const L=__HK.load(n,seed,true);return L.forks.map((f,i)=>({i,v:f.v,grate:f.grate,hp:f.hp,H:f.H,Xl:f.Xl,rUp:f.rUp,rLow:f.rLow,dir:f.dir,
  tl:f.tilesLong,ts:f.tilesShort,tL:f.tLong,tS:f.tShort,kit:f.kit,hasGate:!!f.gate}));}'''
RUN='''([n,seed,i,fight])=>{const H=__HK;const L=H.load(n,seed,!fight),f=L.forks[i];window.__hurts=[];
  const sc=f.sc.map(a=>Object.assign({},a));if(f.hp&&sc[0].a==='hangdrop'){sc[0]={a:'drop',from:sc[0].from,dir:sc[0].dir};sc.splice(1,0,{a:'look',f:200});} // (stand a moment after the hurt landing)
  const path=[...L.path.slice(0,f.holeIdx),...sc,...L.path.slice(f.footIdx)].map(a=>Object.assign({},a));
  const r=runBot(n,seed,{fight,path});return {ok:r.ok,hurt:r.hurt,why:r.why,fights:r.fights,trace:r.trace?r.trace.slice(-4):null,hp0:H.P.maxHp};}'''
GRATE='''([n,seed,i])=>{const H=__HK;const L=H.load(n,seed,true),f=L.forks[i];const cell=L.base[f.rUp*L.cols+f.H]===1&&L.feat[f.rUp*L.cols+f.H]&&L.feat[f.rUp*L.cols+f.H].t==='grate';
  const gateOf=LL=>LL.dyn.find(o=>o.f.t==='gate'&&o.f.loop&&o.c===f.gate.c&&o.r===f.gate.r),flask=L.items.find(it=>it.fork&&it.r===f.rLow);
  let open=null;const r=runBot(n,seed,{fight:false,stop:H=>{if(open===null&&Math.floor((H.P.y-1)/64)===f.rLow&&Math.abs(H.P.x-flask.x)<40)open=gateOf(H.L).f.open;return open!==null;}});
  return {cell,hasFlask:!!flask,open,gateBetween:flask&&Math.sign(flask.c-f.gate.c)===-f.dir};}'''
tot=ok=0;bad=[];stats={1:[0,0],2:[0,0],3:[0,0],4:[0,0],'g':[0,0]};saved=[]
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':844,'height':390}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+F); pg.wait_for_timeout(300); pg.add_script_tag(path='bot.js')
    for n in range(lo,hi+1):
        for s in range(ns):
            seed=700000+n*97+s*13
            for f in pg.evaluate(FIND,[n,seed]):
                tot+=1; key='g' if f['grate'] else f['v']
                if f['grate']:
                    r=pg.evaluate(GRATE,[n,seed,f['i']]); good=r['cell'] and r['hasFlask'] and r['open'] is not None and r['open']>0.9
                else:
                    r=pg.evaluate(RUN,[n,seed,f['i'],f['v']==1]); good=r['ok'] is True and (r['hurt']==f['hp'] if f['v']!=1 else True)
                    if f['hp']: saved.append((f['tl']-f['ts'],f['tL']-f['tS'],f['tL']))
                stats[key][0]+=1; stats[key][1]+=1 if good else 0; ok+=1 if good else 0
                if not good: bad.append((n,seed,f,r))
    print('forks ok',ok,'/',tot,' by kind (built, passed):',stats)
    if saved: print('damaging shortcuts: mean tiles saved %.1f, mean seconds saved %.1f (%.0f%% of the long way)'%(sum(x[0] for x in saved)/len(saved),sum(x[1] for x in saved)/len(saved),100*sum(x[1] for x in saved)/sum(x[2] for x in saved)))
    for x in bad[:10]: print(json.dumps(x)[:500])
    print(errs[:3]); b.close()
sys.exit(0 if ok==tot else 1)
