# egyptr25f.py [what] [new.html] [old.html]: round 25f's pictures (owner: "I ment a stiff prince in the broader sense: check all his movements
# for stiffness and make adjustments based on research"), into egypt_themes/.
#   moves  r25f_moves.png: before | after at 4x, the moves as the game makes them frame by frame (the state machine run in a test room, the
#          pose eased as in play, drawn as the game draws it: livePose, the cloth's wind, the squash): idle, the turn, run and stop, the
#          standing jump from its crouch to the settle, a fall of one storey and its landing, the jump up to a ledge and the hang, the crawl;
#          on the after row the parts that differ from before are outlined in red
#   gif    r25f_moves1.gif (idle, turn, run and stop, standing jump with its landing, crouch) and r25f_moves2.gif (jump up to a ledge, hang,
#          climb, a fight exchange, the crawl): in the game at the phone's resolution (852x393 CSS px at 2x, crops 1:1), before | after,
#          Torchlight and Classic
# old.html defaults to round 25b's source (git show a8a0e5f:dev/hourglass-keep.html). Run from dev/tools.
import base64, io, os, subprocess, sys, tempfile, shutil
from PIL import Image, ImageDraw, ImageChops, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
WHAT = a[0] if a else 'all'
NEW = os.path.abspath(a[1] if len(a) > 1 and a[1] else os.path.join(HERE, '..', 'hourglass-keep.html'))
OLD = a[2] if len(a) > 2 and a[2] else None
OUT = os.path.join(HERE, 'egypt_themes')
INK = (20, 16, 24)
BG = (250, 246, 238)
EXPORT = 'window.__R25={skel,PS,mk,lerpPose,crawlPose,figDraw,PAL_HERO,GFX,LEN,livePose,startFall};'

# A test room (as lowceil.py builds one): row R the floor, two storeys open over it, and from column C0+LC a slab one storey up (a ledge he
# can jump up to, with room under it). The prince stands at column C0+start facing right.
ROOM = r'''([start,LC])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS){H.S.hints[id]=1;H.S.learned[id]=1;}
  const L=H.load(2,4321,true);H.banner=null;const R=4,C0=30,W=2,E=0,FL=1,set=(c,r,v)=>{L.base[r*L.cols+c]=v;L.feat[r*L.cols+c]=null;};
  for(let c=C0-2;c<=C0+22;c++)for(let r=R-3;r<=R+2;r++)set(c,r,W);
  for(let i=0;i<22;i++){const c=C0+i;set(c,R,FL);set(c,R-1,LC>0&&i>=LC?FL:E);set(c,R-2,E);}
  L.dyn=L.dyn.filter(d=>d.r<R-3||d.r>R+2||d.c<C0-2||d.c>C0+22);
  H.clearRooms();const P=H.P;P.inv=1e9;P.x=(C0+start)*32+16;P.y=(R+1)*64-4;P.fallY=P.y;P.state='stand';P.face=1;P.vx=P.vy=0;
  H.cam.snap=true;H.tick(40);return [P.x,P.y];}'''
# one game frame with keys (ops: [[key, on], ...]); returns the pose as drawn, and where he is
STEPJS = r'''([ops,rec])=>{const H=__HK,P=H.P,F=window.__R25;for(const [k,on] of ops){if(k==='fall'){P.y-=64;P.fallY=P.y;F.startFall(0);continue;}H.setKey('kb',k,on);}
  H.tick(1);if(!rec)return null;const lk=P.lk||{};
  return {st:P.state,p:Object.assign({},F.livePose(P,P.pose)),x:P.x,y:P.y+(P.rdy||0),yo:P.yo||0,vx:lk.cw||0,vy:lk.cwy||0,sq:lk.sq&&Math.abs(lk.sq-1)>0.004?lk.sq:undefined};}'''
DRAW = r"""([items,S,W])=>{const F=window.__R25;F.GFX().hd=true;const Hh=80,n=items.length,cv=document.createElement('canvas');cv.width=W*S*n;cv.height=Hh*S;const c=cv.getContext('2d');
 c.fillStyle='#e8dcc8';c.fillRect(0,0,cv.width,cv.height);
 for(let j=0;j<n;j++){const it=items[j],fy=72;c.save();c.scale(S,S);c.translate(j*W,0);c.beginPath();c.rect(0,0,W-0.5,Hh);c.clip();
  c.strokeStyle='rgba(0,0,0,.35)';c.lineWidth=0.3;c.beginPath();c.moveTo(1,fy);c.lineTo(W-1,fy);c.stroke();
  if(it.ledge!=null){c.fillStyle='rgba(120,100,80,.45)';c.fillRect(it.ledge,fy-64-4,W,6);}
  F.figDraw(c,it.cx,fy+it.dy,1,F.mk(it.p),F.PAL_HERO,{time:it.t||0,yo:it.yo||0,vx:it.vx||0,vy:it.vy||0,sq:it.sq,hasSword:true,lt:{dir:1,col:'255,220,170',k:0.6}});c.restore();}
 return cv.toDataURL('image/png');}"""


def b64img(u):
    return Image.open(io.BytesIO(base64.b64decode(u.split(',')[1]))).convert('RGB')


def old_src(tmp):
    if OLD:
        return os.path.abspath(OLD)
    fn = os.path.join(tmp, '_r25b.html')
    open(fn, 'w', encoding='utf-8').write(subprocess.run(['git', 'show', 'a8a0e5f:dev/hourglass-keep.html'], cwd=HERE, capture_output=True, text=True, check=True).stdout)
    return fn


def exported(src, tmp, tag):
    s = open(src, encoding='utf-8').read()
    i = s.find('window.__HK={')
    fn = os.path.join(tmp, '_r25f_%s.html' % tag)
    open(fn, 'w', encoding='utf-8').write(s[:i] + EXPORT + s[i:])
    return fn


# the scenes: (title, room start column, ledge column or 0, [(frames, ops at the first frame)], record from frame, every k frames, n)
K = lambda *ks: [[k, True] for k in ks]
U = lambda *ks: [[k, False] for k in ks]
SCENES = [
    ('Idle: breathing and a slow weight shift (every 0.3 s)', 4, 0, [(200, [])], 0, 18, 10),
    ('The turn (Left held two frames): the arms trail from the old side, the knees dip, the cloth swings through', 6, 0, [(2, K('l')), (60, U('l'))], 0, 3, 16),
    ('Running, then the stop (Right let go): 16_08\'s braking and the forearms swinging on', 2, 0, [(50, K('r')), (90, U('r'))], 48, 4, 16),
    ('The standing jump: the crouch with the arms back (13_11), the jump, the landing\'s give and rise (16_05)', 4, 0, [(1, K('j')), (90, U('j'))], 0, 4, 18),
    ('A fall of one storey and its landing (16_05\'s give, by the landing\'s speed)', 6, 0, [(1, [['fall', 1]]), (70, [])], 10, 3, 16),
    ('Jump up to a ledge and hang: the body swings under the grip and settles', 6, 7, [(1, K('u')), (110, U('u'))], 0, 5, 18),
]


def scene(pg, sc, rec=True):
    title, start, lc, steps, r0, every, n = sc
    pg.evaluate(ROOM, [start, lc])
    out, i = [], 0
    for fr, ops in steps:
        for j in range(fr):
            want = rec and i >= r0 and (i - r0) % every == 0 and len(out) < n
            o = pg.evaluate(STEPJS, [ops if j == 0 else [], want])
            if o:
                o['lab'] = 'f%d %s' % (i, o['st'])
                out.append(o)
            i += 1
    return out


def rows_of(pg):
    rows = []
    for sc in SCENES:
        it = scene(pg, sc)
        x0 = it[0]['x']
        y0 = it[0]['y']
        W = 46
        for o in it:
            o['cx'] = 16 + min(14, max(-14, 0)) if sc[0].startswith('Running') else 18
            o['dy'] = o['y'] - y0 if not sc[0].startswith('A fall') else o['y'] - it[-1]['y']
            if sc[2]:
                o['ledge'] = 18 + (30 + sc[2]) * 32 - o['x']
        rows.append((sc[0], it, W))
    crawl = pg.evaluate(r"""()=>{const F=__R25,o=[];for(let j=0;j<8;j++)o.push({lab:'crawl '+j+'/8',p:F.mk(F.crawlPose(j/8)),cx:24,dy:0});return o;}""")
    rows.append(('The crawl\'s keys: the face looks along the tunnel (the neck line 0.64 rad, the skull -0.52 at the atlas; 25b 0.80, -0.45)', crawl, 66))
    return rows


def poses(b, tmp):
    S = 4
    got = {}
    errs = []
    for src, tag in ((old_src(tmp), 'before'), (NEW, 'after')):
        pg = b.new_page()
        pg.errs = []
        pg.on('pageerror', lambda e, pg=pg: pg.errs.append(str(e)))
        pg.goto('file://' + exported(src, tmp, tag))
        pg.wait_for_timeout(700)
        pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true)")
        got[tag] = []
        for lab, items, W in rows_of(pg):
            im = b64img(pg.evaluate(DRAW, [items, S, W]))
            got[tag].append((lab, im, W * S, items))
        errs += pg.errs
        pg.close()
    MAXW = 1840
    parts = []
    for r in range(len(got['after'])):
        lab, ia, cw, items = got['after'][r]
        ib = got['before'][r][1]
        if ib.size == ia.size:   # the parts that changed: outlined in red on the after row
            m = ImageChops.difference(ia, ib).convert('L').point(lambda v: 255 if v > 60 else 0).filter(ImageFilter.MinFilter(5)).filter(ImageFilter.MaxFilter(9))   # (sub-pixel shifts of an edge are left out: only what moved ~1 px or more)
            edge = ImageChops.subtract(m, m.filter(ImageFilter.MinFilter(3)))
            ia = ia.copy()
            ia.paste((210, 30, 30), mask=edge)
        for tag, im in (('before', ib), ('after', ia)):
            d = ImageDraw.Draw(im)
            for j, it in enumerate(items):
                d.text((j * cw + 4, 74 * S), it['lab'], fill=INK)
            step = (MAXW // cw) * cw
            n = (im.width + step - 1) // step
            for q in range(n):
                parts.append(('%s: %s%s' % ('round 25b (before)' if tag == 'before' else 'round 25f (after; red: what changed)', lab, '' if n == 1 else ' (%d/%d)' % (q + 1, n)),
                              im.crop((q * step, 0, min(im.width, (q + 1) * step), im.height))))
    H = 60 + sum(im.height + 28 for _, im in parts)
    out = Image.new('RGB', (MAXW + 16, H), BG)
    d = ImageDraw.Draw(out)
    d.text((8, 8), 'Round 25f at 4x, before | after, frames as the game makes them (the state machine in a test room; the pose as drawn, with the cloth\'s wind and '
           'the squash). Owner: "check all his movements for stiffness and make adjustments based on research".', fill=INK)
    d.text((8, 24), 'Frame numbers are game frames (60 a second). Data: CMU mocap 16_05, 16_08, 13_11, 111_03 (mocap.cs.cmu.edu, NSF EIA-0196217).', fill=INK)
    y = 46
    for k, (lab, im) in enumerate(parts):
        d.text((8, y), lab, fill=INK)
        out.paste(im, (8, y + 14))
        y += im.height + 20
        if k % 2 == 1:
            y += 8
    out = out.crop((0, 0, out.width, y))
    out.save(os.path.join(OUT, 'r25f_moves.png'), optimize=True)
    print('r25f_moves.png', out.size, 'errors', errs[:3])


# ---------------- the GIFs ----------------
GSTEP = r'''([ops])=>{const H=__HK,P=H.P,F=window.__R25;for(const [k,on] of ops){if(k==='fall'){P.y-=64;P.fallY=P.y;F.startFall(0);continue;}H.setKey('kb',k,on);}
  H.tick(1);H.banner=null;__P.draw();const g=P.foe&&P.foe.alive?P.foe:null;return [__P.scr(g?(P.x+g.x)/2:P.x,P.y-({crouch:16,hang:30,climb:34,jumpUp:34}[P.state]||26)),P.state];}'''
# a fight: a real floor's first guard, the prince 46 px from him on his floor; the guard is told to fight at once
FIGHT = r'''([n,sd])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS){H.S.hints[id]=1;H.S.learned[id]=1;}H.load(n,sd,false);H.banner=null;
  const g=H.G.find(g=>g.alive&&!g.skel&&!g.cap&&g.state!=='drop');if(!g)return null;for(const o of H.G)if(o!==g){o.alive=false;o.gone=true;}
  const P=H.P;P.x=g.x-46;P.y=g.y;P.fallY=P.y;P.vx=P.vy=0;P.state='stand';P.face=1;P.inv=0;P.hp=P.maxHp=9;P.peace=0;H.cam.snap=true;H.tick(2);return [g.x,g.y,P.state];}'''
TUNNELG = r"""([n,sd])=>{const H=__HK;let L=null,at=null;
  for(let s=sd;s<sd+40&&!at;s++){L=__P.load(n,s);const C=L.cols,lo=(c,r)=>{const f=L.feat[r*C+c];return f&&f.t==='low';};
    for(let r=1;r<L.rows&&!at;r++)for(let c=6;c<C-8;c++)if(lo(c,r)&&lo(c+1,r)&&lo(c+2,r)&&!lo(c-1,r)&&!lo(c-2,r)&&H.solidBelow(c-2,r)&&H.solidBelow(c-1,r)&&H.solidBelow(c,r)&&H.solidBelow(c+1,r)&&H.solidBelow(c+2,r)){at={c,r,s};break;}}
  if(!at)return null;__P.stand(at.c-2,at.r,1);H.setKey('kb','d',true);H.P.state='crouch';H.P.t=0;H.P.ph=0;H.tick(1);return at;}"""
GIF1 = [('room', 4, 0), (45, []), (2, K('l')), (50, U('l')), (2, K('r')), (40, U('r')), (45, K('r')), (60, U('r')), (1, K('j')), (80, U('j')),
        (36, K('d')), (40, U('d'))]
GIF2 = [('room', 6, 7), (1, K('u')), (76, U('u')), (1, K('u')), (52, U('u')), ('fight', 6, 1), (16, []), (1, K('g')), (40, U('g')), (1, K('g')), (44, U('g')),
        ('tunnel', 5, 1), (12, []), (84, K('r')), (1, U('r', 'd'))]


def run_gif(b, tmp, plan, fn, every=4):
    CW, CH = 168, 184
    import egyptr12 as R12
    R12.OUT = OUT
    cols = {}
    for tag, src in (('before', old_src(tmp)), ('after', NEW)):
        for mode in ('torch', 'classic'):
            pg = R12.page(b, exported(src, tmp, tag + mode), mode)
            fr = []
            i = 0
            for st in plan:
                if isinstance(st[0], str):
                    if st[0] == 'room':
                        pg.evaluate(ROOM, [st[1], st[2]])
                    elif st[0] == 'fight':
                        print(tag, mode, 'fight', pg.evaluate(FIGHT, [st[1], st[2]]))
                    else:
                        print(tag, mode, 'tunnel', pg.evaluate(TUNNELG, [st[1], st[2]]))
                    continue
                n, ops = st
                for j in range(n):
                    xy, s = pg.evaluate(GSTEP, [ops if j == 0 else []])
                    if i % every == 0:
                        fr.append(R12.crop(R12.shot(pg), xy, CW, CH))
                    i += 1
            cols[(tag, mode)] = fr
            print(tag, mode, len(fr), pg.errs[:2])
            pg.close()
    order = [('before', 'torch'), ('after', 'torch'), ('before', 'classic'), ('after', 'classic')]
    N = min(len(v) for v in cols.values())
    out = []
    for i in range(N):
        g = Image.new('RGB', (4 * (CW + 2) - 2, CH + 16), (20, 16, 24))
        for j, k in enumerate(order):
            g.paste(cols[k][i], (j * (CW + 2), 16))
            ImageDraw.Draw(g).text((j * (CW + 2) + 4, 2), '%s %s' % ('25b' if k[0] == 'before' else '25f', 'Torchlight' if k[1] == 'torch' else 'Classic'), fill=(240, 230, 210))
        out.append(g.quantize(colors=56, method=Image.MEDIANCUT, dither=Image.NONE))
    R12.gif(out, fn, int(1000 / 60 * every))
    print(fn, N, 'frames', os.path.getsize(os.path.join(OUT, fn)) // 1024, 'KB')


if __name__ == '__main__':
    from playwright.sync_api import sync_playwright
    tmp = tempfile.mkdtemp(prefix='r25f', dir=HERE)
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
            if WHAT in ('moves', 'all'):
                poses(b, tmp)
            if WHAT in ('gif', 'gif1', 'all'):
                run_gif(b, tmp, GIF1, 'r25f_moves1.gif')
            if WHAT in ('gif', 'gif2', 'all'):
                run_gif(b, tmp, GIF2, 'r25f_moves2.gif')
            b.close()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
