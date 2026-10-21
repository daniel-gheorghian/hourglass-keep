# egyptr24.py [what] [src.html]: round 24's pictures (owner, after v70: "Still too lean: make it bulkier"), into egypt_themes/.
#   bulk   r24_bulk.png: v70 (MUS 1.28) | the three heroic levels 1.45, 1.65 (the game), 1.85: standing at 10x, seven poses at 4x (stand, run,
#          hang, climb, en garde, crouch, drink), 1x/2x/3x beside a robber (robbers keep v70's widths), the table of widths
#   game   r24_game.png: in the game at the phone's resolution, Torchlight and Classic: standing, running, hanging, fighting a robber,
#          v70 (1.28) | round 24 (1.65)
# The levels are picked at run time with __HK.setMus(m). Run from dev/tools. CMU mocap (mocap.cs.cmu.edu, NSF EIA-0196217); ANSUR II.
import base64, io, json, os, sys, tempfile, shutil, textwrap
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
WHAT = a[0] if a else 'all'
SRC = os.path.abspath(a[1] if len(a) > 1 and a[1] else os.path.join(HERE, '..', 'hourglass-keep.html'))
OUT = os.path.join(HERE, 'egypt_themes')
INK = (20, 16, 24)
BG = (250, 246, 238)
EXPORT = 'window.__R23={skel,PS,mk,RP,crawlPose,drinkFrame,climbFrame,figDraw,PAL_HERO,GFX,LEN,guardPal};'
J = json.load(open(os.path.join(HERE, 'r23bulk.json')))
DEF = J['mus']
LV = [1.28, 1.45, 1.65, 1.85]
TAB = {q['m']: q for q in J['levels']}
NAME = {1.28: '1.28 (v70)', 1.45: '1.45', 1.65: '1.65 (the game)', 1.85: '1.85'}

FIG = r'''([m,spec,S,W,Hh,x,y,who,lit,def])=>{const H=window.__HK,F=window.__R23;H.setMus(m);let p,dx=0,dy=0;const [k,v]=spec.split(' ');
 if(spec.startsWith('PS.'))p=F.PS[spec.slice(3)];else if(k==='run')p=F.RP(+v);else if(k==='drink')p=F.drinkFrame(+v).p;
 else if(k==='climb'){const f=F.climbFrame({x0:-6,y0:57,x1:10,y1:0},+v);p=f.p;dx=f.x;dy=f.y;}
 p=Object.assign(F.mk({}),p);F.GFX().hd=true;
 const cv=document.createElement('canvas');cv.width=W*S;cv.height=Hh*S;const c=cv.getContext('2d');c.fillStyle='#e8dcc8';c.fillRect(0,0,cv.width,cv.height);c.scale(S,S);
 c.strokeStyle='rgba(0,0,0,.25)';c.lineWidth=0.25/Math.max(1,S/4);c.beginPath();c.moveTo(0,y);c.lineTo(W,y);c.stroke();
 const sw=['garde','windup','lunge','parry','lowStrike'].some(q=>spec==='PS.'+q),P=who==='rob'?F.guardPal({tier:1}):F.PAL_HERO;
 F.figDraw(c,x+dx,y+dy,1,p,P,{sword:sw,hasSword:true,time:0,lt:lit?{dir:1,col:'255,220,170',k:0.6}:null});H.setMus(def);return cv.toDataURL('image/png');}'''


def b64img(u):
    return Image.open(io.BytesIO(base64.b64decode(u.split(',')[1]))).convert('RGB')


def page(b, src, tmp):
    s = open(src, encoding='utf-8').read()
    i = s.find('window.__HK={')
    fn = os.path.join(tmp, '_r24.html')
    open(fn, 'w', encoding='utf-8').write(s[:i] + EXPORT + s[i:])
    pg = b.new_page()
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://' + fn)
    pg.wait_for_timeout(700)
    return pg, errs


def fig(pg, m, spec, S, W, Hh, x, y, who='hero', lit=True):
    return b64img(pg.evaluate(FIG, [m, spec, S, W, Hh, x, y, who, lit, DEF]))


ROWS = [('deltoid (profile)', 'arm', 0, 'delt'), ('upper arm (biceps)', 'arm', 1, 'arm'), ('above the elbow', 'arm', 2, 'armLo'),
        ('elbow (joint)', 'arm', 3, None), ('forearm', 'arm', 4, 'fore'), ('wrist (joint)', 'arm', 5, None),
        ('thigh at the fold', 'leg', 0, 'thigh'), ('above the knee', 'leg', 2, 'lthigh'), ('knee (joint)', 'leg', 3, None),
        ('calf', 'leg', 4, 'calf'), ('lower calf', 'leg', 5, 'soleus'), ('ankle (joint)', 'leg', 6, None),
        ('chest depth', 'T', 6, 'chest'), ('lower ribs (lats)', 'T', 4, 'lowch'), ('waist depth', 'T', 2, 'waist'),
        ('seat depth', 'T', 0, 'seat'), ('shoulder top depth', 'T', 8, 'trap'), ('neck base across', 'nb', 0, 'neckB')]


def cell(tab, kind, i, rob=False):
    if kind == 'T':
        return (tab['Fo'][i] + tab['BQ'][i]) * (tab['robK'] if rob else 1) + 0.75
    if kind == 'nb':
        return tab['NJ']['nb'][2] + 0.75
    return tab[kind + ('R' if rob else '')][i] + 0.75


def bulk(b):
    tmp = tempfile.mkdtemp(prefix='r24', dir=HERE)
    try:
        pg, errs = page(b, SRC, tmp)
        cmp = J['cm_per_px']
        big = [fig(pg, m, 'PS.stand', 10, 40, 62, 20, 58) for m in LV]
        small = []
        for m in LV:
            t = Image.new('RGB', (300, 200), (232, 220, 200))
            x = 4
            for S in (1, 2, 3):
                h = fig(pg, m, 'PS.stand', S, 22, 62, 11, 58)
                r = fig(pg, m, 'PS.stand', S, 22, 62, 11, 58, 'rob')
                t.paste(h, (x, 196 - h.height))
                t.paste(r, (x + h.width, 196 - r.height))
                x += h.width * 2 + 8
            small.append(t)
        poses = ['PS.stand', 'run 0.25', 'PS.hang', 'climb 0.45', 'PS.garde', 'PS.crouch', 'drink 0.8']
        prow = []
        for m in LV:
            ims = []
            for sp in poses:
                hang = sp in ('PS.hang',)
                ims.append(fig(pg, m, sp, 4, 50, 72, 24 if sp != 'PS.garde' else 20, 62 if hang else 40 if sp.startswith('climb') else 66))
            prow.append(ims)
        CW = 410
        pw = prow[0][0].width
        W = max(CW * 4 + 10, 130 + len(poses) * (pw + 6))
        H = 40 + 654 + 30 + 210 + 30 + (prow[0][0].height + 24) * 4 + 30 + 18 * (len(ROWS) + 3) + 260
        im = Image.new('RGB', (W, H), BG)
        d = ImageDraw.Draw(im)
        d.text((8, 8), 'Round 24: bulkier (owner: "Still too lean: make it bulkier"). v70 (MUS 1.28, the natural near-limit) and three heroic levels past it '
               '(GROW2: deltoid, lats, forearm, calf faster; waist and joints held).', fill=INK)
        d.text((8, 22), 'Skeleton, poses, grips, hit boxes unchanged. Light from his left. Robbers keep v70\'s widths. Data: ANSUR II, CMU mocap '
               '(mocap.cs.cmu.edu, NSF EIA-0196217).', fill=INK)
        y = 40
        for i, m in enumerate(LV):
            im.paste(big[i], (i * CW, y + 34))
            for j, ln in enumerate(textwrap.wrap('MUS %s: %s' % (NAME[m], TAB[m]['basis']), 64)[:2]):
                d.text((i * CW + 4, y + 2 + j * 14), ln, fill=INK)
        y += 654 + 10
        d.text((8, y), 'In game size: 1x, 2x, 3x, each beside a robber (the robber is the same in every column: v70\'s widths, 1.15 times v70\'s prince)', fill=INK)
        y += 18
        for i, t in enumerate(small):
            im.paste(t, (i * CW, y))
        y += 210 + 10
        d.text((8, y), '4x: stand, run, hang, climb (0.45), en garde, crouch, drink; rows are the levels', fill=INK)
        y += 18
        for i, ims in enumerate(prow):
            d.text((4, y + 4), 'MUS %s' % NAME[LV[i]], fill=INK)
            for j, t in enumerate(ims):
                im.paste(t, (124 + j * (pw + 6), y))
            y += t.height + 24
        y += 10
        d.text((8, y), 'Widths across as drawn, outline included (px at 1x; %.2f cm a px below the chin); the step over the level before; '
               'the robber at v70' % cmp, fill=INK)
        y += 18
        cx = [8, 170, 280] + [380 + i * 190 for i in range(4)] + [380 + 4 * 190]
        for j, h in enumerate(['measure', 'rate (GROW2)', 'v70 rate'] + ['MUS ' + NAME[m] for m in LV] + ['robber']):
            d.text((cx[j], y), h, fill=INK)
        y += 18
        for lab, kind, i, g in ROWS:
            d.text((cx[0], y), lab, fill=INK)
            d.text((cx[1], y), '%.2f' % J['grow2'][g] if g else '0 (joint)', fill=INK)
            d.text((cx[2], y), '%.2f' % J['grow'][g] if g else '0', fill=(90, 80, 70))
            prev = None
            for k, m in enumerate(LV):
                v = cell(TAB[m]['table'], kind, i)
                d.text((cx[3 + k], y), '%.2f px%s' % (v, '' if prev is None else '  +%.2f' % (v - prev)), fill=INK)
                prev = v
            d.text((cx[7], y), '%.2f px' % cell(TAB[1.28]['table'], kind, i, rob=kind != 'nb'), fill=(90, 80, 70))
            y += 18
        y += 8
        for m in LV:
            d.text((8, y), 'MUS %s: %s' % (NAME[m], TAB[m]['basis']), fill=INK)
            y += 16
        im = im.crop((0, 0, im.width, y + 10))
        im.save(os.path.join(OUT, 'r24_bulk.png'), optimize=True)
        print('r24_bulk.png', im.size, 'errors', errs[:3])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def game(b):
    import egyptr12 as R12, egyptr19 as R19, egyptr22b as B22, egyptr22c as C22
    R12.OUT = OUT
    tmp = tempfile.mkdtemp(prefix='r24g', dir=HERE)
    try:
        fn = os.path.join(tmp, '_r24_game.html')
        shutil.copy(SRC, fn)
        GP = {mo: R12.page(b, fn, mo) for mo in ('torch', 'classic')}
        VV = ((1.28, 'v70 1.28'), (DEF, 'round 24 %g' % DEF))
        SET = 'm=>__HK.setMus(m)'
        rows, t = [], []
        for mo in ('torch', 'classic'):
            for m, nm in VV:
                pg = GP[mo]
                pg.evaluate(SET, m)
                xy = pg.evaluate(B22.STAND, [7, 1, 1, 1])
                t.append(R12.label(R12.crop(R12.shot(pg), (xy[0], xy[1] - 6), 220, 250), 'standing %s %s' % (mo, nm)))
        for mo in ('torch', 'classic'):
            for m, nm in VV:
                pg = GP[mo]
                pg.evaluate(SET, m)
                q = pg.evaluate(B22.MOMENT, [6, 1, "H.P.state==='run'", 14, 1])
                t.append(R12.label(R12.crop(R12.shot(pg), q['xy'], 220, 250), 'running %s %s' % (mo, nm)))
        rows.append(R12.grid(t, 4))
        hv = None
        for n, sd in R19.HANGS:
            if GP['torch'].evaluate(R19.STOP, [n, sd, False]):
                hv = (n, sd)
                break
        if hv:
            t = []
            for seq, lab, dy in (([(30, None)], 'hanging', 10), ([(30, None), (1, 'u'), (16, None)], 'climbing', -12)):
                for mo in ('torch', 'classic'):
                    for m, nm in VV:
                        pg = GP[mo]
                        pg.evaluate(SET, m)
                        pg.evaluate(R19.STOP, [hv[0], hv[1], False])
                        for kk, key in seq:
                            xy, st = pg.evaluate(R19.STEP, [kk, key])
                        pg.evaluate("()=>{__HK.intro=0;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);__P.draw();}")
                        t.append(R12.label(R12.crop(R12.shot(pg), (xy[0], xy[1] + dy), 220, 250), '%s %s %s' % (lab, mo, nm)))
            rows.append(R12.grid(t, 4))
        t = []
        fgot = None
        for n, sd in ((6, 1), (7, 1), (12, 1), (5, 1)):
            if GP['torch'].evaluate(C22.FIGHT, [n, sd, 25, 1])['ok']:
                fgot = (n, sd)
                break
        if fgot:
            for mo in ('torch', 'classic'):
                for m, nm in VV:
                    pg = GP[mo]
                    pg.evaluate(SET, m)
                    q = pg.evaluate(C22.FIGHT, [fgot[0], fgot[1], 25, 1])
                    t.append(R12.label(R12.crop(R12.shot(pg), q['xy'], 420, 250), 'fight %s %s' % (mo, nm)))
            rows.append(R12.grid(t, 4))
        for pg in GP.values():
            pg.evaluate(SET, DEF)
        im = R12.stack(rows)
        im.save(os.path.join(OUT, 'r24_game.png'), optimize=True)
        print('r24_game.png', im.size, 'hang', hv, 'fight', fgot, 'errors', [e for pg in GP.values() for e in pg.errs][:3])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
        if WHAT in ('bulk', 'all'):
            bulk(b)
        if WHAT in ('game', 'all'):
            game(b)
        b.close()
