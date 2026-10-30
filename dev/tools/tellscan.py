# tellscan.py [file] [lo hi] [per=K]: round 49b's tells (look only), played through the game (__HK.load, setKey, tick).
# On floors lo..hi (default 3-16, seed 4400+n), up to K spots of each kind a floor (tellKind: reach, edge, stakes, flask, low; default 2)
# where he stands still facing it (not in a wind zone, nor within 16 px of one: the game gives no tell in a wind, tellIdle, as a gust's
# lull may end at any moment; round 49d), checks:
#   wait    none before TL_D (0.45 s still: TELL.w 0)
#   on      at 1.2 s still the tell is that kind at full weight, and the drawn pose differs from TELL.off's (head or hand by over 0.08)
#   input   Grab held (it moves nothing standing): the weight drops to 0 in that frame, and 0.35 s later the pose is TELL.off's (head within 0.04)
#   play    P.x, P.y, P.state after it all identical with the tells off (look only)
# and on every 'stand' spot of a floor's plain cells: no tell while Right is held (he runs), none in the fight (a guard near). Prints one
# line per floor, then 'tellscan: ok' or 'tellscan: FAIL n'. Run from dev/tools.
import os, sys
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
SRC = os.path.abspath(next((x for x in a if x.endswith('.html')), os.path.join(HERE, '..', 'hourglass-keep.html')))
NUM = [int(x) for x in a if x.isdigit()]
LO, HI = (NUM[0], NUM[1]) if len(NUM) >= 2 else (3, 16)
PER = int(next((x[4:] for x in a if x.startswith('per=')), 2))
JS = r'''([n,per])=>{const H=__HK,TW=32,S=r=>(r+1)*64-4,sd=4400+n,bad=[],cnt={};
 const keys=o=>{for(const k of ['l','r','u','d','j','g'])H.setKey('kb',k,!!(o&&o[k]));};
 let L=H.load(n,sd,false);const spots=[];
 for(let r=1;r<L.rows-1;r++)for(let c=2;c<L.cols-2;c++){if(H.B(c,r)===H.WALL||!H.solidBelow(c,r)||H.F(c,r))continue;
   for(const fc of [1,-1]){const P=H.P;P.x=c*TW+16+fc*8;P.y=S(r);P.face=fc;if(H.windZoneAt(P.x,P.y,16)>=0)continue;const k=H.tellKind();if(k&&(cnt[k]||0)<per){cnt[k]=(cnt[k]||0)+1;spots.push([k,c,r,fc]);}}}
 const place=(c,r,fc,off)=>{L=H.load(n,sd,false);H.banner=null;H.mode='play';H.intro=0;H.TELL.off=off;keys();for(const e of H.G)e.x=-9999;for(const e of H.SN)e.x=-9999;
   const P=H.P;P.x=c*TW+16+fc*8;P.y=S(r);P.fallY=P.y;P.face=fc;P.state='stand';P.vx=P.vy=0;P.inv=1e9;P.t=0;return P;};
 const hand=P=>{const s=H.skel(P.pose);return [s.hF[0],s.hF[1]];};
 for(const [k,c,r,fc] of spots){const run=off=>{const P=place(c,r,fc,off),o={};H.tick(27);o.w0=H.TELL.w;H.tick(45);o.k=H.TELL.k;o.w=H.TELL.w;o.head=P.pose.head;o.hand=hand(P);
     keys({g:1});H.tick(1);o.wi=H.TELL.w;H.tick(21);o.head2=P.pose.head;keys();o.x=P.x;o.y=P.y;o.st=P.state;return o;};
   const on=run(false),of=run(true);H.TELL.off=false;const id=k+' c'+c+' r'+r+' f'+fc;
   if(on.w0>0)bad.push(id+': tell before TL_D ('+on.w0.toFixed(2)+')');
   if(on.k!==k||on.w<0.999)bad.push(id+': at 1.2 s '+on.k+' w'+on.w.toFixed(2));
   if(Math.abs(on.head-of.head)<0.08&&Math.hypot(on.hand[0]-of.hand[0],on.hand[1]-of.hand[1])<0.08)bad.push(id+': pose unchanged');
   if(on.wi!==0)bad.push(id+': Grab held, weight '+on.wi);
   if(Math.abs(on.head2-of.head2)>0.04)bad.push(id+': 0.35 s after input head off by '+(on.head2-of.head2).toFixed(3));
   if(on.x!==of.x||on.y!==of.y||on.st!==of.st)bad.push(id+': play differs '+[on.x,on.y,on.st,of.x,of.y,of.st].join(' '));}
 // running: Right held from a still stand, never a tell
 if(spots.length){const [k,c,r,fc]=spots[0];const P=place(c,r,fc,false);H.tick(60);keys({[fc>0?'l':'r']:1});let mx=0;for(let i=0;i<40;i++){H.tick(1);if(P.state!=='stand'&&P.state!=='turn')mx=Math.max(mx,H.TELL.w);}keys();if(mx>0)bad.push('moving: weight '+mx);}
 return {n,spots:spots.length,kinds:cnt,bad};}'''
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://' + SRC); pg.wait_for_timeout(500)
    pg.evaluate("()=>{window.__HKfreeze=true;window.__HKnoauto=true;const H=__HK;for(const id in H.HINTS){H.S.hints[id]=1;if(H.S.learned)H.S.learned[id]=1;}H.S.set.cross=false;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);}")
    fails = 0; tot = {}
    for n in range(LO, HI + 1):
        q = pg.evaluate(JS, [n, PER]); fails += len(q['bad'])
        for k, v in q['kinds'].items(): tot[k] = tot.get(k, 0) + v
        print('floor %d: %d spots %s%s' % (n, q['spots'], q['kinds'], ('  FAIL ' + '; '.join(q['bad'][:4])) if q['bad'] else ''), flush=True)
    if errs: fails += 1; print('errors', errs[:3])
    print('spots by kind', tot)
    print('tellscan: ok' if not fails else 'tellscan: FAIL %d' % fails)
    b.close()
