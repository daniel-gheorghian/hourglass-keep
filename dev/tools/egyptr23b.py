# egyptr23b.py [what] [src.html]: round 23b's pictures (the prince's muscle bulk, owner: "Yeah needs to be bulkier. Add a bulk multiplier,
# but in the sense of more muscle. Give me three variants of him with the current size then more and more bulky"), into egypt_themes/.
#   bulk   r23b_bulk.png: the four levels (R23MUS) side by side: standing at 10x, at 1x, 2x and 3x beside a robber, five poses at 4x, the table
#          of widths (px and the measure each stands for)
#   game   r23b_game.png: each level in the game: Torchlight at GLP.rs 1 and .5 and Classic; standing, running, fighting a robber
# The levels are picked at run time with __HK.setMus(m) (window.__MUS before load does the same); the game itself draws level 1.0.
# Run from dev/tools. The data used in this project was obtained from mocap.cs.cmu.edu (NSF EIA-0196217); ANSUR II.
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
EXPORT = 'window.__R23={skel,PS,mk,RP,crawlPose,drinkFrame,climbFrame,swingPose,figDraw,PAL_HERO,GFX,LEN,guardPal};'
J = json.load(open(os.path.join(HERE, 'r23bulk.json')))
LV = [q['m'] for q in J['levels']]
NAME = ['%g%s' % (m, ' (round 23)' if m == 1 else '') for m in LV]

FIG = r'''([m,spec,S,W,Hh,x,y,who,lit])=>{const H=window.__HK,F=window.__R23;H.setMus(m);let p;const [k,v]=spec.split(' ');
 if(spec.startsWith('PS.'))p=F.PS[spec.slice(3)];else if(k==='run')p=F.RP(+v);
 p=Object.assign(F.mk({}),p);F.GFX().hd=true;
 const cv=document.createElement('canvas');cv.width=W*S;cv.height=Hh*S;const c=cv.getContext('2d');c.fillStyle='#e8dcc8';c.fillRect(0,0,cv.width,cv.height);c.scale(S,S);
 c.strokeStyle='rgba(0,0,0,.25)';c.lineWidth=0.25/Math.max(1,S/4);c.beginPath();c.moveTo(0,y);c.lineTo(W,y);c.stroke();
 const sw=['garde','windup','lunge','parry','lowStrike'].some(q=>spec==='PS.'+q),P=who==='rob'?F.guardPal({tier:1}):F.PAL_HERO;
 F.figDraw(c,x,y,1,p,P,{sword:sw,hasSword:true,time:0,lt:lit?{dir:1,col:'255,220,170',k:0.6}:null});H.setMus(1);return cv.toDataURL('image/png');}'''


def b64img(u):
    return Image.open(io.BytesIO(base64.b64decode(u.split(',')[1]))).convert('RGB')


def page(b, src, tmp):
    s = open(src, encoding='utf-8').read()
    i = s.find('window.__HK={')
    fn = os.path.join(tmp, '_r23b.html')
    open(fn, 'w', encoding='utf-8').write(s[:i] + EXPORT + s[i:])
    pg = b.new_page()
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://' + fn)
    pg.wait_for_timeout(700)
    return pg, errs


def fig(pg, m, spec, S, W, Hh, x, y, who='hero', lit=True):
    return b64img(pg.evaluate(FIG, [m, spec, S, W, Hh, x, y, who, lit]))


# the table: what each drawn width stands for (R23D's keys) and the measure behind it
ROWS = [('deltoid (profile)', 'arm', 0, 'delt', 'ANSUR biceps girth/pi x 1.35'), ('upper arm (biceps)', 'arm', 1, 'arm', 'biceps circumference, flexed'),
        ('above the elbow', 'arm', 2, 'armLo', 'brachialis, triceps'), ('elbow (joint)', 'arm', 3, None, 'wrist x 1.35: bone'),
        ('forearm', 'arm', 4, 'fore', 'forearm circumference, flexed'), ('wrist (joint)', 'arm', 5, None, 'wrist circumference: bone'),
        ('thigh at the fold', 'leg', 0, 'thigh', 'thigh circumference'), ('above the knee', 'leg', 2, 'lthigh', 'lower thigh circumference (vastus)'),
        ('knee (joint)', 'leg', 3, None, 'bone'), ('calf', 'leg', 4, 'calf', 'calf circumference'), ('lower calf', 'leg', 5, 'soleus', 'soleus'),
        ('ankle (joint)', 'leg', 6, None, 'ankle circumference: bone'), ('chest depth', 'T', 6, 'chest', 'chest depth (pectorals, lats)'),
        ('waist depth', 'T', 2, 'waist', 'waist depth: held (no fat)'), ('seat depth', 'T', 0, 'seat', 'buttock depth (glutes)'),
        ('shoulder top depth', 'T', 8, 'trap', 'trapezius'), ('neck base across', 'nb', 0, 'neckB', 'neck circumference at its base')]


def cell(tab, kind, i):
    if kind == 'T':
        return tab['Fo'][i] + tab['BQ'][i] + 0.75
    if kind == 'nb':
        return tab['NJ']['nb'][2] + 0.75
    return tab[kind][i] + 0.75


def bulk(b):
    tmp = tempfile.mkdtemp(prefix='r23b', dir=HERE)
    try:
        pg, errs = page(b, SRC, tmp)
        cmp = J['cm_per_px']
        parts = []
        # row A: standing at 10x
        big = [fig(pg, m, 'PS.stand', 10, 40, 62, 20, 58) for m in LV]
        # row B: in game sizes, beside a robber at the same level
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
        poses = ['run 0.25', 'PS.reach', 'PS.hang', 'PS.garde', 'PS.crouch']
        prow = []
        for m in LV:
            ims = []
            for sp in poses:
                hang = sp in ('PS.reach', 'PS.hang')
                ims.append(fig(pg, m, sp, 4, 56, 72, 26 if sp != 'PS.garde' else 22, 62 if hang else 64))
            prow.append(ims)
        CW = 410
        W = CW * 4 + 10
        pw = prow[0][0].width
        H = 40 + 654 + 30 + 210 + 30 + (prow[0][0].height + 24) * 4 + 30 + 22 * (len(ROWS) + 3) + 200
        im = Image.new('RGB', (max(W, pw * 5 + 160), H), BG)
        d = ImageDraw.Draw(im)
        d.text((8, 8), 'Round 23b: the muscle bulk multiplier MUS (the upper arm\'s girth over ANSUR II\'s median; every other measure at its own rate; '
               'joints, bones, skeleton, poses unchanged). Light from his left (the lit side).', fill=INK)
        d.text((8, 22), 'Data: ANSUR II men 17-20 (lean half by waist/chest), CMU mocap (mocap.cs.cmu.edu, NSF EIA-0196217). The game draws 1.0; '
               'the owner picks.', fill=INK)
        y = 40
        for i, (m, q) in enumerate(zip(LV, J['levels'])):
            im.paste(big[i], (i * CW, y + 34))
            for j, ln in enumerate(textwrap.wrap('MUS %s: %s' % (NAME[i], q['basis']), 64)[:2]):
                d.text((i * CW + 4, y + 2 + j * 14), ln, fill=INK)
        y += 654 + 10
        d.text((8, y), 'In game size: 1x, 2x, 3x, each beside a robber of the same level (robbers 1.15 times as broad on top)', fill=INK)
        y += 18
        for i, t in enumerate(small):
            im.paste(t, (i * CW, y))
        y += 210 + 10
        d.text((8, y), '4x: run, reach (jump up to grab), hang, en garde, crouch; rows are the levels', fill=INK)
        y += 18
        for i, ims in enumerate(prow):
            d.text((4, y + 4), 'MUS %s' % NAME[i], fill=INK)
            for j, t in enumerate(ims):
                im.paste(t, (120 + j * (pw + 6), y))
            y += t.height + 24
        y += 10
        d.text((8, y), 'Widths across as drawn, outline included (px; %.2f cm a px below the chin) and the factor on round 23' % cmp, fill=INK)
        y += 18
        cx = [8, 170, 420] + [640 + i * 170 for i in range(4)]
        for j, h in enumerate(['measure', 'stands for', 'growth rate'] + ['MUS ' + n for n in NAME]):
            d.text((cx[j], y), h, fill=INK)
        y += 18
        for lab, kind, i, g, what in ROWS:
            d.text((cx[0], y), lab, fill=INK)
            d.text((cx[1], y), what, fill=(90, 80, 70))
            d.text((cx[2], y), '%.2f' % J['grow'][g] if g else '0 (joint)', fill=INK)
            v0 = cell(J['levels'][0]['table'], kind, i)
            for k, q in enumerate(J['levels']):
                v = cell(q['table'], kind, i)
                d.text((cx[3 + k], y), '%.2f px  %.1f cm  x%.2f' % (v, v * cmp, v / v0), fill=INK)
            y += 18
        y += 8
        for k, q in enumerate(J['levels']):
            d.text((8, y), 'MUS %s: %s' % (NAME[k], q['basis']), fill=INK)
            y += 16
        im = im.crop((0, 0, im.width, y + 10))
        im.save(os.path.join(OUT, 'r23b_bulk.png'), optimize=True)
        print('r23b_bulk.png', im.size, 'errors', errs[:3])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


FIGHT2 = r'''([n,sd,more,rs])=>{const H=__HK;__P.load(n,sd);if(H.GLP)H.GLP.rs=rs;let k=0;const r=runBot(n,sd,{fight:true,stop:h=>h.P.sword&&h.P.foe&&!h.P.foe.dead&&++k>more});
 H.banner=null;H.intro=0;for(const q of ['l','r','u','d','j','g'])H.setKey('kb',q,false);document.querySelectorAll('.screen').forEach(e=>e.hidden=true);__P.draw();
 const P=H.P,f=P.foe;return {ok:k>more,xy:__P.scr(f?(P.x+f.x)/2:P.x,P.y-30)};}'''


def game(b):
    import egyptr12 as R12, egyptr22b as B22
    tmp = tempfile.mkdtemp(prefix='r23bg', dir=HERE)
    try:
        fn = os.path.join(tmp, '_r23b_game.html')
        shutil.copy(SRC, fn)
        GP = {mo: R12.page(b, fn, mo) for mo in ('torch', 'classic')}
        rows = []
        fgot = None
        for n, sd in ((6, 1), (7, 1), (12, 1), (5, 1)):
            if GP['torch'].evaluate(FIGHT2, [n, sd, 25, 1])['ok']:
                fgot = (n, sd)
                break
        for m, nm in zip(LV, NAME):
            t = []
            for mo, rs in (('torch', 1), ('torch', 0.5), ('classic', 1)):
                pg = GP[mo]
                pg.evaluate('m=>__HK.setMus(m)', m)
                xy = pg.evaluate(B22.STAND, [7, 1, 1, rs])
                t.append(R12.label(R12.crop(R12.shot(pg), (xy[0], xy[1] - 6), 200, 230), 'MUS %s standing %s%s' % (nm, mo, ' .5' if rs < 1 else '')))
            for mo, rs in (('torch', 1), ('torch', 0.5), ('classic', 1)):
                pg = GP[mo]
                q = pg.evaluate(B22.MOMENT, [6, 1, "H.P.state==='run'", 14, rs])
                t.append(R12.label(R12.crop(R12.shot(pg), q['xy'], 200, 230), 'running %s%s' % (mo, ' .5' if rs < 1 else '')))
            if fgot:
                for mo, rs in (('torch', 1), ('torch', 0.5), ('classic', 1)):
                    pg = GP[mo]
                    q = pg.evaluate(FIGHT2, [fgot[0], fgot[1], 25, rs])
                    t.append(R12.label(R12.crop(R12.shot(pg), q['xy'], 340, 230), 'fight %s%s' % (mo, ' .5' if rs < 1 else '')))
            g1, g2 = R12.grid(t[:6], 6), R12.grid(t[6:], 3) if len(t) > 6 else None
            row = Image.new('RGB', (g1.width + (g2.width + 4 if g2 else 0), g1.height), (20, 16, 24))
            row.paste(g1, (0, 0))
            if g2:
                row.paste(g2, (g1.width + 4, 0))
            rows.append(row)
        for pg in GP.values():
            pg.evaluate('()=>__HK.setMus(1)')
        im = R12.stack(rows)
        im.save(os.path.join(OUT, 'r23b_game.png'), optimize=True)
        print('r23b_game.png', im.size, 'fight', fgot, 'errors', [e for pg in GP.values() for e in pg.errs][:3])
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
