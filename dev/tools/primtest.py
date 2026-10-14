# primtest.py: the bot plays whole floors that hold each new vertical move (collapse, jumpdown, jumpup) in a turn chamber and
# in a run, and must finish them without taking damage. Run from dev/tools.
from playwright.sync_api import sync_playwright
import sys
PER=int(sys.argv[1]) if len(sys.argv)>1 else 4
FIND='''([act,where,per])=>{const H=__HK,out=[],kind={collapse:'collapse',jumpdown:'jumpdown',jumpup:'jgrab'}[act];
 for(let n=5;n<=27&&out.length<per;n+=3)for(let s=0;s<40;s++){const seed=30000+s*131+n*17,L=H.genLevel(n,seed,true);
  const inTurn=L.segs.some(q=>q.k==='turn-'+act),inRun=act==='jumpdown'?L.segs.some(q=>q.k==='down'&&false):false;
  const cnt=L.path.filter(a=>kind==='jumpdown'?a.jd:a.a===kind).length;
  // in a run: the action appears but not as a turn piece (counted by difference)
  const turnCnt=L.segs.filter(q=>q.k==='turn-'+act).length;
  if(where==='turn'?turnCnt>0:cnt>turnCnt){out.push([n,seed]);break;}}
 return out;}'''
bad=0
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':844,'height':390}); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(300); pg.add_script_tag(path='bot.js')
    for act in ('collapse','jumpdown','jumpup'):
        for where in ('turn','run'):
            fl=pg.evaluate(FIND,[act,where,PER])
            res=[]
            for n,seed in fl:
                r=pg.evaluate('([n,s])=>{window.__hurts=[];const r=runBot(n,s,{});r.h=window.__hurts;return r}',[n,seed])
                good=r.get('ok') is True and not r.get('hurt')
                if not good: bad+=1
                res.append((n,seed,'ok' if good else r.get('why') or r.get('h')))
            print('%-9s in a %-4s: %d floors  %s'%(act,where,len(fl),res))
    # a jump that falls short drops a storey onto plain floor in the pit; he climbs out on the side he came from and may try again
    fl=pg.evaluate(FIND,['jumpup','turn',PER])
    for n,seed in fl:
        r=pg.evaluate('''([n,seed])=>{const L=__HK.genLevel(n,seed,true);let a,sg;for(const x of L.path){if(x.a!=='jgrab')continue;const q=L.segs.find(q=>q.k==='turn-jumpup'&&q.dir===(x.dir||1)&&Math.min(q.c0,q.c1)<=x.from&&Math.max(q.c0,q.c1)>=x.from);if(q){a=x;sg=q;break;}}
          const d=a.dir||1,row=sg.r0;
          const pit=a.from+d;return runBot(n,seed,{path:[{a:'climb',from:pit,to:a.from,dir:d}],at:{c:pit,r:row+1,face:d}});}''',[n,seed])
        good=r.get('ok')=='path done' and not r.get('hurt')
        if not good: bad+=1
        print('jumpup pit climb-out  n=%d seed=%d: %s'%(n,seed,'ok' if good else r))
    print('FAILURES',bad,'errors',errs[:3]); b.close()
