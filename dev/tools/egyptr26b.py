# egyptr26b.py [new.html] [old.html]: round 26b's pictures (owner, a phone shot of the prince hanging from a ledge in Torchlight, the upper
# back behind the shoulder circled: "The last photo shows the prince with a hump of sorts. I don't know if it is because the lights or an
# error in the measurements. In my opinion I'd reduce with 1px the back"), into egypt_themes/r26b_back.png.
#   1. 10x: hang, jumpUp (the reach), the climb's start: before | after, lit from behind (as the owner's lamp) and as a silhouette, the back's
#      contour from the nape to the waist marked (red; before's in blue on after);
#   2. 4x: hang, jumpUp, climb, slide, fall, stand, run: before | after with the contours;
#   3. the numbers: ra (how far the trunk is shaped for raised arms, 0..1), the back's depth behind the spine's line at U .62/.76/.88/.96
#      (px), and on the silhouette how far the upper back stands behind the waist's narrowest point and behind the neck's back (px);
#   4. in game at the phone's resolution (852x393 CSS px at 2x), Torchlight and Classic, the bot stopped at a jump up to a ledge: jumping up,
#      hanging, climbing; 1:1 and a 3x crop, before | after.
# old.html defaults to round 26a's source (git show e9d2a48:dev/hourglass-keep.html). Run from dev/tools. CMU mocap (mocap.cs.cmu.edu, NSF
# EIA-0196217); ANSUR II.
import io, os, subprocess, sys, tempfile, shutil, base64
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
NEW = os.path.abspath(a[0] if a else os.path.join(HERE, '..', 'hourglass-keep.html'))
OLD = a[1] if len(a) > 1 else None
OUT = os.path.join(HERE, 'egypt_themes', 'r26b_back.png')
INK = (20, 16, 24)
TXT = (250, 240, 215)
BG = (232, 220, 200)
EXPORT = 'window.__R23={skel,PS,mk,RP,climbFrame,figDraw,PAL_HERO,GFX,LEN};'
TGX = ('TG={U,TS,fo,bo,sp,F:u=>iv(fo,u),B:u=>iv(bo,u),fl,ra};', 'TG={U,TS,fo,bo,sp,F:u=>iv(fo,u),B:u=>iv(bo,u),fl,ra};window.__TG=TG;')
POSES = [('PS.hang', 'hang'), ('PS.reach', 'jumpUp (reach)'), ('climb 0.05', 'climb start'), ('PS.slide', 'slide'), ('PS.fall', 'fall'),
         ('PS.stand', 'stand'), ('run 0.25', 'run')]
BIG = 3
# a figure facing right at (x, y) in a W x Hh box at scale S; mode 'lit' (a lamp behind him, as the owner's) or 'mono' (the silhouette).
# Returns the picture, the pixel rows of the head's centre and the hip joint, and the trunk's numbers (ra, bo)
FIG = r'''([spec,S,W,Hh,x,y,mode])=>{const F=window.__R23;let p,dx=0,dy=0;const [k,v]=spec.split(' ');
 if(spec.startsWith('PS.'))p=F.PS[spec.slice(3)];else if(k==='run')p=F.RP(+v);
 else if(k==='climb'){const f=F.climbFrame({x0:-6,y0:57,x1:10,y1:0},+v);p=f.p;dx=f.x;dy=f.y;}
 p=Object.assign(F.mk({}),p);F.GFX().hd=true;const s=F.skel(p);
 const cv=document.createElement('canvas');cv.width=W*S;cv.height=Hh*S;const c=cv.getContext('2d');c.fillStyle=mode==='mono'?'#ffffff':'#e8dcc8';c.fillRect(0,0,cv.width,cv.height);c.scale(S,S);
 const o={hasSword:true,time:0};if(mode==='mono')o.mono='#000000';else o.lt={dir:-1,col:'255,205,150',k:0.6};
 F.figDraw(c,x+dx,y+dy,1,p,F.PAL_HERO,o);const T=window.__TG,y0=y+dy-s.hipH;
 return [cv.toDataURL('image/png'),(y0+s.hd[1])*S,y0*S,T.ra,[0.62,0.76,0.88,0.96].map(u=>T.B(u))];}'''


def src_of(fn, tmp, tag):
    s = open(fn, encoding='utf-8').read()
    assert TGX[0] in s
    s = s.replace(TGX[0], TGX[1])
    i = s.find('window.__HK={')
    out = os.path.join(tmp, '_r26b_%s.html' % tag)
    open(out, 'w', encoding='utf-8').write(s[:i] + EXPORT + s[i:])
    return out


def old_src(tmp):
    if OLD:
        return os.path.abspath(OLD)
    fn = os.path.join(tmp, '_r26a.html')
    open(fn, 'w', encoding='utf-8').write(subprocess.run(['git', 'show', 'e9d2a48:dev/hourglass-keep.html'], cwd=HERE, capture_output=True, text=True, check=True).stdout)
    return fn


def img(u):
    return Image.open(io.BytesIO(base64.b64decode(u.split(',')[1]))).convert('RGB')


def contour(mono, ya, yb):
    """the back's contour: the leftmost dark pixel of each row from the head's centre to the hip joint (the figure faces right)"""
    px = mono.load()
    out = []
    for yy in range(max(0, int(ya)), min(mono.height, int(yb))):
        for xx in range(mono.width):
            if px[xx, yy][0] < 128:
                out.append((xx, yy))
                break
    return out


def measures(pts, S, ya, yb):
    """on the silhouette, px at 1x: how far the upper back stands behind the waist's narrowest point, and behind the neck's back (the
    rightmost back point in the top quarter of the span, under the head)"""
    n = len(pts)
    if n < 8:
        return None
    lo = [p for p in pts if p[1] > ya + (yb - ya) * 0.55]
    up = [p for p in pts if ya + (yb - ya) * 0.3 < p[1] <= ya + (yb - ya) * 0.75]
    nk = [p for p in pts if ya + (yb - ya) * 0.12 < p[1] <= ya + (yb - ya) * 0.35]
    if not lo or not up or not nk:
        return None
    back = min(p[0] for p in up)
    waist = max(p[0] for p in lo)
    neck = max(p[0] for p in nk)
    return (waist - back) / S, (neck - back) / S


def mark(im, pts, col, w=2):
    if len(pts) > 1:
        ImageDraw.Draw(im).line(pts, fill=col, width=w)


def label(im, t, xy=(4, 2), col=TXT, bg=(0, 0, 0)):
    d = ImageDraw.Draw(im)
    d.rectangle((xy[0] - 2, xy[1] - 1, xy[0] + 6 * len(t) + 4, xy[1] + 12), fill=bg)
    d.text(xy, t, fill=col)
    return im


def figs(pg, spec, S, W, Hh, x, y):
    u, ya, yb, ra, bo = pg.evaluate(FIG, [spec, S, W, Hh, x, y, 'lit'])
    um = pg.evaluate(FIG, [spec, S, W, Hh, x, y, 'mono'])[0]
    lit, mono = img(u), img(um)
    pts = contour(mono, ya, yb)
    return lit, mono, pts, ra, bo, measures(pts, S, ya, yb)


def posed(b, srcs):
    pages = {}
    for t, s in srcs.items():
        pg = b.new_page()
        pg.errs = []
        pg.on('pageerror', lambda e, pg=pg: pg.errs.append(str(e)))
        pg.goto('file://' + s)
        pg.wait_for_timeout(700)
        pages[t] = pg
    rows, nums = [], []
    # 10x: the three arms-up poses, lit and silhouette, before | after
    for spec, nm in POSES[:BIG]:
        R = {t: figs(pages[t], spec, 10, 44, 64, 22, 60 if spec != 'climb 0.05' else 6) for t in srcs}
        cells = []
        for t in ('before', 'after'):
            lit, mono, pts, ra, bo, m = R[t]
            for im in (lit, mono):
                if t == 'after':
                    mark(im, R['before'][2], (60, 110, 230), 2)
                mark(im, pts, (230, 40, 40), 3)
            cells += [label(lit, '%s, %s, 10x' % (nm, t)), label(mono, 'silhouette, %s' % t)]
        cw, ch = cells[0].size
        row = Image.new('RGB', (4 * cw + 3 * 6, ch), INK)
        for i, c in enumerate(cells):
            row.paste(c, (i * (cw + 6), 0))
        rows.append(row)
    # 4x: every pose, before over after
    for t in ('before', 'after'):
        cells = []
        for spec, nm in POSES:
            lit, mono, pts, ra, bo, m = figs(pages[t], spec, 4, 46, 72, 23, 66 if spec != 'climb 0.05' else 12)
            mark(lit, pts, (230, 40, 40), 2)
            cells.append(label(lit, '%s, %s' % (nm, t)))
            nums.append((t, nm, ra, bo, m))
        cw, ch = cells[0].size
        row = Image.new('RGB', (len(cells) * (cw + 4), ch), INK)
        for i, c in enumerate(cells):
            row.paste(c, (i * (cw + 4), 0))
        rows.append(row)
    for t, pg in pages.items():
        if pg.errs:
            print('errors', t, pg.errs[:3])
    return rows, nums


def table(nums, W):
    lh = 16
    im = Image.new('RGB', (W, lh * (len(nums) // 2 + 4)), INK)
    d = ImageDraw.Draw(im)
    X = [6, 150, 290, 600, 900]
    for x, h in zip(X, ('pose', 'ra: before > after', 'back behind the spine at U .62/.76/.88/.96, px', 'the same, after',
                        'silhouette, px at 1x: upper back behind the waist / behind the neck, before > after')):
        d.text((x, 4), h, fill=TXT)
    B = {nm: (ra, bo, m) for t, nm, ra, bo, m in nums if t == 'before'}
    y = 4 + lh + 4
    f = lambda q: '%.2f / %.2f' % q if q else '-'
    for t, nm, ra, bo, m in nums:
        if t != 'after':
            continue
        r0, b0, m0 = B[nm]
        for x, v in zip(X, (nm, '%.2f > %.2f' % (r0, ra), '  '.join('%.2f' % v for v in b0), '  '.join('%.2f' % v for v in bo), '%s  >  %s' % (f(m0), f(m)))):
            d.text((x, y), v, fill=TXT)
        y += lh
    return im


# ---------------- in game ----------------
# the bot stopped as it jumps up to a ledge he hangs from in plain view (no wall face in front of him: round 19's hidden hang is not the owner's)
STOP = r"""([n,sd])=>{const r=runBot(n,sd,{fight:false,stop:H=>{const p=H.P;if(p.state==='jumpUp'&&p.cs&&p.cs.ledge){const g=p.cs.ledge,b=H.L.base[(g.r+1)*H.L.cols+g.c];return !(g.s<0&&b===2);}return false;}});
  const H=__HK;if(H.P.state!=='jumpUp')return null;for(const k of ['l','r','u','d','j','g'])H.setKey('kb',k,false);H.I.buf={};window.__LG=H.P.cs.ledge;return {name:H.themeName(n)};}"""
STEP = r"""([k,key])=>{const H=__HK;if(key)H.setKey('kb',key,true);H.tick(k);if(key)H.setKey('kb',key,false);H.banner=null;__P.draw();return [__P.scr(H.P.x,H.P.y),H.P.state];}"""
SPOTS = [(5, 782), (9, 782), (13, 782), (17, 801), (6, 801), (7, 1), (8, 1)]


def game(b, srcs):
    import egyptr12 as R12
    tiles = {}
    hv = None
    for mo, mt in (('torch', 'Torchlight'), ('classic', 'Classic')):
        for t, s in srcs.items():
            pg = R12.page(b, s, mo)
            if hv is None:
                for n, sd in SPOTS:
                    if pg.evaluate(STOP, [n, sd]):
                        hv = (n, sd)
                        break
            for seq, lab, dy, zx, zy in (([(4, None)], 'jumping up', -55, 0, -42), ([(30, None)], 'hanging', -55, 0, -42), ([(30, None), (1, 'u'), (12, None)], 'climbing', -40, -14, -4)):
                pg.evaluate(STOP, [hv[0], hv[1]])
                for kk, key in seq:
                    xy, st = pg.evaluate(STEP, [kk, key])
                pg.evaluate("()=>{__HK.intro=0;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);__P.draw();}")
                full = R12.shot(pg)
                one = R12.crop(full, (xy[0], xy[1] + dy), 220, 330)
                z = R12.crop(full, (xy[0] + zx, xy[1] + dy + zy), 110, 110).resize((330, 330), Image.NEAREST)
                cell = Image.new('RGB', (220 + 4 + 330, 330), INK)
                cell.paste(one, (0, 0))
                cell.paste(z, (224, 0))
                label(cell, '%s, %s, %s (1:1 | 3x)' % (lab, mt, t))
                tiles[(lab, mt, t)] = cell
            if pg.errs:
                print('errors', mo, t, pg.errs[:3])
            pg.close()
    rows = []
    for lab in ('jumping up', 'hanging', 'climbing'):
        cells = [tiles[(lab, mt, t)] for mt in ('Torchlight', 'Classic') for t in ('before', 'after')]
        cw, ch = cells[0].size
        row = Image.new('RGB', (4 * cw + 3 * 6, ch), INK)
        for i, c in enumerate(cells):
            row.paste(c, (i * (cw + 6), 0))
        rows.append(row)
    return rows, hv


if __name__ == '__main__':
    tmp = tempfile.mkdtemp()
    try:
        raw = {'before': old_src(tmp), 'after': NEW}
        srcs = {t: src_of(s, tmp, t) for t, s in raw.items()}
        gsrc = {}
        for t, s in raw.items():   # the game's pages: a copy beside nothing else (bot.js is added by path)
            fn = os.path.join(tmp, '_r26b_game_%s.html' % t)
            shutil.copy(s, fn)
            gsrc[t] = fn
        with sync_playwright() as p:
            b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
            prow, nums = posed(b, srcs)
            grow, hv = game(b, gsrc)
            b.close()
        W = max(r.width for r in prow + grow)
        head = Image.new('RGB', (W, 46), INK)
        d = ImageDraw.Draw(head)
        d.text((6, 4), 'Round 26b: the hump behind the shoulder (owner: "the prince with a hump of sorts ... I\'d reduce with 1px the back"). Red: the back\'s '
               'contour, nape to hip; blue on "after": before\'s. Lamp behind him, as in the owner\'s shot.', fill=TXT)
        d.text((6, 22), 'Cause: geometry. A held hand is put on its grip by skel\'s two-bone solve, but the trunk\'s arms-up shaping read the clip\'s arm '
               'angles: the hang\'s arms are drawn overhead (2.69/2.83 rad) and the trunk was shaped for 1.81/1.98 (ra 0.13 of 1).', fill=TXT)
        mid = Image.new('RGB', (W, 22), INK)
        ImageDraw.Draw(mid).text((6, 4), 'In game at the phone\'s resolution, floor %d seed %d, the bot stopped at a jump up to a ledge: Torchlight before | after, '
                                 'Classic before | after' % hv, fill=TXT)
        parts = [head] + prow + [table(nums, W), mid] + grow
        sheet = Image.new('RGB', (W, sum(r.height + 8 for r in parts)), INK)
        y = 0
        for r in parts:
            sheet.paste(r, (0, y))
            y += r.height + 8
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        sheet.save(OUT, optimize=True)
        print('wrote', OUT, sheet.size)
        for t, nm, ra, bo, m in nums:
            print('%-6s %-16s ra %.2f bo %s sil %s' % (t, nm, ra, ['%.2f' % v for v in bo], m and ['%.2f' % v for v in m]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
