# egyptr25a.py [what] [new.html] [old.html]: round 25a's numbers and pictures (owner: "The prince is somewhat stiff when running. Humans are
# somewhat flexible. Research a bit how games are handling that in their characters."), into egypt_themes/.
#   measure  r25a.json: what the run clips carry that round 23's side view threw away (09_01 f42-130, the game's cycle; 09_02, 09_03, 16_35,
#            16_36 for comparison, one stride each found by autocorrelation): trunk lean, the thorax's and the pelvis's pitch and the bend
#            between them, the thorax's yaw against the pelvis's (counter-rotation), each shoulder joint and hip joint fore and aft and the
#            pelvis's drop in px at the game's scale, the foot's pitch, the wrist, the elbow, the head's pitch in the world; and what v71 drew
#   keys     r25a_run.png: the 16 run keys at 4x, v71 | round 25a, with the pelvis (green) and chest (orange) lines and the shoulder joints
#            (near red, far blue) on keys 0, 4, 8, 12, and the clip's stick figure for the same phases at the same scale
#   gif      r25a_run.gif: running in the game at the phone's resolution (852x393 CSS px at 2x), Torchlight and Classic, v71 | round 25a,
#            every game frame (60 a second) shown at 40 ms (0.4 times speed)
# old.html defaults to the v71 release (hk_v71_release.html here or in the main checkout's dev/tools). Run from dev/tools.
# CMU mocap: the data used in this project was obtained from mocap.cs.cmu.edu (created with funding from NSF EIA-0196217).
import base64, io, json, math, os, sys, tempfile, shutil
import numpy as np
from PIL import Image, ImageDraw
import mocap

HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
WHAT = a[0] if a else 'all'
NEW = os.path.abspath(a[1] if len(a) > 1 and a[1] else os.path.join(HERE, '..', 'hourglass-keep.html'))
_old = os.path.join(HERE, 'hk_v71_release.html')
if not os.path.exists(_old):
    _old = os.path.join(HERE, '..', '..', '..', '..', '..', 'dev', 'tools', 'hk_v71_release.html')  # (from a worktree: the main checkout's)
OLD = os.path.abspath(a[2] if len(a) > 2 and a[2] else _old)
OUT = os.path.join(HERE, 'egypt_themes')
INK = (20, 16, 24)
BG = (250, 246, 238)
D = math.degrees
UP = np.array([0, 1.0, 0])
PXM = json.load(open(os.path.join(HERE, 'r23body.json')))['info']['leg_scale'] * 100   # px a metre at the game's scale (legs)
CLIPS = [('09_01', 42, 130, 'the game\'s run (subject 9)'), ('09_02', 0, 129, 'run (subject 9)'), ('09_03', 0, 127, 'run (subject 9)'),
         ('16_35', 0, 161, 'run/jog (subject 16)'), ('16_36', 0, 188, 'run/jog (subject 16)')]


# ---------------- measure ----------------
def series(name, a0, b0):
    c = mocap.Clip(name)
    b0 = min(b0, len(c.frames) - 1)
    fwd = mocap.facing(c.sk, c.frames, a0, b0)
    lat = np.cross(UP, fwd)
    out = []
    for i in range(a0, b0 + 1):
        J = mocap.fk(c.sk, c.frames[i])
        R = J['_R']
        Q = mocap.project(mocap.landmarks(J), fwd)
        p = mocap.params(Q, 'r')
        pitch = lambda R3: D(math.atan2(float((R3 @ UP) @ fwd), float((R3 @ UP)[1])))
        yaw = lambda R3: D(math.atan2(float((R3 @ np.array([0, 0, 1.0])) @ lat), float((R3 @ np.array([0, 0, 1.0])) @ fwd)))
        sm = (Q['shL'][0] + Q['shR'][0]) / 2
        hm = (Q['hipL'][0] + Q['hipR'][0]) / 2
        wr = D(mocap.wrap(mocap.ang_down(Q['wriR'], Q['handR']) - mocap.ang_down(Q['elbR'], Q['wriR'])))
        out.append({'lean': D(p['lean']), 'headW': pitch(R['head']), 'thorax': pitch(R['thorax']), 'pelvis': pitch(R['root']),
                    'bend': pitch(R['thorax']) - pitch(R['root']), 'twist': yaw(R['thorax']) - yaw(R['root']),
                    'shoulder': (Q['shR'][0] - sm) * PXM, 'hip': (Q['hipR'][0] - hm) * PXM, 'drop': (Q['hipR'][1] - Q['hipL'][1]) * PXM,
                    'foot': D(p['ftF']), 'wrist': wr, 'elbow': D(p['eF']), 'arm': D(p['aF']), 'hF': p['hF']})
    return out


ROWS = [('lean', 'trunk lean, hip joints to shoulders (deg)', 'kept (round 23)'),
        ('pelvis', 'pelvis pitch (deg)', 'not drawn: the trunk was one line'),
        ('thorax', 'thorax pitch (deg)', 'not drawn: the trunk was one line'),
        ('bend', 'thorax less pelvis: the spine\'s bend (deg)', 'sb: the spine\'s curve'),
        ('twist', 'thorax yaw less pelvis yaw: counter-rotation (deg)', 'soF/soB: seen in profile as the shoulders\' shift'),
        ('shoulder', 'near shoulder joint fore and aft of the shoulders\' middle (px)', 'soF/soB'),
        ('hip', 'near hip joint fore and aft of the hips\' middle (px)', 'left out: under 0.3 px'),
        ('drop', 'near hip over far hip, the pelvis\'s drop (px)', 'left out: +-0.5 px, hidden by the kilt'),
        ('foot', 'foot pitch, ankle to ball (deg; flat is about -21)', 'fpF/fpB: the foot turns'),
        ('wrist', 'wrist flexion (deg)', 'left out: steady, 0.1 px at the hand'),
        ('elbow', 'elbow bend (deg)', 'kept (round 23)'),
        ('headW', 'head pitch in the world (deg)', 'kept (round 23): steadier than the chest')]


def measure():
    res = {}
    for nm, a0, b0, why in CLIPS:
        S = series(nm, a0, b0)
        per = b0 - a0
        if nm != '09_01':
            x = np.array([s['hF'] for s in S])
            x = x - x.mean()
            best = -1e9
            for p_ in range(50, min(160, len(x) - 10)):
                v = float(np.dot(x[:-p_], x[p_:]) / (len(x) - p_))
                if v > best:
                    best, per = v, p_
            S = S[5:5 + per]
        res[nm] = {'why': why, 'period': per, 'stats': {k: {'mean': round(float(np.mean([s[k] for s in S])), 2), 'min': round(min(s[k] for s in S), 2),
                                                            'max': round(max(s[k] for s in S), 2)} for k, _, _ in ROWS}}
    # what v71 drew of these in the run: the trunk one line (bend 0), the shoulders moved only by the drawing's 0.9 sin(upper arm) px, feet flat
    MCK = json.loads(open(OLD, encoding='utf-8').read().split('const MCK=')[1].split(';\n')[0])
    sh71 = [0.9 * math.sin(q['aF']) for q in MCK['run']]
    MCN = json.loads(open(NEW, encoding='utf-8').read().split('const MCK=')[1].split(';\n')[0])
    res['v71'] = {'shoulder': [round(min(sh71), 2), round(max(sh71), 2)], 'bend': [0, 0], 'foot': [0, 0]}
    res['new'] = {k: [round(min(q[k] for q in MCN['run']), 3), round(max(q[k] for q in MCN['run']), 3)] for k in ('sb', 'soF', 'soB', 'fpF', 'fpB')}
    res['rows'] = ROWS
    json.dump(res, open(os.path.join(OUT, 'r25a.json'), 'w'), indent=1)
    for k, lab, use in ROWS:
        print('%-60s' % lab, '  '.join('%s %6.1f..%6.1f' % (nm, res[nm]['stats'][k]['min'], res[nm]['stats'][k]['max']) for nm, *_ in CLIPS))
    print('v71', res['v71'], 'new', res['new'])


# ---------------- pictures ----------------
EXPORT = 'window.__R25={skel,PS,mk,RP,figDraw,PAL_HERO,GFX,LEN};'
KEYS = r'''([S,n])=>{const F=window.__R25;F.GFX().hd=true;const W=44,Hh=70,cv=document.createElement('canvas');cv.width=W*S*n;cv.height=Hh*S;const c=cv.getContext('2d');
 c.fillStyle='#e8dcc8';c.fillRect(0,0,cv.width,cv.height);const geo=[];
 for(let j=0;j<n;j++){c.save();c.scale(S,S);c.translate(j*W,0);c.strokeStyle='rgba(0,0,0,.3)';c.lineWidth=0.25;c.beginPath();c.moveTo(0,62);c.lineTo(W,62);c.stroke();
  const p=Object.assign(F.mk({}),F.RP(j/n)),s=F.skel(p);F.figDraw(c,20,62,1,p,F.PAL_HERO,{time:0,vx:150,lt:{dir:1,col:'255,220,170',k:0.6}});c.restore();
  geo.push({p:Object.assign({},p),sh:s.sh,hipH:s.hipH,to:F.LEN.to});}
 return [cv.toDataURL('image/png'),geo];}'''


def b64img(u):
    return Image.open(io.BytesIO(base64.b64decode(u.split(',')[1]))).convert('RGB')


def page(b, src, tmp, tag):
    s = open(src, encoding='utf-8').read()
    i = s.find('window.__HK={')
    fn = os.path.join(tmp, '_r25a_%s.html' % tag)
    open(fn, 'w', encoding='utf-8').write(s[:i] + EXPORT + s[i:])
    pg = b.new_page()
    pg.errs = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e)))
    pg.goto('file://' + fn)
    pg.wait_for_timeout(700)
    return pg


def sstep(x):
    x = min(1, max(0, x))
    return x * x * (3 - 2 * x)


def overlay(d, g, ox, S):
    """the pelvis line (the spine's start tangent), the chest line (its end tangent) and the shoulder joints, as drawFigureHD0's torso builds them"""
    p = g['p']
    lean = p['lean']
    nx, ny = math.cos(lean), math.sin(lean)
    sh = g['sh']
    fl = min(1.4, max(-0.6, (p['hF'] + p['hB']) / 2 - lean))
    ra = (sstep((abs(p['aF']) - 1.7) / 0.9) + sstep((abs(p['aB']) - 1.7) / 0.9)) / 2
    cc = -1.1 * fl + 0.9 * ra - g['to'] * 0.5 * math.tan((p.get('sb') or 0) / 2)
    cp = (sh[0] / 2 + nx * cc, sh[1] / 2 + ny * cc)
    X = lambda q: (ox + (20 + q[0]) * S, (62 - g['hipH'] + q[1]) * S)
    def seg(p0, v, L, col):
        n = math.hypot(*v) or 1
        q = (p0[0] + v[0] / n * L, p0[1] + v[1] / n * L)
        d.line([X(p0), X(q)], fill=col, width=3)
    seg((0, 0), cp, 7.5, (40, 150, 60))                                     # pelvis: the spine leaving the hip
    seg(sh, (cp[0] - sh[0], cp[1] - sh[1]), 7.5, (230, 120, 20))             # chest: the spine arriving at the shoulders
    sm = p.get('sm') or 0
    for side, col in (('F', (210, 40, 40)), ('B', (40, 80, 210))):
        k = 0.9 * math.sin(p['a' + side]) * (1 - sm) + (p.get('so' + side) or 0)
        q = X((sh[0] + nx * k, sh[1] + ny * k))
        d.ellipse([q[0] - 4, q[1] - 4, q[0] + 4, q[1] + 4], fill=col, outline=(255, 255, 255))


def sticks(S, n):
    c = mocap.Clip('09_01')
    i0, per = 42, 88
    fwd = mocap.facing(c.sk, c.frames, i0, i0 + per)
    W = 44
    im = Image.new('RGB', (W * S * n, 70 * S), (244, 238, 228))
    d = ImageDraw.Draw(im)
    Qs = [mocap.project(c.P(i), fwd) for i in range(i0, i0 + per + 1)]
    fl = min(min(q[k][1] for k in ('ankleL', 'ankleR', 'ballL', 'ballR', 'toeL', 'toeR')) for q in Qs)
    sc = PXM * S
    for j in range(n):
        Q = Qs[int(round(per * j / n))]
        H = ((Q['hipL'][0] + Q['hipR'][0]) / 2, 0)
        ox = j * W * S + 20 * S - H[0] * sc
        oy = 62 * S + fl * sc
        d.line([(j * W * S, 62 * S), ((j + 1) * W * S - 4, 62 * S)], fill=(180, 170, 160))
        mocap.draw_stick(d, Q, ox, oy, sc, 'r', w=3)
        # the thorax and pelvis lines from the clip: waist->chest->c7 (the spine), the near (red) and far (blue) shoulder joints
        for k, col in (('shR', (210, 40, 40)), ('shL', (40, 80, 210))):
            q = (ox + Q[k][0] * sc, oy - Q[k][1] * sc)
            d.ellipse([q[0] - 4, q[1] - 4, q[0] + 4, q[1] + 4], fill=col)
        d.text((j * W * S + 4, 66 * S), 'f%d' % (i0 + int(round(per * j / n))), fill=INK)
    return im


def keys(b):
    from playwright.sync_api import sync_playwright
    tmp = tempfile.mkdtemp(prefix='r25a', dir=HERE)
    try:
        S, n = 4, 16
        rows = []
        errs = []
        for src, tag in ((OLD, 'v71'), (NEW, 'new')):
            pg = page(b, src, tmp, tag)
            u, geo = pg.evaluate(KEYS, [S, n])
            im = b64img(u)
            d = ImageDraw.Draw(im)
            for j in (0, 4, 8, 12):
                overlay(d, geo[j], j * 44 * S, S)
            rows.append(im)
            errs += pg.errs
            pg.close()
        st = sticks(S, n)
        W = rows[0].width
        half = W // 2
        LBL = ['v71 (round 23: one rigid trunk line, shoulders from the arm swing, flat feet)', 'round 25a (the clip\'s spine bend, shoulder girdle, foot pitch; kilt hem lag)',
               'CMU 09_01, the same phases (stick figure, the game\'s scale)']
        out = Image.new('RGB', (half, 60 + 2 * (3 * (rows[0].height + 22) + 14)), BG)
        dd = ImageDraw.Draw(out)
        dd.text((8, 8), 'Round 25a: the run (owner: "The prince is somewhat stiff when running. Humans are somewhat flexible"). 16 keys a stride at 4x, the near '
                '(right) foot down at key 0, the far at key 8.', fill=INK)
        dd.text((8, 24), 'On keys 0, 4, 8, 12: pelvis line (green: the spine leaving the hip), chest line (orange: the spine at the shoulders), shoulder joints '
                '(near red, far blue). Data: CMU mocap (mocap.cs.cmu.edu, NSF EIA-0196217).', fill=INK)
        y = 46
        for part in (0, 1):
            for im, lab in zip(rows + [st], LBL):
                dd.text((8, y), lab + ('  (keys 0-7)' if part == 0 else '  (keys 8-15)'), fill=INK)
                out.paste(im.crop((part * half, 0, (part + 1) * half, im.height)), (0, y + 16))
                y += im.height + 22
            y += 14
        out = out.crop((0, 0, out.width, y))
        out.save(os.path.join(OUT, 'r25a_run.png'), optimize=True)
        print('r25a_run.png', out.size, 'errors', errs[:3])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


SETUP = r'''([n,sd])=>{const H=__HK;const L=__P.load(n,sd);let pc=-1,r=-1;
 for(let rr=2;rr<L.rows-1&&pc<0;rr++)for(let c=8;c<L.cols-20;c++){let ok=true;for(let k=0;k<=12;k++)if(!H.solidBelow(c+k,rr)||L.feat[rr*L.cols+c+k])ok=false;if(ok){pc=c;r=rr;break;}}
 __P.stand(pc,r,1);H.banner=null;H.intro=0;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);H.setKey('kb','r',true);for(let i=0;i<30;i++)H.tick(1);return [pc,r,H.P.state];}'''
STEP = r'''()=>{const H=__HK;H.tick(1);H.banner=null;__P.draw();return __P.scr(H.P.x,H.P.y-26);}'''


def gif(b):
    import egyptr12 as R12
    R12.OUT = OUT
    pages = {(t, m): R12.page(b, src, m) for t, src in (('v71', OLD), ('new', NEW)) for m in ('torch', 'classic')}
    N = 44
    cols = {}
    for k, pg in pages.items():
        info = pg.evaluate(SETUP, [7, 1])
        fr = []
        for i in range(N):
            xy = pg.evaluate(STEP)
            fr.append(R12.crop(R12.shot(pg), xy, 220, 224))
        cols[k] = (fr, info)
        print(k, info, pg.errs[:2])
    out = []
    order = [('v71', 'torch'), ('new', 'torch'), ('v71', 'classic'), ('new', 'classic')]
    for i in range(N):
        g = Image.new('RGB', (4 * 220 + 6, 224 + 16), (20, 16, 24))
        for j, k in enumerate(order):
            g.paste(cols[k][0][i], (j * 222, 16))
            ImageDraw.Draw(g).text((j * 222 + 4, 2), '%s %s' % ('v71' if k[0] == 'v71' else 'round 25a', 'Torchlight' if k[1] == 'torch' else 'Classic'), fill=(240, 230, 210))
        out.append(g.quantize(colors=112, method=Image.MEDIANCUT, dither=Image.NONE))
    R12.gif(out, 'r25a_run.gif', 40)
    print('r25a_run.gif', os.path.getsize(os.path.join(OUT, 'r25a_run.gif')) // 1024, 'KB')


if __name__ == '__main__':
    if WHAT in ('measure', 'all'):
        measure()
    if WHAT in ('keys', 'gif', 'all'):
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
            if WHAT in ('keys', 'all'):
                keys(b)
            if WHAT in ('gif', 'all'):
                gif(b)
            b.close()
