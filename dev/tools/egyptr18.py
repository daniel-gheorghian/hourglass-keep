# egyptr18.py [new.html] [old.html] [outdir]: round 18's pictures for egypt_themes.html: the jet stream hint (a stream of the theme's
# sand along a move's path) in place of the kick shaft's chevrons, on the swing's throw and on the jump up to a ledge (jgrab), and the
# paternoster without its brass chevrons (old.html, default ../_r17.html, made with git show 6995922:dev/hourglass-keep.html), in the
# game at the phone's resolution (crops of the 1704 px canvas), Torchlight and Classic:
#  r18_shaft.png  the kick shaft mid-climb in two themes, both modes, 1:1 and 2x (a smaller crop enlarged, smoothed)
#  r18_shaft.gif  the climb in both themes, Torchlight, 0.1 s a frame
#  r18_swing.png  the swing once it will carry him (two themes, both modes, 1:1 and 2x); r18_swing.gif the swing and the throw
#  r18_jgrab.png  the jump up to a ledge, two themes, both modes, until the move is learned
#  r18_chain.png  the paternoster before (round 17, chevrons) and after, both modes
# Writes r18.json (the floors used, the swing's predicted and real landings, errors). Hints are set unlearned for the pictures.
# Run from dev/tools.
import json, os, sys
from playwright.sync_api import sync_playwright
from PIL import Image
import egyptr12 as R12
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
NEW = os.path.abspath(a[0] if len(a) > 0 else os.path.join(HERE, '..', 'hourglass-keep.html'))
OLD = os.path.abspath(a[1] if len(a) > 1 else os.path.join(HERE, '..', '_r17.html'))
OUT = a[2] if len(a) > 2 else os.path.join(HERE, 'egypt_themes')
R12.OUT = OUT
SHAFTS = [(7, 802), (17, 802)]   # the Halls of the West, the Green Hall
SWINGS = [6, 17]
JGRABS = [(6, 802, 0), (17, 801, 0)]
SHAFT = r"""([n,seed,k])=>{const H=__HK;__P.load(n,seed);H.S.learned.shaft=0;H.S.learned.walljump=0;const L=H.L;const ins=L.path.find(a=>a.a==='walljump');
 const f=L.dyn.find(d=>d.f.t==='shaftfoot'&&d.c===ins.from);let i=0;
 runBot(n,seed,{path:[ins],at:{c:ins.from,r:f.r,face:ins.dir||1},stop:H=>++i>=k});H.S.learned.shaft=0;H.cam.snap=true;H.tick(1);H.banner=null;__P.draw();
 return {xy:__P.scr(ins.from*32+16,H.P.y-50),look:L.theme.look,name:H.themeName(n)};}"""
SWING = r"""([n,A,th0])=>{const H=__HK;let L,o,SD;for(let sd=1;sd<=25&&!o;sd++){SD=7100+sd;L=__P.load(n,SD);o=L.dyn.find(q=>q.f.t==='bar');}
 const f=o.f,D=L.base[o.r*L.cols+o.c+2]===L.base[o.r*L.cols+o.c]?1:-1,p=H.P;H.S.learned.swing=0;
 p.x=f.x;p.y=f.y+57;p.vx=0;p.vy=0;p.state='air';p.autoGrab=true;p.face=D;p.fallY=p.y;p.inv=1e9;f.ps=0;f.pw=0;H.tick(1);
 p.swTh=th0;p.swOm=Math.sqrt(Math.max(0,2*(Math.cos(th0)-Math.cos(A))))*H.SW_W;H.cam.snap=true;H.tick(1);p.swGl=-9;H.banner=null;__P.draw();
 return {n,seed:SD,D,fx:f.x,fy:f.y,look:L.theme.look,name:H.themeName(n),xy:__P.scr(f.x+D*75,f.y+30)};}"""
LAND = r"""()=>{const H=__HK,p=H.P;let k=0;while(k<200&&!(p.swOm>0&&p.swTh>=0&&p.swTh<0.15)){H.tick(1);k++;}const pp=H.jsSwingPath(),e=[pp.x[pp.n-2],pp.y[pp.n-2]+30];
 H.setKey('kb','j',true);H.tick(1);H.setKey('kb','j',false);k=0;while(k<200&&p.state==='air'){H.tick(1);k++;}return {pred:e.map(Math.round),land:[Math.round(p.x),Math.round(p.y)],state:p.state};}"""
JG = r"""([n,sd,k])=>{const H=__HK;const L=__P.load(n,sd);H.S.learned.jgrab=0;const a=L.path.filter(q=>q.a==='jgrab')[k];const d=a.to>a.from?1:-1;
 let r=-1;for(let rr=1;rr<L.rows-1&&r<0;rr++){const f=L.feat[rr*L.cols+a.from+d];if(f&&f.t==='jgrab')r=rr;}
 __P.stand(a.from-d,r,d);H.tick(20);H.banner=null;__P.draw();return {xy:__P.scr((a.from+a.to)*16+16,r*64),look:L.theme.look,name:H.themeName(n)};}"""
CHAIN = r"""([lo])=>{const H=__HK;for(let n=lo;n<lo+30;n++)for(const sd of [801,802,803]){const L=__P.load(n,sd);const f=L.lifts.find(q=>q.t==='chain');if(!f)continue;
 const xE=f.c0*32+16,d=f.c1>f.c0?1:-1;__P.stand(f.c0-2*d,f.rB,d);H.tick(10);H.banner=null;__P.draw();return {n,seed:sd,name:H.themeName(n),xy:__P.scr((f.c0+f.c1)*16+16,(f.yT+f.yB)/2)};}return null;}"""
STEP = r"""(k)=>{const H=__HK;H.tick(k);H.banner=null;__P.draw();}"""
AT = r"""([x,y])=>__P.scr(x,y)"""


def up(im, k=2):
    return im.resize((im.width * k, im.height * k), Image.LANCZOS)


def lab(im, t):
    return R12.label(im, t)


if __name__ == '__main__':
    J = {'errors': []}
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
        P = {m: R12.page(b, NEW, m) for m in ('torch', 'classic')}
        # ---- the kick shaft, mid-climb (after 40 frames of the bot's climb)
        t1, t2 = [], []
        for n, sd in SHAFTS:
            for m in ('torch', 'classic'):
                q = P[m].evaluate(SHAFT, [n, sd, 40]); im = R12.shot(P[m])
                t1.append(lab(R12.crop(im, q['xy'], 300, 420), '%s, floor %d, %s, 1:1' % (q['name'], n, m)))
                t2.append(lab(up(R12.crop(im, q['xy'], 150, 210)), '2x'))
        R12.grid([x for pr in zip(t1, t2) for x in pr], 4).save(os.path.join(OUT, 'r18_shaft.png'))
        cols = []
        for n, sd in SHAFTS:
            fr = []
            for k in range(2, 92, 3):
                q = P['torch'].evaluate(SHAFT, [n, sd, k])
                fr.append(lab(R12.crop(R12.shot(P['torch']), q['xy'], 300, 420), '%s' % q['name']))
            cols.append(fr)
        R12.gif([R12.grid([c[k] for c in cols], len(cols)).convert('P', palette=Image.ADAPTIVE, colors=200) for k in range(len(cols[0]))], 'r18_shaft.gif', 100)
        J['shafts'] = SHAFTS
        # ---- the swing: once it will carry him; the predicted landing against the real one
        J['swing'] = []
        for n in SWINGS:
            for A in (0.6, 0.8, 1.0):
                P['torch'].evaluate(SWING, [n, A, 0.0]); r = P['torch'].evaluate(LAND); r.update(n=n, A=A); J['swing'].append(r)
        t1, t2 = [], []
        for n in SWINGS:
            for m in ('torch', 'classic'):
                q = P[m].evaluate(SWING, [n, 0.85, 0.25]); im = R12.shot(P[m])
                t1.append(lab(R12.crop(im, q['xy'], 760, 400), '%s, floor %d, %s, 1:1' % (q['name'], n, m)))
                t2.append(lab(up(R12.crop(im, q['xy'], 380, 200)), '2x'))
        R12.stack([R12.grid(t1, 2), R12.grid(t2, 2)]).save(os.path.join(OUT, 'r18_swing.png'))
        cols = []
        for n in SWINGS:
            pt = P['torch']; q = pt.evaluate(SWING, [n, 0.5, 0.0]); fr = []
            for k in range(34):
                if k == 22:
                    pt.evaluate("()=>{const H=__HK,p=H.P;let i=0;while(i<120&&!(p.swOm>0&&p.swTh>=0&&p.swTh<0.15)){H.tick(1);i++;}H.setKey('kb','j',true);H.tick(1);H.setKey('kb','j',false);}")
                elif k < 22:  # pumping: a press the way he swings at each turn
                    pt.evaluate("()=>{const H=__HK,p=H.P,d=p.swOm>=0?(p.face>0?'r':'l'):(p.face>0?'l':'r');H.setKey('kb',d,true);H.tick(1);H.setKey('kb',d,false);}")
                pt.evaluate(STEP, 5)
                xy = pt.evaluate(AT, [q['fx'] + q['D'] * 75, q['fy'] + 30])
                fr.append(lab(R12.crop(R12.shot(pt), xy, 760, 400), q['name']))
            cols.append(fr)
        R12.gif([R12.grid([c[k] for c in cols], 1).convert('P', palette=Image.ADAPTIVE, colors=200) for k in range(len(cols[0]))], 'r18_swing.gif', 100)
        # ---- the jump up to a ledge (shown until the move is learned)
        t1 = []
        for n, sd, k in JGRABS:
            for m in ('torch', 'classic'):
                q = P[m].evaluate(JG, [n, sd, k])
                t1.append(lab(R12.crop(R12.shot(P[m]), q['xy'], 560, 380), '%s, floor %d, %s, 1:1' % (q['name'], n, m)))
        R12.grid(t1, 2).save(os.path.join(OUT, 'r18_jgrab.png'))
        J['jgrabs'] = JGRABS
        J['errors'] += P['torch'].errs + P['classic'].errs
        # ---- the paternoster: before (round 17, chevrons) and after
        O = {m: R12.page(b, OLD, m) for m in ('torch', 'classic')}
        t1 = []
        for m in ('torch', 'classic'):
            for tag, pg in (('before (round 17)', O[m]), ('after', P[m])):
                q = pg.evaluate(CHAIN, [8])
                t1.append(lab(R12.crop(R12.shot(pg), q['xy'], 420, 520), '%s, floor %d, %s, %s' % (q['name'], q['n'], m, tag)))
        R12.grid(t1, 4).save(os.path.join(OUT, 'r18_chain.png'))
        J['chain'] = q
        J['errors'] += P['torch'].errs + P['classic'].errs
        json.dump(J, open(os.path.join(OUT, 'r18.json'), 'w'), indent=1)
        print(json.dumps(J['swing']), 'errors', J['errors'][:5])
        b.close()
