# windscan.py [file.html] [lo hi] [seeds] [nopush]: round 44's wind (placeWinds, L.winds). For every floor lo..hi (default 1-48) and seed
# (default 1,2,3): how many winds of each kind (s a steady draught, g gusts at a window, d the wind over a drift), the floors that needed the
# one-cell clearance, and the time they add to a run held through them (a steady draught at 65 px/s, a gust taken at its worst, 40, a drift's
# approach at 70 and its wade at 33); and the rules: every wind cell is plain floor (FLOOR, no feature, no wall over it), off every timed
# stretch (the segs from a timed gate's plate to its gate), off the dark's chase, off guards' and snakes' ground, the doors; at least z.jm
# cells (WIND_JM 3, or 1 where 3 leaves no stretch on the floor) from every cell of a seg that is not plain floor, on that seg's rows (no
# generated jump, fall, grab or swing in it); it blows against the run (the flat seg's way); 3-8 cells (s, g); a gust only from floor
# WIND_G0 with a window (round 45: or a court's open side) over it; a drift's wind covers its drift; none on floors 1-2, at least one steady or gust a floor from 3. Then the
# push: he stands in each gust zone (its two ends and its middle) with no key for 9 s (two gusts): he must stay in the zone, on his feet, alive.
# Prints a table by floor band and 'windscan: ok'. Run from dev/tools.
import os, sys
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
SRC = os.path.abspath(next((x for x in a if x.endswith('.html')), os.path.join(HERE, '..', 'hourglass-keep.html')))
NUM = [int(x) for x in a if x.isdigit()]
LO, HI = (NUM[0], NUM[1]) if len(NUM) >= 2 else (1, 48)
SEEDS = [int(s) for s in next((x for x in a if ',' in x), '1,2,3').split(',')]
PUSH = 'nopush' not in a

JS = r'''([n,sd])=>{const H=__HK,L=H.genLevel(n,sd,true),C=L.cols,TW=32,ws=L.winds||[],bad=[],B=(c,r)=>L.base[r*C+c],F=(c,r)=>L.feat[r*C+c];
  const flatDir=new Map();L.segs.forEach(q=>{if(q.k!=='flat'||q.r0!==q.r1)return;const d=q.dir||(q.c1>=q.c0?1:-1);for(let c=Math.min(q.c0,q.c1);c<=Math.max(q.c0,q.c1);c++)if(c!==q.c0)flatDir.set(q.r0*C+c,d);});
  const segAt=(c,r)=>{const o=[];L.segs.forEach((q,i)=>{if(c>=Math.min(q.c0,q.c1)&&c<=Math.max(q.c0,q.c1)&&r>=Math.min(q.r0,q.r1)&&r<=Math.max(q.r0,q.r1))o.push(i);});return o;};
  const timed=new Set();for(const o of L.dyn){const f=o.f;if(f.t!=='plate'||!f.g||f.g.latch||!(f.g.dur>0))continue;const go=L.dyn.find(q=>q.f===f.g);if(!go)continue;
    const A=segAt(o.c,o.r),Bb=segAt(go.c,go.r),all=A.concat(Bb);if(!all.length)continue;for(let i=Math.min(...all);i<=Math.max(...all);i++){const q=L.segs[i];for(let r=Math.min(q.r0,q.r1);r<=Math.max(q.r0,q.r1);r++)for(let c=Math.min(q.c0,q.c1);c<=Math.max(q.c0,q.c1);c++)timed.add(r*C+c);}}
  const near=(list,f)=>list.some(f),ch=L.ext.chase;let extra=0,jm1=0;
  for(const z of ws){const tag=z.k+'@'+z.c+','+z.r;if(z.jm===1)jm1=1;
    if(z.k!=='d'&&(z.n<3||z.n>8))bad.push(tag+' length '+z.n);
    if(z.k==='g'){if(n<H.WIND_G0)bad.push(tag+' gust before floor '+H.WIND_G0);if(!z.src||!((L.windows||[]).some(w=>(w.r===z.r||w.r===z.r-1)&&w.c>=z.c&&w.c<z.c+z.n)||(L.courts||[]).some(k=>k.k!=='well'&&k.r===z.r&&Math.floor(z.src.x/TW)>=k.c0&&Math.floor(z.src.x/TW)<=k.c1)))bad.push(tag+' gust with no window or court over it');}
    if(z.k==='d'){const h=(L.hills||[]).find(h=>h.d&&h.r===z.r&&h.c>=z.c&&h.c+h.n<=z.c+z.n);if(!h)bad.push(tag+' drift wind with no drift');else if(z.dir!==-h.dir)bad.push(tag+' drift wind with the run');}
    for(let c=z.c;c<z.c+z.n;c++){const r=z.r,k=r*C+c;
      if(B(c,r)!==1||F(c,r))bad.push(tag+' not plain floor at '+c);
      if(B(c,r-1)===2)bad.push(tag+' a wall over it at '+c);
      if(timed.has(k))bad.push(tag+' on a timed stretch at '+c);
      if(z.k!=='d'&&flatDir.has(k)&&flatDir.get(k)!==-z.dir)bad.push(tag+' blows with the run at '+c);
      if(z.k!=='d'&&!flatDir.has(k))bad.push(tag+' not a run\'s plain floor at '+c);
      if(ch&&r>=ch.rTop&&r<=ch.rBot&&c>=ch.c0-4&&c<=ch.c1+4)bad.push(tag+' in the chase');
      if(near(L.guards,g=>g.r===r&&c>=Math.floor(g.lo/TW)-2&&c<=Math.floor(g.hi/TW)+2)||near(L.snakeSpecs,s=>s.r===r&&c>=Math.floor(s.lo/TW)-2&&c<=Math.floor(s.hi/TW)+2))bad.push(tag+' on a fighter\'s ground at '+c);
      if(L.door.r===r&&Math.abs(L.door.c-c)<=2)bad.push(tag+' by the door');
      for(const q of L.segs){if(q.k==='flat')continue;if(r<Math.min(q.r0,q.r1)||r>Math.max(q.r0,q.r1))continue;if(c>=Math.min(q.c0,q.c1)-z.jm&&c<=Math.max(q.c0,q.c1)+z.jm){bad.push(tag+' within '+z.jm+' of seg '+q.k+' at '+c);break;}}}
    if(z.k==='d'){const h=(L.hills||[]).find(h=>h.d&&h.r===z.r&&h.c>=z.c&&h.c+h.n<=z.c+z.n);if(h)extra+=(z.n-h.n)*TW*(1/70-1/100)+h.n*TW*(1/(42*(1-0.25*H.WIND_DE))-1/42);}
    else extra+=z.n*TW*(1/(z.k==='g'?40:65)-1/100);}
  const gz=ws.filter(z=>z.k==='g').map(z=>[z.c,z.r,z.n,z.dir]);
  return {n,sd,lk:L.theme.look,w:ws.map(z=>({k:z.k,n:z.n})),jm1,extra,bad,gz,hg:(L.hangings||[]).filter(h=>h.wz).length};}'''
# he stands in a gust zone with no key for 9 s: he must stay in it, standing, alive
PUSHJS = r'''([n,sd,c,r,nn,dir,u])=>{const H=__HK;const L=H.load(n,sd,true);H.banner=null;const P=H.P;P.inv=1e9;for(const e of H.G)e.x=-9999;
  const a=c*32,b=(c+nn)*32;P.x=a+u*(b-a);P.y=(r+1)*64-4;P.fallY=P.y;P.vx=0;P.face=-dir;P.state='stand';H.mode='play';
  for(const k of ['l','r','u','d','j','g'])H.setKey('kb',k,false);let lo=P.x,hi=P.x,moved=0;const x0=P.x;
  for(let i=0;i<540;i++){H.tick(1);lo=Math.min(lo,P.x);hi=Math.max(hi,P.x);if(P.state!=='stand'||H.mode!=='play')return {ok:false,why:'state '+P.state+' '+H.mode,x:P.x};}
  return {ok:lo>=a-0.5&&hi<=b+0.5,lo,hi,a,b,moved:Math.abs(P.x-x0)};}'''

if __name__ == '__main__':
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto('file://' + SRC); pg.wait_for_timeout(600)
        rows = [pg.evaluate(JS, [n, sd]) for n in range(LO, HI + 1) for sd in SEEDS]
        pushes = []
        if PUSH:
            for r in rows:
                for (c, rr, nn, dr) in r['gz']:
                    for u in (0.06, 0.5, 0.94):
                        q = pg.evaluate(PUSHJS, [r['n'], r['sd'], c, rr, nn, dr, u]); q['at'] = (r['n'], r['sd'], c, rr, u); pushes.append(q)
        b.close()
    bad = [(r['n'], r['sd'], x) for r in rows for x in r['bad']]
    none = [(r['n'], r['sd'], r['lk']) for r in rows if r['n'] >= 3 and not any(w['k'] != 'd' for w in r['w'])]
    early = [(r['n'], r['sd']) for r in rows if r['n'] < 3 and r['w']]
    bands = [(1, 2), (3, 4), (5, 12), (13, 24), (25, 36), (37, 48)]
    print('floors %d-%d, seeds %s: %d floors' % (LO, HI, SEEDS, len(rows)))
    print('band     floors  winds/floor  steady  gusts  drifts  hangings  1-cell floors  extra s/floor (mean, max)')
    for lo, hi in bands:
        rs = [r for r in rows if lo <= r['n'] <= hi]
        if not rs: continue
        ws = [w for r in rs for w in r['w']]
        v = lambda k: sum(1 for w in ws if w['k'] == k)
        ex = [r['extra'] for r in rs]
        print('%2d-%-3d   %4d    %5.2f        %4d   %4d    %4d    %4d      %4d           %.1f, %.1f' % (lo, hi, len(rs), len(ws) / len(rs), v('s'), v('g'), v('d'), sum(r['hg'] for r in rs), sum(r['jm1'] for r in rs), sum(ex) / len(ex), max(ex)))
    sl = [w['n'] for r in rows for w in r['w'] if w['k'] != 'd']
    if sl: print('steady/gust lengths', {k: sl.count(k) for k in sorted(set(sl))})
    pb = [q for q in pushes if not q['ok']]
    if PUSH: print('push: %d stands in gusts, %d left the zone or fell; moved mean %.1f px, max %.1f px' % (len(pushes), len(pb), sum(q.get('moved', 0) for q in pushes) / max(1, len(pushes)), max([q.get('moved', 0) for q in pushes] or [0])))
    print('floors from 3 with no steady wind or gust: %d %s' % (len(none), none[:12]))
    for x in bad[:20]: print('BAD', x)
    for q in pb[:10]: print('PUSH', q)
    if early: print('BAD winds on floors 1-2', early[:5])
    if errs: print('errors', errs[:5])
    ok = not bad and not none and not errs and not pb and not early
    print('windscan: ok' if ok else 'windscan: FAIL (%d faults, %d floors without one, %d pushes)' % (len(bad), len(none), len(pb)))
