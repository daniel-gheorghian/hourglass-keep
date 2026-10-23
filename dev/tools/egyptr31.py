# egyptr31.py [new.html] [old.html]: round 31's picture, egypt_themes/r31_sheen.png.
# Owner (floor 13, Torchlight, iPhone): "I love the effect of the floor, but it doesn't look correct in the perspective, at least I think it
# doesn't. And it is drawn on top of things including the prince." The effect on floor 13 (the Forges of Meroe) is the embers in the floor's
# cracks; the wet flagstones' sheen (dungeon and crypt floors) was drawn the same way. Both were bands from the slab's front edge to its back
# edge, upright in the screen, laid over the finished scene at a quarter of the resolution: over his feet, the saw and its slot.
# Rows: the owner's floor (13, a saw in its slot, the prince standing where a band of the old look crossed the floor), Torchlight, before |
# after, the whole floor run and 3x crops at his feet and the slot; the same at GLP.rs .5; the wet sheen on floor 2 (the Waters of Nun) and
# floor 17 (the Green Hall of Osiris) with the prince by a lamp; Classic's embers on floor 13. Then the numbers: the share of the figure's
# and the saw's pixels the floor's looks changed (before | after).
# The first lines of the text block: the mean light the embers add over the floor's top face, v76 / round 31, both modes (--measure prints only
# those, faster); round 31 keeps it within 20% of v76 (the owner loves the effect).
# old.html defaults to v76's source (dev/tools/hk_v76_release.html if present, else git show d11123a:dev/hourglass-keep.html). Run from dev/tools.
import io, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageChops
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
a = [x for x in sys.argv[1:] if not x.startswith('--')]
NEW = os.path.abspath(a[0] if a else os.path.join(HERE, '..', 'hourglass-keep.html'))
OLD = a[1] if len(a) > 1 else None
OUTD = os.path.join(HERE, 'egypt_themes')
INK = (20, 16, 24)
TXT = (250, 240, 215)
D = 2  # device pixel ratio (the phone's canvas is capped at 2)

# a saw with plain floor right of its slot (floor n); or a lamp with plain floor round it
FIND = r'''([n,kind])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS)H.S.hints[id]=1;
  for(let sd=1;sd<200;sd++){const L=H.load(n,1000+sd);window.__L=L;H.banner=null;const C=L.cols,B=(c,r)=>L.base[r*C+c],ok=(c,r)=>B(c,r)!==2&&(B(c,r+1)===2||B(c,r+1)===1)&&!L.feat[r*C+c];
    if(kind==='lamp'){for(const q of L.torches){if(q.broken||q.c<12||q.c>L.cols-12)continue;let g=true;for(let d=-4;d<=4;d++)g=g&&ok(q.c+d,q.r);if(!g)continue;
      window.__O={x0:q.c*32+16-150,x1:q.c*32+16+150,lamp:q.c*32+16,y:(q.r+1)*64-4};return [n,1000+sd,H.themeName(n)];}continue;}
    for(const o of L.dyn){if(o.f.t!=='saw')continue;const f=o.f,c1=Math.floor((f.x1+14)/32);let g=true;for(let c=c1+1;c<=c1+5;c++)g=g&&ok(c,o.r);if(!g)continue;
      window.__O={x0:f.x0-14,x1:f.x1+14,y:(o.r+1)*64-4};return [n,1000+sd,H.themeName(n)];}}return null;}'''
# the scene: the prince at px (world), facing right; frozen clock and random numbers; fx false turns the theme's looks off (to find the old bands)
SHOW = r'''([px,rs,fx,ns,gr,dt,co])=>{const H=__HK,o=window.__O,P=H.P,L=window.__L;const PH=H.PAL_HERO;if(!window.__PH)window.__PH=Object.assign({},PH);for(const k in PH)if(typeof PH[k]==='string')PH[k]=gr?'#00ff00':window.__PH[k];const sv=L.dyn.filter(q=>q.f.t==='saw');if(ns)for(const q of sv)L.dyn.splice(L.dyn.indexOf(q),1);let T=1e6+(dt||0)*1000;H.setClock(()=>T);let a=12345;Math.random=()=>{a=(a*16807)%2147483647;return a/2147483647;};
  H.GLFX.sheen=fx;const me=H.LFX.meroe;if(me._e===undefined)me._e=me.embers;me.embers=fx?me._e:0;P.inv=1e9;P.state='stand';P.face=1;P.x=px;P.y=o.y;for(const e of H.G)e.x=-9999;
  H.cam.x=(o.lamp||o.x1)-H.viewW/2+(o.lamp?0:60)+(co||0);H.cam.y=o.y-64*2.2;H.cam.gy=H.cam.y;H.mode='play';if(H.GLP){H.GLP.pipe=false;H.GLP.rs=rs;}
  for(let i=0;i<4;i++){a=12345;H.render();}if(ns)L.dyn.push(...sv);const X=H.XF,cv=[...document.querySelectorAll('canvas')].find(c=>c.getBoundingClientRect().width>0),R=cv.getBoundingClientRect(),
    sp=(wx,wy)=>[(R.left+(wx*X.VZ-X.camD)/cv.width*R.width)*DPR,(R.top+(wy*X.VZ-X.camDY)/cv.height*R.height)*DPR];
  return {P:sp(P.x,o.y),saw:sp((o.x0+o.x1)/2,o.y),x0:sp(o.x0,o.y),x1:sp(o.x1,o.y),kz:X.VZ*R.width/cv.width*DPR,camD:X.camD,w:cv.width,cw:R.width};}'''.replace('DPR', str(D))


def old_src(tmp):
    if OLD:
        return os.path.abspath(OLD)
    rel = os.path.join(HERE, 'hk_v76_release.html')
    if os.path.exists(rel):
        return rel
    fn = os.path.join(tmp, '_v76.html')
    open(fn, 'w', encoding='utf-8').write(subprocess.run(['git', 'show', 'd11123a:dev/hourglass-keep.html'], cwd=HERE, capture_output=True, text=True, check=True).stdout)
    return fn


def page(b, src, mode):
    pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=D)
    pg.errs = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e)))
    pg.route('**/fonts.g*/**', lambda r: r.abort())  # (no web fonts: they can hold the page's load)
    pg.goto('file://' + src, wait_until='domcontentloaded', timeout=120000)
    pg.wait_for_function('()=>window.__HK', timeout=120000)
    pg.wait_for_timeout(700)
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.body.classList.remove('panelOpen')")
    pg.evaluate("m=>{__HK.S.set.lightMode=m;}", mode)
    return pg


def shot(pg, px, rs=1, fx=True, nosaw=False, green=False, dt=0, co=0):
    info = pg.evaluate(SHOW, [px, rs, fx, nosaw, green, dt, co])
    return Image.open(io.BytesIO(pg.screenshot())).convert('RGB'), info


def label(im, t):
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 8 + 6 * len(t), 13), fill=(0, 0, 0))
    d.text((4, 1), t, fill=TXT)


def crop(im, cx, cy, w, h, z=1):
    x0 = int(min(max(0, cx - w // 2), im.width - w)); y0 = int(min(max(0, cy - h // 2), im.height - h))
    k = im.crop((x0, y0, x0 + w, y0 + h))
    return k.resize((w * z, h * z), Image.NEAREST) if z > 1 else k


def warm_x(pg, info0, y_floor):
    """screen x (device px) along the floor's top where the old look adds the most: the scene with the looks on less the scene with them off"""
    on, _ = shot(pg, -9999, 1, True)
    off, _ = shot(pg, -9999, 1, False)
    diff = ImageChops.subtract(on, off).convert('L')
    y = int(y_floor)
    best, bx = -1, None
    x0, x1 = int(info0['x1'][0]) + 80, min(diff.width - 60, int(info0['x1'][0]) + 900)
    for x in range(x0, x1):
        v = sum(diff.getpixel((x, yy)) for yy in range(y - 10, y + 6))
        if v > best:
            best, bx = v, x
    return bx


def row_of(title, cells, gap=8):
    W = sum(c.width for c in cells) + gap * (len(cells) - 1)
    H = max(c.height for c in cells)
    row = Image.new('RGB', (W, H + 22), INK)
    ImageDraw.Draw(row).text((6, 5), title, fill=TXT)
    x = 0
    for c in cells:
        row.paste(c, (x, 22)); x += c.width + gap
    return row


def sheet(rows, name):
    H = sum(r.height for r in rows) + 8 * (len(rows) - 1)
    im = Image.new('RGB', (max(r.width for r in rows), H), (250, 246, 238))
    y = 0
    for r in rows:
        im.paste(r, (0, y)); y += r.height + 8
    fn = os.path.join(OUTD, name)
    im.save(fn)
    print('wrote', fn, im.size)
    return fn


def mask_of(a, b, thr=24):
    """the pixels where two pictures differ (a thing drawn in one and not the other)"""
    return ImageChops.difference(a, b).convert('L').point(lambda v: 255 if v > thr else 0)


def over(on, off, m):
    """the share of the mask's pixels that the floor's looks change (|looks on - looks off| > 12)"""
    d = ImageChops.difference(on, off).convert('L').point(lambda v: 255 if v > 12 else 0)
    n = m.histogram()[255]
    return ImageChops.multiply(d, m).histogram()[255] / max(1, n), n


def floor_light(pg):
    """the mean light the floor's looks add over the floor's top face (the storey's band across the screen, less the saw's slot), the prince away:
    looks on less looks off, R+G+B in 8-bit levels per device pixel, averaged over seven views: three moments (the embers pulse) and four pans along the storey"""
    tot = 0.0; m = 0
    for co, dt in ((0, 0), (0, 0.7), (0, 1.9), (-420, 0.3), (420, 1.1), (840, 2.6), (-840, 0.5)):  # (and the view panned along the storey: Classic's embers are few)
        on, inf = shot(pg, -9999, 1, True, dt=dt, co=co); off, _ = shot(pg, -9999, 1, False, dt=dt, co=co); m += 1
        k = inf['kz']; y = inf['x1'][1]; n = 0; acc = 0
        for xa, xb in ((0, int(inf['x0'][0] - 2 * k)), (int(inf['x1'][0] + 2 * k), on.width)):  # the whole storey across the screen, less the slot
            if xb - xa < 4:
                continue
            box = (xa, int(y - 4 * k), xb, int(y + 4 * k))
            d = ImageChops.subtract(on.crop(box), off.crop(box))
            acc += sum(sum(i * c for i, c in enumerate(d.getchannel(ch).histogram())) for ch in 'RGB'); n += d.width * d.height
        tot += acc / max(1, n)
    return tot / m


def main():
    os.makedirs(OUTD, exist_ok=True)
    tmp = tempfile.mkdtemp()
    srcs = {'before': old_src(tmp), 'after': NEW}
    rows, nums = [], []
    with sync_playwright() as p:
        b = p.chromium.launch()
        pt = {t: page(b, s, 'torch') for t, s in srcs.items()}
        pc = {t: page(b, s, 'classic') for t, s in srcs.items()}
        # 1. the owner's floor: 13, a saw in its slot, the prince standing on a band of the old look
        for pg in list(pt.values()) + list(pc.values()):
            q = pg.evaluate(FIND, [13, 'saw'])
        print('floor 13 case', q)
        _, i0 = shot(pt['before'], -9999)
        bx = warm_x(pt['before'], i0, i0['saw'][1])
        # world x of that screen x: camD/VZ + device px / (VZ * device px per canvas px)
        info = pt['before'].evaluate(r'''(sx)=>{const X=__HK.XF,cv=[...document.querySelectorAll('canvas')].find(c=>c.getBoundingClientRect().width>0),R=cv.getBoundingClientRect();
          return ((sx/%d-R.left)*cv.width/R.width+X.camD)/X.VZ;}''' % D, bx)
        px = info - 3  # his feet over the band
        print('old band at device x', bx, '-> prince at world x', round(px, 1))
        for mode, d_ in (('Torchlight', pt), ('Classic', pc)):
            fl = {t: floor_light(d_[t]) for t in ('before', 'after')}
            nums.append('%s, floor 13: the mean light the embers add over the floor\'s top face (R+G+B levels a pixel, 7 views): v76 %.2f / round 31 %.2f (%.0f%%)' % (mode, fl['before'], fl['after'], 100 * fl['after'] / max(1e-6, fl['before'])))
            print(nums[-1], flush=True)
        if '--measure' in sys.argv:
            return
        S = {}
        for t in ('before', 'after'):
            for rs in (1, 0.5):
                S[(t, rs)] = shot(pt[t], px, rs, True)
            S[(t, 'off')] = shot(pt[t], px, 1, False)
            S[(t, 'classic')] = shot(pc[t], px, 1, True)
            S[(t, 'classicoff')] = shot(pc[t], px, 1, False)
        for rs in (1, 0.5):
            cells = []
            for t in ('before', 'after'):
                im, inf = S[(t, rs)]
                k = crop(im, (inf['x0'][0] + inf['P'][0]) / 2 + 60, inf['P'][1] - 70, 900, 220); label(k, '%s, Torchlight%s' % (t, '' if rs == 1 else ', GLP.rs .5')); cells.append(k)
            rows.append(row_of('Floor 13 (%s, seed %d): the saw in its slot and the prince standing where a band of the old look crossed the floor; 1:1 device px%s' % (q[2], q[1], '' if rs == 1 else ', the scene at GLP.rs .5'), cells))
            cells = []
            for t in ('before', 'after'):
                im, inf = S[(t, rs)]
                k = crop(im, inf['P'][0] + 6, inf['P'][1] - 8, 100, 56, 3); label(k, '%s: his feet, 3x' % t); cells.append(k)
                k = crop(im, inf['saw'][0] + 30, inf['saw'][1] - 8, 160, 56, 3); label(k, '%s: the saw and its slot, 3x' % t); cells.append(k)
            rows.append(row_of('Floor 13, 3x: before (the bands stand upright, over his feet, the blade and the slot) | after (the embers lie in the flagstones\' joints, along the depth, under what stands on the floor)', cells))
        # Classic
        cells = []
        for t in ('before', 'after'):
            im, inf = S[(t, 'classic')]
            k = crop(im, (inf['x0'][0] + inf['P'][0]) / 2 + 60, inf['P'][1] - 70, 900, 220); label(k, '%s, Classic' % t); cells.append(k)
        rows.append(row_of('Floor 13, Classic: its embers, before (a round glow at a fixed spot on one tile in five, drawn after everything) | after (along the joints, cut round him and off the traps)', cells))
        cells = []
        for t in ('before', 'after'):
            im, inf = S[(t, 'classic')]
            k = crop(im, inf['P'][0] + 6, inf['P'][1] - 8, 100, 56, 3); label(k, '%s, Classic: his feet, 3x' % t); cells.append(k)
            k = crop(im, inf['saw'][0] + 30, inf['saw'][1] - 8, 160, 56, 3); label(k, '%s, Classic: the saw, 3x' % t); cells.append(k)
        rows.append(row_of('Classic, 3x at his feet and the saw', cells))
        # numbers: how many of the prince's pixels and the saw's (blade and slot) the floor's looks change
        for t in ('before', 'after'):
            for mode, pgs, on, off in (('Torchlight', pt, (t, 1), (t, 'off')), ('Classic', pc, (t, 'classic'), (t, 'classicoff'))):
                a_, inf = S[on]; b_, _ = S[off]
                nop, _ = shot(pgs[t], px, 1, False, False, True); nos, _ = shot(pgs[t], px, 1, False, True)  # (the prince's own pixels: drawn in green against his own colours)
                mp, ms = mask_of(b_, nop), mask_of(b_, nos)
                fp, n1 = over(a_, b_, mp); fs, n2 = over(a_, b_, ms)
                nums.append('%s, %s: the prince %.1f%% of his %d px, the saw and its slot %.1f%% of their %d px' % (t, mode, 100 * fp, n1, 100 * fs, n2))
        # 2. the wet sheen: floor 2 (dungeon), floor 17 (crypt), the prince by a lamp
        for n in (2, 17):
            cells, zc = [], []
            for t in ('before', 'after'):
                q = pt[t].evaluate(FIND, [n, 'lamp'])
                im, inf = shot(pt[t], pt[t].evaluate('()=>window.__O.lamp+44'), 1, True)
                off, _ = shot(pt[t], pt[t].evaluate('()=>window.__O.lamp+44'), 1, False)
                nop, _ = shot(pt[t], pt[t].evaluate('()=>window.__O.lamp+44'), 1, False, False, True)
                k = crop(im, inf['P'][0] - 60, inf['P'][1] - 80, 760, 240); label(k, '%s, Torchlight' % t); cells.append(k)
                z = crop(im, inf['P'][0] - 40, inf['P'][1] - 10, 200, 60, 3); label(z, '%s: the floor by the lamp, 3x' % t); zc.append(z)
                fp, n1 = over(im, off, mask_of(off, nop))
                nums.append('%s, floor %d (wet sheen), Torchlight: the prince %.1f%% of his %d px' % (t, n, 100 * fp, n1))
            rows.append(row_of('Floor %d (%s, seed %d): the wet sheen, the prince by a lamp; before | after' % (n, q[2], q[1]), cells))
            rows.append(row_of('Floor %d, 3x: the streaks stay upright under the lights (a reflection); the wet patches now lie along the floor; nothing over his feet' % n, zc))
        for d in (pt, pc):
            for t, pg in d.items():
                if pg.errs:
                    print('errors', t, pg.errs[:3])
                pg.close()
        b.close()
    tw = max(r.width for r in rows)
    txt = Image.new('RGB', (tw, 16 * len(nums) + 30), INK)
    dd = ImageDraw.Draw(txt)
    dd.text((6, 5), 'Pixels of the figure (his drawing, found by drawing him in green) and of the saw and its slot (the scene without the saw) that the floor\'s looks change (|looks on - looks off| > 12, frozen clock, 1:1 device px):', fill=TXT)
    for i, s in enumerate(nums):
        dd.text((6, 22 + 16 * i), s, fill=TXT)
        print(s)
    rows.append(txt)
    sheet(rows, 'r31_sheen.png')


if __name__ == '__main__':
    main()
