# guardscan.py [lo hi [seeds]]: guards and snakes are fighters on their own budgets, not traps (guardBudget / snakeBudget in the page).
# Per floor lo..hi (default 1..35) x seeds (default 8) it counts guards (skeletons, captains), snakes, reinforcements, ambushes and the
# sources of the guards, and checks: encounters (guards + the reinforcements they call + ambushes) within the floor's budget (the top of
# its jitter, the garrison floor doubled); snakes within theirs and fewer than the guards' top budget; a captain on every fifth floor
# from 5 and nowhere else; reinforcements only from the captain and the garrison; sources only the meaningful spots (gate, exit, fork,
# garrison; ambush counted from the secret passage); guards of one row at least 25 tiles apart (fork guards aside). Exit 1 on any breach.
import sys
from playwright.sync_api import sync_playwright
lo,hi=(int(sys.argv[1]),int(sys.argv[2])) if len(sys.argv)>2 else (1,35)
ns=int(sys.argv[3]) if len(sys.argv)>3 else 8
JS='''([lo,hi,ns])=>{const H=__HK,out=[],bad=[];
 for(let n=lo;n<=hi;n++){const rows=[];
  for(let s=0;s<ns;s++){const sd=30000+s*101+n*7,L=H.genLevel(n,sd,true),g=L.guards,flag=L.feature&&L.feature.flag,barr=flag==='barracks';
   const src={};for(const q of g)src[q.src||'?']=(src[q.src||'?']||0)+1;
   const amb=(L.detours||[]).filter(q=>q.amb).length,rf=g.filter(q=>q.reinf).length,cap=g.filter(q=>q.cap).length,sk=g.filter(q=>q.skel).length;
   const enc=g.length+rf+amb,top=H.guardBudget(n,0,barr),stop=H.snakeBudget(n,0),gtop=H.guardBudget(n,0,false);
   const why=[];
   if(enc>top)why.push('encounters '+enc+' over budget '+top);
   if(L.snakeSpecs.length>stop)why.push('snakes '+L.snakeSpecs.length+' over '+stop);
   if(stop>=gtop&&gtop>0||stop>gtop)why.push('snake budget not below guards');
   const want=n%5===0&&n>=5?1:0;
   if(cap!==want)why.push('captains '+cap+' want '+want);
   for(const q of g){if(q.reinf&&!q.cap&&q.src!=='garrison')why.push('reinforcement from '+q.src);
     if(!['gate','exit','fork','garrison'].includes(q.src))why.push('guard source '+q.src);
     if(q.src==='garrison'&&!barr)why.push('garrison on an ordinary floor');}
   const nf=g.filter(q=>q.src!=='fork');
   for(let i=0;i<nf.length;i++)for(let j=i+1;j<nf.length;j++)if(nf[i].r===nf[j].r&&Math.abs(nf[i].x-nf[j].x)<25*32)why.push('two guards '+Math.round(Math.abs(nf[i].x-nf[j].x)/32)+' tiles apart');
   if(why.length)bad.push({n,seed:sd,why});
   rows.push({g:g.length,sn:L.snakeSpecs.length,cap,sk,rf,amb,enc,top,barr,src,fork:(src.fork||0)});}
  out.push({n,rows});}
 return {out,bad};}'''
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(300)
    R=pg.evaluate(JS,[lo,hi,ns]); b.close()
m=lambda a:sum(a)/max(1,len(a))
print('floor guards snakes captains skel reinf amb encounters/budget  sources (all seeds)')
for f in R['out']:
    r=f['rows']; src={}
    for x in r:
        for k,v in x['src'].items(): src[k]=src.get(k,0)+v
    print('%5d %6.1f %6.1f %8.2f %4.2f %5.2f %3.2f %6.1f/%-4.1f  %s'%(f['n'],m([x['g'] for x in r]),m([x['sn'] for x in r]),m([x['cap'] for x in r]),m([x['sk'] for x in r]),m([x['rf'] for x in r]),m([x['amb'] for x in r]),m([x['enc'] for x in r]),m([x['top'] for x in r]),' '.join('%s=%d'%kv for kv in sorted(src.items()))))
for x in R['bad'][:25]: print('BREACH floor %d seed %d: %s'%(x['n'],x['seed'],'; '.join(sorted(set(x['why'])))))
if errs: print('page errors',errs[:3])
ok=not R['bad'] and not errs
print('guardscan OK (%d breaches)'%len(R['bad']) if ok else 'GUARDSCAN FAILURES %d'%len(R['bad']))
sys.exit(0 if ok else 1)
