# slabscan.py [file.html] [lo hi] [seeds]: every stone slab that slides up (a granite portcullis, a counterweight lift's mouth slab
# on either landing; with EGP.traps off the same places hold iron gratings) must have stone above it to go into: the cell over the
# slab's cell a wall, or a floor (its slab). Round 25d (owner: "lift slab with no ceiling above it"): the open-hall pass gave every
# lift's top landing a row of headroom, mouth and shaft top included, so the top slab stood free against the hall. Floors lo..hi
# (default 1..48: all twelve themes), seeds 701 and 4400+n+97k (default 3 a floor). The check is on the tiles, so it holds for
# Classic and Torchlight alike (both draw the slab from the same cell). Prints the counts, each slab without stone, then
# 'slabscan: ok' or 'slabscan: FAIL n'. Run from dev/tools.
import os, sys
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
SRC = os.path.abspath(next((x for x in a if x.endswith('.html')), os.path.join(HERE, '..', 'hourglass-keep.html')))
NUM = [int(x) for x in a if x.isdigit()]
LO, HI = (NUM[0], NUM[1]) if len(NUM) >= 2 else (1, 48)
NS = NUM[2] if len(NUM) >= 3 else 3
JS = r'''([lo,hi,ns])=>{const H=__HK,out={n:0,gate:0,top:0,bot:0,bad:[]};
  for(let n=lo;n<=hi;n++)for(let s=0;s<ns;s++){const seed=s===0?701:4400+n+s*97,L=H.load(n,seed,true),C=L.cols,
      B=(c,r)=>(r<0||c<0||c>=C)?2:L.base0[r*C+c],stone=(c,r)=>{const b=B(c,r);return b===2||b===1;}; // (base0: the terrain as built and drawn)
    const chk=(k,c,r,x)=>{out.n++;out[k]++;if(!stone(c,r-1))out.bad.push([k,n,seed,H.themeName(n),c,r,B(c,r-1),x]);};
    for(const o of L.dyn)if(o.f.t==='gate')chk('gate',o.c,o.r,'');
    for(const f of L.lifts){if(f.t!=='lift'||f.sand)continue; // (the sand lift has no slab)
      if(f.sT)chk('top',f.sc+f.sT,f.rT,'shaft '+f.sc);if(f.sB)chk('bot',f.sc+f.sB,f.rB,'shaft '+f.sc);}}
  return out;}'''
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page()
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://' + SRC)
    pg.wait_for_timeout(500)
    r = pg.evaluate(JS, [LO, HI, NS])
    b.close()
print('floors %d-%d, %d seeds: %d slabs (%d portcullises, %d top lift mouths, %d bottom lift mouths), %d without stone above' % (LO, HI, NS, r['n'], r['gate'], r['top'], r['bot'], len(r['bad'])))
for x in r['bad'][:40]:
    print('  no stone above: %s floor %d seed %d (%s) cell %d,%d above=%d %s' % tuple(x))
if errs:
    print('errors', errs[:3])
print('slabscan: ok' if not r['bad'] and not errs else 'slabscan: FAIL %d' % (len(r['bad']) + len(errs)))
sys.exit(1 if r['bad'] or errs else 0)
