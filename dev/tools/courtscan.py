# courtscan.py [file.html] [lo hi] [seeds] [nodrown]: round 45's courts (placeCourts, L.courts). For every floor lo..hi (default 1-48) and seed
# (default 1,2,3): the courts' placement, counts, kinds and pools, and that nothing of the wall they replace is left. Placement: every court's
# cells have headroom (EMPTY over the walking row) with the ceiling's stone straight over it (WALL two rows up) and nothing in either; each cell
# is plain walking floor (FLOOR, any feature but a kick shaft's foot, a banner, a lift or a damaging drop) or a pool's pit; both ends are floor;
# 4-8 cells (a light well 2); none within 2 cells of a lift's shaft or 3 of a door; none on floors 1-2; 7 or 8 a floor from 3 (CT_WANT, or
# every stretch that qualifies where fewer do); never two in view at once (within 3 rows and 14 cells). Kinds by theme (CT_KIND: West, Blue,
# Hawara a peristyle; Shali, Kerma a vine pergola; Napata, Meroe, Garama, the Well Corridors, Aksum a pylon court with its far side; Nun a light
# well; Meroe one court in three a light well; Osiris one of peristyle or pergola a floor). Pools: every one-storey spiked pit inside a court
# (not a deeper drop, not on the route's own way) is a pool, its stakes hidden (L._ctP), and every pool is one. Suppressed: no window, open
# arch or breach of the wall inside a court sends a beam (ryOps) or opens its own view (openingsIn: only the court's own bays), every lamp
# inside one stands or hangs free (lampFree), no hanging is left on it, no arch is drawn there (isArchTop). Gusts: from floor 13 a gust whose
# source lies in a court comes in through it (counted). Then (unless nodrown) for the first pool of each floor band he walks off its coping
# with the arrow held: he must die drowned (P.cause 'drown') with his feet at the water's surface. Prints a table by floor band and
# 'courtscan: ok'. Run from dev/tools.
import os, sys
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
SRC = os.path.abspath(next((x for x in a if x.endswith('.html')), os.path.join(HERE, '..', 'hourglass-keep.html')))
NUM = [int(x) for x in a if x.isdigit()]
LO, HI = (NUM[0], NUM[1]) if len(NUM) >= 2 else (1, 48)
SEEDS = [int(s) for s in next((x for x in a if ',' in x), '1,2,3').split(',')]
DROWN = 'nodrown' not in a

JS = r'''([n,sd])=>{const H=__HK,L=H.load(n,sd,true),C=L.cols,TW=32,B=(c,r)=>c<0||c>=C||r<0||r>=L.rows?2:L.base[r*C+c],F=(c,r)=>c<0||c>=C||r<0||r>=L.rows?null:L.feat[r*C+c],bad=[];
  const cs=L.courts||[],lk=L.theme.look,KIND={west:'peri',blue:'peri',hawara:'peri',shali:'perg',deffufa:'perg',napata:'fore',meroe:'fore',foggara:'fore',wells:'fore',aksum:'fore',nun:'well'};
  const NOF=new Set(['shaftfoot','banner','lift','chain','hurtdrop']),seg=(c,r)=>L.segs.some(q=>c>=Math.min(q.c0,q.c1)&&c<=Math.max(q.c0,q.c1)&&r>=Math.min(q.r0,q.r1)&&r<=Math.max(q.r0,q.r1));
  const pitOk=(c,r)=>{const s=F(c,r+1);return B(c,r)===0&&B(c,r+1)===1&&s&&s.t==='spikes'&&B(c,r+2)!==0&&!seg(c,r+1);};
  if(n<3&&cs.length)bad.push('courts on floor '+n);
  const sdc=L.start.door===undefined?Math.floor(L.start.x/TW):L.start.door;let pools=0,cells=0;const kinds={};
  for(const k of cs){const tag=k.k+'@'+k.c0+'-'+k.c1+','+k.r,len=k.c1-k.c0+1;kinds[k.k]=(kinds[k.k]||0)+1;cells+=len;
    if(k.k==='well'?len!==2:len<4||len>8)bad.push(tag+' length '+len);
    if(lk==='osiris'){if(k.k!=='peri'&&k.k!=='perg')bad.push(tag+' kind in osiris');}else if(lk==='meroe'){if(k.k!=='fore'&&k.k!=='well')bad.push(tag+' kind in meroe');}else if(KIND[lk]!==k.k)bad.push(tag+' kind for '+lk);
    if(B(k.c0,k.r)!==1||B(k.c1,k.r)!==1)bad.push(tag+' an end not floor');
    for(let c=k.c0;c<=k.c1;c++){const r=k.r;
      if(B(c,r-1)!==0||B(c,r-2)!==2||F(c,r-1)||F(c,r-2))bad.push(tag+' no headroom under stone at '+c);
      const f=F(c,r);if(f&&NOF.has(f.t))bad.push(tag+' over '+f.t+' at '+c);
      if(B(c,r)!==1&&!pitOk(c,r))bad.push(tag+' not floor or a pool at '+c);
      if(r===L.door.r&&Math.abs(c-L.door.c)<=3||r===L.start.r&&Math.abs(c-sdc)<=3)bad.push(tag+' by a door at '+c);
      for(const lf of L.lifts){const ca=lf.ca??lf.c0??lf.sc,cb=lf.cb??lf.c1??lf.sc,r0=Math.min(lf.rT??lf.rB,lf.rB)-1,r1=(lf.rD??lf.rB)+1;if(c>=ca-2&&c<=cb+2&&(r>=r0&&r<=r1||r-1>=r0&&r-1<=r1)){bad.push(tag+' by a lift at '+c);break;}}
      if(k.k!=='well'){if(pitOk(c,r)){if(!L._ctP.has(r*C+c)||!L._ctP.has((r+1)*C+c))bad.push(tag+' a pit not a pool at '+c);}else if(L._ctP.has(r*C+c))bad.push(tag+' a pool that is no pit at '+c);
        if(H.isArchTop(c,r-1))bad.push(tag+' an arch at '+c);}}
    pools+=k.pits.length;
    if(k.k!=='well'){const x0=k.c0*TW,x1=(k.c1+1)*TW,y0=(k.r-1)*64,y1=(k.r+1)*64-4;
      for(const o of H.ryOps())if(o.x1>x0+2&&o.x0<x1-2&&o.y1>y0+2&&o.y0<y1-2)bad.push(tag+' a '+o.kind+' beam inside it');
      for(const o of H.openingsIn(x0,x1,y0,y1)){const inside=o[0]>=x0-1&&o[0]+o[2]<=x1+1&&o[1]>=y0-1&&o[1]+o[3]<=y1;if(inside&&!(o[1]===y0&&o[2]<=2*TW&&(o[0]-x0)%TW===0))bad.push(tag+' an opening of its own inside it at '+Math.round(o[0]));}
      for(const t of L.torches)if(t.r===k.r&&t.c>=k.c0&&t.c<=k.c1&&!H.lampFree(t))bad.push(tag+' a lamp on the gone wall at '+t.c);
      for(const h of L.hangings||[])if(h.c>=k.c0-1&&h.c<=k.c1+1&&h.r>=k.r-1&&h.r<=k.r)bad.push(tag+' a hanging at '+h.c);}}
  for(const [i,k] of cs.entries())for(const o of cs.slice(i+1))if(Math.abs(o.r-k.r)<=3&&k.c0<=o.c1+14&&o.c0<=k.c1+14)bad.push('two in view: '+k.c0+','+k.r+' and '+o.c0+','+o.r);
  let pits=0;for(const p of new Set(L._ctP.values()))pits++;if(pits!==pools)bad.push('pool map '+pits+' for '+pools+' pools');
  const gc=(L.winds||[]).filter(z=>z.k==='g'&&z.src&&cs.some(k=>k.k!=='well'&&Math.floor(z.src.x/TW)>=k.c0&&Math.floor(z.src.x/TW)<=k.c1&&Math.floor(z.src.y/64)===k.r-1)).length;
  const first=cs.find(k=>k.pits.length);
  return {n,sd,lk,cnt:cs.length,kinds,cells,pools,gc,g:(L.winds||[]).filter(z=>z.k==='g').length,bad,pool:first?[first.r,first.pits[0][0],first.pits[0][1]]:null};}'''
# he walks off the coping into the pool
DROWNJS = r'''([n,sd,r,a,b])=>{const H=__HK;for(const id in H.HINTS){H.S.hints[id]=1;H.S.learned[id]=1;}const L=H.load(n,sd,true);H.banner=null;const P=H.P;for(const e of H.G)e.x=-9999;for(const s of H.SN)s.x=-9999;
  P.x=(a-1)*32+6;P.y=(r+1)*64-4;P.fallY=P.y;P.vx=0;P.face=1;P.state='stand';H.mode='play';for(const k of ['l','r','u','d','j','g'])H.setKey('kb',k,false);H.tick(10);
  H.setKey('kb','r',true);let i=0,y=null;while(i++<300&&H.mode!=='dead'){H.tick(1);}y=P.y;H.setKey('kb','r',false);
  return {mode:H.mode,cause:P.cause,y,wy:(r+1)*64-4+11};}'''

if __name__ == '__main__':
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto('file://' + SRC); pg.wait_for_timeout(600)
        rows = [pg.evaluate(JS, [n, sd]) for n in range(LO, HI + 1) for sd in SEEDS]
        bad = [(r['n'], r['sd'], x) for r in rows for x in r['bad']]
        few = [(r['n'], r['sd'], r['cnt']) for r in rows if r['n'] >= 3 and r['cnt'] < 7]
        drowns = []
        if DROWN:
            done = set()
            for r in rows:
                band = (r['n'] - 1) // 12
                if r['pool'] and band not in done:
                    done.add(band); q = pg.evaluate(DROWNJS, [r['n'], r['sd']] + r['pool'])
                    ok = q['mode'] == 'dead' and q['cause'] == 'drown' and abs(q['y'] - q['wy']) < 0.5
                    drowns.append((r['n'], r['sd'], ok, q))
        print('floors     courts/floor  min  max  cells/floor  pools  peri perg fore well  gusts (in a court)')
        for lo in range(LO, HI + 1, 12):
            rr = [r for r in rows if lo <= r['n'] < lo + 12]
            if not rr: continue
            k = lambda t: sum(r['kinds'].get(t, 0) for r in rr)
            print('%2d-%-2d      %5.2f        %3d  %3d  %6.1f       %4d   %4d %4d %4d %4d  %3d (%d)' % (lo, min(lo + 11, HI), sum(r['cnt'] for r in rr) / len(rr), min(r['cnt'] for r in rr), max(r['cnt'] for r in rr),
                  sum(r['cells'] for r in rr) / len(rr), sum(r['pools'] for r in rr), k('peri'), k('perg'), k('fore'), k('well'), sum(r['g'] for r in rr), sum(r['gc'] for r in rr)))
        for d in drowns: print('drown floor %d seed %d: %s %s' % d)
        for x in bad[:30]: print('BAD floor %d seed %d: %s' % x)
        for x in few[:10]: print('FEW floor %d seed %d: %d courts' % x)
        ok = not bad and not few and not errs and all(d[2] for d in drowns)
        if errs: print('page errors:', errs[:3])
        print('courtscan: ' + ('ok' if ok else 'FAIL (%d bad, %d floors with fewer than 7)' % (len(bad), len(few))))
        b.close(); sys.exit(0 if ok else 1)
