# egyptr25b.py [what] [new.html] [old.html]: round 25b's pictures (owner: "when the prince is jumping from a standstill on a lower coridor
# the raises this right arm but his left remains besides him. That is weird"; and of the crawl: "nobody crawls with their head pointing
# down, should be pointing forward"), into egypt_themes/.
#   poses  r25b_poses.png: before | after at 4x, the poses as the game makes them frame by frame (the state machine run in a test room, the
#          pose eased as in play): the low standing leap from the crouch through take-off, flight and landing; the running low leap; the open
#          standing jump (jumpS); the crawl's keys, its start from standing and its stop, the sword held low and the poke; the ceiling's
#          underside drawn as a line where there is one
#   game   r25b_game.png: in the game at the phone's resolution (852x393 CSS px at 2x, crops 1:1), Torchlight and Classic: the low standing
#          leap in mid-flight and the crawl in a tunnel, before | after
# old.html defaults to round 25a's source (git show c8a2c69:dev/hourglass-keep.html). Run from dev/tools.
import base64, io, json, os, subprocess, sys, tempfile, shutil
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
WHAT = a[0] if a else 'all'
NEW = os.path.abspath(a[1] if len(a) > 1 and a[1] else os.path.join(HERE, '..', 'hourglass-keep.html'))
OLD = a[2] if len(a) > 2 and a[2] else None
OUT = os.path.join(HERE, 'egypt_themes')
INK = (20, 16, 24)
BG = (250, 246, 238)
EXPORT = 'window.__R25={skel,PS,mk,lerpPose,crawlPose,figDraw,PAL_HERO,GFX,LEN};'

# a test room as lowceil.py builds it: row R floor ('_'), overhead '#' stone or ' ' open; the prince stands at column C0+start
ROOM = r'''([plan,over,start,kind,N])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS)H.S.hints[id]=1;
  const L=H.load(2,4321,true);H.banner=null;const R=4,C0=30,W=2,E=0,FL=1,set=(c,r,v)=>{L.base[r*L.cols+c]=v;L.feat[r*L.cols+c]=null;};
  for(let c=C0-2;c<=C0+22;c++)for(let r=R-3;r<=R+2;r++)set(c,r,W);
  for(let i=0;i<22;i++){const c=C0+i,p=plan[i],o=over[i]!=='#';set(c,R,FL);if(o){set(c,R-1,E);set(c,R-2,E);}}
  L.dyn=L.dyn.filter(d=>d.r<R-3||d.r>R+2||d.c<C0-2||d.c>C0+22);
  H.clearRooms();const P=H.P;P.inv=1e9;P.x=(C0+start)*32+16;P.y=(R+1)*64-4;P.fallY=P.y;P.state='stand';P.face=1;P.hp=P.hp||3;
  H.cam.snap=true;H.tick(3);const out=[];let jumped=false;if(kind==='run')H.setKey('kb','r',true);
  for(let i=0;i<120&&out.length<N;i++){
    if(!jumped&&(kind==='stand'||(P.state==='run'&&P.x>=(C0+start+3)*32+16))){H.setKey('kb','j',true);H.tick(1);H.setKey('kb','j',false);jumped=true;}
    else H.tick(1);
    if(jumped&&kind==='run'&&P.state==='air')H.setKey('kb','r',false);
    if(jumped)out.push({i,st:P.state,p:Object.assign({},P.pose),dy:P.y+(P.rdy||0)-R*64,yo:P.yo||0});
    if(jumped&&P.state==='stand')break;}
  H.setKey('kb','r',false);return out;}'''
# the crawl: keys, the start from standing (the pose eased toward the crawl at the game's rate 30 a second, from the standing pose), the
# stop, the sword held low, the poke. ceil: the ceiling's underside over the floor (px): 30 in a low tunnel (LOW_H 30 px of stone at the
# top of a 64 px cell, the floor 4 px under its bottom); none while he stands (he ducks before he goes in, stands once out)
CRAWL = r"""()=>{const F=__R25,out=[];const cp=k=>F.mk(F.crawlPose(k));
  for(let j=0;j<8;j++)out.push({lab:'crawl '+j+'/8',p:cp(j/8),ceil:30});
  {const p=cp(0.25);p.hold=0;p.aF=0.55;p.eF=-0.45;p.sw=0.03;out.push({lab:'sword low',p,sw:1,ceil:30});}
  for(const t of [0.05,0.1,0.2]){const p=cp(0.25),k=t<0.1?t/0.1:Math.max(0,1-(t-0.16)/0.18);p.hold=0;p.aF=0.55+0.9*k;p.eF=-0.45+0.45*k;p.sw=0.03;out.push({lab:'poke '+t+' s',p,sw:1,ceil:30});}
  // the start: P.pose eases toward the target by 1-exp(-rate dt) a frame (rate 30): from the standing pose, frames 2, 4, 8; the stop at 24
  for(const n of [2,4,8]){const k=1-Math.exp(-30*n/60);out.push({lab:'start f'+n,p:F.lerpPose(F.PS.stand,cp(0),k)});}
  for(const n of [3,8]){const k=1-Math.exp(-24*n/60);out.push({lab:'stop f'+n,p:F.lerpPose(cp(0.25),F.PS.stand,k)});}
  return out;}"""
DRAW = r"""([items,S,W])=>{const F=window.__R25;F.GFX().hd=true;const Hh=74,n=items.length,cv=document.createElement('canvas');cv.width=W*S*n;cv.height=Hh*S;const c=cv.getContext('2d');
 c.fillStyle='#e8dcc8';c.fillRect(0,0,cv.width,cv.height);
 for(let j=0;j<n;j++){const it=items[j],p=F.mk(it.p),fy=66;c.save();c.scale(S,S);c.translate(j*W,0);c.beginPath();c.rect(0,0,W-0.5,Hh);c.clip();
  c.strokeStyle='rgba(0,0,0,.35)';c.lineWidth=0.3;c.beginPath();c.moveTo(1,fy);c.lineTo(W-1,fy);c.stroke();
  if(it.ceil){c.fillStyle='rgba(120,100,80,.25)';c.fillRect(0,0,W,fy-it.ceil);c.strokeStyle='rgba(150,30,30,.85)';c.lineWidth=0.4;c.beginPath();c.moveTo(0,fy-it.ceil);c.lineTo(W,fy-it.ceil);c.stroke();}
  const y=it.dy!=null?fy-60+it.dy:fy;F.figDraw(c,it.x||18,y,1,p,F.PAL_HERO,{time:0,yo:it.yo||0,sword:!!it.sw,hasSword:true,lt:{dir:1,col:'255,220,170',k:0.6}});c.restore();}
 return cv.toDataURL('image/png');}"""


def b64img(u):
    return Image.open(io.BytesIO(base64.b64decode(u.split(',')[1]))).convert('RGB')


def old_src(tmp):
    if OLD:
        return os.path.abspath(OLD)
    fn = os.path.join(tmp, '_r25a.html')
    open(fn, 'w', encoding='utf-8').write(subprocess.run(['git', 'show', 'c8a2c69:dev/hourglass-keep.html'], cwd=HERE, capture_output=True, text=True, check=True).stdout)
    return fn


def page(b, src, tmp, tag):
    s = open(src, encoding='utf-8').read()
    i = s.find('window.__HK={')
    fn = os.path.join(tmp, '_r25b_%s.html' % tag)
    open(fn, 'w', encoding='utf-8').write(s[:i] + EXPORT + s[i:])
    pg = b.new_page()
    pg.errs = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e)))
    pg.goto('file://' + fn)
    pg.wait_for_timeout(700)
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true)")
    return pg


def rows_of(pg):
    """[(label, items, cell width)] as the game makes them"""
    out = []
    st = lambda L: [dict(x, lab='f%d %s' % (x['i'], x['st']), ceil=60) for x in L]
    low = pg.evaluate(ROOM, ['_' * 22, '#' * 22, 6, 'stand', 40])
    out.append(('The low standing leap under stone at his height (jumpPrep: crouch; air: jumpLowS, eased toward land as he falls; every 2nd game frame)', st(low[0:34:2]), 46))
    lr = [x for x in pg.evaluate(ROOM, ['_' * 22, '#' * 22, 3, 'run', 40]) if x['st'] in ('air', 'land')]
    out.append(('The running low leap (jumpLow, unchanged: both arms forward already)', st(lr[0:26:2]), 46))
    op = pg.evaluate(ROOM, ['_' * 22, ' ' * 22, 6, 'stand', 40])
    out.append(('The standing jump in an open room (jumpS)', [dict(x, lab='f%d %s' % (x['i'], x['st'])) for x in op[0:34:2]], 46))
    cr = [dict(x, x=24) for x in pg.evaluate(CRAWL)]
    out.append(('The crawl in a low tunnel (30 px of headroom, red): its keys, the sword held low, the poke; then going in and coming out (no ceiling)', cr, 66))
    return out


def poses(b, tmp):
    S = 4
    got = {}
    errs = []
    for src, tag in ((old_src(tmp), 'before'), (NEW, 'after')):
        pg = page(b, src, tmp, tag)
        got[tag] = []
        for lab, items, W in rows_of(pg):
            im = b64img(pg.evaluate(DRAW, [items, S, W]))
            im.cw = W * S
            d = ImageDraw.Draw(im)
            for j, it in enumerate(items):
                d.text((j * W * S + 4, 69 * S), it['lab'], fill=INK)
            got[tag].append((lab, im))
        errs += pg.errs
        pg.close()
    MAXW = 1840
    parts = []
    for r in range(len(got['after'])):
        lab = got['after'][r][0]
        for tag in ('before', 'after'):
            im = got[tag][r][1]
            cw = got[tag][r][1].cw
            step = (MAXW // cw) * cw            # (whole cells a line)
            n = (im.width + step - 1) // step
            for q in range(n):
                parts.append(('%s: %s%s' % ('round 25a (before)' if tag == 'before' else 'round 25b (after)', lab, '' if n == 1 else ' (%d/%d)' % (q + 1, n)),
                              im.crop((q * step, 0, min(im.width, (q + 1) * step), im.height))))
    H = 60 + sum(im.height + 28 for _, im in parts)
    out = Image.new('RGB', (MAXW + 16, H), BG)
    d = ImageDraw.Draw(out)
    d.text((8, 8), 'Round 25b at 4x, before | after, frames as the game makes them. Owner: "when the prince is jumping from a standstill on a lower corridor ... raises '
           'this right arm but his left remains besides him"; "nobody crawls with their head pointing down, should be pointing forward".', fill=INK)
    d.text((8, 24), 'Red: the ceiling\'s underside (60 px over the floor in a storey with stone overhead, 30 in a low tunnel). Data: CMU mocap 13_11, 49_04, 16_05, 111_03 '
           '(mocap.cs.cmu.edu, NSF EIA-0196217).', fill=INK)
    y = 46
    for k, (lab, im) in enumerate(parts):
        d.text((8, y), lab, fill=INK)
        out.paste(im, (8, y + 14))
        y += im.height + 20
        if k % 2 == 1:
            y += 8
    out = out.crop((0, 0, out.width, y))
    out.save(os.path.join(OUT, 'r25b_poses.png'), optimize=True)
    print('r25b_poses.png', out.size, 'errors', errs[:3])


# in the game: the low standing leap k frames after the jump (lowceil.py's room), and the crawl in a real tunnel of a generated floor
LEAP = ROOM.replace("if(jumped)out.push({i,st:P.state,p:Object.assign({},P.pose),dy:P.y+(P.rdy||0)-R*64,yo:P.yo||0});", "if(jumped&&i>=N){H.banner=null;__P.draw();return __P.scr(P.x,P.y-30);}")
TUNNEL = r"""([n,sd,ph])=>{const H=__HK;let L=null,at=null;
  for(let s=sd;s<sd+40&&!at;s++){L=__P.load(n,s);const C=L.cols,lo=(c,r)=>{const f=L.feat[r*C+c];return f&&f.t==='low';};
    for(let r=1;r<L.rows&&!at;r++)for(let c=4;c<C-8;c++)if(lo(c,r)&&lo(c+1,r)&&lo(c+2,r)&&lo(c+3,r)&&H.solidBelow(c+1,r)&&H.solidBelow(c+2,r)){at={c:c+2,r,s};break;}}
  if(!at)return null;const P=H.P;__P.stand(at.c,at.r,1);P.state='crouch';P.ph=ph;P.lowSword=false;for(let i=0;i<40;i++){H.tick(1);P.ph=ph;}H.banner=null;__P.draw();
  return {xy:__P.scr(P.x,P.y-14),at,st:P.state};}"""


def game(b, tmp):
    import egyptr12 as R12
    cols = []
    for src, tag in ((old_src(tmp), 'before'), (NEW, 'after')):
        for mode in ('torch', 'classic'):
            pg = R12.page(b, src, mode)
            xy = pg.evaluate(LEAP, ['_' * 22, '#' * 22, 6, 'stand', 14])
            a = R12.crop(R12.shot(pg), xy, 300, 260)
            t = pg.evaluate(TUNNEL, [5, 1, 0.3])
            c = R12.crop(R12.shot(pg), t['xy'], 300, 200)
            print(tag, mode, t['at'], t['st'], pg.errs[:2])
            cols.append(('%s, %s' % ('round 25a' if tag == 'before' else 'round 25b', 'Torchlight' if mode == 'torch' else 'Classic'), a, c))
            pg.close()
    order = [cols[0], cols[2], cols[1], cols[3]]
    W = 300
    out = Image.new('RGB', (4 * (W + 6) + 6, 40 + 260 + 200 + 40), (20, 16, 24))
    d = ImageDraw.Draw(out)
    d.text((6, 4), 'In the game at the phone\'s resolution (852x393 CSS px at 2x, crops 1:1): the low standing leap 14 frames after the jump; the crawl in a tunnel', fill=(240, 230, 210))
    for j, (lab, a, c) in enumerate(order):
        x = 6 + j * (W + 6)
        d.text((x, 22), lab, fill=(240, 230, 210))
        out.paste(a, (x, 38))
        out.paste(c, (x, 38 + 260 + 6))
    out = out.crop((0, 0, out.width, 38 + 260 + 6 + 200 + 6))
    out.save(os.path.join(OUT, 'r25b_game.png'), optimize=True)
    print('r25b_game.png', out.size)


if __name__ == '__main__':
    from playwright.sync_api import sync_playwright
    tmp = tempfile.mkdtemp(prefix='r25b', dir=HERE)
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
            if WHAT in ('poses', 'all'):
                poses(b, tmp)
            if WHAT in ('game', 'all'):
                game(b, tmp)
            b.close()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
