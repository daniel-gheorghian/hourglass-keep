# egyptr22c.py [new.html] [old.html] [r22b.html] [outdir]: round 22c's pictures for egypt_themes.html, the prince's neck after the audit of
# round 22b's measures. Builds: v69 (old.html, default hk_v69_release.html here or in the main checkout's dev/tools), round 22b (r22b.html,
# default ../_r22b.html, made with git show 0a4e1ad:dev/hourglass-keep.html), after (new.html), and two variants of after made by rewriting its
# NJ line (the neck's junction with the trunk) 0.5 px shorter and 0.5 px longer. Landmarks and ratios come from r22cmeasure.py.
#  r22c_variants.png  standing, v69 | 22b | shorter | recommended (after) | longer: at 10x lit from his back, the silhouette with the landmarks,
#                     and in the game at its own scale (Torchlight and Classic, floor 7), each labelled with chin to acromion and the ratios
#  r22c_guide.png     standing at 10x, v69 | 22b | after, lit, and the silhouette with chin, pit of the neck, acromion top, shoulder joint, C7,
#                     nape, hip; right, ANSUR II's youth in the body's scale as a ruler from the hip
#  r22c_poses.png     every pose at 4x, v69 | 22b | after, lit from his back, and a robber
#  r22c_game.png      in the game, Torchlight (GLP.rs 1 and .5) and Classic: standing (floors 7 and 14), v69 | 22b | after; hanging on a near
#                     face, climbing onto it, crawling, swinging and in a fight, 22b | after
# Writes r22c.json (measures, ratios, page errors). Run from dev/tools.
import base64, io, json, os, re, shutil, sys, tempfile
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw
import egyptr12 as R12
import egyptr18 as E18
import egyptr19 as R19
import egyptr22b as B
import r22cmeasure as M
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
NEW = os.path.abspath(a[0] if len(a) > 0 and a[0] else os.path.join(HERE, '..', 'hourglass-keep.html'))
_old = os.path.join(HERE, 'hk_v69_release.html')
if not os.path.exists(_old):
    _old = os.path.join(HERE, '..', '..', '..', '..', '..', 'dev', 'tools', 'hk_v69_release.html')
OLD = os.path.abspath(a[1] if len(a) > 1 and a[1] else _old)
R22B = os.path.abspath(a[2] if len(a) > 2 and a[2] else os.path.join(HERE, '..', '_r22b.html'))
OUT = a[3] if len(a) > 3 else os.path.join(HERE, 'egypt_themes')
R12.OUT = OUT
WHITE = (240, 230, 210)
INK = (20, 16, 24)


def variant(txt, s):
    """the after build with the neck's junction moved s px (positive: a longer neck): the pit of the neck, C7 and the deltoid's cap lower"""
    m = re.search(r'const NJ=(\{[^\n]*\});', txt)
    J = json.loads(re.sub(r'([a-z0-9]+):', r'"\1":', m.group(1)))
    J['th'][0] -= s
    J['c7'][0] -= s
    J['bk'][1][0] -= s
    J['km'][0] -= s / 2
    J['dq'] += s
    js = json.dumps(J, separators=(',', ':'))
    js = re.sub(r'"([a-z0-9]+)":', r'\1:', js)
    return txt[:m.start()] + 'const NJ=' + js + ';' + txt[m.end():]


S10 = 10
# the standing figure through the hooked build (__FS): lit (dir) or a silhouette; the hip's canvas row returned with it
FIGS = r'''([S,W,Hh,X,Y,dir,mono])=>{const F=__FS;F.GFX().hd=true;const p=F.mk(F.PS.stand),s=F.skel(p),cv=document.createElement('canvas');cv.width=W*S;cv.height=Hh*S;
 const c=cv.getContext('2d');c.fillStyle=mono?'#e8dcc8':'#5a4434';c.fillRect(0,0,cv.width,cv.height);c.scale(S,S);
 F.figDraw(c,X,Y,1,p,F.PAL_HERO,{sword:false,hasSword:true,time:0,mono:mono||undefined,lt:{dir,col:'255,220,170',k:0.6}});return [cv.toDataURL('image/png'),(Y-s.hipH)*S];}'''
LMK = [('crown', 'crown', (200, 140, 20)), ('nape', 'nape', (120, 120, 120)), ('chinG', 'chin', (40, 110, 220)), ('c7', 'C7', (230, 120, 0)),
       ('notch', 'pit of the neck', (30, 150, 60)), ('acrG', 'acromion top', (210, 40, 40)), ('joint', 'shoulder joint', (150, 60, 170)), ('hip', 'hip (trochanter)', (90, 90, 90))]


def place(d, items, x0, xl):
    """labels at the right of their lines, pushed apart (11 px), with a leader from the line's end (x0) to the label (xl)"""
    items = sorted(items, key=lambda q: q[0])
    prev = -1e9
    for y, txt, col in items:
        ty = max(y - 6, prev + 11)
        prev = ty
        d.line([(x0, y), (xl - 2, ty + 6)], fill=col, width=1)
        d.text((xl, ty), txt, fill=col)


def marks(im, hipY, m, x1=None):
    d = ImageDraw.Draw(im)
    x1 = x1 or im.width - 130
    it = []
    for k, name, col in LMK:
        h = 0 if k == 'hip' else m[k]
        y = hipY - h * S10
        d.line([(0, y), (x1, y)], fill=col, width=1)
        it.append((y, '%s %.1f' % (name, h), col))
    place(d, it, x1, x1 + 12)
    return im


def ratio_text(m, A):
    return ['chin-acromion %.2f px' % m['chin_acr'], 'chin-pit %.2f, C7 %.2f under chin' % (m['chin_notch'], m['c7_under_chin']),
            'nape-C7 %.1f px, neck %.1f wide' % (m['neck_back'], m['neckDepth']),
            'neck/trunk %.3f (ANSUR %.3f)' % (m['R_neck_trunk'], A['R_neck_trunk']), 'C7/trunk %.3f (%.3f)' % (m['R_c7_trunk'], A['R_c7_trunk']),
            'nape-C7/trunk %.2f (%.2f)' % (m['R_back_trunk'], A['R_back_trunk']), 'neck/chest %.2f (%.2f)' % (m['R_neckD_chest'], A['R_neckD_chest']),
            'trunk/leg %.3f (%.3f)' % (m['R_trunk_leg'], A['R_trunk_leg'])]


def ruler(Hh, hipY):
    # ANSUR II's men aged 17-20 in the body's scale (3.7 cm a px, the trochanter at the hip), heights over the trochanter
    A = M.ANSUR
    k = 37.0
    im = Image.new('RGB', (260, Hh * S10), (232, 220, 200)); d = ImageDraw.Draw(im)
    gh = A['acromion'] - 40
    mk = [('crown (real head)', A['stature']), ('C7', A['cervicale']), ('chin', A['chin']), ('pit of the neck', A['suprasternale']),
          ('acromion', A['acromion']), ('shoulder joint (~40 mm under)', gh), ('trochanter', A['trochanter']), ('sole', 0)]
    d.line([(20, hipY - (A['stature'] - A['trochanter']) / k * S10), (20, hipY + A['trochanter'] / k * S10)], fill=INK, width=3)
    it = []
    for name, mm in mk:
        y = hipY - (mm - A['trochanter']) / k * S10
        d.line([(10, y), (30, y)], fill=INK, width=2)
        it.append((y, '%s %.1f' % (name, (mm - A['trochanter']) / k), INK))
    place(d, it, 30, 44)
    d.text((4, 4), 'ANSUR II, men 17-20', fill=INK)
    d.text((4, 16), 'body scale, px over the hip', fill=INK)
    return im


FIGHT = r'''([n,sd,more,rs])=>{const H=__HK;__P.load(n,sd);if(H.GLP)H.GLP.rs=rs;let k=0;const r=runBot(n,sd,{fight:true,stop:h=>h.P.sword&&h.P.foe&&!h.P.foe.dead&&++k>more});
 H.banner=null;H.intro=0;for(const q of ['l','r','u','d','j','g'])H.setKey('kb',q,false);document.querySelectorAll('.screen').forEach(e=>e.hidden=true);__P.draw();
 return {ok:k>more,st:H.P.state,xy:__P.scr(H.P.x-H.P.face*10,H.P.y-30),name:H.themeName(n)};}'''


def dataimg(d):
    return Image.open(io.BytesIO(base64.b64decode(d.split(',')[1]))).convert('RGB')


def fit(im, w, h, bg=(20, 16, 24)):
    g = Image.new('RGB', (w, h), bg); g.paste(im, (0, 0)); return g


if __name__ == '__main__':
    if not os.path.exists(R22B):
        os.system('git -C "%s" show 0a4e1ad:dev/hourglass-keep.html > "%s"' % (HERE, R22B))
    J = {'errors': [], 'measure': {}, 'ansur': M.ansur_ratios(), 'moves': {}}
    newt = open(NEW, encoding='utf-8').read()
    tmp = tempfile.mkdtemp(prefix='r22c', dir=HERE)
    TXT = {'v69': open(OLD, encoding='utf-8').read(), '22b': open(R22B, encoding='utf-8').read(), 'shorter': variant(newt, -0.5), 'after': newt, 'longer': variant(newt, 0.5)}
    TAG = {'v69': 'v69', '22b': 'round 22b', 'shorter': 'shorter (-0.5)', 'after': 'after (recommended)', 'longer': 'longer (+0.5)'}
    FILES = {}
    for k, t in TXT.items():
        fn = os.path.join(tmp, '_r22c_game_%s.html' % k)
        open(fn, 'w', encoding='utf-8').write(t)
        FILES[k] = fn
    A = J['ansur']
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
            Mz = M.measure(b, list(TXT.items()), tmp)
            J['measure'] = {k: {q: v for q, v in m.items() if q != 'errors'} for k, m in Mz.items()}
            for k, m in Mz.items():
                J['errors'] += ['%s: %s' % (k, e) for e in m['errors']]
                print(k, {q: round(v, 3) for q, v in m.items() if isinstance(v, float)}, flush=True)
            HP = {}
            for k, t in TXT.items():
                fn = M.hooked(t, 'fig_' + k, tmp)
                pg = b.new_page(); pg.goto('file://' + fn); pg.wait_for_timeout(500); HP[k] = pg
            # ---- 1. the variants
            W, Hh, X, Y = 40, 40, 16, 57
            cols = []
            GP = {}
            for k in ('v69', '22b', 'shorter', 'after', 'longer'):
                for mo in ('torch', 'classic'):
                    GP[(k, mo)] = R12.page(b, FILES[k], mo)
            for k in ('v69', '22b', 'shorter', 'after', 'longer'):
                m = Mz[k]
                d1, hipY = HP[k].evaluate(FIGS, [S10, W, Hh, X, Y, -1, None])
                lit = R12.label(dataimg(d1), '%s, 10x' % TAG[k])
                d2, _ = HP[k].evaluate(FIGS, [S10, W, Hh, X, Y, 1, '#120c18'])
                sil = marks(dataimg(d2), hipY, m)
                g = []
                for mo in ('torch', 'classic'):
                    pg = GP[(k, mo)]
                    xy = pg.evaluate(B.STAND, [7, 1, 1, 1])
                    im = R12.shot(pg)
                    c = R12.crop(im, (xy[0], xy[1] - 20), 96, 120)
                    g.append(R12.label(c.resize((192, 240), Image.NEAREST), '%s, game px x2' % mo))
                    g.append(R12.label(R12.crop(im, (xy[0], xy[1] + 4), 96, 150), '1:1'))
                gm = Image.new('RGB', (W * S10, 250), (20, 16, 24))
                gm.paste(g[0], (0, 0)); gm.paste(g[2], (196, 0))
                txt = Image.new('RGB', (W * S10, 130), (232, 220, 200)); dd = ImageDraw.Draw(txt)
                for i, l in enumerate(ratio_text(m, A)):
                    dd.text((4, 4 + i * 15), l, fill=INK)
                sm = Image.new('RGB', (W * S10, 154), (20, 16, 24)); sm.paste(g[1], (0, 0)); sm.paste(g[3], (100, 0))
                cols.append(R12.stack([lit.crop((0, 0, W * S10, 320)), sil.crop((0, 0, W * S10, 320)), txt, gm, sm], pad=2))
            v = R12.grid([fit(c, max(q.width for q in cols), max(q.height for q in cols)) for c in cols], 5)
            v.save(os.path.join(OUT, 'r22c_variants.png'))
            print('variants done', flush=True)
            # ---- 2. the guide
            W2, H2, X2, Y2 = 40, 60, 16, 57
            t = []
            for k in ('v69', '22b', 'after'):
                d1, hipY = HP[k].evaluate(FIGS, [S10, W2, H2, X2, Y2, -1, None])
                t.append(R12.label(dataimg(d1), '%s, lit from his back' % TAG[k]))
                d2, _ = HP[k].evaluate(FIGS, [S10, W2, H2, X2, Y2, 1, '#120c18'])
                sil = marks(dataimg(d2), hipY, Mz[k])
                ImageDraw.Draw(sil).text((4, 4), '%s: landmarks (px over the hip)' % TAG[k], fill=INK)
                t.append(sil)
            t.append(ruler(H2, hipY))
            g = Image.new('RGB', (sum(i.width for i in t) + 2 * len(t), H2 * S10), INK); xx = 0
            for i in t:
                g.paste(i, (xx, 0)); xx += i.width + 2
            g.save(os.path.join(OUT, 'r22c_guide.png'))
            print('guide done', flush=True)
            # ---- 3. every pose, v69 | 22b | after
            pn = GP[('after', 'classic')]
            poses = pn.evaluate(B.POSES)
            tiles = []
            for k, q in list(poses.items()) + [('robber', 'rob')]:
                tr = []
                for vv in ('v69', '22b', 'after'):
                    qq, pk = (poses['stand'], 'rob') if q == 'rob' else (q, 'hero')
                    air = k in ('hang', 'pull', 'press', 'reach', 'slide', 'kneel')
                    tr.append(dataimg(GP[(vv, 'classic')].evaluate(B.FIG, [qq, 4, 44, 72, 36 if k == 'dead' else 20, 60 if air else 68, -1, None, pk])))
                tiles.append(R12.label(R12.grid(tr, 3, 1), '%s: v69 | 22b | after' % k))
            R12.grid(tiles, 5).save(os.path.join(OUT, 'r22c_poses.png'))
            print('poses done', flush=True)
            # ---- 4. the game
            rows = []
            t, big = [], []
            for n, face in ((7, 1), (14, -1)):
                for mo, rs in (('torch', 1), ('torch', 0.5), ('classic', 1)):
                    for vv in ('v69', '22b', 'after'):
                        pg = GP[(vv, mo)]
                        xy = pg.evaluate(B.STAND, [n, 1, face, rs])
                        im = R12.shot(pg)
                        t.append(R12.label(R12.crop(im, xy, 150, 200), '%s %s%s' % (vv, mo, ' .5' if rs < 1 else '')))
                        if n == 7:
                            big.append(R12.label(R12.crop(im, (xy[0], xy[1] - 24), 70, 90).resize((210, 270), Image.LANCZOS), '%s %s%s 3x' % (vv, mo, ' .5' if rs < 1 else '')))
            rows.append(R12.grid(t, 9)); rows.append(R12.grid(big, 9))
            for pg in GP.values():
                pg.evaluate("()=>{if(__HK.GLP)__HK.GLP.rs=1;}")
            hv = None
            for n, sd in R19.HANGS:
                if GP[('after', 'torch')].evaluate(R19.STOP, [n, sd, False]):
                    hv = (n, sd); break
            J['moves']['hanging'] = hv
            if hv:
                t = []
                for seq, lab, dy in (([(30, None)], 'hanging', 10), ([(30, None), (1, 'u'), (12, None)], 'climbing', -12)):
                    for mo in ('torch', 'classic'):
                        for vv in ('22b', 'after'):
                            pg = GP[(vv, mo)]
                            pg.evaluate(R19.STOP, [hv[0], hv[1], False])
                            for kk, key in seq:
                                xy, st = pg.evaluate(R19.STEP, [kk, key])
                            pg.evaluate("()=>{__HK.intro=0;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);__P.draw();}")
                            t.append(R12.label(R12.crop(R12.shot(pg), (xy[0], xy[1] + dy), 200, 200), '%s %s %s' % (lab, mo, vv)))
                rows.append(R12.grid(t, 8))
            t = []
            name, cond, more, floors = B.MOVES[0]
            got = None
            for n, sd in [tuple(q) for q in GP[('after', 'torch')].evaluate(B.FINDA, floors)]:
                if GP[('after', 'torch')].evaluate(B.MOMENT, [n, sd, cond, more, 1])['ok']:
                    got = (n, sd); break
            J['moves']['crawling'] = got
            if got:
                for mo in ('torch', 'classic'):
                    for vv in ('22b', 'after'):
                        q = GP[(vv, mo)].evaluate(B.MOMENT, [got[0], got[1], cond, more, 1])
                        t.append(R12.label(R12.crop(R12.shot(GP[(vv, mo)]), q['xy'], 200, 200), 'crawling %s %s' % (mo, vv)))
            for mo in ('torch', 'classic'):
                for vv in ('22b', 'after'):
                    pg = GP[(vv, mo)]
                    q = pg.evaluate(E18.SWING, [6, 0.85, 0.25])
                    pg.evaluate("()=>{__HK.intro=0;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);__P.draw();}")
                    t.append(R12.label(R12.crop(R12.shot(pg), pg.evaluate(E18.AT, [q['fx'], q['fy'] + 22]), 200, 200), 'swinging %s %s' % (mo, vv)))
            rows.append(R12.grid(t, 8))
            t = []
            fgot = None
            for n, sd in ((6, 1), (7, 1), (12, 1), (5, 1)):
                if GP[('after', 'torch')].evaluate(FIGHT, [n, sd, 25, 1])['ok']:
                    fgot = (n, sd); break
            J['moves']['fight'] = fgot
            if fgot:
                for mo, rs in (('torch', 1), ('torch', 0.5), ('classic', 1)):
                    for vv in ('22b', 'after'):
                        q = GP[(vv, mo)].evaluate(FIGHT, [fgot[0], fgot[1], 25, rs])
                        t.append(R12.label(R12.crop(R12.shot(GP[(vv, mo)]), q['xy'], 200, 200), 'fight %s%s %s' % (mo, ' .5' if rs < 1 else '', vv)))
                rows.append(R12.grid(t, 6))
            R12.stack(rows).save(os.path.join(OUT, 'r22c_game.png'))
            print('game done', J['moves'], flush=True)
            for (vv, mo), pg in GP.items():
                J['errors'] += ['%s %s: %s' % (vv, mo, e) for e in pg.errs]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    json.dump(J, open(os.path.join(OUT, 'r22c.json'), 'w'), indent=1)
    print('errors', J['errors'][:5])
