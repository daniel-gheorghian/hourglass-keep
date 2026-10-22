# egyptr28a.py [new.html] [old.html]: round 28a's picture (owner, a phone shot of floor 11, the Blue Chambers, Torchlight, the prince standing
# still, arms down, facing right, the upper back and the shoulder circled: "Prince hump in the first photo - I don't think the upper back sticks
# out as much in a muscular teen seen from the side"), into egypt_themes/r28a_back.png:
#   1. the owner's scene: floor 11 (the Blue Chambers), the prince standing beside a lamp, at 844x390 CSS px and DPR 3 (an iPhone in landscape),
#      Torchlight and Classic, before | after: a 1:1 crop of the device pixels and a 3x crop of his shoulders;
#   2. the profile measured: the stand at 10x (MUS 1.65), lit and as a silhouette, before | after, the back's contour from the nape to the hip
#      (red; before's in blue on after) and the drawn trunk's back offsets; and a table of the silhouette's numbers (px at 1x) for every pose
#      at the levels 1.0, 1.28 and 1.65: the upper back behind the seat's line, behind the nape, its bulge over the chord nape -> waist, and how
#      far under the shoulder joint the back is fullest;
#   3. a strip of poses before | after: drawn at 1x (shown 3x, nearest) and drawn at 3x (the phone's DPR);
#   4. the research summary.
# old.html defaults to the v74 release (hk_v74_release.html here or in the main checkout's dev/tools). Run from dev/tools. CMU mocap
# (mocap.cs.cmu.edu, NSF EIA-0196217); ANSUR II.
import io, os, sys, base64, math, tempfile, shutil
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
NEW = os.path.abspath(a[0] if a else os.path.join(HERE, '..', 'hourglass-keep.html'))
_old = os.path.join(HERE, 'hk_v74_release.html')
if not os.path.exists(_old):
    _old = os.path.join(HERE, '..', '..', '..', '..', '..', 'dev', 'tools', 'hk_v74_release.html')   # (from a worktree: the main checkout's)
OLD = os.path.abspath(a[1] if len(a) > 1 else _old)
OUT = os.path.join(HERE, 'egypt_themes', 'r28a_back.png')
INK = (20, 16, 24)
TXT = (250, 240, 215)
TGX = ('TG={U,TS,fo,bo,sp,F:u=>iv(fo,u),B:u=>iv(bo,u),fl,ra};', 'TG={U,TS,fo,bo,sp,F:u=>iv(fo,u),B:u=>iv(bo,u),fl,ra};window.__TG=TG;')
EXPORT = 'window.__R={skel,PS,mk,RP,walkPose,crawlPose,climbFrame,figDraw,PAL_HERO,GFX,LEN,setMus,getRD:()=>RD};'
# a figure facing right at (x, y) in a W x Hh box at scale S, bulk mus; mode 'lit' (a lamp behind him, as the owner's) or 'mono'
FIG = r'''([spec,S,W,Hh,x,y,mode,mus])=>{const F=window.__R;F.setMus(mus);let p,dx=0,dy=0;const [k,v]=spec.split(' ');
 if(spec.startsWith('PS.'))p=F.PS[spec.slice(3)];else if(k==='run')p=F.RP(+v);else if(k==='walk')p=F.walkPose(+v);else if(k==='crawl')p=F.crawlPose(+v);
 else if(k==='climb'){const f=F.climbFrame({x0:-6,y0:57,x1:10,y1:0},+v);p=f.p;dx=f.x;dy=f.y;}
 p=Object.assign(F.mk({}),p);F.GFX().hd=true;const s=F.skel(p);
 const cv=document.createElement('canvas');cv.width=W*S;cv.height=Hh*S;const c=cv.getContext('2d');c.fillStyle=mode==='mono'?'#ffffff':'#e8dcc8';c.fillRect(0,0,cv.width,cv.height);c.scale(S,S);
 const o={hasSword:true,time:0};if(mode==='mono')o.mono='#000000';else o.lt={dir:-1,col:'255,205,150',k:0.6};
 F.figDraw(c,x+dx,y+dy,1,p,F.PAL_HERO,o);const T=window.__TG,y0=y+dy-s.hipH;F.setMus(1.65);
 return [cv.toDataURL('image/png'),(y0+s.hd[1])*S,y0*S,(y0+s.sh[1])*S,T.U.map(u=>+T.B(u).toFixed(2))];}'''
POSES = [('PS.stand', 'stand'), ('PS.turn', 'turn'), ('walk 0', 'walk'), ('walk 0.5', 'walk .5'), ('run 0', 'run'), ('run 0.25', 'run .25'),
         ('run 0.5', 'run .5'), ('run 0.75', 'run .75'), ('PS.land', 'land'), ('PS.jumpS', 'jump'), ('PS.jumpR', 'run jump'), ('PS.fall', 'fall'),
         ('PS.hang', 'hang'), ('PS.reach', 'jump up'), ('PS.pull', 'pull up'), ('crawl 0.2', 'crawl'), ('PS.crouch', 'crouch'), ('PS.garde', 'en garde'),
         ('PS.windup', 'windup'), ('PS.lunge', 'lunge')]
TABLE = ['PS.stand', 'PS.turn', 'walk 0', 'walk 0.5', 'run 0.5', 'PS.land', 'PS.jumpS', 'PS.fall', 'PS.hang', 'PS.reach', 'PS.garde', 'PS.windup']


def src_of(fn, tmp, tag):
    s = open(fn, encoding='utf-8').read()
    assert TGX[0] in s
    s = s.replace(TGX[0], TGX[1])
    i = s.find('window.__HK={')
    out = os.path.join(tmp, '_r28a_%s.html' % tag)
    open(out, 'w', encoding='utf-8').write(s[:i] + EXPORT + s[i:])
    return out


def img(u):
    return Image.open(io.BytesIO(base64.b64decode(u.split(',')[1]))).convert('RGB')


def label(im, t, xy=(4, 2)):
    d = ImageDraw.Draw(im)
    d.rectangle((xy[0] - 2, xy[1] - 1, xy[0] + 6 * len(t) + 4, xy[1] + 12), fill=(0, 0, 0))
    d.text(xy, t, fill=TXT)
    return im


def contour(mono, y0, y1):
    """the back's contour: the leftmost dark pixel of each row (the figure faces right)"""
    px = mono.load()
    out = {}
    for yy in range(max(0, int(y0)), min(mono.height, int(y1))):
        for xx in range(mono.width):
            if px[xx, yy][0] < 128:
                out[yy] = xx
                break
    return out


def metrics(c, S, yh, yhip, ysh):
    """px at 1x: the upper back (its fullest point from 4 px over to 9 px under the shoulder joint) behind the seat's fullest point, behind the
    nape (the back's most forward point between the head's centre and the shoulder joint), the bulge of the back beyond the chord nape -> waist,
    and how far under the shoulder joint the back is fullest"""
    ys = sorted(c)
    try:
        seat = min(c[y] for y in ys if yhip - 3 * S <= y <= yhip + 4 * S)
        ub, uy = min((c[y], y) for y in ys if ysh - 4 * S <= y <= ysh + 9 * S)
        nx, ny = max((c[y], y) for y in ys if yh + 2 * S <= y <= ysh - S)
    except ValueError:
        return None
    wl = [(c[y], y) for y in ys if uy < y < yhip - 3 * S]
    wx, wy = max(wl) if wl else (ub, uy)
    dx, dy = wx - nx, wy - ny
    L = math.hypot(dx, dy) or 1
    bul = max(((nx - c[y]) * dy - (ny - y) * dx) / L for y in ys if ny <= y <= wy) if wy > ny else 0
    return (seat - ub) / S, (nx - ub) / S, bul / S, (uy - ysh) / S


def fig(pg, spec, S, mus, mode):
    W, Hh, x, y = 50, 70, 25, 64
    if spec.startswith('climb'):
        y = 10
    u, yh, yhip, ysh, bo = pg.evaluate(FIG, [spec, S, W, Hh, x, y, mode, mus])
    return img(u), yh, yhip, ysh, bo


def profile(pages):
    """10x stand, lit and silhouette, before | after with the contours; and the numbers"""
    R = {}
    for t, pg in pages.items():
        lit = fig(pg, 'PS.stand', 10, 1.65, 'lit')
        mono = fig(pg, 'PS.stand', 10, 1.65, 'mono')
        R[t] = (lit[0], mono[0], contour(mono[0], mono[1], mono[2] + 40), mono)
    cells = []
    for t in ('before', 'after'):
        lit, mono, c, _ = R[t]
        for im in (lit, mono):
            d = ImageDraw.Draw(im)
            if t == 'after':
                d.line([(x, y) for y, x in sorted(R['before'][2].items())], fill=(60, 110, 230), width=3)
            d.line([(x, y) for y, x in sorted(c.items())], fill=(230, 40, 40), width=3)
        cells += [label(lit.crop((80, 40, 420, 660)), 'stand, %s, 10x' % t), label(mono.crop((80, 40, 420, 660)), 'silhouette, %s (blue: before)' % t if t == 'after' else 'silhouette, before')]
    cw, ch = cells[0].size
    row = Image.new('RGB', (4 * cw + 3 * 8, ch), INK)
    for i, cc in enumerate(cells):
        row.paste(cc, (i * (cw + 8), 0))
    # numbers
    nums = {}
    for t, pg in pages.items():
        for mus in (1.0, 1.28, 1.65):
            for spec in TABLE:
                im, yh, yhip, ysh, bo = fig(pg, spec, 10, mus, 'mono')
                nums[(t, mus, spec)] = (metrics(contour(im, yh, yhip + 400), 10, yh, yhip, ysh), bo)
    lh = 15
    tb = Image.new('RGB', (row.width, lh * (len(TABLE) * 3 + 6) + 8), INK)
    d = ImageDraw.Draw(tb)
    X = [6, 170, 330, 490, 650, 820]
    d.text((6, 4), 'The silhouette at 10x, px at 1x, before > after. Behind the seat: the upper back\'s fullest point behind the seat\'s (the wall line: 0 or less). '
           'Behind the nape: behind the neck\'s back under the skull. Bulge: past the chord nape -> waist. Fullest: how far under the shoulder joint.', fill=TXT)
    for x, h in zip(X, ('pose, MUS', 'behind the seat', 'behind the nape', 'bulge', 'fullest under the joint', 'drawn back offsets U .62/.76/.88/.96/1 (trunk frame), before > after')):
        d.text((x, 4 + lh + 4), h, fill=(255, 210, 140))
    y = 4 + 2 * lh + 8
    f = lambda v: '%.1f' % v
    for mus in (1.65, 1.28, 1.0):
        for spec in TABLE:
            (m0, b0), (m1, b1) = nums[('before', mus, spec)], nums[('after', mus, spec)]
            cols = ['%s, %.2f' % (spec.replace('PS.', ''), mus)]
            for i in range(4):
                cols.append('%s > %s' % (f(m0[i]), f(m1[i])) if m0 and m1 else '-')
            cols.append(', '.join('%.2f' % v for v in b0[4:]) + '  >  ' + ', '.join('%.2f' % v for v in b1[4:]))
            for x, v in zip(X, cols):
                d.text((x, y), v, fill=TXT if mus == 1.65 else (190, 182, 165))
            y += lh
        y += 4
    return [row, tb], nums


def strip(pages):
    rows = []
    for S, lab in ((1, 'drawn at 1x, shown 3x (nearest)'), (3, 'drawn at 3x (the phone\'s DPR 3)')):
        for t in ('before', 'after'):
            cells = []
            for spec, nm in POSES:
                im = fig(pages[t], spec, S, 1.65, 'lit')[0]
                im = im.crop((5 * S, 4 * S, 45 * S, 68 * S))
                if S == 1:
                    im = im.resize((im.width * 3, im.height * 3), Image.NEAREST)
                cells.append(label(im, '%s' % nm))
            cw, ch = cells[0].size
            row = Image.new('RGB', (len(cells) * (cw + 3), ch + 16), INK)
            ImageDraw.Draw(row).text((4, 2), '%s, %s' % (t, lab), fill=TXT)
            for i, cc in enumerate(cells):
                row.paste(cc, (i * (cw + 3), 16))
            rows.append(row)
    return rows


# ---------------- the owner's scene ----------------
SCENE = r'''([rs])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS)H.S.hints[id]=1;let T=1e6;H.setClock(()=>T);let a=12345;Math.random=()=>{a=(a*16807)%2147483647;return a/2147483647;};
  let L=null,q=null,sd0=0;for(let sd=1;sd<60&&!q;sd++){L=H.load(11,1100+sd);H.banner=null;const C=L.cols,B=(c,r)=>L.base[r*C+c],ok=(c,r)=>B(c,r)!==2&&(B(c,r+1)===2||B(c,r+1)===1);
    for(const t of L.torches){if(t.broken||t.c<10||t.c>C-12)continue;let g=true;for(let dd=-3;dd<=5;dd++)g=g&&ok(t.c+dd,t.r);if(g){q=t;sd0=1100+sd;break;}}}
  const y=(q.r+1)*64-4,P=H.P;P.inv=1e9;P.state='stand';P.face=1;P.x=q.c*32+16+44;P.y=y;for(const e of H.G)e.x=-9999;
  H.cam.x=P.x-H.viewW*0.45;H.cam.y=y-64*2.2;H.cam.gy=H.cam.y;H.mode='play';if(H.GLP){H.GLP.pipe=false;H.GLP.rs=rs;}
  for(let i=0;i<4;i++){a=12345;H.render();}const X=H.XF,cv=[...document.querySelectorAll('canvas')].find(c=>c.getBoundingClientRect().width>0),R=cv.getBoundingClientRect();
  return {seed:sd0,name:H.themeName(11),P:[R.left+(P.x*X.VZ-X.camD)/cv.width*R.width,R.top+((y-30)*X.VZ-X.camDY)/cv.height*R.height]};}'''


def page(b, src, mode, vw=844, vh=390, dpr=3):
    pg = b.new_page(viewport={'width': vw, 'height': vh}, device_scale_factor=dpr)
    pg.errs = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e)))
    pg.goto('file://' + src)
    pg.wait_for_timeout(700)
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.body.classList.remove('panelOpen')")
    pg.evaluate("m=>{__HK.S.set.lightMode=m;}", mode)
    return pg


def scene(b, srcs):
    D = 3
    tiles, info = {}, None
    for mo, mt in (('torch', 'Torchlight'), ('classic', 'Classic')):
        for t, s in srcs.items():
            pg = page(b, s, mo)
            info = pg.evaluate(SCENE, [1])
            im = Image.open(io.BytesIO(pg.screenshot())).convert('RGB')
            cx, cy = int(info['P'][0] * D), int(info['P'][1] * D)
            one = im.crop((cx - 150, cy - 170, cx + 150, cy + 190))
            z = im.crop((cx - 40, cy - 105, cx + 40, cy - 5)).resize((240, 300), Image.NEAREST)
            cell = Image.new('RGB', (300 + 6 + 240, 360), INK)
            cell.paste(one, (0, 0))
            cell.paste(z, (306, 0))
            label(cell, '%s, %s (1:1 device px | 3x)' % (mt, t))
            tiles[(mt, t)] = cell
            if pg.errs:
                print('errors', mo, t, pg.errs[:3])
            pg.close()
    cells = [tiles[(mt, t)] for mt in ('Torchlight', 'Classic') for t in ('before', 'after')]
    cw, ch = cells[0].size
    row = Image.new('RGB', (4 * cw + 3 * 8, ch + 20), INK)
    ImageDraw.Draw(row).text((6, 4), 'The owner\'s scene: floor 11 (%s), seed %d, the prince standing beside a lamp, 844x390 CSS px at DPR 3: Torchlight before | after, '
                             'Classic before | after' % (info['name'], info['seed']), fill=TXT)
    for i, cc in enumerate(cells):
        row.paste(cc, (i * (cw + 8), 20))
    return row


RESEARCH = [
    'Research (sources on the page, round 28a):',
    '- Wall test (Mayo Clinic, via HealthDay): standing well, the back of the head, the shoulder blades and the buttocks touch one wall, a flat hand fits behind the low back. So the',
    '  upper back stands on the seat\'s line, not behind it (before 0.6 px behind standing, 1.2 walking; after 0.1 and 0.7).',
    '- Thoracic kyphosis in adolescents: normal 20-45 degrees Cobb (T2-T12; Lowell and Winters; boys 13-18: 35.5 +- 7.8, Kermanshah 2014; Fon, Pitt, Thies 1980: grows with age).',
    '  The curve\'s apex is mid-thoracic (T6-T8, the shoulder blades\' lower half): the back is fullest there and rounds over into the trapezius slope up to C7; the cervical',
    '  curve leaves the nape a few cm in front (5 cm is 1.5 px at the game\'s 29.4 px/m). Before, the arms-down back was fullest 0.7 px under the shoulder joint, 2.1 px behind the nape.',
    '- Artists: Proko (deltoids): three heads from the clavicle, acromion and scapular spine; not a ball ("bubblemen"); Bridgman and Loomis: in profile the back of the neck',
    '  runs into the trapezius in one slope to the shoulder blades, which then fall to the waist; the shoulder\'s cap is under the line from the neck to the acromion.',
    '- Muscle grows from fixed origins: a bigger trapezius thickens up its slope; a bigger deltoid swells down and out over the arm. Round 24 laid 65-75% of the growth at the',
    '  shoulder\'s top behind the trunk and grew the deltoid\'s round root about its centre, so at MUS 1.65 its cap stood 0.8 px over the chin.',
    '- Small sprites (PoP1\'s rotoscoped kid, round 22): the build reads in the outline\'s whole pixels; one long back line, no corner at the neck.',
    'Perspective: a pure side view. The far arm is drawn first, behind the trunk; its deltoid shows behind the back only where it passes the trunk\'s outline, so the trunk\'s top',
    '  must stay deeper than the deltoid\'s rear edge (3.8 px at 1.65) where the arm hangs: the dropped root keeps it inside. The near arm\'s cap is over the trunk, its outline',
    '  soft (no line at the shoulder). Shading: the lit and shaded planes follow the outline; RD.mh\'s deltoid V moves down with the root; no new line at the back.',
]


if __name__ == '__main__':
    tmp = tempfile.mkdtemp()
    try:
        raw = {'before': OLD, 'after': NEW}
        srcs = {t: src_of(s, tmp, t) for t, s in raw.items()}
        gsrc = {}
        for t, s in raw.items():
            fn = os.path.join(tmp, '_r28a_game_%s.html' % t)
            shutil.copy(s, fn)
            gsrc[t] = fn
        with sync_playwright() as p:
            b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
            pages = {}
            for t, s in srcs.items():
                pg = b.new_page()
                pg.errs = []
                pg.on('pageerror', lambda e, pg=pg: pg.errs.append(str(e)))
                pg.goto('file://' + s)
                pg.wait_for_timeout(700)
                pages[t] = pg
            prow, nums = profile(pages)
            srow = strip(pages)
            for t, pg in pages.items():
                if pg.errs:
                    print('errors', t, pg.errs[:3])
            sc = scene(b, gsrc)
            b.close()
        W = max(r.width for r in prow + srow + [sc])
        head = Image.new('RGB', (W, 46), INK)
        d = ImageDraw.Draw(head)
        d.text((6, 4), 'Round 28a: the hump behind the shoulder, arms down (owner: "Prince hump ... I don\'t think the upper back sticks out as much in a muscular teen seen from '
               'the side"). Before: v74; after: this source.', fill=TXT)
        d.text((6, 22), 'Cause: round 24\'s growth behind the trunk kept its full share to the shoulder joint (the back 4.8 px behind the spine at U .62-.96, 4.5 at the joint: '
               'fullest 0.7 px under it) and the deltoid\'s root grew round its centre (its cap 0.8 px over the chin).', fill=TXT)
        rs = Image.new('RGB', (W, 16 * len(RESEARCH) + 8), INK)
        d = ImageDraw.Draw(rs)
        for i, t in enumerate(RESEARCH):
            d.text((6, 4 + 16 * i), t, fill=TXT)
        parts = [head, sc] + prow + srow + [rs]
        sheet = Image.new('RGB', (W, sum(r.height + 8 for r in parts)), INK)
        y = 0
        for r in parts:
            sheet.paste(r, (0, y))
            y += r.height + 8
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        sheet.save(OUT, optimize=True)
        print('wrote', OUT, sheet.size)
        for (t, mus, spec), (m, bo) in sorted(nums.items()):
            if mus == 1.65:
                print('%-6s %-10s %s %s' % (t, spec, m and ['%.2f' % v for v in m], bo[4:]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
