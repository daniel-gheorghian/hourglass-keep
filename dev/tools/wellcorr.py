# wellcorr.py [lo] [hi] [seeds] [file]: round 30's check that no sand well stands in a corridor (owner: "a corridor above another corridor
# doesn't use sand tiles, but instead regular tiles"). For every well group (wellGroup) of floors lo..hi (default 1..48), seeds 801..800+seeds
# (default 3), it reads the tiles under the row of slabs: on every row from the slab's own floor down to each column's floor (looseWell's k),
# the cells on both sides of each column must be stone (WALL) or the same group's own pit (a neighbour of the row whose floor is no higher).
#  open     a side cell that is neither: the sand would stand as a column in the open (a corridor, a landing, a drop beside the shaft)
#  walk     of those, a cell with a floor under it he can walk onto from beside (a corridor under the corridor: the owner's screenshot)
# Prints one line per floor, the total of well groups and slabs, and 'wellcorr: ok' (no open side) or 'wellcorr: FAIL n'. Run from dev/tools.
import os, sys
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
LO = int(a[0]) if len(a) > 0 else 1
HI = int(a[1]) if len(a) > 1 else 48
NS = int(a[2]) if len(a) > 2 else 3
SRC = os.path.abspath(a[3] if len(a) > 3 else os.path.join(HERE, '..', 'hourglass-keep.html'))
JS = r'''([n,sd])=>{const H=__HK;window.__HKfreeze=true;H.load(n,sd,true);const L=H.L,C=L.cols,WALL=2,FLOOR=1;
  const B=(c,r)=>c<0||c>=C||r<0?WALL:r>=L.rows?0:L.base[r*C+c],sb=(c,r)=>{const b=B(c,r);return b===FLOOR||(b!==WALL&&r+1<L.rows&&B(c,r+1)===WALL);};
  let groups=0,slabs=0,open=0,walk=0;const bad=[],seen=new Set();
  for(const o of L.dyn){if(o.f.t!=='loose'||o.f.plank)continue;const g=H.wellGroup(o);if(!g||seen.has(g))continue;seen.add(g);groups++;slabs+=g.n;
    const kk=g.os.map(q=>H.looseWell(q));let ob=0,wb=0,at=null;
    for(let j=0;j<g.n;j++)for(let rr=g.r+1;rr<=g.r+kk[j];rr++)for(const sd of [-1,1]){const c=g.c0+j+sd,jn=j+sd;
      if(B(c,rr)===WALL||(jn>=0&&jn<g.n&&rr<=g.r+kk[jn]))continue;ob++;if(sb(c,rr))wb++;if(!at)at=[g.c0+j,rr,sd];}
    if(ob){open++;if(wb)walk++;bad.push([g.c0,g.r,g.n,kk.join(''),at]);}}
  return {groups,slabs,open,walk,bad};}'''
if __name__ == '__main__':
    T = dict(groups=0, slabs=0, open=0, walk=0)
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={'width': 852, 'height': 393})
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto('file://' + SRC); pg.wait_for_timeout(500)
        pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true)")
        for n in range(LO, HI + 1):
            for sd in range(801, 801 + NS):
                r = pg.evaluate(JS, [n, sd])
                for k in T: T[k] += r[k]
                print('floor', n, 'seed', sd, 'groups', r['groups'], 'slabs', r['slabs'], 'open', r['open'], 'walk', r['walk'], r['bad'][:3])
        print('page errors', errs[:3])
        b.close()
    print('wellcorr total: groups %(groups)d slabs %(slabs)d open %(open)d walk %(walk)d' % T)
    print('wellcorr: ok' if T['open'] == 0 and not errs else 'wellcorr: FAIL %d' % T['open'])
