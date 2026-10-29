# hilljump.py [file.html] [lo hi] [seeds] [step=N]: round 47a's play rule for the heaps and drifts (owner: "you shouldn't be able to jump over
# them, only way is to walk at the pace they let you"). For every hill on floors lo..hi (default 3-48) and seed (default 1,2), with the game's
# own physics (H.tick at 60 Hz, guards and snakes out of the way):
#   run    a running jump pressed every step px (default 4) from 2 to 122 px before its foot, on the plain floor before it (the arrow held);
#   stand  a standing jump pressed from 2 to 50 px before it;
#   on     Jump pressed every 8 px along it while clambering or wading;
#   crawl  crouched 6 px before it, Down and the arrow held for 3 s.
# Rules (the low leap, under a ceiling at his height, is left out: owner): no flight lands at or past a hill's foot; no flight leaves the floor
# while his feet are on a hill; the crossing (its near edge to its far edge) is never faster than walking it at its pace by more than 0.1 s;
# a crawl never enters a hill. v88 fails every hill; round 47a prints 'hilljump: ok'. Run from dev/tools.
import os, sys, json
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
SRC = os.path.abspath(next((x for x in a if x.endswith('.html')), os.path.join(HERE, '..', 'hourglass-keep.html')))
NUM = [int(x) for x in a if x.isdigit()]
LO, HI = (NUM[0], NUM[1]) if len(NUM) >= 2 else (3, 48)
SEEDS = [int(s) for s in next((x for x in a if ',' in x), '1,2').split(',')] if any(',' in x for x in a) else ([NUM[2]] if len(NUM) >= 3 else [1, 2])
STEPPX = int(next((x[5:] for x in a if x.startswith('step=')), 4))
JS = r'''([n,sd,stp])=>{const H=__HK,TW=32,STEP=1/60,keys=['l','r','u','d','j','g'];let L=H.load(n,sd,true);const hs=(L.hills||[]).map(h=>({...h})),out=[];
 const prep=(x0,r,dir,st,vx)=>{L=H.load(n,sd,true);H.banner=null;const P=H.P;P.inv=1e9;for(const e of H.G)e.x=-9999;for(const s of H.SN||[])s.alive=false;
   P.x=x0;P.y=(r+1)*64-4;P.fallY=P.y;P.vx=vx||0;P.face=dir;P.state=st;P.stumble=0;P.pendingJump=false;P.jumpKind=null;H.mode='play';for(const k of keys)H.setKey('kb',k,false);return P;};
 const okFloor=(c,r)=>{const C=H.L.cols;return H.L.base[r*C+c]===1&&!H.L.feat[r*C+c]&&H.L.base[(r+1)*C+c]!==0;};
 // one try: start at x0 in state st, keys held, Jump pressed when pressAt(P) first holds; until P.x passes tgt along dir, or 12 s
 const trial=(h,x0,st,vx,hold,pressAt,tgt)=>{const dir=h.dir,P=prep(x0,h.r,dir,st,vx);for(const k of hold)H.setKey('kb',k,true);
   let t=0,pressed=false,lastAir=false,tA=null,tB=null;const fl=[];let inHill=false,cur=null;
   for(let i=0;i<720;i++){if(!pressed&&pressAt(P)){H.setKey('kb','j',true);pressed=true;}else if(pressed)H.setKey('kb','j',false);
     const onH=!!H.hillOn(P.x,P.y);H.tick(1);t+=STEP;const air=P.state==='air';
     if(air&&!lastAir){cur={jx:P.jx,low:!!P.lowJump,kind:P.jumpKind,fromHill:onH};fl.push(cur);}
     if(lastAir&&!air&&cur){cur.lx=P.x;cur=null;}
     lastAir=air;if(tA===null&&(P.x-h._xa)*dir>=0)tA=t;if(tB===null&&(P.x-h._xb)*dir>=0)tB=t;
     if(P.state==='crouch'&&H.hillOn(P.x,P.y))inHill=true;
     if(P.state==='dead'||H.mode!=='play')break;if((P.x-tgt)*dir>=0)break;}
   for(const k of keys)H.setKey('kb',k,false);return {fl,cross:(tA!=null&&tB!=null)?tB-tA:null,dead:P.state==='dead',inHill,x:P.x};};
 const ar=d=>d>0?'r':'l';
 for(let hi=0;hi<hs.length;hi++){const h=hs[hi],dir=h.dir,xa=dir>0?h.c*TW:(h.c+h.n)*TW,xb=dir>0?(h.c+h.n)*TW:h.c*TW,tgt=xb+dir*48;h._xa=xa;h._xb=xb;
   let back=0;{let c=dir>0?h.c-1:h.c+h.n;while(back<5&&okFloor(c,h.r)){back++;c-=dir;}}
   const rec={n,sd,v:h.v,d:h.d,c:h.c,r:h.r,len:h.n*TW,dir,bad:[],tries:0,low:0,checked:0};
   const look=(tag,base,j)=>{rec.tries++;for(const f of j.fl){if(f.low){rec.low++;continue;}
       if(f.fromHill)rec.bad.push(tag+' took off on the hill');
       if(f.lx!=null&&(f.lx-xa)*dir>=0)rec.bad.push(tag+' landed '+((f.lx-xa)*dir).toFixed(1)+' px past the foot');}
     if(j.fl.some(f=>f.low))return;if(j.dead)rec.bad.push(tag+' died');
     if(base!=null&&j.cross!=null&&j.cross<base-0.1)rec.bad.push(tag+' crossed in '+j.cross.toFixed(2)+' s, the pace '+base.toFixed(2));};
   const maxd=back*TW;let base=null;
   if(maxd>=8){const b=trial(h,xa-dir*6,'run',dir*100,[ar(dir)],()=>false,tgt);base=b.cross;rec.pace=base;}
   for(let d=2;d<=Math.min(122,maxd-2);d+=stp){const x0=xa-dir*d;look('run '+d,base,trial(h,x0,'run',dir*100,[ar(dir)],P=>true,tgt));}
   for(let d=2;d<=Math.min(50,maxd-2);d+=stp){const x0=xa-dir*d;look('stand '+d,base,trial(h,x0,'stand',0,[ar(dir)],P=>true,tgt));}
   if(maxd>=8){for(let u=0;u<h.n*TW;u+=8)look('on '+u,base,trial(h,xa-dir*6,'run',dir*100,[ar(dir)],P=>(P.x-(xa+dir*u))*dir>=0,tgt));
     const cr=trial(h,xa-dir*6,'crouch',0,['d',ar(dir)],()=>false,tgt);rec.tries++;if(cr.inHill)rec.bad.push('crawled into it');}
   rec.back=back;out.push(rec);}
 return out;}'''

if __name__ == '__main__':
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto('file://' + SRC); pg.wait_for_timeout(800)
        rows = []
        for n in range(LO, HI + 1):
            for sd in SEEDS: rows += pg.evaluate(JS, [n, sd, STEPPX])
        b.close()
    bad = [r for r in rows if r['bad']]
    heaps = [r for r in rows if not r['d']]; drifts = [r for r in rows if r['d']]
    print('floors %d-%d seeds %s: %d hills (%d heaps, %d drifts), %d tries, %d low leaps left out' % (LO, HI, SEEDS, len(rows), len(heaps), len(drifts), sum(r['tries'] for r in rows), sum(r['low'] for r in rows)))
    for k, rs in (('heaps', heaps), ('drifts', drifts)):
        print('  %s: %d of %d break the rule' % (k, sum(1 for r in rs if r['bad']), len(rs)))
    for r in bad[:15]: print('BAD floor %d seed %d %s c%d r%d: %s' % (r['n'], r['sd'], r['v'], r['c'], r['r'], '; '.join(r['bad'][:3])))
    if errs: print('errors', errs[:5])
    print('hilljump: ok' if not bad and not errs else 'hilljump: FAIL (%d of %d hills)' % (len(bad), len(rows)))
    sys.exit(0 if not bad and not errs else 1)
