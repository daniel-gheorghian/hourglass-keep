# hdtest.py: the damaging shortcut (a one-tile hole with floor two storeys under it, in a chamber on floor 5 on).
# 1. the regression bot jumps the hole (it never takes damage there: run2.py covers that);
# 2. here the bot is sent in instead: it walks off the edge, must lose exactly one life (128px fall: hurts, does not kill),
#    land on the floor under the hole and still finish the floor along the rest of its path. Run from dev/tools.
from playwright.sync_api import sync_playwright
import sys
WANT=int(sys.argv[1]) if len(sys.argv)>1 else 4
FIND='''(want)=>{const H=__HK,out=[];for(let n=5;n<=27&&out.length<want;n+=3)for(let s=0;s<60;s++){const seed=40000+s*131+n*17,L=H.genLevel(n,seed,true);
  if(L.hurtdrops&&L.hurtdrops.length){const h=L.hurtdrops[0],j=L.path[h.jump];out.push({n,seed,h,j,k:L.hurtdrops.length});break;}}return out;}'''
RUN='''([n,seed,h,j,mode])=>{const L=__HK.genLevel(n,seed,true),p=L.path;
  const hole={a:'drop',from:j.from};if(j.dir)hole.dir=j.dir;
  const path=mode==='drop'?[...p.slice(0,h.jump),hole,...p.slice(h.next)]:p;
  window.__hurts=[];const r=runBot(n,seed,{path});r.h=window.__hurts;r.hp0=__HK.P.maxHp;r.hp=__HK.P.hp;return r;}'''
bad=0
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':844,'height':390}); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(300); pg.add_script_tag(path='bot.js')
    fl=pg.evaluate(FIND,WANT)
    print('floors with a chamber shortcut (hgap, now only where it saves a quarter of the chamber and ten tiles):',len(fl),'(the damaging forks of kinds 2 and 4 are in forktest.py)')
    for f in fl:
        # the drop route: one life lost, then the rest of the floor along the bot's path, all the way to the door
        r=pg.evaluate('''([n,seed,h,j])=>{const L=__HK.genLevel(n,seed,true),p=L.path;const hole={a:'drop',from:j.from};if(j.dir)hole.dir=j.dir;
          const path=[...p.slice(0,h.jump),hole,...p.slice(h.next)];window.__hurts=[];const r=runBot(n,seed,{path});r.h=window.__hurts;return r;}''',[f['n'],f['seed'],f['h'],f['j']])
        good=r.get('hurt')==1 and (r.get('ok') is True or r.get('ok')=='path done')
        if not good: bad+=1
        print(' n=%d seed=%d drop route: ok=%s damage=%s %s'%(f['n'],f['seed'],r.get('ok'),r.get('hurt'),'' if good else r))
    print('FAILURES',bad,'errors',errs[:3]); b.close()
