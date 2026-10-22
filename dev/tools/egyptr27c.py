# egyptr27c.py [new.html] [old.html]: rounds 27c and 27d's pictures, into egypt_themes/.
# 27c (owner: "Soldiers don't seem to cast shadows and the light beams are drawn over them"; "it happens on all levels, torchlight graphics"):
#   r27c_guards.png: a guard beside a lamp and a guard in a sky beam on several floors (floor 10 is the owner's look, the Blue Chambers), at the
#   phone's resolution (852x393 CSS px at 2x, crops of the canvas at 1:1, and a 3x crop round the guard): Torchlight, Torchlight at GLP.rs .5,
#   Classic, each before | after.
# 27d (owner's screenshot, floor 10: "What are those slanted bars in the red circles? They are moving when the prince is running and are drawn
#   over windows and light beams"): r27d_bars.png: the owner's scene (floor 10, seed 1234: lamps on the faience dado, a breach with columns, the
#   prince between the lamps) at 844x390 CSS px and DPR 3 (an iPhone in landscape), before | after; crops at the lamps and the breach at three
#   moments half a second apart (the bars slid), at GLP.rs 1 and .5, and with the theme's look effects off (the cause); r27d_bars.gif: the prince
#   running past the lamps toward the breach, Torchlight, before | after.
# old.html defaults to HEAD's source (git show HEAD:dev/hourglass-keep.html, i.e. round 27b). Run from dev/tools.
import io, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
NEW = os.path.abspath(a[0] if a else os.path.join(HERE, '..', 'hourglass-keep.html'))
OLD = a[1] if len(a) > 1 else None
OUTD = os.path.join(HERE, 'egypt_themes')
INK = (20, 16, 24)
TXT = (250, 240, 215)

# a guard's place: 'beam' in front of an open arch (its beam lands there), 'lamp' 40 px right of a lamp on plain floor; returns where it stands
FIND = r'''([n,skip,kind])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS)H.S.hints[id]=1;let k=0;
  for(let sd=1;sd<80;sd++){const L=H.load(n,700+sd);H.banner=null;const C=L.cols,B=(c,r)=>L.base[r*C+c],ok=(c,r)=>B(c,r)!==2&&(B(c,r+1)===2||B(c,r+1)===1);
    if(kind==='beam'){for(const o of H.ryOps()){if(o.kind!=='arch'||o.sh.own||o.x0<12*32||o.x1>(L.cols-12)*32)continue;const r=Math.floor((o.y1-2)/64);let c=-1;
      for(let cc=Math.floor(o.x0/32);cc<=Math.floor(o.x1/32)+1;cc++){if(!ok(cc,r))continue;if(B(cc-1,r)!==2&&B(cc+1,r)!==2&&cc*32+16>o.x0-6&&cc*32+16<o.x1+6){c=cc;break;}}
      if(c<0)continue;if(k++<skip)continue;window.__O={x:c*32+16,y:(r+1)*64-4};return [n,700+sd,H.themeName(n)];}}
    else for(const q of L.torches){if(q.broken||q.c<12||q.c>L.cols-12)continue;let g=true;for(let d=-4;d<=3;d++)g=g&&ok(q.c+d,q.r);if(!g)continue;
      if(k++<skip)continue;window.__O={x:q.c*32+16+40,y:(q.r+1)*64-4};return [n,700+sd,H.themeName(n)];}}
  return null;}'''
# the guard there facing left, the prince 110 px to the left (beam) or 150 (lamp), a frozen clock and random numbers; returns the guard's place
# on the page
SHOW = r'''([rs,pdx])=>{const H=__HK,o=window.__O,P=H.P;let T=1e6;H.setClock(()=>T);let a=12345;Math.random=()=>{a=(a*16807)%2147483647;return a/2147483647;};
  P.inv=1e9;P.state='stand';P.face=1;P.x=o.x-pdx;P.y=o.y;const g=H.G.find(e=>e.alive&&!e.gone);if(!g)return null;g.x=o.x;g.y=o.y;g.face=-1;g.state='idle';
  for(const e of H.G)if(e!==g)e.x=-9999;
  H.cam.x=o.x-H.viewW/2;H.cam.y=o.y-64*2.2;H.cam.gy=H.cam.y;H.mode='play';if(H.GLP){H.GLP.pipe=false;H.GLP.rs=rs;}
  for(let i=0;i<4;i++){a=12345;H.render();}const X=H.XF,cv=[...document.querySelectorAll('canvas')].find(c=>c.getBoundingClientRect().width>0),R=cv.getBoundingClientRect();
  return [R.left+(o.x*X.VZ-X.camD)/cv.width*R.width,R.top+((o.y-34)*X.VZ-X.camDY)/cv.height*R.height];}'''
SPOTS = [  # (title, floor, skip, kind)
    ('Floor 10 (the Blue Chambers, the owner\'s look): a guard beside a lamp', 10, 0, 'lamp'),
    ('Floor 10: a guard in the moon\'s beam from an open arch', 10, 0, 'beam'),
    ('Floor 7: a guard in a beam from an open arch', 7, 0, 'beam'),
    ('Floor 14 at dusk: a guard beside a lamp', 14, 0, 'lamp'),
    ('Floor 23 at night: a guard in a beam', 23, 0, 'beam'),
    ('Floor 31: a guard beside a lamp', 31, 0, 'lamp'),
]
MODES = [('Torchlight', 'torch', 1), ('Torchlight GLP.rs .5', 'torch', 0.5), ('Classic', 'classic', 1)]
CW, CH = 360, 300
ZW, ZH = 120, 100


def old_src(tmp):
    if OLD:
        return os.path.abspath(OLD)
    fn = os.path.join(tmp, '_r27b.html')
    open(fn, 'w', encoding='utf-8').write(subprocess.run(['git', 'show', 'HEAD:dev/hourglass-keep.html'], cwd=HERE, capture_output=True, text=True, check=True).stdout)
    return fn


def page(b, src, mode, vw=852, vh=393, dpr=2):
    pg = b.new_page(viewport={'width': vw, 'height': vh}, device_scale_factor=dpr)
    pg.errs = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e)))
    pg.goto('file://' + src)
    pg.wait_for_timeout(700)
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.body.classList.remove('panelOpen')")
    pg.evaluate("m=>{__HK.S.set.lightMode=m;}", mode)
    return pg


def label(im, t):
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 8 + 6 * len(t), 13), fill=(0, 0, 0))
    d.text((4, 1), t, fill=TXT)


def guard_shot(pg, spot, rs):
    _, n, skip, kind = spot
    q = pg.evaluate(FIND, [n, skip, kind])
    if not q:
        return None, None
    xy = pg.evaluate(SHOW, [rs, 110 if kind == 'beam' else 150])
    if not xy:
        return None, None
    im = Image.open(io.BytesIO(pg.screenshot())).convert('RGB')
    cx, cy = xy[0] * 2, xy[1] * 2
    x0 = int(min(max(0, cx - CW * 0.6), im.width - CW)); y0 = int(min(max(0, cy - CH * 0.55), im.height - CH))
    full = im.crop((x0, y0, x0 + CW, y0 + CH))
    zx = int(cx - ZW * 0.75); zy = int(cy - ZH * 0.5)
    zoom = im.crop((zx, zy, zx + ZW, zy + ZH)).resize((ZW * 3, ZH * 3), Image.NEAREST)
    return q, (full, zoom)


def guards(b, srcs):
    pages = {(t, m): page(b, s, m) for t, s in srcs.items() for m in ('torch', 'classic')}
    rows = []
    for spot in SPOTS:
        cells = []
        for (mt, m, rs) in MODES:
            for t in ('before', 'after'):
                q, r = guard_shot(pages[(t, m)], spot, rs)
                if not r:
                    print('no case', spot); break
                label(r[0], '%s, %s' % (mt, t)); label(r[1], '%s, %s, 3x' % (mt, t))
                cells.append(r)
        if len(cells) != 6:
            continue
        print('spot', spot[0], q, flush=True)
        W = 6 * CW + 3 * 4 + 2 * 12
        row = Image.new('RGB', (W, 22 + CH + 4 + ZH * 3), INK)
        ImageDraw.Draw(row).text((6, 5), '%s (floor %d, seed %d, %s)' % (spot[0], q[0], q[1], q[2]), fill=TXT)
        x = 0
        for i, (full, zoom) in enumerate(cells):
            row.paste(full, (x, 22)); row.paste(zoom.crop((0, 0, CW, ZH * 3)), (x, 22 + CH + 4))
            x += CW + (4 if i % 2 == 0 else 12)
        rows.append(row)
    for k, pg in pages.items():
        if pg.errs:
            print('errors', k, pg.errs[:3])
        pg.close()
    return sheet(rows, 'r27c_guards.png')


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


# ---- 27d: the owner's scene. Floor 10, seed 1234, the first breach: the two lamps left of it on its storey, the prince between them ----
SCENE = r'''([rs,dt,pre])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS)H.S.hints[id]=1;if(pre)H.GLFX.lookfx=false;else H.GLFX.lookfx=true;
  const L=H.load(10,1234);H.banner=null;let T=1e6+dt;H.setClock(()=>T);let a=12345;Math.random=()=>{a=(a*16807)%2147483647;return a/2147483647;};
  const o=H.ryOps().filter(o=>o.kind==='br'&&!o.sh.own)[0],r=Math.floor((o.y1-2)/64),y=(r+1)*64-4;
  const ls=L.torches.filter(q=>q.r===r&&!q.broken&&q.c*32+16<o.x0&&q.c*32+16>o.x0-400).map(q=>q.c*32+16).sort((p,q)=>p-q);
  const l2=ls[ls.length-1],l1=ls.length>1?ls[ls.length-2]:l2-250,P=H.P;P.inv=1e9;P.state='stand';P.face=1;P.x=l2-62;P.y=y;for(const e of H.G)e.x=-9999;
  H.cam.x=Math.min(l1-H.viewW*0.12,o.x0-H.viewW*0.7);H.cam.y=y-64*2.2;H.cam.gy=H.cam.y;H.mode='play';if(H.GLP){H.GLP.pipe=false;H.GLP.rs=rs;}
  for(let i=0;i<4;i++){a=12345;H.render();}const X=H.XF,cv=[...document.querySelectorAll('canvas')].find(c=>c.getBoundingClientRect().width>0),R=cv.getBoundingClientRect(),
    sp=(wx,wy)=>[R.left+(wx*X.VZ-X.camD)/cv.width*R.width,R.top+(wy*X.VZ-X.camDY)/cv.height*R.height];
  return {lamps:ls.map(x=>sp(x,y-40)),br:sp(o.x0+20,y-40),P:sp(P.x,y-30)};}'''


def bars(b, srcs):
    D = 3
    shots = {}
    pages = {t: page(b, s, 'torch', 844, 390, D) for t, s in srcs.items()}
    for t, pg in pages.items():
        for rs in (1, 0.5):
            for dt in (0, 0.5, 1.0):
                info = pg.evaluate(SCENE, [rs, dt, False])
                shots[(t, rs, dt)] = (Image.open(io.BytesIO(pg.screenshot())).convert('RGB'), info)
        info = pg.evaluate(SCENE, [1, 0, True])
        shots[(t, 'nolx')] = (Image.open(io.BytesIO(pg.screenshot())).convert('RGB'), info)
    rows = []
    # the whole screen, before | after
    a, info = shots[('before', 1, 0)]; c, _ = shots[('after', 1, 0)]
    sw = a.width // 2
    row = Image.new('RGB', (sw * 2 + 12, a.height // 2 + 22), INK)
    ImageDraw.Draw(row).text((6, 5), 'Floor 10, seed 1234 (the Blue Chambers), Torchlight at 844x390 CSS px, DPR 3: before | after (the whole screen at half size)', fill=TXT)
    for i, im in enumerate((a, c)):
        s = im.resize((sw, im.height // 2), Image.LANCZOS); label(s, ('before', 'after')[i]); row.paste(s, (i * (sw + 12), 22))
    rows.append(row)
    # crops at the lamps and the breach: 1:1 device pixels, three moments half a second apart, rs 1 and .5; then look effects off
    pts = [('lamp 1', info['lamps'][-2] if len(info['lamps']) > 1 else info['lamps'][0]), ('lamp 2, the prince', info['lamps'][-1]), ('the breach', info['br'])]
    KW, KH = 420, 330
    for nm, (px, py) in pts:
        cx, cy = int(px * D), int(py * D)
        row = Image.new('RGB', (7 * KW + 6 * 6 + 12, KH + 22), INK)
        ImageDraw.Draw(row).text((6, 5), '%s: 1:1 device pixels; before at 0, 0.5, 1 s | after at 0, 0.5, 1 s | before with the theme\'s look effects off (GLFX.lookfx)' % nm, fill=TXT)
        x = 0
        for key, lb in [(('before', 1, 0), 'before 0 s'), (('before', 1, 0.5), 'before 0.5 s'), (('before', 1, 1.0), 'before 1 s'),
                        (('after', 1, 0), 'after 0 s'), (('after', 1, 0.5), 'after 0.5 s'), (('after', 1, 1.0), 'after 1 s'), (('before', 'nolx'), 'before, lookfx off')]:
            im = shots[key][0]
            x0 = min(max(0, cx - KW // 2), im.width - KW); y0 = min(max(0, cy - KH // 2), im.height - KH)
            k = im.crop((x0, y0, x0 + KW, y0 + KH)); label(k, lb); row.paste(k, (x, 22)); x += KW + (12 if lb == 'before 1 s' else 6)
        rows.append(row)
    # GLP.rs .5 (the phone's slow-frame scale) and a 3x zoom of the dado by lamp 2 after the fix (no blocks at the quarter-resolution pass)
    px, py = pts[1][1]
    cx, cy = int(px * D), int(py * D)
    row = Image.new('RGB', (4 * KW + 3 * 6, KH + 22), INK)
    ImageDraw.Draw(row).text((6, 5), 'GLP.rs .5: before | after; and 3x of the dado by lamp 2 (non-pixelated check): before | after', fill=TXT)
    x = 0
    for key, lb in [(('before', 0.5, 0), 'before, rs .5'), (('after', 0.5, 0), 'after, rs .5')]:
        im = shots[key][0]; x0 = min(max(0, cx - KW // 2), im.width - KW); y0 = min(max(0, cy - KH // 2), im.height - KH)
        k = im.crop((x0, y0, x0 + KW, y0 + KH)); label(k, lb); row.paste(k, (x, 22)); x += KW + 6
    for key, lb in [(('before', 1, 0), 'before, 3x'), (('after', 1, 0), 'after, 3x')]:
        im = shots[key][0]; zw, zh = KW // 3, KH // 3; x0 = cx - zw - 20; y0 = cy - zh // 3
        k = im.crop((x0, y0, x0 + zw, y0 + zh)).resize((zw * 3, zh * 3), Image.NEAREST); label(k, lb); row.paste(k, (x, 22)); x += KW + 6
    rows.append(row)
    for t, pg in pages.items():
        if pg.errs:
            print('errors', t, pg.errs[:3])
        pg.close()
    return sheet(rows, 'r27d_bars.png')


RUN = r'''([pre])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS){H.S.hints[id]=1;if(H.S.learned)H.S.learned[id]=1;}
  const L=H.load(10,1234);H.banner=null;const o=H.ryOps().filter(o=>o.kind==='br'&&!o.sh.own)[0],r=Math.floor((o.y1-2)/64),y=(r+1)*64-4;
  const ls=L.torches.filter(q=>q.r===r&&!q.broken&&q.c*32+16<o.x0&&q.c*32+16>o.x0-400).map(q=>q.c*32+16).sort((p,q)=>p-q);
  const P=H.P;P.inv=1e9;P.state='stand';P.face=1;P.x=ls[ls.length-1]-58;P.y=y;for(const e of H.G)e.x=-9999;H.cam.snap=true;if(H.GLP)H.GLP.pipe=false;
  H.setKey('kb','r',true);H.tick(2);H.render();}'''


def gif(b, srcs):
    frames = {}
    for t, s in srcs.items():
        pg = page(b, s, 'torch', 844, 390, 1)
        pg.evaluate(RUN, [False])
        seq = []
        for f in range(26):
            pg.evaluate("()=>{const H=__HK;H.tick(3);H.render();}")
            seq.append(Image.open(io.BytesIO(pg.screenshot())).convert('RGB'))
        pg.close()
        frames[t] = seq
    out = []
    for a, c in zip(frames['before'], frames['after']):
        a = a.crop((0, 60, 844, 330)); c = c.crop((0, 60, 844, 330))
        a = a.resize((a.width * 2 // 3, a.height * 2 // 3), Image.LANCZOS); c = c.resize((c.width * 2 // 3, c.height * 2 // 3), Image.LANCZOS)
        im = Image.new('RGB', (a.width, a.height * 2 + 34), INK)
        d = ImageDraw.Draw(im)
        d.text((4, 2), 'before (27b): the glaze\'s slanted bars slide along the dado', fill=TXT); im.paste(a, (0, 16))
        d.text((4, a.height + 18), 'after (27d): a soft sheen in the lamps\' light, never on the sky', fill=TXT); im.paste(c, (0, a.height + 34))
        out.append(im.quantize(colors=96, method=Image.MEDIANCUT, dither=Image.NONE))
    fn = os.path.join(OUTD, 'r27d_bars.gif')
    out[0].save(fn, save_all=True, append_images=out[1:], duration=100, loop=0, optimize=True)
    print('wrote', fn, os.path.getsize(fn))
    return fn


if __name__ == '__main__':
    tmp = tempfile.mkdtemp()
    srcs = {'before': old_src(tmp), 'after': NEW}
    os.makedirs(OUTD, exist_ok=True)
    which = os.environ.get('ONLY', 'guards,bars,gif').split(',')
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
        if 'guards' in which:
            guards(b, srcs)
        if 'bars' in which:
            bars(b, srcs)
        if 'gif' in which:
            gif(b, srcs)
        b.close()
