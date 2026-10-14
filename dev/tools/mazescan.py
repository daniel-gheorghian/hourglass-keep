# mazescan.py [lo hi [seeds]]: gate puzzles per floor on floors forced to the maze flag against ordinary floors (no flag forced),
# per band; the maze must hold at least 1.5 times as many (unit G1). Also longway: forks per floor on longway floors (>= 1).
import sys,statistics as S
from playwright.sync_api import sync_playwright
lo,hi=(int(sys.argv[1]),int(sys.argv[2])) if len(sys.argv)>2 else (5,27)
ns=int(sys.argv[3]) if len(sys.argv)>3 else 12
JS='''([lo,hi,ns,flag])=>{const o={};for(let n=lo;n<=hi;n++){const a=[];for(let s=0;s<ns;s++){window.__FEAT=flag?{flag}:null;const L=__HK.genLevel(n,50000+s*131+n*17,true);
 if(flag&&(L.feature||{}).flag!==flag){a.push(null);continue;}if(!flag&&(L.feature||{}).flag){a.push(null);continue;}
 a.push([L.puzzles.length,L.forks.length]);}o[n]=a.filter(x=>x);}window.__FEAT=null;return o;}'''
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(300)
    R={f:pg.evaluate(JS,[lo,hi,ns,f]) for f in (None,'maze','longway')}; b.close()
bands=[(5,8),(9,14),(15,20),(21,27)]
lost=sum(max(0,ns-len(R['longway'].get(str(n),[]))) for n in range(max(lo,6),hi+1)) # longway floors that lost the flag (no fork fits)
totl=ns*len(range(max(lo,6),hi+1))
ok=True
print('band   normal-puz maze-puz ratio | longway-forks (floors with a fork / floors)')
for a,z in bands:
    g=lambda f,i:[x[i] for n in range(max(a,lo),min(z,hi)+1) for x in R[f].get(str(n),[])]
    pn,pm=g(None,0),g('maze',0)
    if not pn or not pm: continue
    r=S.mean(pm)/S.mean(pn); lw=g('longway',1) if z>=6 else []
    print('%2d-%-2d  %6.2f  %6.2f  %5.2f | %s'%(a,z,S.mean(pn),S.mean(pm),r,'%.2f (%d/%d)'%(S.mean(lw),sum(1 for x in lw if x>=1),len(lw)) if lw else '-'))
    if r<1.5: ok=False
    if lw and min(lw)<1: ok=False
print('longway floors that fell back to no flag: %d / %d'%(lost,totl))
print('maze/longway OK' if ok and not errs else 'MAZE/LONGWAY FAIL'); 
if errs: print(errs[:3])
sys.exit(0 if ok and not errs else 1)
