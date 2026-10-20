# egyptr22.py [new.html] [old.html] [outdir]: round 22's pictures for egypt_themes.html, the prince's back in profile, before (old.html, default
# the v69 release, hk_v69_release.html here or in the main checkout's dev/tools) and after:
#  r22_guide.png  the standing figure at 10x, before | after: lit from his back, from his front, and the silhouette with the guides of the
#                 research: the wall line (back of the skull, shoulder blades and seat touch a wall: Mayo Clinic's wall test), the plumb line
#                 (ear, shoulder joint, hip), the lumbar gap (a flat hand, about 1.5 px at this scale), C7 about 2 px in front of the wall
#                 line, and the back's edge measured row by row (before red, after green, both on each); then the same silhouettes in motion
#                 (run 0, 0.5, step, garde, lunge, crouch, hang)
#  r22_poses.png  every pose at 4x, before row over after row, and a robber
#  r22_game.png   the prince standing in the game, crops of the 1704 px canvas: Torchlight at GLP.rs 1 and 0.5 and Classic, facing both ways
#                 (floors 7 and 14); then 3x enlargements of the Torchlight crops
# Writes r22.json (back-edge measures, page errors). Run from dev/tools.
import base64, io, json, os, sys
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw
import egyptr12 as R12
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
NEW = os.path.abspath(a[0] if len(a) > 0 else os.path.join(HERE, '..', 'hourglass-keep.html'))
_old = os.path.join(HERE, 'hk_v69_release.html')
if not os.path.exists(_old):
    _old = os.path.join(HERE, '..', '..', '..', '..', '..', 'dev', 'tools', 'hk_v69_release.html')  # (from a worktree: the main checkout's)
OLD = os.path.abspath(a[1] if len(a) > 1 and a[1] else _old)
OUT = a[2] if len(a) > 2 else os.path.join(HERE, 'egypt_themes')
R12.OUT = OUT
TAG = {'old': 'before (v69)', 'new': 'after (22)'}
# the figure drawn alone on a canvas S times its size, facing right; returns the picture and, in canvas px, the points the guides need
FIG = r'''([p,S,W,Hh,x,y,dir,mono,pk])=>{const H=__HK;p=Object.assign(H.mk({}),p);const pal=pk==='rob'?H.guardPal({tier:1}):H.PAL_HERO;
 const cv=document.createElement('canvas');cv.width=W*S;cv.height=Hh*S;const c=cv.getContext('2d');c.fillStyle=mono?'#e8dcc8':'#5a4434';c.fillRect(0,0,cv.width,cv.height);c.scale(S,S);
 H.figDraw(c,x,y,1,p,pal,{sword:!!p._sw,hasSword:true,time:0,mono:mono||undefined,lt:{dir,col:'255,220,170',k:0.6}});
 return cv.toDataURL('image/png');}'''
GEO = r'''([p,x,y])=>{const H=__HK;p=Object.assign(H.mk({}),p);const L={th:12,sh:12,to:15,nk:2.5,hd:4.6};
 // (the skeleton as skel() builds it, enough for the guides: hips, shoulder joint, head centre and its axis)
 const sh=[L.to*Math.sin(p.lean),-L.to*Math.cos(p.lean)],ha=p.lean+p.head,hd=[sh[0]+(L.nk+L.hd)*Math.sin(ha),sh[1]-(L.nk+L.hd)*Math.cos(ha)];
 const kF=[L.th*Math.sin(p.hF),L.th*Math.cos(p.hF)],fF=[kF[0]+L.sh*Math.sin(p.hF-p.kF),kF[1]+L.sh*Math.cos(p.hF-p.kF)],kB=[L.th*Math.sin(p.hB),L.th*Math.cos(p.hB)],fB=[kB[0]+L.sh*Math.sin(p.hB-p.kB),kB[1]+L.sh*Math.cos(p.hB-p.kB)];
 const low=Math.max(fF[1],fB[1]),hipH=low+(p.hy-low)*p.air,oy=y-hipH,r=L.hd,hx=Math.sin(ha),hy=-Math.cos(ha),hnx=-hy,hny=hx;
 const P=q=>[x+q[0],oy+q[1]];return {hip:P([0,0]),sh:P(sh),hd:P(hd),ear:P([hd[0]-hnx*r*0.2-hx*r*0.1,hd[1]-hny*r*0.2-hy*r*0.1])};}'''
POSES = r'''()=>{const H=__HK,o={};for(const k of ['stand','step','turn','crouch','jumpR','jumpS','hang','pull','press','garde','lunge','parry','windup','hurt','dead'])o[k]=Object.assign({},H.PS[k]);
 for(const ph of [0,0.25,0.5,0.75])o['run '+ph]=Object.assign({},H.RP(ph));o.drink=Object.assign({},H.drinkFrame(0.7).p);o.garde._sw=1;o.lunge._sw=1;o.parry._sw=1;o.windup._sw=1;return o;}'''
STAND = r'''([n,sd,face,rs])=>{const H=__HK;const L=__P.load(n,sd);let pc=-1,r=-1;
 for(let rr=1;rr<L.rows&&pc<0;rr++)for(let c=12;c<L.cols-12;c++){let ok=true;for(let k=-3;k<=4;k++)if(!H.solidBelow(c+k,rr)||L.feat[rr*L.cols+c+k])ok=false;if(ok){pc=c;r=rr;break;}}
 __P.stand(pc,r,face);for(let i=0;i<40;i++){H.tick(1);H.P.x=pc*32+16;H.P.state='stand';}if(H.GLP)H.GLP.rs=rs;__P.draw();return __P.scr(pc*32+16,(r+1)*64-34);}'''
S = 10


def dataimg(d):
    return Image.open(io.BytesIO(base64.b64decode(d.split(',')[1]))).convert('RGB')


def back_edge(im):
    # row by row, the leftmost pixel of the silhouette (dark on the light ground), in canvas px; None where the row is empty
    px = im.load(); out = []
    for y in range(im.height):
        e = None
        for x in range(im.width):
            if sum(px[x, y]) < 200:
                e = x; break
        out.append(e)
    return out


def guides(im, g, edges, upto):
    # the research's guides over a silhouette, in canvas px (S per figure px)
    d = ImageDraw.Draw(im)
    sk = [x * S for x in g['hd']]
    wall = min(e for e in edges['new'][:int(g['sh'][1] * S)] if e is not None)  # (the back of the skull: the leftmost point above the shoulders)
    d.line([(wall, 0), (wall, im.height)], fill=(40, 110, 220), width=2)                       # the wall line
    d.text((wall + 4, 4), 'wall line', fill=(40, 110, 220))
    ex = g['ear'][0] * S
    d.line([(ex, 0), (ex, im.height)], fill=(200, 140, 20), width=1)                           # the plumb line through the ear
    d.ellipse([ex - 4, g['ear'][1] * S - 4, ex + 4, g['ear'][1] * S + 4], outline=(200, 140, 20), width=2)
    for k in ('sh', 'hip'):
        q = g[k]; d.ellipse([q[0] * S - 5, q[1] * S - 5, q[0] * S + 5, q[1] * S + 5], outline=(200, 140, 20), width=2)
    d.text((ex + 4, im.height - 14), 'plumb: ear, shoulder, hip', fill=(200, 140, 20))
    d.line([(wall + 2.0 * S, g['sh'][1] * S - 2.8 * S), (wall + 2.0 * S, g['sh'][1] * S - 1.6 * S)], fill=(150, 60, 170), width=3)  # C7 ~2 px in front
    d.text((wall + 2.2 * S, g['sh'][1] * S - 2.6 * S), 'C7', fill=(150, 60, 170))
    wy = (g['hip'][1] - 4.5) * S
    d.line([(wall, wy), (wall + 1.5 * S, wy)], fill=(150, 60, 170), width=3)                   # the lumbar gap: a flat hand
    d.text((wall + 1.6 * S, wy - 6), 'hand gap', fill=(150, 60, 170))
    for v, col in (('old', (220, 40, 40)), ('new', (30, 160, 60))):
        pts = [(e, y) for y, e in enumerate(edges[v]) if e is not None and y < upto]
        for i in range(1, len(pts)):
            if abs(pts[i][0] - pts[i - 1][0]) < 3 * S:
                d.line([pts[i - 1], pts[i]], fill=col, width=2)
    return im


if __name__ == '__main__':
    J = {'errors': [], 'edges': {}}
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
        P = {(v, m): R12.page(b, src, m) for v, src in (('old', OLD), ('new', NEW)) for m in ('torch', 'classic')}
        pn = P[('new', 'classic')]
        poses = pn.evaluate(POSES)
        # ---- 1. the guide sheet
        W, Hh, X, Y = 24, 58, 12, 55
        rows = []
        t = []
        g = pn.evaluate(GEO, [poses['stand'], X, Y])
        edges = {v: back_edge(dataimg(P[(v, 'classic')].evaluate(FIG, [poses['stand'], S, W, Hh, X, Y, 1, '#120c18', 'hero']))) for v in ('old', 'new')}
        J['edges']['stand'] = {v: [e / S if e is not None else None for e in edges[v][::S]] for v in edges}
        for v in ('old', 'new'):
            for dr in (-1, 1):
                t.append(R12.label(dataimg(P[(v, 'classic')].evaluate(FIG, [poses['stand'], S, W, Hh, X, Y, dr, None, 'hero'])), '%s, lit from his %s' % (TAG[v], 'back' if dr < 0 else 'front')))
            sil = dataimg(P[(v, 'classic')].evaluate(FIG, [poses['stand'], S, W, Hh, X, Y, 1, '#120c18', 'hero']))
            t.append(R12.label(guides(sil, g, edges, int(g['hip'][1] * S + 40)), '%s: silhouette, guides; back edge before red, after green' % TAG[v][:6], (4, Hh * S - 30)))
        rows.append(R12.grid(t, 6))
        t = []
        S2 = 6
        for k in ('run 0', 'run 0.5', 'step', 'turn', 'garde', 'lunge', 'crouch', 'jumpR', 'hang', 'pull'):
            q = poses[k]
            yk = 12 - pn.evaluate(GEO, [q, 15, 0])['hd'][1] + (4 if k == 'hang' else 0)  # (the head's top near the tile's top; the hang's hands above it)
            ims = {v: dataimg(P[(v, 'classic')].evaluate(FIG, [q, S2, 34, 40, 15, yk, 1, '#120c18', 'hero'])) for v in ('old', 'new')}
            # the two silhouettes laid over each other: both black, only before red, only after green
            o, nn = ims['old'].load(), ims['new'].load(); im = Image.new('RGB', ims['old'].size, (232, 220, 200)); px = im.load()
            for yy in range(im.height):
                for xx in range(im.width):
                    a0, a1 = sum(o[xx, yy]) < 200, sum(nn[xx, yy]) < 200
                    px[xx, yy] = (18, 12, 24) if a0 and a1 else (220, 40, 40) if a0 else (30, 160, 60) if a1 else (232, 220, 200)
            ImageDraw.Draw(im).text((4, 3), k + ' (red: before only, green: after only)', fill=(20, 16, 24))
            t.append(im)
        rows.append(R12.grid(t, 6))
        R12.stack(rows).save(os.path.join(OUT, 'r22_guide.png'))
        print('guide done', flush=True)
        # ---- 2. every pose at 4x
        rows = []
        for v in ('old', 'new'):
            t = []
            for k, q in poses.items():
                air = k in ('hang', 'pull', 'press')
                t.append(R12.label(dataimg(P[(v, 'classic')].evaluate(FIG, [q, 4, 44, 72, 36 if k == 'dead' else 20, 60 if air else 68, -1, None, 'hero'])), k))
            t.append(R12.label(dataimg(P[(v, 'classic')].evaluate(FIG, [poses['stand'], 4, 44, 72, 20, 68, -1, None, 'rob'])), 'robber'))
            rows.append(R12.label(R12.grid(t, 11), TAG[v], (4, 276)))
        R12.stack(rows).save(os.path.join(OUT, 'r22_poses.png'))
        print('poses done', flush=True)
        # ---- 3. in the game
        t, big = [], []
        for n, face in ((7, 1), (14, -1)):
            for m, rs in (('torch', 1), ('torch', 0.5), ('classic', 1)):
                for v in ('old', 'new'):
                    xy = P[(v, m)].evaluate(STAND, [n, 1, face, rs])
                    im = R12.shot(P[(v, m)])
                    t.append(R12.label(R12.crop(im, xy, 150, 200), '%s, %s%s' % (TAG[v][:6], m, ' .5' if rs < 1 else '')))
                    if m == 'torch':
                        big.append(R12.label(R12.crop(im, (xy[0], xy[1] - 24), 70, 90).resize((210, 270), Image.LANCZOS), '%s %s 3x' % (TAG[v][:6], 'rs .5' if rs < 1 else 'rs 1')))
        R12.stack([R12.grid(t, 12), R12.grid(big, 8)]).save(os.path.join(OUT, 'r22_game.png'))
        print('game done', flush=True)
        for (v, m), pg in P.items():
            J['errors'] += ['%s %s: %s' % (v, m, e) for e in pg.errs]
    json.dump(J, open(os.path.join(OUT, 'r22.json'), 'w'), indent=1)
    print('errors', J['errors'][:5])
