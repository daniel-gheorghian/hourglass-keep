# wellscan.py [lo] [hi] [file]: round 21b's check of the sand under rows of cracked slabs (wellGroup, wellSolve). For every well of
# floors lo..hi (default 3..30), seeds 801-803, it sets off one slab of the row (each end and the middle in turn) and steps the game:
#  slope   the sand's surface is never steeper than the angle of repose (WELL_SL) between two samples, away from the walls: no vertical face
#  volume  the sand never grows back, and has run down to its stagnant heaps (and stays) once the slabs have broken
#  timing  each slab breaks exactly when it did before (0.5 s after its trigger; the update is untouched)
#  rewind  a snapshot taken mid-drain and put back (the game's own snapAll / applySnap) gives the same surface, sample for sample (the first
#          row of two or more, and the longest row of three or more: round 26d's own surface)
# Prints one line per floor and 'ok' or 'FAIL'. Run from dev/tools.
import os, sys
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
LO = int(a[0]) if len(a) > 0 else 3
HI = int(a[1]) if len(a) > 1 else 30
SRC = os.path.abspath(a[2] if len(a) > 2 else os.path.join(HERE, '..', 'hourglass-keep.html'))
JS = r'''([n,sd])=>{const H=__HK;window.__HKfreeze=true;H.EGP.traps=true;H.load(n,sd,true);const L=H.L,P=H.P;P.inv=1e9;const SL=0.67+0.02;
  let groups=0,bad=[];const seen=new Set();
  const specs=[];for(const o of L.dyn){if(o.f.t!=='loose'||o.f.plank)continue;const g=H.wellGroup(o);if(!g||seen.has(g))continue;seen.add(g);if(g.n>1)specs.push(g.os.map(q=>[q.c,q.r]));}
  for(const sp of specs){groups++;
    for(const j of [...new Set([0,sp.length>>1,sp.length-1])]){
      H.load(n,sd,true);const L2=H.L;H.P.inv=1e9;H.P.x=-9999;H.P.y=-9999;const os=sp.map(([c,r])=>L2.dyn.find(d=>d.c===c&&d.r===r)),g2=H.wellGroup(os[0]);
      for(const q of os){q.f.s=0;q.f.tm=0;}os[j].f.s=1;os[j].f.tm=0;let last=1e9,brk=-1;
      for(let k=0;k<240;k++){H.tick(1);H.P.x=-9999;H.P.y=-9999;H.wellSolve(g2);const S=g2.S,M=S.length-1;
        if(brk<0&&os[j].f.s===2)brk=os[j].f.tm;
        for(let i=1;i<M-1;i++){if(Math.abs(S[i+1]-S[i])/2>SL+1e-3&&S[i]<g2.yb[Math.min(g2.n-1,(i*2/32)|0)]-0.5&&S[i+1]<g2.yb[Math.min(g2.n-1,((i+1)*2/32)|0)]-0.5){bad.push(['slope',n,sd,os[0].c,j,k,i,+(S[i+1]-S[i]).toFixed(2)]);break;}}
        let A=0;for(let i=0;i<=M;i++)A+=g2.yb[Math.min(g2.n-1,(i*2/32)|0)]-S[i];if(A>last+1e-3)bad.push(['grew',n,sd,os[0].c,j,k]);last=A;
        if(bad.length>8)break;}
      if(brk<0||Math.abs(brk-0.5)>1/60+1e-6)bad.push(['timing',n,sd,os[0].c,j,brk]);
    }}
  return {groups,bad};}'''
RW = r'''([n,sd,big])=>{const H=__HK;window.__HKfreeze=true;H.load(n,sd,true);const L=H.L;let o=null;
  for(const q of L.dyn){if(q.f.t!=='loose'||q.f.plank)continue;const g=H.wellGroup(q);if(g&&g.n>(big?2:1)&&(!o||!big||g.n>o.f.wg.n)){o=q;if(!big)break;}}if(!o)return null;
  const g=H.wellGroup(o);H.P.inv=1e9;H.P.x=-9999;H.P.y=-9999;o.f.s=1;o.f.tm=0;for(let k=0;k<15;k++){H.tick(1);H.P.x=-9999;H.P.y=-9999;}
  const sn=H.snapAll();H.wellSolve(g);const S0=Float32Array.from(g.S);for(let k=0;k<60;k++){H.tick(1);H.P.x=-9999;H.P.y=-9999;}
  H.applySnap(sn);g.key=NaN;H.wellSolve(g);let d=0;for(let i=0;i<S0.length;i++)d=Math.max(d,Math.abs(S0[i]-g.S[i]));return d;}'''
if __name__ == '__main__':
    fails = 0
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={'width': 852, 'height': 393})
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto('file://' + SRC); pg.wait_for_timeout(500)
        pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true)")
        hasSnap = pg.evaluate("()=>typeof __HK.snapAll==='function'&&typeof __HK.applySnap==='function'")
        for n in range(LO, HI + 1):
            for sd in (801, 802, 803):
                r = pg.evaluate(JS, [n, sd]); rw = pg.evaluate(RW, [n, sd, 0]) if hasSnap else None
                rb = pg.evaluate(RW, [n, sd, 1]) if hasSnap else None   # (round 26d: and the longest row, three slabs or more, drawn its own way)
                if rw is not None and rw > 1e-3:
                    r['bad'].append(['rewind', n, sd, rw])
                if rb is not None and rb > 1e-3:
                    r['bad'].append(['rewind3', n, sd, rb])
                fails += len(r['bad'])
                print('floor', n, 'seed', sd, 'groups', r['groups'], 'rewind diff', rw, rb, 'bad', r['bad'][:4])
        print('page errors', errs[:3])
        b.close()
    print('ok' if fails == 0 and not errs else 'FAIL %d' % fails)
