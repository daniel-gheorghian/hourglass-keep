# egyptr19.py [new.html] [old.html] [outdir]: round 19's pictures for egypt_themes.html, before (old.html, default ../_r18c.html, made
# with git show 8c1bf18:dev/hourglass-keep.html) and after, in the game at the phone's resolution (crops of the 1704 px canvas, i.e. 2x
# the game's pixels; the 2x rows enlarged again, smoothed):
#  r19_lamps.png  lamps the old placement set against a step's front face, and the same places now (Torchlight, Classic)
#  r19_hang.png   jumping up to, hanging from, climbing onto and dropping from a ledge on a wall's near side, two themes, both modes
#  r19_hang.mp4   the same played (8 s, 30 fps), Torchlight, before (left) and after (right), a lamp set beside the step as in the
#                 owner's picture (the figure's shadow on the face's left edge, and the ghost drawn through the wall while he moved)
#  r19_sand.png   the sand lift's slab at the top, part way down and at the bottom, three themes, both modes
#  r19_pose.png   the arms-up poses (hang, reach, fall, slide, the swing both ways) drawn alone at 6x, and the swing in the game
# ONLY=pose (env) remakes only r19_pose.png. Writes r19.json (places, errors). Needs ffmpeg (FFMPEG, default /usr/local/bin/ffmpeg). Run from dev/tools.
import base64, io, json, os, shutil, subprocess, sys, tempfile
from playwright.sync_api import sync_playwright
from PIL import Image
import egyptr12 as R12
import egyptr18 as E
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
NEW = os.path.abspath(a[0] if len(a) > 0 else os.path.join(HERE, '..', 'hourglass-keep.html'))
OLD = os.path.abspath(a[1] if len(a) > 1 else os.path.join(HERE, '..', '_r18c.html'))
OUT = a[2] if len(a) > 2 else os.path.join(HERE, 'egypt_themes')
R12.OUT = OUT
FF = os.environ.get('FFMPEG', '/usr/local/bin/ffmpeg')
FPS = 30
TAG = {'old': 'before (18c)', 'new': 'after (19)'}
HANGS = [(5, 782), (9, 782), (13, 782), (17, 801), (6, 801)]   # tried in turn for two themes with a near-face ledge on the bot's way
# a lamp the old placement put right against a WALL beside it (the step's front face), in floors lo..hi
LAMPW = r"""([lo,hi])=>{const H=__HK;for(let n=lo;n<=hi;n++)for(const sd of [1,2,3]){const L=__P.load(n,sd),C=L.cols;
  for(const t of L.torches){if(t.broken)continue;if(L.base[t.r*C+t.c+1]===2&&L.base[t.r*C+t.c-1]!==2&&L.base[t.r*C+t.c-2]!==2&&L.base[t.r*C+t.c-3]!==2)return {n,sd,c:t.c,r:t.r,name:H.themeName(n)};}}return null;}"""
LAMPS = r"""([q])=>{const H=__HK,L=__P.load(q.n,q.sd);__P.stand(q.c-3,q.r,1);__P.draw();const near=L.torches.filter(t=>!t.broken&&t.r===q.r&&Math.abs(t.c-q.c)<=8).map(t=>t.c);
  return {xy:__P.scr(q.c*32+8,(q.r+1)*64-40),near};}"""
STOP = r"""([n,sd,lamp])=>{const r=runBot(n,sd,{fight:false,stop:H=>{const p=H.P;if(p.state==='jumpUp'&&p.cs&&p.cs.ledge&&p.cs.ledge.s<0){const b=H.L.base[(p.cs.ledge.r+1)*H.L.cols+p.cs.ledge.c];return b===2;}return false;}});
  const H=__HK;if(H.P.state!=='jumpUp')return null;for(const k of ['l','r','u','d','j','g'])H.setKey('kb',k,false);H.I.buf={};const lg=window.__LG=H.P.cs.ledge;
  if(lamp){H.L.torches.push({c:lg.c-1,r:lg.r+1});H.clearRooms();}return {name:H.themeName(n),c:lg.c,r:lg.r};}"""
STEP = r"""([k,key])=>{const H=__HK;if(key)H.setKey('kb',key,true);H.tick(k);if(key)H.setKey('kb',key,false);H.banner=null;__P.draw();const lg=window.__LG;return [__P.scr(lg.xe-4,lg.ys+6),H.P.state];}"""
SAND = r"""([n,sd,fr])=>{const H=__HK,L=__P.load(n,sd),f=L.lifts.find(q=>q.sand);__P.stand(f.sc+2,fr===1?f.rB:f.rT,1);const P=H.P;
  const set=()=>{f.y=f.yT+(f.yB-f.yT)*fr;if(fr>0){f.s=fr<1?1:2;f.tm=9;}P.x=f.sc*32+16;P.y=f.y;P.state='stand';P.face=1;};set();H.cam.snap=true;H.tick(1);set();__P.draw();
  return {xy:__P.scr(f.sc*32+16,f.y-2),name:H.themeName(n)};}"""
SANDF = r"""()=>{const H=__HK,out=[],seen=new Set();for(let n=3;n<=60&&out.length<3;n++)for(const sd of [1,2,3,4]){const L=__P.load(n,sd);if(L.lifts.some(q=>q.sand)&&!seen.has(L.theme.style)){seen.add(L.theme.style);out.push([n,sd]);break;}}return out;}"""
FIG = r"""([poses,Z])=>{const H=__HK,c=document.createElement('canvas'),W=46,Hh=104;c.width=W*Z*poses.length;c.height=Hh*Z;const g=c.getContext('2d');g.fillStyle='#3a332c';g.fillRect(0,0,c.width,c.height);
  poses.forEach((q,i)=>{g.save();g.setTransform(Z,0,0,Z,i*W*Z,0);H.figDraw(g,23,100,1,q,H.PAL_HERO,{time:0,hasSword:true,lt:{dir:-1,col:'255,205,150',k:0.6}});g.restore();});return c.toDataURL();}"""


def up(im, k=2):
    return im.resize((im.width * k, im.height * k), Image.LANCZOS)


def video(frames, fn):
    d = tempfile.mkdtemp()
    for i, f in enumerate(frames):
        f.save(os.path.join(d, '%04d.png' % i))
    subprocess.run([FF, '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(d, '%04d.png'), '-vf', 'pad=ceil(iw/2)*2:ceil(ih/2)*2',
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-movflags', '+faststart', os.path.join(OUT, fn)], check=True)
    shutil.rmtree(d)


# the stills: jump up, hang (just caught, then still), climbing, and (a second run) dropping off
SEQ = [(0, None, 'jumping up'), (4, None, 'hanging'), (30, None, 'hanging still'), (1, 'u', 'climbing'), (5, None, 'climbing')]
DROP = [(30, None, 'hanging still'), (1, 'd', 'dropping'), (4, None, 'dropping')]


def hang_stills(pg, n, sd, lamp, seq):
    q = pg.evaluate(STOP, [n, sd, lamp]); out = []
    for k, key, lab in seq:
        xy, st = pg.evaluate(STEP, [k, key])
        out.append((R12.shot(pg), xy, lab))
    return q, out


def hang_video(pg, n, sd, tag):
    q = pg.evaluate(STOP, [n, sd, True]); fr = []
    for i in range(FPS * 4):
        xy, st = pg.evaluate(STEP, [1, 'u' if i == 75 else None])
        fr.append(R12.label(R12.crop(R12.shot(pg), xy, 300, 300), '%s, %s, %s' % (q['name'], st, tag)))
    q = pg.evaluate(STOP, [n, sd, True])
    for i in range(FPS * 4):
        xy, st = pg.evaluate(STEP, [1, 'd' if i == 75 else None])
        fr.append(R12.label(R12.crop(R12.shot(pg), xy, 300, 300), '%s, %s, %s' % (q['name'], st, tag)))
    return fr


if __name__ == '__main__':
    J = {'errors': []}
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
        P = {(v, m): R12.page(b, src, m) for v, src in (('old', OLD), ('new', NEW)) for m in ('torch', 'classic')}
        ONLY = os.environ.get('ONLY')
        if not ONLY:  # ---- the lamps
            t1, t2 = [], []
            J['lamps'] = [P[('old', 'torch')].evaluate(LAMPW, [lo, lo + 3]) for lo in (5, 9)]
            for q in J['lamps']:
                for m in ('torch', 'classic'):
                    for v in ('old', 'new'):
                        r = P[(v, m)].evaluate(LAMPS, [q]); im = R12.shot(P[(v, m)])
                        t1.append(R12.label(R12.crop(im, r['xy'], 420, 300), '%s, floor %d, %s, %s' % (q['name'], q['n'], m, TAG[v])))
                        t2.append(R12.label(up(R12.crop(im, r['xy'], 210, 150)), '2x, %s, %s' % (m, TAG[v])))
            R12.stack([R12.grid(t1, 4), R12.grid(t2, 4)]).save(os.path.join(OUT, 'r19_lamps.png'))
            # ---- the ledge: two themes
            places = []
            for n, sd in HANGS:
                q = P[('new', 'torch')].evaluate(STOP, [n, sd, False])
                if q and all(q['name'] != x[2] for x in places):
                    places.append((n, sd, q['name']))
                if len(places) == 2:
                    break
            J['hangs'] = places
            rows = []
            for n, sd, name in places:
                for m in ('torch', 'classic'):
                    for v in ('old', 'new'):
                        q, s1 = hang_stills(P[(v, m)], n, sd, True, SEQ)
                        q, s2 = hang_stills(P[(v, m)], n, sd, True, DROP)
                        row = [R12.label(R12.crop(im, xy, 240, 300), '%s, %s, %s' % (lab, m, TAG[v])) for im, xy, lab in s1 + s2[1:]]
                        rows.append(R12.grid(row, len(row)))
                        if m == 'torch':
                            im, xy, lab = s1[2]
                            rows.append(R12.label(up(R12.crop(im, xy, 160, 150)), '2x, %s, %s, %s' % (name, lab, TAG[v])))
            R12.stack(rows).save(os.path.join(OUT, 'r19_hang.png'))
            vids = [[hang_video(P[(v, 'torch')], n, sd, TAG[v]) for v in ('old', 'new')] for n, sd, name in places]
            video([R12.grid([c[k] for r in vids for c in r], 2) for k in range(FPS * 8)], 'r19_hang.mp4')
            # ---- the sand lift
            S = P[('new', 'torch')].evaluate(SANDF); J['sand'] = S; t1, t2 = [], []
            for n, sd in S:
                for m in ('torch', 'classic'):
                    for v in ('old', 'new'):
                        for fr in (0, 0.06, 0.5, 1):
                            r = P[(v, m)].evaluate(SAND, [n, sd, fr]); im = R12.shot(P[(v, m)])
                            t1.append(R12.label(R12.crop(im, [r['xy'][0], r['xy'][1] + 12], 240, 200), '%s, %s, %s, %s' % (r['name'][:22], {0: 'top', 0.06: 'leaving', 0.5: 'riding', 1: 'bottom'}[fr], m, TAG[v])))
                            if m == 'torch' and fr in (0, 1):
                                t2.append(R12.label(up(R12.crop(im, [r['xy'][0], r['xy'][1] + 12], 120, 100)), '2x, %s, %s' % ({0: 'top', 1: 'bottom'}[fr], TAG[v])))
            R12.stack([R12.grid(t1, 8), R12.grid(t2, 8)]).save(os.path.join(OUT, 'r19_sand.png'))
        # ---- the arms-up poses
        rows = []
        for v in ('old', 'new'):
            pg = P[(v, 'classic')]
            poses = pg.evaluate('()=>["hang","reach","pull","fall","slide"].map(k=>__HK.mk(__HK.PS[k]))')
            for th in (0.25, -0.4):
                pg.evaluate(E.SWING, [6, 0.85, th]); poses.append(pg.evaluate('()=>__HK.mk(__HK.P.pose)'))
            u = pg.evaluate(FIG, [poses, 6])
            rows.append(R12.label(Image.open(io.BytesIO(base64.b64decode(u.split(',')[1]))).convert('RGB'), 'hang, reach, pull, fall, slide, swing back, swing forward: %s (6x)' % TAG[v]))
        sw = []
        for m in ('torch', 'classic'):
            for v in ('old', 'new'):
                q = P[(v, m)].evaluate(E.SWING, [17, 0.85, 0.25])
                sw.append(R12.label(R12.crop(R12.shot(P[(v, m)]), P[(v, m)].evaluate(E.AT, [q['fx'], q['fy'] + 26]), 240, 300), '%s, swing, %s, %s' % (q['name'][:20], m, TAG[v])))
        rows.append(up(R12.grid(sw, 4)))
        R12.stack(rows).save(os.path.join(OUT, 'r19_pose.png'))
        for pg in P.values():
            J['errors'] += pg.errs
        if not ONLY:
            json.dump(J, open(os.path.join(OUT, 'r19.json'), 'w'), indent=1)
        print(json.dumps(J)[:600])
        b.close()
