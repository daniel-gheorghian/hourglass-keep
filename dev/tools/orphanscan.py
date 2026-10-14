# orphanscan.py [lo hi [seeds]]: dead-end side rooms. Every gate side passage (detour, alcove, remote branch) must hold the plate it
# was carved for; a branch whose plate was dropped (its gate found no room in the turn) is an orphan: a room to walk into for nothing.
# Counts them over floors lo..hi (default 1..27) x seeds (default 20); exit 1 if any.
import sys
from playwright.sync_api import sync_playwright
lo,hi=(int(sys.argv[1]),int(sys.argv[2])) if len(sys.argv)>2 else (1,27)
ns=int(sys.argv[3]) if len(sys.argv)>3 else 20
JS='''([lo,hi,ns])=>{const out=[];let tot=0,br=0;
 for(let n=lo;n<=hi;n++)for(let s=0;s<ns;s++){const sd=30000+s*101+n*7,L=__HK.genLevel(n,sd,true);tot++;
  const plates=[];for(const k in L.feat){const f=L.feat[k];if(f&&f.t==='plate')plates.push([+k%L.cols,Math.floor(+k/L.cols),f]);}
  for(const dd of L.detours||[]){
   if(dd.secret||dd.double||dd.puz==='P2G1'||dd.puz==='P3G1')continue; // (secrets hold a flask, the slab puzzles' plate lies on the corridor)
   br++;const ok=plates.some(([c,r])=>c>=dd.c0-1&&c<=dd.c1+1&&r!==dd.r&&Math.abs(r-dd.r)<=3);
   if(!ok)out.push({n,seed:sd,k:dd.puz||'detour',c0:dd.c0,r:dd.r});}}
 return {out,tot,br};}'''
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(300)
    R=pg.evaluate(JS,[lo,hi,ns]); b.close()
print('floors %d, side-passage branches %d, orphans %d'%(R['tot'],R['br'],len(R['out'])))
for o in R['out'][:20]: print(' ',o)
if errs: print('page errors',errs[:3])
print('orphans OK' if not R['out'] and not errs else 'ORPHANS FOUND')
sys.exit(1 if R['out'] or errs else 0)
