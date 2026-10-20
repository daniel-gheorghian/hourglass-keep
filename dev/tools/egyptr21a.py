# egyptr21a.py [new.html] [old.html] [outdir]: round 21a's pictures for egypt_themes.html, before (old.html, default the v68 release,
# hk_v68_release.html here or in the main checkout's dev/tools) and after:
#  r21a_prince.png     the prince standing in the game (crops of the 1704 px canvas: Torchlight at GLP.rs 1 and 0.5, Classic; facing both ways),
#                      then the upper body drawn alone at 10x (light from his back and his front, the silhouette), then every pose at 4x
#                      (stand, the run cycle, step, turn, crouch, jump, hang, pull, fight stances, hurt, drink, dead) and a robber
#  r21a_lift.png       the counterweight lift: its platform mid-shaft (alone) and docked with him on it, in the game (both modes, rs .5), and
#                      Classic close-ups at 6x of the platform's ropes and the counterweight
#  r21a_paternoster.png  the paternoster's slabs riding the rope loop, in the game (both modes) and close-ups at 6x
# Writes r21a.json (cases, page errors). Run from dev/tools.
import base64, io, json, os, re, sys
from playwright.sync_api import sync_playwright
from PIL import Image
import egyptr12 as R12
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
NEW = os.path.abspath(a[0] if len(a) > 0 else os.path.join(HERE, '..', 'hourglass-keep.html'))
_old = os.path.join(HERE, 'hk_v68_release.html')
if not os.path.exists(_old):
    _old = os.path.join(HERE, '..', '..', '..', '..', '..', 'dev', 'tools', 'hk_v68_release.html')  # (from a worktree: the main checkout's)
OLD = os.path.abspath(a[1] if len(a) > 1 else _old)
OUT = a[2] if len(a) > 2 else os.path.join(HERE, 'egypt_themes')
R12.OUT = OUT
TAG = {'old': 'before (v68)', 'new': 'after (21a)'}
# ---- 1: the prince
STAND = r'''([n,sd,face,rs])=>{const H=__HK;const L=__P.load(n,sd);let pc=-1,r=-1;
 for(let rr=1;rr<L.rows&&pc<0;rr++)for(let c=12;c<L.cols-12;c++){let ok=true;for(let k=-3;k<=4;k++)if(!H.solidBelow(c+k,rr)||L.feat[rr*L.cols+c+k])ok=false;if(ok){pc=c;r=rr;break;}}
 __P.stand(pc,r,face);for(let i=0;i<40;i++){H.tick(1);H.P.x=pc*32+16;H.P.state='stand';}if(H.GLP)H.GLP.rs=rs;__P.draw();return __P.scr(pc*32+16,(r+1)*64-34);}'''
FIG = r'''([p,S,W,Hh,x,y,dir,mono,pk])=>{const H=__HK;p=Object.assign(H.mk({}),p);const pal=pk==='rob'?H.guardPal({tier:1}):H.PAL_HERO;
 const cv=document.createElement('canvas');cv.width=W*S;cv.height=Hh*S;const c=cv.getContext('2d');c.fillStyle='#5a4434';c.fillRect(0,0,cv.width,cv.height);c.scale(S,S);
 H.figDraw(c,x,y,1,p,pal,{sword:!!p._sw,hasSword:true,time:0,mono:mono||undefined,lt:{dir,col:'255,220,170',k:0.6}});return cv.toDataURL('image/png');}'''
POSES = r'''()=>{const H=__HK,o={};for(const k of ['stand','step','turn','crouch','jumpR','jumpS','hang','pull','press','garde','lunge','parry','windup','hurt','dead'])o[k]=Object.assign({},H.PS[k]);
 for(const ph of [0,0.25,0.5,0.75])o['run '+ph]=Object.assign({},H.RP(ph));o.drink=Object.assign({},H.drinkFrame(0.7).p);o.garde._sw=1;o.lunge._sw=1;o.parry._sw=1;o.windup._sw=1;return o;}'''
# ---- 2, 3: the lifts
FIND = r'''([kind])=>{const H=__HK;const lo=kind.startsWith('chn')?8:3;for(let n=lo;n<=27;n+=2)for(let s=0;s<80;s++){const seed=60000+s*137+n*19,L=H.genLevel(n,seed,true);if(L.segs.some(q=>q.k==='turn-'+kind))return [n,seed];}return null;}'''
SETLIFT = r'''([n,seed,want,frac,alone])=>{const H=__HK;const L=__P.load(n,seed);
  const sg=L.segs.find(q=>q.k==='turn-'+want);const lf=L.lifts.find(q=>q.ca>=Math.min(sg.c0,sg.c1)-1&&q.cb<=Math.max(sg.c0,sg.c1)+1&&q.rT>=Math.min(sg.r0,sg.r1)&&q.rB<=Math.max(sg.r0,sg.r1));const P=H.P;let x,y;
  if(lf.t==='lift'){lf.y=lf.yT+(lf.yB-lf.yT)*frac;P.x=lf.sc*32+16;P.y=lf.y;P.state='stand';P.face=1;L.base[lf.rT*L.cols+lf.sc]=frac===0?1:0;lf.gT=frac===0?1:0;lf.gB=frac===1?1:0;x=P.x;y=lf.y;}
  else{H.tick(Math.round(frac*60));const q=H.chainPos(lf,0,H.gameTime);P.x=q.x;P.y=q.y;P.state='lift';P.lift=lf;P.slab=0;P.bx=q.x;P.by=q.y;P.bt=0;x=q.x;y=q.y;}
  if(alone)P.x=-999;
  return {x,y,yT:lf.yT,yB:lf.yB,k:lf.k};}'''
VIEW = r'''([x,y,rs])=>{const H=__HK;if(H.GLP)H.GLP.rs=rs;H.cam.x=x-H.viewW/2;H.cam.y=y-150;H.cam.gy=H.cam.y;H.render();H.render();H.render();return __P.scr(x,y);}'''
_ls = open(os.path.join(HERE, 'liftshot.py')).read()
CLOSE = re.search(r"JS='''(.*?)'''", _ls, re.S).group(1).replace('P.bt=0;}', 'P.bt=0;if(alone)P.x=-999;}').replace(
    'return {u:cv.toDataURL(),k:lf.k}', "const q=lf.t==='lift'?{x:lf.sc*32+16,y:lf.y}:H.chainPos(lf,0,H.gameTime);return {u:cv.toDataURL(),k:lf.k,px:q.x-x0,py:q.y-y0}")


def dataimg(d):
    return Image.open(io.BytesIO(base64.b64decode(d.split(',')[1]))).convert('RGB')


def close(pg, ns, want, frac, Z, alone, box):
    pg.evaluate("window.__HKfreeze=true")
    u = pg.evaluate(CLOSE, [ns[0], ns[1], want, frac, Z, alone])
    im = dataimg(u['u']); cx, cy = u['px'] * Z, u['py'] * Z
    return im.crop((int(cx + box[0] * Z), int(cy + box[1] * Z), int(cx + box[2] * Z), int(cy + box[3] * Z)))


if __name__ == '__main__':
    J = {'errors': [], 'cases': {}}
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
        P = {(v, m): R12.page(b, src, m) for v, src in (('old', OLD), ('new', NEW)) for m in ('torch', 'classic')}
        for pg in P.values():
            pg.evaluate("()=>{__HK.EGP.traps=true;}")
        pn = P[('new', 'classic')]
        # ---- 1. the prince standing
        rows = []
        t = []
        for n, face in ((7, 1), (14, -1)):
            for m, rs in (('torch', 1), ('torch', 0.5), ('classic', 1)):
                for v in ('old', 'new'):
                    xy = P[(v, m)].evaluate(STAND, [n, 1, face, rs])
                    t.append(R12.label(R12.crop(R12.shot(P[(v, m)]), xy, 150, 200), '%s, %s%s' % (TAG[v][:6], m, ' .5' if rs < 1 else '')))
        rows.append(R12.grid(t, 12))
        poses = pn.evaluate(POSES)
        t = []
        for dr, mono in ((-1, None), (1, None), (1, '#120c18')):
            for v in ('old', 'new'):
                t.append(R12.label(dataimg(P[(v, 'classic')].evaluate(FIG, [poses['stand'], 10, 26, 30, 13, 58, dr, mono, 'hero'])), '%s, %s' % (TAG[v], 'silhouette' if mono else 'lit from his %s' % ('back' if dr < 0 else 'front'))))
        rows.append(R12.grid(t, 6))
        for v in ('old', 'new'):
            t = []
            for k, q in poses.items():
                air = k in ('hang', 'pull', 'press')
                t.append(R12.label(dataimg(P[(v, 'classic')].evaluate(FIG, [q, 4, 44, 72, 36 if k == 'dead' else 20, 60 if air else 68, -1, None, 'hero'])), k))
            t.append(R12.label(dataimg(P[(v, 'classic')].evaluate(FIG, [poses['stand'], 4, 44, 72, 20, 68, -1, None, 'rob'])), 'robber'))
            rows.append(R12.label(R12.grid(t, 11), TAG[v], (4, 276)))
        R12.stack(rows).save(os.path.join(OUT, 'r21a_prince.png'))
        print('prince done', flush=True)
        # ---- 2. the counterweight lift; 3. the paternoster
        for want, fn, cases in (('lift2d', 'r21a_lift.png', ((0.5, True), (0.0, False))), ('chn2d', 'r21a_paternoster.png', ((0.3, True), (0.9, True)))):
            ns = pn.evaluate(FIND, [want]); J['cases'][want] = ns
            rows = []
            t = []
            for frac, alone in cases:
                for m, rs in (('torch', 1), ('torch', 0.5), ('classic', 1)):
                    for v in ('old', 'new'):
                        pg = P[(v, m)]
                        q = pg.evaluate(SETLIFT, [ns[0], ns[1], want, frac, alone])
                        xy = pg.evaluate(VIEW, [q['x'], q['y'], rs])
                        t.append(R12.label(R12.crop(R12.shot(pg), (xy[0] + 8, xy[1] - 34), 240, 210), '%s, %s%s' % (TAG[v][:6], m, ' .5' if rs < 1 else '')))
            rows.append(R12.grid(t, 6))
            t = []
            for frac, alone in cases:
                for v in ('old', 'new'):
                    t.append(R12.label(close(P[(v, 'classic')], ns, want, frac, 6, alone, (-40, -64, 40, 14)), '%s, 6x' % TAG[v]))
            rows.append(R12.grid(t, 4))
            R12.stack(rows).save(os.path.join(OUT, fn))
            print(fn, 'done', ns, flush=True)
        for (v, m), pg in P.items():
            J['errors'] += ['%s %s: %s' % (v, m, e) for e in pg.errs]
    json.dump(J, open(os.path.join(OUT, 'r21a.json'), 'w'), indent=1)
    print('errors', J['errors'][:5])
