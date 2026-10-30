#!/usr/bin/env python3
# chimtest.py [file] [lo hi] [seeds]: round 48b's locked chimney, played through the game's own input (__HK.load, setKey, tick).
# For every kick shaft (bot action walljump) on floors lo..hi (default 1-48) x seeds 1..seeds (default 3):
#  climb   the way in (a standing Jump at the foot, Up at the foot, or a running Jump at its wall, in turn by shaft), then one press of Up
#          in each stance: every stance on the grid (feet CHM_G0 + CHM_GS n px over the foot's floor, to the pixel), on the ledge's wall
#          and the wall behind in turn, the Y from the top stance, landed with the standing jump's landing ('sl'), standing CHM_YX px past
#          the lip (within 3 px), no life lost
#  held    Up held 2 s in the first stance: exactly one kick
#  jump    Jump pressed three times in the first stance: nothing moves
#  down    Down in each stance: he lets go at once and lands at the foot with a fall's damage (100 px or more one life, 170 or more death)
#  rewind  a snapshot in mid-kick: the climb finished, then the snapshot put back: the lock, plant and drawing session are his own copies
#          (not shared with the snapshot), the flight goes on and the climb finishes again
#  walk    walking into the foot does not lock him
# And per floor, up to 4 walls outside the shafts: in the air against one, Jump and Up neither plant, kick nor lock (no single-wall kick).
# Prints one line per floor, the stance heights with what a let-go costs from each, the climb's times per shaft height and way in, then
# 'chimtest: ok' or 'chimtest: FAIL n'. Run from dev/tools.
import os, sys, json, statistics as st
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
SRC = os.path.abspath(next((x for x in a if x.endswith('.html')), os.path.join(HERE, '..', 'hourglass-keep.html')))
NUM = [int(x) for x in a if x.isdigit()]
LO, HI = (NUM[0], NUM[1]) if len(NUM) >= 2 else (1, 48)
SEEDS = list(range(1, (NUM[2] if len(NUM) > 2 else 3) + 1))

JS = r'''()=>{const H=__HK;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);
window.__C={
 keys(o){for(const k of ['l','r','u','d','j','g'])H.setKey('kb',k,!!(o&&o[k]));},
 shafts(n,s){const L=H.load(n,s,true),o=[];for(const a of L.path){if(a.a!=='walljump')continue;let rf=-1;for(let r=0;r<L.rows;r++){const f=H.F(a.from,r);if(f&&f.t==='shaftfoot')rf=r;}o.push({c:a.from,rf,k:a.k,dir:a.dir||1});}return o;},
 // cells of plain floor behind the foot on its row (up to 2): where a run in starts
 back(sh){let b=0;while(b<2){const c=sh.c-sh.dir*(b+1);const t=H.B(c,sh.rf);if(t===H.WALL||(t===0&&H.B(c,sh.rf+1)!==H.WALL))break;b++;}return b;},
 setup(n,s,sh,back){for(const id in H.HINTS){H.S.hints[id]=1;H.S.learned[id]=1;}H.load(n,s,true);H.banner=null;H.mode='play';this.keys();
   const P=H.P;P.x=(sh.c-sh.dir*back)*32+16;P.y=(sh.rf+1)*64-4;P.fallY=P.y;P.face=sh.dir;P.state='stand';P.vx=0;P.vy=0;P.inv=0;P.jumpKind=null;P.autoGrab=false;P.stumble=0;P.lock=null;P.plant=null;
   H.tick(2);return H.chimFoot(sh.c,sh.rf);},
 press(k){H.setKey('kb',k,true);H.tick(1);H.setKey('kb',k,false);},
 // the way in, then a press of Up at each new stance; stopAt: return in that stance (planted, before its press)
 climb(n,s,sh,entry,stopAt,setup){const y0=(sh.rf+1)*64-4,dk=sh.dir>0?'r':'l';if(setup!==false){this.setup(n,s,sh,0);if(entry==='run')this.setup(n,s,sh,this.back(sh));}
   const ev={st:[],stand:null,sl:false,hp0:H.P.hp,t0:0,err:null,locked:false};let f=0;
   if(entry==='run'){H.setKey('kb',dk,true);for(;f<240;f++){const P=H.P;if(P.state==='run'&&(P.x-(sh.c*32+16-14*sh.dir))*sh.dir>=0)break;H.tick(1);}
     ev.t0=H.gameTime;H.setKey('kb','j',true);H.tick(1);H.setKey('kb','j',false);for(;f<300&&H.P.state!=='air';f++)H.tick(1);H.setKey('kb',dk,false);}
   else if(entry){ev.t0=H.gameTime;this.press(entry);}
   let lastN=H.P.lock?H.P.lock.n:-9;
   for(;f<60*20;f++){const P=H.P;if(P.lock)ev.locked=true;
     if(P.state==='land'&&P.stK==='sl')ev.sl=true;
     if(P.lock&&P.lock.ph==='plant'&&P.plant&&P.plant.y==null&&P.lock.n!==lastN){lastN=P.lock.n;ev.st.push({n:P.lock.n,h:Math.round((y0-P.y)*1000)/1000,sd:P.plant.sd,t:H.gameTime-ev.t0});
       if(stopAt===P.lock.n)return ev;this.press('u');continue;}
     if(P.state==='stand'&&Math.floor((P.y-1)/64)<sh.rf){ev.stand={x:P.x,y:P.y,t:H.gameTime-ev.t0,lipd:(P.x-(sh.dir>0?(sh.c+1)*32:sh.c*32))*sh.dir};break;}
     if(P.state==='dead'){ev.err='died';break;}
     H.tick(1);}
   ev.hp=H.P.hp;ev.state=H.P.state;return ev;},
 shaft(n,s,sh,i){const C=this,out={c:sh.c,k:sh.k,bad:[]},CH=H.CHM();
   const lk=C.setup(n,s,sh,0);let entry=['j','u','run'][(n+s+i)%3];if(entry==='run'&&!C.back(sh))entry='u';if(!lk){out.bad.push('no chimney at its foot');return out;}
   const ys=lk.ys,y0=lk.y0;out.lip=y0-ys;
   // the stances it should have
   const want=[];for(let m=0;m<12;m++){want.push(H.chimH(m));if(y0-ys-H.chimH(m)<=CH.YD)break;}out.want=want;
   // climb
   for(const e of [entry]){const ev=C.climb(n,s,sh,e);out.entry=e;out.climb=ev.stand?ev.stand.t:null;
     if(!ev.stand)out.bad.push('climb ('+e+') did not reach the ledge: '+ev.state+' '+JSON.stringify(ev.st.map(q=>q.h))+(ev.err||''));
     else{if(Math.abs(ev.stand.lipd-CH.YX)>3)out.bad.push('stands '+ev.stand.lipd.toFixed(1)+' px past the lip');if(!ev.sl)out.bad.push('no standing landing');}
     if(ev.hp<ev.hp0)out.bad.push('climb lost '+(ev.hp0-ev.hp));
     const hs=ev.st.map(q=>q.h);if(JSON.stringify(hs)!==JSON.stringify(want))out.bad.push('stances '+JSON.stringify(hs)+' want '+JSON.stringify(want));
     ev.st.forEach((q,m)=>{if(q.sd!==(m%2?-lk.F:lk.F))out.bad.push('stance '+m+' on the wrong wall');});
     out.times=ev.st.map(q=>q.t);}
   // held Up: one kick
   {let ev=C.climb(n,s,sh,'j',0);H.setKey('kb','u',true);let mx=0;for(let f=0;f<120;f++){H.tick(1);if(H.P.lock)mx=Math.max(mx,H.P.lock.n);}H.setKey('kb','u',false);H.tick(1);
     const P=H.P;if(!(P.lock&&P.lock.n===1&&P.lock.ph==='plant'&&mx===1))out.bad.push('held Up: stance '+(P.lock?P.lock.n+' '+P.lock.ph:'none')+' max '+mx);}
   // Jump does nothing
   {C.climb(n,s,sh,'u',0);const P=H.P,x=P.x,y=P.y;for(let q=0;q<3;q++){C.press('j');H.tick(10);}
     const Q=H.P;if(!(Q.lock&&Q.lock.n===0&&Q.lock.ph==='plant'&&Q.x===x&&Q.y===y))out.bad.push('Jump moved him in the chimney');}
   // Down at each stance
   out.down=[];
   for(let m=0;m<want.length;m++){const ev=C.climb(n,s,sh,'j',m);const h=ev.st.length?ev.st[ev.st.length-1].h:-1,hp0=H.P.hp;
     H.setKey('kb','d',true);H.tick(1);const at=!H.P.lock&&H.P.state==='air';let f=0;for(;f<240&&H.P.state==='air';f++)H.tick(1);H.setKey('kb','d',false);H.tick(30);
     const P=H.P,dead=P.state==='dead'||P.state==='dying'||H.mode==='dead',lost=hp0-P.hp,exp=h>=170?'dead':h>=100?1:0;
     out.down.push({h,lost:dead?'dead':lost});
     if(!at)out.bad.push('Down at stance '+m+': not let go at once');
     if((dead?'dead':lost)!==exp)out.bad.push('Down at stance '+m+' ('+h+' px): '+(dead?'dead':lost)+' want '+exp);
     if(!dead&&Math.floor((P.y-1)/64)!==sh.rf)out.bad.push('Down at stance '+m+': not at the foot');}
   // rewind in mid-kick
   {C.climb(n,s,sh,'j',0);C.press('u');H.tick(12);const sn=H.snapAll(),P=H.P,k0={n:P.lock&&P.lock.n,ph:P.lock&&P.lock.ph,x:P.x,y:P.y,fn:P.lock&&P.lock.fn};
     const e1=C.climb(n,s,sh,null,undefined,false);H.applySnap(sn);const Q=H.P;
     if(!(Q.lock&&Q.lock.n===k0.n&&Q.lock.ph===k0.ph&&Q.lock.fn===k0.fn&&Q.x===k0.x&&Q.y===k0.y))out.bad.push('rewind: lock not restored '+JSON.stringify(k0));
     if(Q.lock===sn.P.lock||(Q.chm&&Q.chm===sn.P.chm))out.bad.push('rewind: shares the snapshot\'s objects');
     const e2=C.climb(n,s,sh,null,undefined,false);if(!e1.stand||!e2.stand)out.bad.push('rewind: climb not finished '+!!e1.stand+' '+!!e2.stand);}
   // walking in does not lock
   {C.setup(n,s,sh,0);C.setup(n,s,sh,Math.max(1,C.back(sh)));H.setKey('kb',sh.dir>0?'r':'l',true);let lk2=false;for(let f=0;f<120;f++){H.tick(1);if(H.P.lock||H.P.state==='air')lk2=true;}C.keys();if(lk2)out.bad.push('walking in locked him');}
   return out;},
 walls(n,s){const L=H.load(n,s,true),W=H.WALL,o=[];let tries=0,bad=0;
   for(let r=2;r<L.rows-1&&o.length<4;r++)for(let c=2;c<L.cols-2&&o.length<4;c++){if(H.B(c,r)===W||H.B(c,r+1)!==W)continue;
     for(const sd of [1,-1]){if(H.B(c+sd,r)!==W||H.B(c+sd,r-1)!==W)continue;const f=H.F(c,r);if(f&&f.t==='shaftfoot')continue;if((c*7+r*13)%5)continue;o.push([c,r,sd]);break;}}
   for(const [c,r,sd] of o){H.load(n,s,true);H.mode='play';const P=H.P;P.x=sd>0?(c+1)*32-6.5:c*32+6.5;P.y=(r+1)*64-4-30;P.fallY=P.y;P.state='air';P.vx=0;P.vy=-60;P.jumpKind='stand';P.autoGrab=false;P.face=sd;P.lock=null;P.plant=null;
     tries++;let k=false;for(const key of ['j','u']){H.setKey('kb',key,true);H.tick(2);H.setKey('kb',key,false);for(let i=0;i<20;i++){const Q=H.P;if(Q.plant||Q.lock||Q.jumpKind==='kick')k=true;H.tick(1);}}
     if(k)bad++;}
   return {tries,bad};}};}'''

fails = []
rows = []
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 852, 'height': 393}); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://' + SRC); pg.wait_for_timeout(400); pg.evaluate(JS)
    for n in range(LO, HI + 1):
        for s in SEEDS:
            sh = pg.evaluate('([n,s])=>__C.shafts(n,s)', [n, s])
            res = [pg.evaluate('([n,s,sh,i])=>__C.shaft(n,s,sh,i)', [n, s, q, i]) for i, q in enumerate(sh)]
            w = pg.evaluate('([n,s])=>__C.walls(n,s)', [n, s])
            nb = sum(len(r['bad']) for r in res) + w['bad']
            for r in res:
                r['n'] = n; r['s'] = s; rows.append(r)
                for m in r['bad']: fails.append('floor %d seed %d shaft c%d k%d: %s' % (n, s, r['c'], r['k'], m))
            if w['bad']: fails.append('floor %d seed %d: %d of %d single walls planted, kicked or locked' % (n, s, w['bad'], w['tries']))
            if sh or nb: print('floor %2d seed %d: shafts %d (k %s), walls tried %d, faults %d' % (n, s, len(sh), ','.join(str(q['k']) for q in sh), w['tries'], nb), flush=True)
    b.close()
json.dump(rows, open(os.path.join(HERE, 'chimtest.json'), 'w'))
print('shafts', len(rows))
for k in sorted(set(r['k'] for r in rows)):
    q = [r for r in rows if r['k'] == k]
    if not q: continue
    w = q[0].get('want', []); d = q[0].get('down', [])
    print('k=%d: %d shafts, lip %s px; stances (feet over the foot) %s; Down from each: %s' % (k, len(q), sorted(set(r.get('lip') for r in q)), w,
          ', '.join('%g px %s' % (x['h'], 'death' if x['lost'] == 'dead' else ('%d life' % x['lost'] if x['lost'] else 'unhurt')) for x in d)))
    for e in ('j', 'u', 'run'):
        t = [r['climb'] for r in q if r.get('entry') == e and r.get('climb')]
        if t: print('   way in %-3s: press to standing on the ledge %.2f-%.2f s (mean %.2f, n %d)' % (e, min(t), max(t), st.mean(t), len(t)))
print('errors', errs[:3])
for x in fails[:30]: print('FAIL', x)
print('chimtest: ok' if not fails and not errs else 'chimtest: FAIL %d' % (len(fails) + len(errs)))
sys.exit(1 if fails or errs else 0)
