# egyptr27b.py [new.html] [old.html] [--quick]: round 27b's numbers and pictures (owner: "The background moves too fast: do some research into
# the equations that govern how much a backgrounds like ours should move ... We should keep the illusion of distance between that background
# and our walls and windows. If it is cheap we can add multiple backgrounds that scroll at different speeds and so simulate closeness and
# farness"), into egypt_themes/:
#   r27b_parallax.png  1. the depth equation: a camera Z0 from the play plane, a layer Z away: f = Z0/Z, and h = s f H, so f = h/(s H);
#                      2. the table: every layer of the twelve looks, what it shows, its drawn height h (measured on its canvas), the real
#                         height H, the factor before and what it implied (the height and the distance), the factor after and its depth;
#                      3. what moves how fast: the camera's speeds measured with the bot, and each kind of layer's screen speed before | after;
#                      4. before | after frame strips of a pan past the largest opening (100 px/s, the run's speed), four looks, Torchlight
#                         and Classic, crops that follow the opening (what slides past the window), every 0.4 s;
#                      5. the cost: a frame's render time with a big opening on the screen, before | after, both modes.
#   r27b_parallax.gif  in game, the bot running past openings, before | after, Torchlight.
#   r27b.json          the numbers.
# old.html defaults to round 27a's source (git show 952fdbd:dev/hourglass-keep.html). Run from dev/tools.
import io, json, math, os, subprocess, sys, tempfile, shutil, statistics as st
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
args = [x for x in sys.argv[1:] if not x.startswith('--')]
QUICK = '--quick' in sys.argv
NEW = os.path.abspath(args[0] if args else os.path.join(HERE, '..', 'hourglass-keep.html'))
OLD = args[1] if len(args) > 1 else None
OUTD = os.path.join(HERE, 'egypt_themes')
INK, TXT, DIM, OLDC, NEWC, GRID = (20, 16, 24), (250, 240, 215), (170, 160, 140), (226, 96, 70), (90, 160, 235), (60, 52, 62)
S = 51.5 / 1.75             # px a metre on the play plane (the prince: 1.75 m, 51.5 px)
Z0 = 6.52 / 2 / math.tan(math.radians(30))   # the camera's distance for a 60 degree vertical view of the 192 px (6.52 m) frame: 5.65 m
LOOKS = ['nun', 'west', 'blue', 'meroe', 'osiris', 'foggara', 'deffufa', 'wells', 'napata', 'aksum', 'hawara', 'shali']
# what each layer shows and its real size: (what, H in metres, what is measured: 'h' the drawn height over its ground, 'w' a width, or None:
# the depth is given (sky, clouds, water, the far ridge), source)
REAL = {
    ('nun', 'pcolon', 0): ('papyrus-bundle columns, far row', 3.0, 'w', 'hypostyle column ~3 m across (Karnak)'),
    ('nun', 'pcolon', 1): ('papyrus-bundle columns, near row', 3.0, 'w', 'hypostyle column ~3 m across (Karnak)'),
    ('nun', 'water', 0): ('the water at the near row', None, None, 'at the near columns'),
    ('nun', 'ropes', 0): ('ropes and slung jars', 1.4, 'jar', 'a large storage jar ~1.4 m'),
    ('west', 'qurn', 0): ('el-Qurn over the Theban hills', 345, 'h', 'el-Qurn ~420 m asl over a ~75 m plain'),
    ('west', 'pylons', 0): ('a temple\'s pylon towers', 24, 'h', 'Luxor\'s first pylon 24 m'),
    ('west', 'palms', 0): ('date palms', 18, 'h', 'Phoenix dactylifera 15-23 m'),
    ('blue', 'hills', 0): ('the desert\'s ridges', 150, 'h', 'desert edge ridges, ~150 m'),
    ('blue', 'steppyr', 0): ('Djoser\'s step pyramid', 62.5, 'h', 'Djoser 62.5 m'),
    ('blue', 'niched', 0): ('the niched enclosure wall', 10.5, 'h', 'Djoser\'s enclosure wall 10.5 m'),
    ('blue', 'palms', 0): ('date palms', 18, 'h', 'Phoenix dactylifera 15-23 m'),
    ('meroe', 'kushpyr', 0): ('the royal pyramids', 25, 'h', 'Meroe\'s pyramids 6-30 m'),
    ('meroe', 'chimneys', 0): ('furnace stacks', 30, 'h', '(art: tall brick stacks)'),
    ('meroe', 'furnaces', 0): ('the smelting halls', 12, 'h', '(art: halls with roofs)'),
    ('meroe', 'smoke', 0): ('the town\'s smoke', None, None, 'between pyramids and stacks'),
    ('meroe', 'ropes', 0): ('ropes and slung baskets', 1.4, 'jar', 'an ore basket ~1.4 m'),
    ('osiris', 'obelisks', 0): ('obelisks', 29.5, 'h', 'Hatshepsut\'s at Karnak 29.5 m'),
    ('osiris', 'shrines', 0): ('lit shrines', 7, 'h', 'a bark shrine ~6-7 m'),
    ('osiris', 'trees', 0): ('sycomore figs', 15, 'h', 'Ficus sycomorus to ~20 m'),
    ('foggara', 'escarp', 0): ('the Messak escarpment', 150, 'h', 'a scarp 100-300 m'),
    ('foggara', 'mounds', 0): ('foggara shaft mounds, far', 15, 'sp', 'shafts 10-20 m apart'),
    ('foggara', 'mounds', 1): ('foggara shaft mounds, near', 15, 'sp', 'shafts 10-20 m apart'),
    ('foggara', 'palms', 0): ('date palms', 18, 'h', 'Phoenix dactylifera 15-23 m'),
    ('deffufa', 'dunes', 0): ('dunes', 25, 'h', 'dunes 20-50 m'),
    ('deffufa', 'deffufa', 0): ('the Western Deffufa', 19, 'h', 'Western Deffufa 18-20 m'),
    ('deffufa', 'huts', 0): ('round huts', 4.5, 'h', 'a thatched hut ~4-5 m'),
    ('deffufa', 'acacia', 0): ('umbrella acacias', 9, 'h', 'Vachellia tortilis 4-20 m'),
    ('wells', 'qurn', 0): ('el-Qurn', 345, 'h', 'el-Qurn ~420 m asl over a ~75 m plain'),
    ('wells', 'cliffs', 0): ('the Valley\'s cliffs', 100, 'h', 'limestone cliffs ~100 m'),
    ('wells', 'hills', 0): ('the near scree slopes', 15, 'h', 'scree and spoil ~15 m'),
    ('napata', 'barkal', 0): ('Gebel Barkal', 98, 'h', 'Gebel Barkal 98 m'),
    ('napata', 'kushpyr', 0): ('Barkal\'s pyramids', 18, 'h', 'Napatan pyramids 10-20 m'),
    ('napata', 'water', 0): ('the Nile', None, None, 'between pyramids and palms'),
    ('napata', 'palms', 0): ('date palms', 18, 'h', 'Phoenix dactylifera 15-23 m'),
    ('aksum', 'ambas', 0): ('flat-topped ambas', 300, 'h', 'ambas some hundreds of m'),
    ('aksum', 'stelae', 0): ('the storeyed stelae', 24, 'h', 'Ezana\'s stela ~21 m, the Obelisk 24.6 m'),
    ('aksum', 'trees', 0): ('trees', 15, 'h', 'highland trees ~15 m'),
    ('hawara', 'ruinpyr', 0): ('the worn mudbrick pyramid', 30, 'h', 'Hawara 58 m built, its core ~30 m'),
    ('hawara', 'water', 0): ('the Fayum\'s water', None, None, 'between pyramid and walls'),
    ('hawara', 'labwalls', 0): ('the Labyrinth\'s broken walls', 8, 'h', 'walls and piers ~8 m'),
    ('hawara', 'palms', 0): ('date palms', 18, 'h', 'Phoenix dactylifera 15-23 m'),
    ('shali', 'hills', 0): ('Siwa\'s hills', 150, 'h', 'hills ~150 m'),
    ('shali', 'saltlake', 0): ('a salt lake', None, None, 'between hills and town'),
    ('shali', 'shali', 0): ('Shali on its rock', 40, 'h', 'the town on its rock ~40 m'),
    ('shali', 'palms', 0): ('date palms', 18, 'h', 'Phoenix dactylifera 15-23 m'),
}
FIXED = {'stars': ('stars, the moon', 'at infinity'), 'clouds': ('clouds', 'km off and high'), 'farridge': ('a far ridge in the air\'s colour', 'km off: aerial perspective'),
         'near': ('the near band: blocks, scrub or reeds', '1-4 m things, h 7-30 px')}

LAYERS = r'''([look])=>{const H=__HK,art=H.BGART[look],ly=H.bgLayers(look,0).filter(l=>!l.moon),out=[];
  art.layers.forEach((a,i)=>{const c=ly[i].c,g=c.getContext('2d'),w=c.width,h=c.height,sc=w/640,d=g.getImageData(0,0,w,h).data;let top=h;
    for(let x=0;x<w;x+=2)for(let y=0;y<top;y++)if(d[(y*w+x)*4+3]>110){top=y;break;}
    out.push({kind:a.kind,f:a.f,lift:a.lift||0,w:a.w||0,gap:a.gap||0,sz:a.sz||1,top:top/sc});});return out;}'''


def old_src(tmp):
    if OLD:
        return os.path.abspath(OLD)
    fn = os.path.join(tmp, '_r27a.html')
    open(fn, 'w', encoding='utf-8').write(subprocess.run(['git', 'show', '952fdbd:dev/hourglass-keep.html'], cwd=HERE, capture_output=True, text=True, check=True).stdout)
    return fn


def page(b, src, mode='torch', dpr=2):
    pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=dpr)
    pg.errs = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e)))
    pg.goto('file://' + src)
    pg.wait_for_timeout(700)
    pg.add_script_tag(path=os.path.join(HERE, 'bot.js'))
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.body.classList.remove('panelOpen')")
    pg.evaluate("m=>{__HK.S.set.lightMode=m;}", mode)
    return pg


def table_rows(pn, po):
    rows = []
    for look in LOOKS:
        ln, lo = pn.evaluate(LAYERS, [look]), po.evaluate(LAYERS, [look])
        olds = iter(lo)
        seen = {}
        for L in ln:
            o = None if L['kind'] in ('farridge', 'near') else next(olds)
            k = seen.get(L['kind'], 0); seen[L['kind']] = k + 1
            B = 176 - L['lift']
            r = {'look': look, 'kind': L['kind'], 'fo': o['f'] if o else None, 'fn': L['f'], 'h': None, 'H': None}
            if (look, L['kind'], k) in REAL:
                what, H, how, src = REAL[(look, L['kind'], k)]
                r['what'], r['src'] = what, src
                if how == 'h':
                    r['h'] = B - L['top']
                elif how == 'w':
                    r['h'] = L['w']
                elif how == 'jar':
                    r['h'] = 10.4 if look == 'nun' else 12
                elif how == 'sp':
                    r['h'] = 11.5 * L['sz']
                r['H'] = H
            else:
                r['what'], r['src'] = FIXED.get(L['kind'], (L['kind'], ''))
            if r['h'] and r['H']:
                r['fs'] = r['h'] / (S * r['H'])          # the factor the drawing's size says
                r['Ho'] = r['h'] / (S * r['fo']) if r['fo'] else None   # the height the old factor implied
            r['dn'] = Z0 / r['fn'] - Z0 if r['fn'] > 0 else float('inf')
            r['do'] = (Z0 / r['fo'] - Z0 if r['fo'] > 0 else float('inf')) if r['fo'] is not None else None
            rows.append(r)
    return rows


def dist(d):
    if d is None:
        return '-'
    if d == float('inf'):
        return 'inf'
    return '%.1f km' % (d / 1000) if d >= 1000 else '%.0f m' % d


def table_img(rows, W):
    lh = 15
    im = Image.new('RGB', (W, lh * (len(rows) + 5) + 12), INK)
    d = ImageDraw.Draw(im)
    X = [6, 64, 128, 400, 446, 498, 556, 640, 730, 800, 880, 960]
    H = ('look', 'kind', 'shows', 'h px', 'H m', 'f=h/sH', 'f before', 'it implied', 'd before', 'f after', 'd after', 'source of H')
    for x, h in zip(X, H):
        d.text((x, 4), h, fill=TXT)
    y = 4 + lh + 2
    last = None
    for r in rows:
        if r['look'] != last:
            d.line((6, y - 1, W - 6, y - 1), fill=GRID); last = r['look']
        cells = [r['look'], r['kind'], r['what'][:44], '%.0f' % r['h'] if r['h'] else '-', '%g' % r['H'] if r['H'] else '-',
                 '%.4f' % r['fs'] if r.get('fs') else '-', '%.3f' % r['fo'] if r['fo'] is not None else 'new',
                 ('H %.0f m' % r['Ho']) if r.get('Ho') else '-', dist(r['do']), '%.4g' % r['fn'], dist(r['dn']), r['src'][:42]]
        for i, (x, c) in enumerate(zip(X, cells)):
            d.text((x, y), c, fill=OLDC if i in (6, 7, 8) else NEWC if i in (9, 10) else TXT if i < 3 else DIM)
        y += lh
    for t in ('h: the drawn height of the tallest thing in the layer over its own ground (game px; for columns their width, for the mounds their spacing, for the '
              'ropes the slung jar), measured on the layer\'s canvas. H: what it shows, in metres.',
              'f = h/(s H) with s = 29.4 px/m (the prince 1.75 m = 51.5 px): the factor at which a thing that big, drawn that big, moves (pinhole: f = Z0/Z). '
              '"It implied": the height the old factor gave it.',
              'd: the depth behind the play plane, Z - Z0, Z0 = 5.65 m (a 60 degree vertical view of the 6.5 m frame). The new factors follow f = h/(sH) within '
              'the order of the layers (far to near).'):
        d.text((6, y + 4), t, fill=DIM); y += lh
    return im


def diagram(W, rows):
    H = 300
    im = Image.new('RGB', (W, H), INK)
    d = ImageDraw.Draw(im)
    d.text((6, 4), 'The equation. Seen from above: the camera at C, the play plane (walls, windows, the prince) Z0 away, a layer Z away. The camera pans by x: a '
           'point of the play plane moves x on the screen,', fill=TXT)
    d.text((6, 20), 'a point of the layer x Z0/Z (pinhole: screen x\' = Z0 X / Z). So the layer\'s factor is f = Z0/Z and it slides past the windows by 1 - f. '
           'A thing H m high at Z is drawn h = s f H px (s on the play plane):', fill=TXT)
    d.text((6, 36), 'f = h / (s H): no lens to choose. Vertically (round 25e) each opening looks out from its own storey: the same equation for an eye that '
           'travels BG_VK = 0.2 of the camera\'s height (slide 0.2 (1 - f)).', fill=TXT)
    # the sketch
    ox, oy = 40, 70
    d.ellipse((ox - 5, oy + 105, ox + 5, oy + 115), fill=TXT); d.text((ox - 4, oy + 120), 'C', fill=TXT)
    for k, (xx, lab, col) in enumerate(((140, 'play plane (Z0 = 5.65 m)', TXT), (260, 'palms Z = 43 m (f .13)', NEWC), (420, 'pylons Z = 81 m (f .07)', NEWC), (600, 'el-Qurn Z = 1.1 km (f .005)', NEWC))):
        d.line((ox + xx, oy, ox + xx, oy + 220), fill=col)
        d.text((ox + xx + 4 - (150 if k == 3 else 0), oy + 206 if k == 3 else oy), lab, fill=col)
    # two camera positions a pan apart, and their lines of sight to one point of the play plane and one of el-Qurn: the near one swings far
    for cy, c in ((oy + 110, (200, 190, 170)), (oy + 70, (130, 120, 110))):
        d.ellipse((ox - 3, cy - 3, ox + 3, cy + 3), outline=c)
        d.line((ox, cy, ox + 140, oy + 150), fill=c)
        d.line((ox, cy, ox + 600, oy + 60), fill=c)
    d.text((ox - 30, oy + 60), 'pan', fill=DIM); d.line((ox - 18, oy + 106, ox - 18, oy + 74), fill=DIM)
    # the plot: f against depth on a log scale, every layer before (red) and after (blue)
    px0, px1, py0, py1 = 720, W - 20, 70, 270
    d.rectangle((px0, py0, px1, py1), outline=GRID)
    lo, hi = math.log10(10), math.log10(5000)
    X = lambda dd: px0 + (px1 - px0) * (math.log10(max(10, min(5000, dd))) - lo) / (hi - lo)
    Y = lambda f: py1 - (py1 - py0) * min(1, f / 0.35)
    pts = [(dd, Z0 / (Z0 + dd)) for dd in [10 * 1.1 ** k for k in range(70)] if dd <= 5000]
    d.line([(X(a), Y(b)) for a, b in pts], fill=TXT, width=1)
    for t in (10, 30, 100, 300, 1000, 3000):
        d.line((X(t), py1, X(t), py1 + 4), fill=DIM); d.text((X(t) - 8, py1 + 6), ('%dk' % (t // 1000)) if t >= 1000 else str(t), fill=DIM)
    for f in (0.1, 0.2, 0.3):
        d.line((px0 - 4, Y(f), px0, Y(f)), fill=DIM); d.text((px0 - 30, Y(f) - 6), '%.1f' % f, fill=DIM)
    for r in rows:
        if r.get('fs') and r['fo']:
            dd = Z0 / r['fs'] - Z0
            d.ellipse((X(dd) - 2, Y(r['fo']) - 2, X(dd) + 2, Y(r['fo']) + 2), fill=OLDC)
        if r['fn'] > 0 and r['dn'] < 1e6:
            d.ellipse((X(r['dn']) - 2, Y(r['fn']) - 2, X(r['dn']) + 2, Y(r['fn']) + 2), fill=NEWC)
    d.text((px0, py0 - 14), 'f = Z0/(Z0+d) against d (m, log); red: old factors at the depth the drawing\'s size gives, blue: new', fill=DIM)
    return im


def speeds_img(W, cam, rows):
    lh = 15
    im = Image.new('RGB', (W, lh * 14), INK)
    d = ImageDraw.Draw(im)
    vx, vy = cam['vx_p90'], cam['vy_p90']
    d.text((6, 4), 'What moves how fast. The camera (the bot, floors 5, 9, 14, 21, 26, 30): across %.0f px/s moving (median), %.0f (p90), %.0f peak (a turn); '
           'up and down %.0f%% of the time, %.0f px/s median, %.0f p90, %.0f peak.' % (cam['vx_med'], vx, cam['vx_max'], cam['vy_frac'] * 100, cam['vy_med'], vy, cam['vy_max']), fill=TXT)
    d.text((6, 20), 'On the screen a layer moves f times the walls\' speed across, (1 - 0.2 (1 - f)) times it up and down (round 25e). At the run\'s 100 px/s '
           '(205 CSS px/s on a phone, 2.05 px a game px):', fill=TXT)
    X = [6, 230, 330, 430, 560, 690]
    for x, h in zip(X, ('kind of layer', 'f before', 'f after', 'across before', 'across after', 'up/down (both)')):
        d.text((x, 40), h, fill=TXT)
    groups = [('sky, stars, moon, sun', ['stars']), ('clouds', ['clouds']), ('mountains, escarpments, ambas', ['qurn', 'escarp', 'ambas', 'hills<']),
              ('monuments', ['steppyr', 'kushpyr', 'barkal', 'ruinpyr', 'pylons', 'deffufa', 'obelisks', 'stelae', 'shali', 'cliffs']),
              ('walls, huts, shrines, mounds, scree', ['niched', 'huts', 'shrines', 'labwalls', 'mounds', 'dunes', 'hills>']),
              ('palms and trees', ['palms', 'trees', 'acacia']), ('interiors\' near ropes', ['ropes']), ('new: far ridge', ['farridge']), ('new: near band', ['near'])]
    y = 58
    for name, ks in groups:
        rs = [r for r in rows if r['kind'] in ks or (r['kind'] + ('<' if r['fn'] < 0.05 else '>')) in ks]
        fo = [r['fo'] for r in rs if r['fo'] is not None]
        fn = [r['fn'] for r in rs]
        rng = lambda v: '-' if not v else ('%.3g' % min(v) if min(v) == max(v) else '%.3g-%.3g' % (min(v), max(v)))
        sp = lambda v: '-' if not v else ('%.1f' % (min(v) * 100) if min(v) == max(v) else '%.1f-%.1f' % (min(v) * 100, max(v) * 100))
        cells = [name, rng(fo), rng(fn), sp(fo) + ' px/s', sp(fn) + ' px/s', '%.0f-%.0f%%' % (100 * (0.8 + 0.2 * min(fn)), 100 * (0.8 + 0.2 * max(fn)))]
        for i, (x, c) in enumerate(zip(X, cells)):
            d.text((x, y), c, fill=OLDC if i in (1, 3) else NEWC if i in (2, 4) else TXT)
        y += lh
    d.text((6, y + 4), 'The vertical is round 25e\'s rule (each opening keeps its own storey\'s view; its slide is held under 1 px a frame in descents, so BG_VK stays 0.2): '
           'unchanged but for f. Sky and sun: 0.985 > 1 across (f 0.015 > 0), 0.803 > 0.8 up and down.', fill=DIM)
    return im


SETUP = r'''([n,seed])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS)H.S.hints[id]=1;H.load(n,seed,true);H.banner=null;let T=1e6;H.setClock(()=>T);
  let a=12345;Math.random=()=>{a=(a*16807)%2147483647;return a/2147483647;};H.P.x=-9999;H.P.inv=1e9;for(const e of H.G)e.x=-9999;H.mode='play';if(H.GLP)H.GLP.pipe=false;
  const ops=H.openingsIn(-1e9,1e9,-1e9,1e9);let best=null;for(const o of ops){const a=o[2]*o[3];if(!o[4]&&(!best||a>best[2]*best[3]))best=o;}if(!best)best=ops[0];
  return [best,H.bgAnchor(best)];}'''
PAN = r'''([o,an,dx])=>{const H=__HK;H.cam.x=o[0]+o[2]/2-H.viewW/2-80+dx;H.cam.y=an;H.cam.snap=false;H.render();H.render();const X=H.XF,cv=document.getElementById('game'),R=cv.getBoundingClientRect();
  const k=R.width/cv.width;return [(o[0]*X.VZ-X.camD)*k,(o[1]*X.VZ-X.camDY)*k,o[2]*X.VZ*k,o[3]*X.VZ*k];}'''
STRIPS = [(5, 'west'), (9, 'blue'), (25, 'deffufa'), (45, 'shali')]


def strips(b, srcs):
    out = []
    for mode in ('torch', 'classic'):
        for n, look in (STRIPS[:2] if QUICK else STRIPS):
            row = []
            for t, s in srcs.items():
                pg = page(b, s, mode)
                o, an = pg.evaluate(SETUP, [n, 1])
                cr = []
                for dx in (0, 40, 80, 120, 160):
                    x, y, w, h = pg.evaluate(PAN, [o, an, dx])
                    im = Image.open(io.BytesIO(pg.screenshot())).convert('RGB')
                    m = 8
                    cr.append(im.crop((int((x - m) * 2), int((y - m) * 2), int((x + w + m) * 2), int((y + h + m) * 2))))
                if pg.errs:
                    print('errors', t, pg.errs[:3])
                pg.close()
                row.append((t, cr))
            ch = max(c.height for _, cr in row for c in cr)
            cw = max(c.width for _, cr in row for c in cr)
            sc = min(1.0, 104 / ch, 200 / cw)
            tw, th = int(cw * sc), int(ch * sc)
            im = Image.new('RGB', (150 + 5 * (tw + 4), 2 * (th + 4) + 4), INK)
            d = ImageDraw.Draw(im)
            d.text((4, 2), '%s (floor %d)' % (look, n), fill=TXT)
            d.text((4, 18), 'Torchlight' if mode == 'torch' else 'Classic', fill=DIM)
            for j, (t, cr) in enumerate(row):
                y0 = 2 + j * (th + 4)
                d.text((90, y0 + th // 2 - 6), 'before' if t == 'before' else 'after', fill=OLDC if t == 'before' else NEWC)
                for i, c in enumerate(cr):
                    im.paste(c.resize((int(c.width * sc), int(c.height * sc)), Image.LANCZOS), (150 + i * (tw + 4), y0))
            out.append(im)
    return out


COST = r'''([o,an,mode,N])=>{const H=__HK;H.S.set.lightMode=mode;const t=[];for(let i=0;i<N;i++){H.cam.x=o[0]+o[2]/2-H.viewW/2+(i%40);H.cam.y=an;const a=performance.now();H.render();t.push(performance.now()-a);}
  t.sort((a,b)=>a-b);return t[Math.floor(t.length/2)];}'''


def timing(b, srcs):
    """median render time of a frame with the largest opening of the floor on the screen (classic and Torchlight), before | after, the two
    pages measured in turn, three rounds"""
    res = {}
    pages = {t: page(b, s, 'classic', dpr=2) for t, s in srcs.items()}
    for n, look in STRIPS:
        oa = {t: pg.evaluate(SETUP, [n, 1]) for t, pg in pages.items()}
        for pg in pages.values():
            pg.evaluate("()=>{const H=__HK;const pn=Performance.prototype.now;H.setClock(()=>pn.call(performance));}")
        for mode, N in (('classic', 120), ('torch', 20)):
            for t, pg in pages.items():
                pg.evaluate(COST, [oa[t][0], oa[t][1], mode, 5])
            for rnd in range(3):
                for t, pg in pages.items():
                    res.setdefault(mode, {}).setdefault(t, []).append(pg.evaluate(COST, [oa[t][0], oa[t][1], mode, N]))
    for pg in pages.values():
        pg.close()
    return {m: {t: round(st.median(v), 2) for t, v in d.items()} for m, d in res.items()}


RECORD = r'''([n,seed,F])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS)H.S.hints[id]=1;
  const g=botGen(n,seed,{});const out=[];let r=g.next(),f=0;
  while(!r.done&&f<F){H.tick(1);f++;const c=H.cam;const ops=H.openingsIn(c.x,c.x+H.viewW,c.y,c.y+192);let a=0;for(const o of ops)a+=o[2]*o[3];out.push([+c.x.toFixed(2),+c.y.toFixed(2),a]);r=g.next();}
  return out;}'''


def camstats(b, src):
    pg = page(b, src, 'classic', dpr=1)
    vx, vy, n, nm = [], [], 0, 0
    paths = {}
    for fl in ((5, 9) if QUICK else (5, 9, 14, 21, 26, 30)):
        c = pg.evaluate(RECORD, [fl, 1, 60 * 120])
        paths[fl] = c
        for i in range(1, len(c)):
            ax, ay = abs(c[i][0] - c[i - 1][0]) * 60, abs(c[i][1] - c[i - 1][1]) * 60
            n += 1
            if ax > 5:
                vx.append(ax)
            if ay > 5:
                vy.append(ay)
    pg.close()
    q = lambda a, p: sorted(a)[int(len(a) * p)]
    return {'vx_med': q(vx, .5), 'vx_p90': q(vx, .9), 'vx_max': max(vx), 'vy_med': q(vy, .5), 'vy_p90': q(vy, .9), 'vy_max': max(vy), 'vy_frac': len(vy) / n}, paths


GCROP = (0, 0, 852, 393)


def gif(b, srcs, path, fl):
    # the 6 s with the most opening area on the screen while the camera moves across
    best, bi = -1, 0
    L = 330
    for i in range(0, len(path) - L, 10):
        mv = abs(path[i + L][0] - path[i][0])
        a = sum(p[2] for p in path[i:i + L]) / L
        if mv > 150 and a > best:
            best, bi = a, i
    frames = {}
    for t, s in srcs.items():
        pg = page(b, s, 'torch', dpr=1)
        pg.evaluate("([n,s])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS){H.S.hints[id]=1;if(H.S.learned)H.S.learned[id]=1;}window.__g=botGen(n,s,{});window.__f=0;window.__r=__g.next();if(H.GLP)H.GLP.pipe=false;}", [fl, 1])
        seq = []
        for f in range(bi, bi + L, 5):
            pg.evaluate("t=>{const H=__HK;while(__f<t&&!__r.done){H.tick(1);__f++;__r=__g.next();}H.render();}", f)
            seq.append(Image.open(io.BytesIO(pg.screenshot())).convert('RGB').crop(GCROP))
        pg.close()
        frames[t] = seq
    out = []
    for a, c in zip(frames['before'], frames['after']):
        a = a.resize((a.width // 2, a.height // 2), Image.LANCZOS); c = c.resize((c.width // 2, c.height // 2), Image.LANCZOS)
        im = Image.new('RGB', (a.width + c.width + 6, a.height + 16), INK)
        d = ImageDraw.Draw(im)
        d.text((4, 2), 'before (27a)', fill=OLDC); d.text((a.width + 10, 2), 'after (27b): factors from depth, a near band', fill=NEWC)
        im.paste(a, (0, 16)); im.paste(c, (a.width + 6, 16))
        out.append(im.quantize(colors=64, method=Image.MEDIANCUT, dither=Image.NONE))
    fn = os.path.join(OUTD, 'r27b_parallax.gif')
    out[0].save(fn, save_all=True, append_images=out[1:], duration=83, loop=0, optimize=True)
    return fn, len(out), bi


if __name__ == '__main__':
    tmp = tempfile.mkdtemp()
    try:
        srcs = {'before': old_src(tmp), 'after': NEW}
        with sync_playwright() as p:
            b = p.chromium.launch()
            pn, po = page(b, srcs['after'], 'classic'), page(b, srcs['before'], 'classic')
            rows = table_rows(pn, po)
            pn.close(); po.close()
            cam, paths = camstats(b, srcs['after'])
            tm = timing(b, srcs)
            srow = strips(b, srcs)
            gfn, gn, gi = gif(b, srcs, paths[5], 5)
            b.close()
        W = 1240
        head = Image.new('RGB', (W, 40), INK)
        d = ImageDraw.Draw(head)
        d.text((6, 4), 'Round 27b: the view through the openings, each layer at the depth it shows (owner: "The background moves too fast ... keep the illusion of '
               'distance between that background and our walls and windows").', fill=TXT)
        d.text((6, 20), 'Cause: the factors were 3 to 10 times too large for what the layers show, so the land read as a small painted flat a few metres behind the '
               'window. Now f = h/(s H): far land 0.004-0.012, monuments 0.03-0.11, palms 0.12-0.16, a new near band 0.25.', fill=TXT)
        cst = Image.new('RGB', (W, 36), INK)
        d = ImageDraw.Draw(cst)
        d.text((6, 4), 'Cost: a frame\'s render with the largest opening of floors 5, 9, 25, 45 on the screen (median ms, this Mac, headless; Torchlight is software '
               'WebGL here): Classic %.2f > %.2f, Torchlight %.2f > %.2f.' % (tm['classic']['before'], tm['classic']['after'], tm['torch']['before'], tm['torch']['after']), fill=TXT)
        d.text((6, 20), 'One more layer (two in five looks) is one more copy of a cached canvas into the low-resolution backdrop target: no new full-screen pass.', fill=DIM)
        mid = Image.new('RGB', (W, 20), INK)
        ImageDraw.Draw(mid).text((6, 4), 'A pan past the largest opening at the run\'s 100 px/s, crops that follow the opening every 0.4 s: what slides past the window, '
                                 'before | after (no figures, a frozen clock).', fill=TXT)
        parts = [head, diagram(W, rows), table_img(rows, W), speeds_img(W, cam, rows), cst, mid] + srow
        sheet = Image.new('RGB', (W, sum(r.height + 6 for r in parts)), INK)
        y = 0
        for r in parts:
            sheet.paste(r.crop((0, 0, min(W, r.width), r.height)), (0, y))
            y += r.height + 6
        sheet.save(os.path.join(OUTD, 'r27b_parallax.png'), optimize=True)
        json.dump({'rows': rows, 'cam': cam, 'timing': tm, 'gif_from_frame': gi}, open(os.path.join(HERE, 'r27b.json'), 'w'), indent=1, default=str)
        print('wrote r27b_parallax.png', sheet.size, gfn, gn, 'frames', round(os.path.getsize(gfn) / 1e6, 2), 'MB')
        print('cam', cam)
        print('timing', tm)
        for r in rows:
            print('%-8s %-9s h %-6s H %-6s fs %-8s fo %-6s Ho %-7s fn %-6s dn %s' % (r['look'], r['kind'], r['h'] and round(r['h'], 1), r['H'], r.get('fs') and round(r['fs'], 4),
                  r['fo'], r.get('Ho') and round(r['Ho'], 1), r['fn'], dist(r['dn'])))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
