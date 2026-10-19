# swingfeel.py [game.html] [out.json] [floor]: how hard the swing bar is to pump, played by simulated people instead of the bot.
# On the first bar of a floor (from a few seeds), from a standing catch (hanging still) it plays each input style 40 times with its
# own seeded jitter and prints, per style, how many runs reach SW_CLEAR within 12 s, the median and 90th-percentile time to it, and
# how many presses (direction changes) and pumps (kicks, round 16b on) it took; then a let-go after the cue (Jump on the next forward swing, timed by a person)
# and whether he lands on the far side. Styles, as a phone player plays them:
#   alt R+-j    alternate with the swing: switch to the way he is moving R s after each turn, give or take j s (a person reacting)
#   alt 0+-j    the same, anticipating the turn (no mean delay)
#   tap         a short tap (0.12 to 0.25 s) the way he is moving, after each turn (a thumb that taps instead of holding)
#   rhythm T    alternating on a beat of T s, not locked to the swing (a person's guess of its tempo), +-0.1 s a press
#   hold fwd    holding forward only; mash: alternating every 0.08 to 0.2 s at random
# Every style runs through the touch source (setKey('touch',...)), the one the phone's pad drives. Also a release grid: for an
# amplitude A and an angle at which Jump is pressed on the forward swing, whether he lands on the far side.
import json, os, sys
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
JS = r'''([n,styles,N])=>{const H=__HK;window.__HKfreeze=true;window.__HKnoauto=true;for(const id in H.HINTS){H.S.hints[id]=1;H.S.learned[id]=1;}
 let L=null,o=null,SD=0;for(let sd=1;sd<=25&&!o;sd++){SD=7100+sd;L=H.load(n,SD,true);H.banner=null;o=L.dyn.find(q=>q.f.t==='bar');}
 if(!o)return {skip:'no bar'};
 let f=o.f;const RL=()=>{L=H.load(n,SD,true);H.banner=null;o=L.dyn.find(q=>q.f.t==='bar');f=o.f;};
 const D=L.base[o.r*L.cols+o.c+2]===L.base[o.r*L.cols+o.c]?1:-1,FW=D>0?'r':'l',BK=D>0?'l':'r',c=o.c-2*D,P=()=>H.P,SRC='touch';
 const clr=()=>['l','r','j','d','u','g'].forEach(k=>{H.setKey('kb',k,false);H.setKey('touch',k,false);}),amp=()=>H.swAmp(P().swTh,P().swOm);
 const hold=(th,om)=>{RL();clr();const p=P();p.x=f.x;p.y=f.y+57;p.vx=0;p.vy=0;p.state='air';p.autoGrab=true;p.face=D;p.fallY=p.y;p.inv=1e9;f.ps=0;f.pw=0;H.tick(1);
   p.swTh=th;p.swOm=om;return p.state==='swing';};
 const done=()=>['stand','land','landHurt','hang','dead','run','crouch','climb'].includes(P().state);
 const land=()=>{let k=0;while(k<240&&!done()){H.tick(1);k++;}const st=P().state,col=(Math.floor(P().x/32)-c)*D;return {st,col,ok:(st==='land'||st==='stand'||st==='run'||st==='hang'||st==='climb')&&col>=4};};
 let s=1;const rnd=()=>{s=(s+0x6D2B79F5)|0;let t=Math.imul(s^(s>>>15),1|s);t=(t+Math.imul(t^(t>>>7),61|t))^t;return((t^(t>>>14))>>>0)/4294967296;},U=(a,b)=>a+(b-a)*rnd();
 const DT=1/60,out={seed:SD,clear:H.SW_CLEAR,styles:{}};
 // one run of a style: returns time to the cue, presses, and the let-go's outcome
 const run=(st,seed)=>{s=seed*7919+13;if(!hold(0,0))return {err:'no catch'};let t=0,want=0,lastOm=0,turnT=-9,sched=[],presses=0,beat=U(0,0.5),tc=null,rel=null,tRel=null,kicks=0,kt=P().swKT;
   const setW=w=>{if(w!==want){want=w;if(w)presses++;}};
   while(t<14){const p=P();const om=p.swOm;
     // the person sees a turn (or the first movement) and schedules a switch to the new way
     const sg=Math.abs(om)>0.05?Math.sign(om):0;if(sg&&sg!==lastOm){lastOm=sg;turnT=t;
       if(st.k==='alt')sched.push([t+Math.max(0,st.R+U(-st.j,st.j)),sg,null]);
       if(st.k==='tap'){const t0=t+Math.max(0,0.15+U(-0.1,0.1));sched.push([t0,sg,null]);sched.push([t0+U(0.12,0.25),0,null]);}}
     if(st.k==='alt'||st.k==='tap'){while(sched.length&&sched[0][0]<=t){setW(sched.shift()[1]);}}
     if(st.k==='alt'&&t<0.05&&!want)setW(1); // the first push: forward
     if(st.k==='tap'&&t<0.05&&!want){sched.push([0.2,0,null]);setW(1);}
     if(st.k==='rhythm'){if(t>=beat){beat=t+st.T+U(-0.1,0.1);setW(want>0?-1:1);}}
     if(st.k==='hold')setW(1);
     if(st.k==='mash'){if(t>=beat){beat=t+U(0.08,0.2);setW(want>0?-1:1);}}
     H.setKey(SRC,FW,want>0);H.setKey(SRC,BK,want<0);
     // the let-go: after the cue, on the next forward swing, Jump about at the bottom (a person: 0.29 s after the turn, -0.12 to +0.2)
     if(tc!==null&&tRel===null&&lastOm>0&&turnT>tc)tRel=turnT+0.29+U(-0.12,0.2);
     if(tRel!==null&&t>=tRel){const a0=amp();H.setKey(SRC,'j',true);H.tick(1);H.setKey(SRC,'j',false);clr();rel=land();rel.a=+a0.toFixed(2);break;}
     H.tick(1);t+=DT;if(tc===null&&P().swKT!==kt){kicks++;kt=P().swKT;}if(tc===null&&amp()>=H.SW_CLEAR)tc=t;}
   clr();return {tc:tc===null?null:+tc.toFixed(2),presses,kicks,rel};};
 for(const st of styles){const R=[];for(let i=0;i<N;i++)R.push(run(st,i+1));out.styles[st.name]=R;}
 // the release grid: amplitude x angle on the forward swing (Jump pressed when the angle is reached)
 out.grid=[];for(const A of [0.4,0.5,0.55,0.6,0.7,0.8,0.9,1.0]){const row=[];for(const tr of [-0.6,-0.5,-0.4,-0.2,0,0.1,0.2,0.3,0.4]){if(tr>=A-0.02){row.push(null);continue;}
   hold(-A,0);let k=0;while(k<200&&!(P().swOm>0&&P().swTh>=tr)){H.tick(1);k++;}H.setKey('kb','j',true);H.tick(1);H.setKey('kb','j',false);const q=land();row.push(q.ok?1:0);}out.grid.push([A,row]);}
 out.gridAngles=[-0.6,-0.5,-0.4,-0.2,0,0.1,0.2,0.3,0.4];
 return out;}'''
STY = [dict(name='alt 0.2+-0.08', k='alt', R=0.2, j=0.08), dict(name='alt 0.2+-0.15', k='alt', R=0.2, j=0.15), dict(name='alt 0+-0.15', k='alt', R=0.0, j=0.15),
       dict(name='alt 0.35+-0.15', k='alt', R=0.35, j=0.15), dict(name='tap', k='tap'),
       dict(name='rhythm 0.45', k='rhythm', T=0.45), dict(name='rhythm 0.58', k='rhythm', T=0.58), dict(name='rhythm 0.75', k='rhythm', T=0.75),
       dict(name='hold fwd', k='hold'), dict(name='mash', k='mash')]


def pct(v, q):
    v = sorted(v); return v[min(len(v) - 1, int(q * (len(v) - 1) + 0.5))] if v else None


def summary(r):
    S = {}
    for nm, R in r['styles'].items():
        tc = [x['tc'] for x in R if x.get('tc') is not None]
        rel = [x['rel'] for x in R if x.get('rel')]
        S[nm] = dict(n=len(R), cleared=len(tc), med=pct(tc, 0.5), p90=pct(tc, 0.9), presses=pct([x['presses'] for x in R if x.get('tc') is not None], 0.5), kicks=pct([x['kicks'] for x in R if x.get('tc') is not None], 0.5),
                     landed=sum(1 for q in rel if q['ok']))
    return S


if __name__ == '__main__':
    a = sys.argv[1:]
    HTML = 'file://' + os.path.abspath(a[0] if a else os.path.join(HERE, '..', 'hourglass-keep.html'))
    OUT = a[1] if len(a) > 1 else None
    FLOOR = int(a[2]) if len(a) > 2 else 6
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(HTML); pg.wait_for_timeout(300)
        r = pg.evaluate(JS, [FLOOR, STY, 40]); b.close()
    if 'skip' in r:
        print('skip', r); sys.exit()
    S = summary(r)
    print('floor', FLOOR, 'seed', r['seed'], 'SW_CLEAR', r['clear'], 'errors', errs[:2])
    print('%-16s %8s %7s %7s %8s %6s %7s' % ('style', 'cleared', 'median', 'p90', 'presses', 'pumps', 'landed'))
    for nm, q in S.items():
        print('%-16s %5d/%-3d %7s %7s %8s %6s %4d/%d' % (nm, q['cleared'], q['n'], q['med'], q['p90'], q['presses'], q['kicks'], q['landed'], q['n']))
    print('release grid (1 = lands on the far side); angles', r['gridAngles'])
    for A, row in r['grid']:
        print('  A %.2f  %s' % (A, ' '.join('.' if v is None else str(v) for v in row)))
    if OUT:
        json.dump(dict(summary=S, raw=r), open(OUT, 'w'))
