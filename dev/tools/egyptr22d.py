# egyptr22d.py [new.html] [old.html] [r22c.html] [outdir]: round 22d's pictures for egypt_themes.html, the prince rebuilt to the 1989 Prince
# of Persia kid's proportions (owner: "I like best the proportions in the original PoP sprite. Replicate the proportions from there").
# Builds: v69 (old.html, default hk_v69_release.html here or in the main checkout's dev/tools), round 22c (r22c.html, default ../_r22c.html,
# made with git show 06a0143:dev/hourglass-keep.html), after (new.html). The kid's frames come from ref/pop_kid.png and .json (the PrinceJS
# project's assets/gfx, https://github.com/oklemenz/PrinceJS; frame numbers as SDLPoP's src/types.h names them), shown only as a measured
# reference, upscaled nearest neighbour and aspect-corrected (a DOS pixel 1.2 times taller than wide: each is drawn 1.2 times as tall as
# its width), at the same height as our figure (his 41 rows standing = our standing height).
#  r22d_compare.png  the kid | v69 | 22c | after in seven poses (stand 15, run 12, step 124, crouch 109, hang 91, climb 141 (ours: press), fight 158), soles
#                    on one line (hanging: hands on one line); the standing row carries the kid's landmarks as guide lines (crown, chin,
#                    shoulder, waist, hip, crotch, knee, sole) across all four
#  r22d_poses.png    every pose at 4x, 22c | after, lit from his back, and a robber
#  r22d_game.png     in the game, Torchlight (GLP.rs 1 and .5) and Classic: standing, running, hanging, climbing, crawling, swinging, fighting,
#                    22c | after
# Writes r22d.json (the measures of r22dmeasure.py for the kid and the three builds, page errors). Run from dev/tools.
import base64, io, json, os, shutil, sys, tempfile
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw
import egyptr12 as R12
import egyptr18 as E18
import egyptr19 as R19
import egyptr22b as B
import egyptr22c as C
import r22dmeasure as D
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
NEW = os.path.abspath(a[0] if len(a) > 0 and a[0] else os.path.join(HERE, '..', 'hourglass-keep.html'))
_old = os.path.join(HERE, 'hk_v69_release.html')
if not os.path.exists(_old):
    _old = os.path.join(HERE, '..', '..', '..', '..', '..', 'dev', 'tools', 'hk_v69_release.html')
OLD = os.path.abspath(a[1] if len(a) > 1 and a[1] else _old)
R22C = os.path.abspath(a[2] if len(a) > 2 and a[2] else os.path.join(HERE, '..', '_r22c.html'))
OUT = a[3] if len(a) > 3 else os.path.join(HERE, 'egypt_themes')
R12.OUT = OUT
INK = (20, 16, 24)
BG = (232, 220, 200)
VV = ('v69', '22c', 'after')
# kid frame, our pose (a PS key, or 'run 0.25'), hanging (aligned at the top)
POSE = [('15', 'stand', 'standing (frame 15)'), ('12', 'run 0.5', 'running (frame 12)'), ('124', 'step', 'stepping (frame 124)'),
        ('109', 'crouch', 'crouching (frame 109)'), ('91', 'hang', 'hanging (frame 91)'), ('141', 'press', 'climbing (frame 141)'),
        ('158', 'garde', 'en garde (frame 158)')]
FIGP = r'''([k,S,W,Hh,x,y])=>{const H=__HK;let p;if(k.startsWith('run '))p=H.RP(+k.slice(4));else p=H.PS[k];p=Object.assign(H.mk({}),p);
 const cv=document.createElement('canvas');cv.width=W*S;cv.height=Hh*S;const c=cv.getContext('2d');c.fillStyle='#e8dcc8';c.fillRect(0,0,cv.width,cv.height);c.scale(S,S);
 H.figDraw(c,x,y,-1,p,H.PAL_HERO,{sword:k==='garde',hasSword:true,time:0,lt:{dir:1,col:'255,220,170',k:0.6}});return cv.toDataURL('image/png');}'''


def dlabel(im, txt):
    ImageDraw.Draw(im).text((4, 3), txt, fill=INK)
    return im


def kid_frame(n, rowpx):
    J = json.load(open(os.path.join(D.REF, 'pop_kid.json')))['frames']
    im = Image.open(os.path.join(D.REF, 'pop_kid.png')).convert('RGBA')
    f = J['kid-' + n]['frame']
    c = im.crop((f['x'], f['y'], f['x'] + f['w'], f['y'] + f['h']))
    return c.resize((max(1, round(f['w'] * rowpx / D.PAR)), round(f['h'] * rowpx)), Image.NEAREST)


def bbox(im, bg=(232, 220, 200)):
    px = im.load()
    xs, ys = [], []
    for y in range(im.height):
        for x in range(0, im.width):
            p = px[x, y]
            if abs(p[0] - bg[0]) + abs(p[1] - bg[1]) + abs(p[2] - bg[2]) > 30:
                xs.append(x); ys.append(y)
    return min(xs), min(ys), max(xs) + 1, max(ys) + 1


if __name__ == '__main__':
    if not os.path.exists(R22C):
        os.system('git -C "%s" show 06a0143:dev/hourglass-keep.html > "%s"' % (HERE, R22C))
    J = {'errors': [], 'kid': {k: v for k, v in D.kid().items() if k != 'profile'}, 'measure': {}, 'moves': {}}
    TXT = {'v69': open(OLD, encoding='utf-8').read(), '22c': open(R22C, encoding='utf-8').read(), 'after': open(NEW, encoding='utf-8').read()}
    tmp = tempfile.mkdtemp(prefix='r22d', dir=HERE)
    FILES = {}
    for k, t in TXT.items():
        fn = os.path.join(tmp, '_r22d_game_%s.html' % k)
        open(fn, 'w', encoding='utf-8').write(t)
        FILES[k] = fn
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
            Mz = D.ours(b, list(TXT.items()), tmp)
            J['measure'] = {k: {q: v for q, v in m.items() if q not in ('profile', 'errors')} for k, m in Mz.items()}
            print(D.table(D.kid(), Mz), flush=True)
            GP = {}
            for k in VV:
                for mo in ('torch', 'classic'):
                    GP[(k, mo)] = R12.page(b, FILES[k], mo)
            # ---- 1. the kid beside ours
            S = 6
            Hs = {k: Mz[k]['height'] for k in VV}
            rowpx = S * Hs['after'] / D.KID_H   # the kid's row in canvas px: his 41 rows = our standing height
            TW, TH = 46 * S, 74 * S
            rows = []
            KL = D.KID_LM
            hipK = KL['crotch'][0] - 1.5
            GUIDE = [('crown', KL['crown'][0]), ('chin', KL['chin'][0]), ('shoulder', KL['acromion'][0]), ('waist', KL['waist'][0]), ('hip', hipK),
                     ('crotch', KL['crotch'][0]), ('knee', KL['knee'][0]), ('sole', KL['sole'][0])]
            for n, pk, lab in POSE:
                kf = kid_frame(n, rowpx)
                tiles = []
                hang = pk == 'hang'
                base = TH - 3 * S if not hang else 3 * S
                t0 = Image.new('RGB', (TW, TH), BG)
                ky = base - kf.height if not hang else base
                t0.paste(kf, ((TW - kf.width) // 2, ky), kf)
                tiles.append((t0, 'PoP 1989 kid, %s' % lab))
                for vv in VV:
                    d = GP[(vv, 'classic')].evaluate(FIGP, [pk, S, 46, 74, 23, 60])
                    im = R12.dataimg(d) if hasattr(R12, 'dataimg') else Image.open(io.BytesIO(base64.b64decode(d.split(',')[1]))).convert('RGB')
                    x0, y0, x1, y1 = bbox(im)
                    t = Image.new('RGB', (TW, TH), BG)
                    sh = (base - y1) if not hang else (base - y0)
                    t.paste(im, (0, sh))
                    tiles.append((t, '%s' % {'v69': 'v69', '22c': 'round 22c', 'after': 'after (22d)'}[vv]))
                if pk == 'stand':
                    for t, _ in tiles:
                        dd = ImageDraw.Draw(t)
                        for name, r in GUIDE:
                            y = base - (D.KID_H - r) * rowpx
                            dd.line([(0, y), (TW, y)], fill=(200, 40, 40), width=1)
                            dd.text((2, y - 11), name, fill=(200, 40, 40))
                rows.append(R12.grid([dlabel(t, l) for t, l in tiles], 4))
            # (seven rows of four: two blocks side by side)
            half = (len(rows) + 1) // 2
            L1 = R12.stack(rows[:half], pad=4)
            L2 = R12.stack(rows[half:], pad=4)
            g = Image.new('RGB', (L1.width + L2.width + 8, max(L1.height, L2.height)), INK)
            g.paste(L1, (0, 0)); g.paste(L2, (L1.width + 8, 0))
            g.save(os.path.join(OUT, 'r22d_compare.png'))
            print('compare done', flush=True)
            # ---- 2. every pose, 22c | after
            pn = GP[('after', 'classic')]
            poses = pn.evaluate(B.POSES)
            tiles = []
            for k, q in list(poses.items()) + [('robber', 'rob'), ('robber en garde', 'robg')]:
                tr = []
                for vv in ('22c', 'after'):
                    qq, pk = (poses['stand'], 'rob') if q == 'rob' else ((poses['garde'], 'rob') if q == 'robg' else (q, 'hero'))
                    air = k in ('hang', 'pull', 'press', 'reach', 'slide', 'kneel')
                    tr.append(C.dataimg(GP[(vv, 'classic')].evaluate(B.FIG, [qq, 4, 44, 72, 36 if k == 'dead' else 20, 60 if air else 68, -1, None, pk])))
                tiles.append(R12.label(R12.grid(tr, 2, 1), '%s: 22c | after' % k))
            R12.grid(tiles, 6).save(os.path.join(OUT, 'r22d_poses.png'))
            print('poses done', flush=True)
            # ---- 3. the game
            rows = []
            t = []
            for mo, rs in (('torch', 1), ('torch', 0.5), ('classic', 1)):
                for vv in ('22c', 'after'):
                    pg = GP[(vv, mo)]
                    xy = pg.evaluate(B.STAND, [7, 1, 1, rs])
                    im = R12.shot(pg)
                    t.append(R12.label(R12.crop(im, (xy[0], xy[1] - 6), 220, 250), 'standing %s%s %s' % (mo, ' .5' if rs < 1 else '', vv)))
            for mo, rs in (('torch', 1), ('torch', 0.5), ('classic', 1)):
                for vv in ('22c', 'after'):
                    q = GP[(vv, mo)].evaluate(B.MOMENT, [6, 1, "H.P.state==='run'", 14, rs])
                    t.append(R12.label(R12.crop(R12.shot(GP[(vv, mo)]), q['xy'], 220, 250), 'running %s%s %s' % (mo, ' .5' if rs < 1 else '', vv)))
            rows.append(R12.grid(t, 6))
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
                        for vv in ('22c', 'after'):
                            pg = GP[(vv, mo)]
                            pg.evaluate(R19.STOP, [hv[0], hv[1], False])
                            for kk, key in seq:
                                xy, st = pg.evaluate(R19.STEP, [kk, key])
                            pg.evaluate("()=>{__HK.intro=0;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);__P.draw();}")
                            t.append(R12.label(R12.crop(R12.shot(pg), (xy[0], xy[1] + dy), 220, 250), '%s %s %s' % (lab, mo, vv)))
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
                    for vv in ('22c', 'after'):
                        q = GP[(vv, mo)].evaluate(B.MOMENT, [got[0], got[1], cond, more, 1])
                        t.append(R12.label(R12.crop(R12.shot(GP[(vv, mo)]), q['xy'], 220, 250), 'crawling %s %s' % (mo, vv)))
            for mo in ('torch', 'classic'):
                for vv in ('22c', 'after'):
                    pg = GP[(vv, mo)]
                    q = pg.evaluate(E18.SWING, [6, 0.85, 0.25])
                    pg.evaluate("()=>{__HK.intro=0;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);__P.draw();}")
                    t.append(R12.label(R12.crop(R12.shot(pg), pg.evaluate(E18.AT, [q['fx'], q['fy'] + 22]), 220, 250), 'swinging %s %s' % (mo, vv)))
            rows.append(R12.grid(t, 8))
            t = []
            fgot = None
            for n, sd in ((6, 1), (7, 1), (12, 1), (5, 1)):
                if GP[('after', 'torch')].evaluate(C.FIGHT, [n, sd, 25, 1])['ok']:
                    fgot = (n, sd); break
            J['moves']['fight'] = fgot
            if fgot:
                for mo, rs in (('torch', 1), ('torch', 0.5), ('classic', 1)):
                    for vv in ('22c', 'after'):
                        q = GP[(vv, mo)].evaluate(C.FIGHT, [fgot[0], fgot[1], 25, rs])
                        t.append(R12.label(R12.crop(R12.shot(GP[(vv, mo)]), q['xy'], 280, 250), 'fight %s%s %s' % (mo, ' .5' if rs < 1 else '', vv)))
                rows.append(R12.grid(t, 6))
            R12.stack(rows).save(os.path.join(OUT, 'r22d_game.png'))
            print('game done', J['moves'], flush=True)
            for (vv, mo), pg in GP.items():
                J['errors'] += ['%s %s: %s' % (vv, mo, e) for e in pg.errs]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    json.dump(J, open(os.path.join(OUT, 'r22d.json'), 'w'), indent=1, default=str)
    print('errors', J['errors'][:5])
