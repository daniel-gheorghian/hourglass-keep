# windscan.py [file.html] [lo hi] [seeds] [nopush] [noease]: the wind (round 44, placed by openings since round 45c: placeWinds, L.winds). For every
# floor lo..hi (default 1-48) and seed (default 1,2,3): how many zones of each kind (s steady, g gusts, d a drift's wind), by source (a window, a breach,
# a court's open side), the floors with none, and how many generated jumps lie in them; and the rules:
#  - every zone cell has headroom and is plain floor (FLOOR, no feature) or a one-storey gap he jumps (EMPTY over a floor); every seg there is calm
#    (flat, puzzle, rem-plate, detour, secret, block, double, skel) or a gap jump (gap1-3, spikes, bridge), and no other seg within a cell of it on its
#    row (no swing, saw, chamber, kick shaft, lift, timed trap); off timed stretches, the dark's chase, fighters' ground, the doors and the lifts;
#  - it blows against the run there (the seg's way); 3-8 cells (a drift's: its drift and approach);
#  - gusts only from floor WIND_G0 (7), their peak by band (1.15 to 12, 1.25 to 24, 1.375 on), a lull of at least 1.8 s, the warning 0.6 s, a gust
#    0.9-1.8 s; a steady zone's strength 1, 0.75 or 0.5 and every jump it lies over made at it (windReach against the gap, windJumpE);
#  - the push: he stands in each gust zone (its ends and middle) with no key for 9 s: he stays in it, on his feet, alive;
#  - the ease: in one gust zone a floor band, a death there eases it to 0.6 of its strength, a rewind keeps that, a second death 0.3.
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
EASE = 'noease' not in a

JS = r'''([n,sd])=>{const H=__HK,L=H.genLevel(n,sd,true),C=L.cols,TW=32,ws=L.winds||[],bad=[],B=(c,r)=>c<0||c>=C||r<0||r>=L.rows?2:L.base[r*C+c],F=(c,r)=>L.feat[r*C+c];
  const CALM=new Set(['flat','puzzle','rem-plate','detour','secret','block','double','skel']),JMP=new Set(['gap1','gap2','gap3','spikes','bridge']),JA=new Set(['rjump','rjumpg','dashjump','sjump']);
  const segAt=(c,r)=>{const o=[];L.segs.forEach((q,i)=>{if(c>=Math.min(q.c0,q.c1)&&c<=Math.max(q.c0,q.c1)&&r>=Math.min(q.r0,q.r1)&&r<=Math.max(q.r0,q.r1))o.push(i);});return o;};
  const timed=new Set();for(const o of L.dyn){const f=o.f;if(f.t!=='plate'||!f.g||f.g.latch||!(f.g.dur>0))continue;const go=L.dyn.find(q=>q.f===f.g);if(!go)continue;const all=segAt(o.c,o.r).concat(segAt(go.c,go.r));if(!all.length)continue;
    for(let i=Math.min(...all);i<=Math.max(...all);i++){const q=L.segs[i];for(let r=Math.min(q.r0,q.r1);r<=Math.max(q.r0,q.r1);r++)for(let c=Math.min(q.c0,q.c1);c<=Math.max(q.c0,q.c1);c++)timed.add(r*C+c);}}
  const ch=L.ext.chase,peak=n<13?1.15:n<25?1.25:1.375;let jumps={s:0,g:0};
  for(const z of ws){const tag=z.k+'@'+z.c+','+z.r;
    if(z.k!=='d'&&(z.n<3||z.n>8))bad.push(tag+' length '+z.n);
    if(z.k==='g'){if(n<H.WIND_G0)bad.push(tag+' gust before floor '+H.WIND_G0);if(Math.abs(z.gp-peak)>1e-6)bad.push(tag+' peak '+z.gp);if(!(z.gl>=1.8))bad.push(tag+' lull '+z.gl);if(!(z.gg>=0.9&&z.gg<=1.8))bad.push(tag+' gust '+z.gg);
      if(Math.abs(z.T-(z.gl+0.6+z.gg+0.4))>1e-6)bad.push(tag+' cycle');if(!z.src)bad.push(tag+' gust with no source');}
    if(z.k==='s'&&![1,0.75,0.5].includes(z.e||1))bad.push(tag+' strength '+z.e);
    if(z.k==='d'){const h=(L.hills||[]).find(h=>h.d&&h.r===z.r&&h.c>=z.c&&h.c+h.n<=z.c+z.n);if(!h)bad.push(tag+' drift wind with no drift');continue;}
    for(let c=z.c;c<z.c+z.n;c++){const r=z.r,k=r*C+c,b=B(c,r);
      if(!(b===1&&!F(c,r)||b===0&&B(c,r+1)===1))bad.push(tag+' not plain floor or a gap at '+c);
      if(B(c,r-1)===2)bad.push(tag+' a wall over it at '+c);
      if(timed.has(k))bad.push(tag+' on a timed stretch at '+c);
      if(ch&&r>=ch.rTop&&r<=ch.rBot&&c>=ch.c0-4&&c<=ch.c1+4)bad.push(tag+' in the chase');
      if(L.guards.some(g=>g.r===r&&c>=Math.floor(g.lo/TW)-2&&c<=Math.floor(g.hi/TW)+2)||L.snakeSpecs.some(s=>s.r===r&&c>=Math.floor(s.lo/TW)-2&&c<=Math.floor(s.hi/TW)+2))bad.push(tag+' on a fighter\'s ground at '+c);
      if(L.door.r===r&&Math.abs(L.door.c-c)<=2)bad.push(tag+' by the door');
      for(const q of L.segs){if(r<Math.min(q.r0,q.r1)||r>Math.max(q.r0,q.r1))continue;const a=Math.min(q.c0,q.c1),b2=Math.max(q.c0,q.c1);if(CALM.has(q.k)||JMP.has(q.k)){if(c>=a&&c<=b2&&q.r0===q.r1&&(q.dir||(q.c1>=q.c0?1:-1))!==-z.dir)bad.push(tag+' blows with the run at '+c);continue;}
        if(c>=a-1&&c<=b2+1){bad.push(tag+' within a cell of seg '+q.k+' at '+c);break;}}}
    for(const act of L.path){if(!JA.has(act.a))continue;const lo=Math.min(act.from,act.to),hi=Math.max(act.from,act.to);if(hi<z.c||lo>z.c+z.n-1)continue;
      if(!L.segs.some(sg=>sg.r0===z.r&&sg.r1===z.r&&JMP.has(sg.k)&&Math.min(sg.c0,sg.c1)<=hi&&Math.max(sg.c0,sg.c1)>=lo))continue;
      jumps[z.k]++;if(z.k==='s'){const need=(hi-lo-1)*TW+10;if(H.windJumpE(act)<(z.e||1))bad.push(tag+' '+act.a+' '+act.from+'>'+act.to+' not made at '+(z.e||1));}}}
  const gz=ws.filter(z=>z.k==='g').map(z=>[z.c,z.r,z.n,z.dir,z.i]);
  return {n,sd,lk:L.theme.look,w:ws.map(z=>({k:z.k,o:z.o||'drift',e:z.e||1})),bad,gz,jumps};}'''
PUSHJS = r'''([n,sd,c,r,nn,dir,u])=>{const H=__HK;const L=H.load(n,sd,true);H.banner=null;const P=H.P;P.inv=1e9;for(const e of H.G)e.x=-9999;
  const a=c*32,b=(c+nn)*32;P.x=a+u*(b-a);P.y=(r+1)*64-4;P.fallY=P.y;P.vx=0;P.face=-dir;P.state='stand';H.mode='play';
  if(H.L.base[r*H.L.cols+Math.floor(P.x/32)]!==1)return {ok:true,skip:1};
  for(const k of ['l','r','u','d','j','g'])H.setKey('kb',k,false);let lo=P.x,hi=P.x;const x0=P.x;
  for(let i=0;i<540;i++){H.tick(1);lo=Math.min(lo,P.x);hi=Math.max(hi,P.x);if(P.state!=='stand'||H.mode!=='play')return {ok:false,why:'state '+P.state+' '+H.mode,x:P.x};}
  return {ok:lo>=a-0.5&&hi<=b+0.5,lo,hi,a,b,moved:Math.abs(P.x-x0)};}'''
# a death in the zone eases it; a rewind keeps the ease; a second death eases it more
EASEJS = r'''([n,sd,c,r,nn,i])=>{const H=__HK;for(const id in H.HINTS){H.S.hints[id]=1;H.S.learned[id]=1;}H.S.windDeaths={};const L=H.load(n,sd,true);H.banner=null;const P=H.P;for(const e of H.G)e.x=-9999;
  let fl=-1;for(let cc=c;cc<c+nn;cc++)if(L.base[r*L.cols+cc]===1){fl=cc;break;}if(fl<0)return {skip:1};
  P.x=fl*32+16;P.y=(r+1)*64-4;P.fallY=P.y;P.vx=0;P.state='stand';H.mode='play';for(const k of ['l','r','u','d','j','g'])H.setKey('kb',k,false);
  const z=L.winds[i],e0=H.windEase(z);H.tick(150);H.die('fall');const e1=H.windEase(z);let rw=false;
  if(H.canRewind()){H.startRewind();for(let t=0;t<900&&H.mode!=='play';t++)H.tick(1);rw=H.mode==='play';}
  const e2=H.windEase(z);P.x=fl*32+16;P.y=(r+1)*64-4;H.tick(5);H.die('fall');const e3=H.windEase(z);return {e0,e1,e2,e3,rw,deaths:JSON.stringify(H.S.windDeaths)};}'''

if __name__ == '__main__':
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto('file://' + SRC); pg.wait_for_timeout(600)
        rows = [pg.evaluate(JS, [n, sd]) for n in range(LO, HI + 1) for sd in SEEDS]
        pushes, eases = [], []
        if PUSH:
            for r in rows:
                for (c, rr, nn, d, i) in r['gz']:
                    for u in (0.15, 0.5, 0.85):
                        q = pg.evaluate(PUSHJS, [r['n'], r['sd'], c, rr, nn, d, u])
                        if not q.get('skip'): pushes.append((r['n'], r['sd'], c, q))
        if EASE:
            done = set()
            for r in rows:
                band = (r['n'] - 1) // 12
                if r['gz'] and band not in done:
                    done.add(band); c, rr, nn, d, i = r['gz'][0]; q = pg.evaluate(EASEJS, [r['n'], r['sd'], c, rr, nn, i])
                    if not q.get('skip'): eases.append((r['n'], r['sd'], q))
        bad = [(r['n'], r['sd'], x) for r in rows for x in r['bad']]
        print('floors   steady  gusts  drift | windows breaches courts | weakened (0.75 / 0.5) | floors with none | jumps under steady / gusts')
        for lo in range(LO, HI + 1, 12):
            rr = [r for r in rows if lo <= r['n'] < lo + 12]
            if not rr: continue
            cnt = lambda f: sum(1 for r in rr for w in r['w'] if f(w)) / len(rr)
            none = sum(1 for r in rr if not any(w['k'] != 'd' for w in r['w']))
            print('%2d-%-2d    %5.2f  %5.2f  %5.2f | %5.2f %5.2f %5.2f | %d / %d | %d of %d | %d / %d' % (lo, min(lo + 11, HI), cnt(lambda w: w['k'] == 's'), cnt(lambda w: w['k'] == 'g'), cnt(lambda w: w['k'] == 'd'),
                  cnt(lambda w: w['o'] == 'win'), cnt(lambda w: w['o'] == 'breach'), cnt(lambda w: w['o'] == 'court'),
                  sum(1 for r in rr for w in r['w'] if w['e'] == 0.75), sum(1 for r in rr for w in r['w'] if w['e'] == 0.5), none, len(rr),
                  sum(r['jumps']['s'] for r in rr), sum(r['jumps']['g'] for r in rr)))
        pb = [x for x in pushes if not x[3]['ok']]
        if pushes:
            mv = [x[3].get('moved', 0) for x in pushes if x[3]['ok']]
            print('push: %d stands in gusts, %d left the zone or fell; moved mean %.1f px, max %.1f px' % (len(pushes), len(pb), sum(mv) / max(1, len(mv)), max(mv or [0])))
        eb = []
        for n, sd, q in eases:
            ok = q['e0'] == 1 and abs(q['e1'] - 0.6) < 1e-9 and abs(q['e2'] - 0.6) < 1e-9 and abs(q['e3'] - 0.3) < 1e-9 and q['rw']
            print('ease floor %d seed %d: %s -> %s, after the rewind %s, a second death %s %s' % (n, sd, q['e0'], q['e1'], q['e2'], q['e3'], 'ok' if ok else 'BAD ' + str(q)))
            if not ok: eb.append(q)
        for x in bad[:30]: print('BAD floor %d seed %d: %s' % x)
        for x in pb[:10]: print('PUSH floor %d seed %d zone %d: %s' % (x[0], x[1], x[2], x[3]))
        if errs: print('page errors:', errs[:3])
        ok = not bad and not pb and not eb and not errs
        print('windscan: ' + ('ok' if ok else 'FAIL'))
        b.close(); sys.exit(0 if ok else 1)
