# hillscan.py [file.html] [lo hi] [seeds]: round 43's heaps and drifts (placeHills). For every floor lo..hi (default 1-48) and seed (default
# 1,2,3): how many hills, of which kind and look, and the time they add to the bot's way at the held pace (a drift's length at HILL_WADE
# instead of RUN, a heap's at HILL_CLIMB); and the rules: every hill cell is plain floor (FLOOR, no feature) of a run's own plain floor (a
# 'flat' seg, never breathe()'s padding), with headroom (a heap: open above), off the dark's chase, off every timed stretch (the segs from a
# timed gate's plate to its gate), clear of lamps (their own cell), clocks and flasks (a cell either side), of guards' and snakes' ground, doors, lifts and
# movable blocks; none on floors 1-2, no drift before floor 5 or in Nun, Osiris or Aksum; a heap 2 tiles, a drift 3-6; and at least one a
# floor from floor 3. Prints a table by floor band and 'hillscan: ok'. Run from dev/tools.
import os, sys, json
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
SRC = os.path.abspath(next((x for x in a if x.endswith('.html')), os.path.join(HERE, '..', 'hourglass-keep.html')))
NUM = [int(x) for x in a if x.isdigit()]
LO, HI = (NUM[0], NUM[1]) if len(NUM) >= 2 else (1, 48)
SEEDS = [int(s) for s in next((x for x in a if ',' in x), '1,2,3').split(',')]

JS = r'''([n,sd])=>{const H=__HK,L=H.genLevel(n,sd,true),C=L.cols,TW=32,hs=L.hills||[],bad=[],B=(c,r)=>L.base[r*C+c],F=(c,r)=>L.feat[r*C+c];
  const flat=new Set();L.segs.forEach((q,i)=>{if(q.k!=='flat'||q.r0!==q.r1)return;for(let c=Math.min(q.c0,q.c1);c<=Math.max(q.c0,q.c1);c++)if(c!==q.c0)flat.add(q.r0*C+c);});
  const segAt=(c,r)=>{const o=[];L.segs.forEach((q,i)=>{if(c>=Math.min(q.c0,q.c1)&&c<=Math.max(q.c0,q.c1)&&r>=Math.min(q.r0,q.r1)&&r<=Math.max(q.r0,q.r1))o.push(i);});return o;};
  const timed=new Set();for(const o of L.dyn){const f=o.f;if(f.t!=='plate'||!f.g||f.g.latch||!(f.g.dur>0))continue;const go=L.dyn.find(q=>q.f===f.g);if(!go)continue;
    const A=segAt(o.c,o.r),Bb=segAt(go.c,go.r),all=A.concat(Bb);if(!all.length)continue;for(let i=Math.min(...all);i<=Math.max(...all);i++){const q=L.segs[i];for(let r=Math.min(q.r0,q.r1);r<=Math.max(q.r0,q.r1);r++)for(let c=Math.min(q.c0,q.c1);c<=Math.max(q.c0,q.c1);c++)timed.add(r*C+c);}}
  const near=(list,f)=>list.some(f),lk=L.theme.look,ch=L.ext.chase;let extra=0;
  for(const h of hs){const tag=h.v+'@'+h.c+','+h.r;
    if(h.d?(h.n<3||h.n>6):h.n!==2)bad.push(tag+' length '+h.n);
    if(h.d&&(n<5||['nun','osiris','aksum'].includes(lk)))bad.push(tag+' drift in '+lk+' floor '+n);
    for(let c=h.c;c<h.c+h.n;c++){const r=h.r,k=r*C+c;
      if(B(c,r)!==1||F(c,r))bad.push(tag+' not plain floor at '+c);
      if(!flat.has(k))bad.push(tag+' not a run\'s plain floor at '+c);
      if(timed.has(k))bad.push(tag+' on a timed stretch at '+c);
      if(B(c,r-1)===2||(h.d===0&&B(c,r-1)!==0))bad.push(tag+' no headroom at '+c);
      if(ch&&r>=ch.rTop&&r<=ch.rBot&&c>=ch.c0-4&&c<=ch.c1+4)bad.push(tag+' in the chase');
      if(near(L.torches,t=>t.r===r&&t.c===c)||near(L.cps,q=>q.r===r&&Math.abs(q.c-c)<=1)||near(L.items,q=>q.r===r&&Math.abs(q.c-c)<=1))bad.push(tag+' beside a lamp, clock or flask at '+c);
      if(near(L.guards,g=>g.r===r&&c>=Math.floor(g.lo/TW)-2&&c<=Math.floor(g.hi/TW)+2)||near(L.snakeSpecs,s=>s.r===r&&c>=Math.floor(s.lo/TW)-2&&c<=Math.floor(s.hi/TW)+2))bad.push(tag+' on a fighter\'s ground at '+c);
      if((L.door.r===r&&Math.abs(L.door.c-c)<=2))bad.push(tag+' by the door');}
    extra+=h.n*TW*(1/(h.d?H.HILL_WADE:H.HILL_CLIMB)-1/100);}
  return {n,sd,lk,th:H.themeName(n),hills:hs.map(h=>({v:h.v,d:h.d,n:h.n,blk:!!h.blk})),extra,bad};}'''

if __name__ == '__main__':
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto('file://' + SRC); pg.wait_for_timeout(600)
        rows = [pg.evaluate(JS, [n, sd]) for n in range(LO, HI + 1) for sd in SEEDS]
        b.close()
    bad = [(r['n'], r['sd'], x) for r in rows for x in r['bad']]
    none = [(r['n'], r['sd'], r['lk']) for r in rows if r['n'] >= 3 and not r['hills']]
    bands = [(1, 2), (3, 4), (5, 12), (13, 24), (25, 36), (37, 48)]
    print('floors %d-%d, seeds %s: %d floors' % (LO, HI, SEEDS, len(rows)))
    print('band     floors  hills/floor  heaps (B1/B2/B3)   drifts (with blocks)  extra s/floor (mean, max)')
    for lo, hi in bands:
        rs = [r for r in rows if lo <= r['n'] <= hi]
        if not rs: continue
        hs = [h for r in rs for h in r['hills']]
        v = lambda k: sum(1 for h in hs if h['v'] == k)
        ex = [r['extra'] for r in rs]
        print('%2d-%-3d   %4d    %5.2f        %3d (%d/%d/%d)      %3d (%d)             %.1f, %.1f' % (lo, hi, len(rs), len(hs) / len(rs), v('B1') + v('B2') + v('B3'), v('B1'), v('B2'), v('B3'),
              v('C2'), sum(1 for h in hs if h['blk']), sum(ex) / len(ex), max(ex)))
    dl = [h['n'] for r in rows for h in r['hills'] if h['d']]
    if dl: print('drift lengths', {k: dl.count(k) for k in sorted(set(dl))})
    print('floors from 3 with no hill: %d %s' % (len(none), none[:12]))
    for x in bad[:20]: print('BAD', x)
    if errs: print('errors', errs[:5])
    print('hillscan: ok' if not bad and not none and not errs else 'hillscan: FAIL (%d faults, %d floors without one)' % (len(bad), len(none)))
