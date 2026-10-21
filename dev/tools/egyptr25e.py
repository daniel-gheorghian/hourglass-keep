# egyptr25e.py [new.html] [old.html] [--quick]: round 25e's measurement and pictures (owner: "the backgrounds that are seen through the
# windows: they sometimes change wildly and are distracting especially when going downwards. Something is broken between the camera
# movement and the background layer").
# Until 25d the view through the openings was pinned to the screen vertically (its layers moved 0.18 of their depth factor, clamped at
# 22 px; the sky not at all), so every opening slid over it at the camera's full speed: a storey down (a third of the screen) took a window
# from the dark land through the bright horizon into the sky. Now each opening looks out at the eye level of its own storey and its view
# moves with the keep but for a small vertical parallax (BG_VK of the camera's travel away from that storey's rest, (1-f) of it per layer).
#  1. The bot plays floors 7, 14, 23, 10, 33 and 41 (new source; the camera's path is the same in both, play is unchanged) and its camera
#     path is recorded. Descents (falls, drops, lifts, slides, climbs down), ascents and level runs are cut from it.
#  2. Each segment's camera path is replayed in both sources and both modes on the same floor with no figures and a frozen clock (so the
#     backdrop is the only thing that moves against the openings), and each opening's inner box is read back from the screen every frame
#     and compared pixel by pixel with the frame before, in the opening's own coordinates: how much the view through it changed. (Any
#     motion counts: across, a palm trunk moving 1 px with the horizontal parallax in a small window counts as much as a jump, so the
#     frames moving straight up or down are also counted apart, 'down|' and 'up|'.)
#  3. The view's place through each opening (the sky's, a layer at f .015, and the near land's, f .3: where the picture stands against the
#     opening's top) is computed from the old formula and from the new one (bgAnchor, bgLayerY), frame by frame.
# Writes egypt_themes/r25e_backdrop.png (plots: view offset against the camera through descents, before | after; the measured change a
# frame; window strips before | after in both modes), egypt_themes/r25e_descent.gif (a descent past windows, the bot playing: before |
# after, Torchlight over Classic) and r25e.json (the numbers). Prints the per-frame statistics; exits 1 if a descent or an ascent after
# the fix moves the view through an opening by more than 1 px a frame (computed).
# old.html defaults to round 25d's source (git show e5d9aa2:dev/hourglass-keep.html). Run from dev/tools.
import io, json, math, os, subprocess, sys, tempfile, unicodedata
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
args = [x for x in sys.argv[1:] if not x.startswith('--')]
QUICK = '--quick' in sys.argv
NEW = os.path.abspath(args[0] if args else os.path.join(HERE, '..', 'hourglass-keep.html'))
OLD = args[1] if len(args) > 1 else None
OUTD = os.path.join(HERE, 'egypt_themes')
FLOORS = [(7, 1), (14, 1), (23, 1)] if QUICK else [(7, 1), (14, 1), (23, 1), (10, 1), (33, 1), (41, 1)]
SEGS_PER = 2 if QUICK else 3   # descents per floor (and as many ascents and level runs, for comparison)
JMAX = 4.0                     # (a guide line on the plots: a change a frame of the view through an opening, mean absolute difference 0-255)
FRAME = 0.6; ROOM_H = 192; TH = 64; BG_BASE = 176
INK = (20, 16, 24); PAPER = (250, 246, 238); OLDC = (196, 70, 52); NEWC = (40, 110, 190); CAMC = (120, 120, 120)

RECORD = r'''([n,seed])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS)H.S.hints[id]=1;
  const g=botGen(n,seed,{});const out=[];let r=g.next(),f=0;
  while(!r.done&&f<60*300){H.tick(1);f++;out.push([+H.cam.x.toFixed(3),+H.cam.y.toFixed(3),H.P.state]);r=g.next();}
  const L=H.L,ops=H.openingsIn?H.openingsIn(-1e9,1e9,-1e9,1e9):[];
  return {theme:H.themeName(n),rows:L.rows,sink:L.prog?L.prog.sink:0,cam:out,ops:ops.map(o=>[o[0],o[1],o[2],o[3],H.bgAnchor(o)])};}'''
SETUP = r'''([n,seed])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS)H.S.hints[id]=1;H.load(n,seed,true);H.banner=null;let T=1e6;H.setClock(()=>T);
  let a=12345;Math.random=()=>{a=(a*16807)%2147483647;return a/2147483647;};H.P.x=-9999;H.P.inv=1e9;for(const e of H.G)e.x=-9999;H.mode='play';if(H.GLP)H.GLP.pipe=false;
  window.__rb=document.createElement('canvas');window.__rg=__rb.getContext('2d',{willReadFrequently:true});return 1;}'''
# replay a camera path; per frame, for each opening fully on the screen, how much the view through it changed since the last frame: the mean
# absolute difference (0-255, over R, G and B) of its inner box (inset 3 px), pixel by pixel in the opening's own coordinates (the world is
# drawn at whole device pixels, so a box that moves with the keep is compared with itself), read at the canvas's full size
REPLAY = r'''([path,ops,torch])=>{const H=__HK,out=[],prev=new Map();const src=torch&&H.GLP&&H.GLP.cv?H.GLP.cv:document.getElementById('game');
  for(const [x,y] of path){H.cam.x=x;H.cam.y=y;H.cam.snap=false;H.render();const X=H.XF,w=src.width,h=src.height;
    if(__rb.width!==w||__rb.height!==h){__rb.width=w;__rb.height=h;}__rg.clearRect(0,0,w,h);__rg.drawImage(src,0,0,w,h);const rec=[],seen=new Set();
    ops.forEach((o,i)=>{const x0=Math.round((o[0]+3)*X.VZ-X.camD),y0=Math.round((o[1]+3)*X.VZ-X.camDY),bw=Math.round((o[2]-6)*X.VZ),bh=Math.round((o[3]-6)*X.VZ);
      if(x0<0||y0<0||x0+bw>w||y0+bh>h-1||bw<2||bh<2)return;const d=__rg.getImageData(x0,y0,bw,bh).data,p=prev.get(i);seen.add(i);
      if(p&&p.length===d.length){let s=0;for(let k=0;k<d.length;k+=4)s+=Math.abs(d[k]-p[k])+Math.abs(d[k+1]-p[k+1])+Math.abs(d[k+2]-p[k+2]);rec.push([i,s/(d.length/4*3)]);}
      prev.set(i,d);});
    for(const i of [...prev.keys()])if(!seen.has(i))prev.delete(i);
    out.push(rec);}
  return out;}'''


def old_src(tmp):
    if OLD:
        return os.path.abspath(OLD)
    fn = os.path.join(tmp, '_r25d.html')
    open(fn, 'w', encoding='utf-8').write(subprocess.run(['git', 'show', 'e5d9aa2:dev/hourglass-keep.html'], cwd=HERE, capture_output=True, text=True, check=True).stdout)
    return fn


def page(b, src, mode, dpr=2):
    pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=dpr)
    pg.errs = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e)))
    pg.goto('file://' + src)
    pg.wait_for_timeout(700)
    pg.add_script_tag(path=os.path.join(HERE, 'bot.js'))
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.body.classList.remove('panelOpen')")
    pg.evaluate("m=>{__HK.S.set.lightMode=m;}", mode)
    return pg


def segments(cam, ops, kind):
    """runs of frames where the camera moves down (kind 'down'), up ('up') or level ('level'), with an opening in view"""
    out, i, n = [], 1, len(cam)
    def mv(k):
        dx, dy = cam[k][0] - cam[k - 1][0], cam[k][1] - cam[k - 1][1]
        return dy > 0.3 if kind == 'down' else dy < -0.3 if kind == 'up' else (abs(dx) > 0.8 and abs(dy) < 0.05)
    while i < n:
        if mv(i):
            j = i
            while j + 1 < n and mv(j + 1):
                j += 1
            a, b = max(0, i - 20), min(n - 1, j + 30)
            travel = abs(cam[j][1] - cam[i - 1][1]) if kind != 'level' else abs(cam[j][0] - cam[i - 1][0])
            if travel >= (40 if kind != 'level' else 120):
                vis = sum(1 for o in ops if any(cam[k][0] - 10 < o[0] and o[0] + o[2] < cam[k][0] + 420 and cam[k][1] < o[1] and o[1] + o[3] < cam[k][1] + ROOM_H for k in range(a, b + 1, 5)))
                if vis:
                    out.append((a, b, travel, vis))
            i = j + 1
        else:
            i += 1
    out.sort(key=lambda s: -s[3] * s[2])
    return out[:SEGS_PER]


# the view's place against an opening's top (view units, + = the picture sits lower in the opening): old formula and new
def off_old(o, cy, f, rows, sink):
    midY = rows * TH / 2; hz = ROOM_H * 0.7 - BG_BASE
    oy = hz + sink - max(-22, min(22, (cy - midY) * f * 0.18)) if f > 0.02 else 0.0
    return oy - (o[1] - cy)


def off_new(o, cy, f, rows, sink, vk):
    midY = rows * TH / 2; hz = ROOM_H * 0.7 - BG_BASE; an = o[4]
    if f > 0.02:
        oy = hz + sink - max(-22, min(22, (an - midY) * f * 0.18)) - (1 - vk * (1 - f)) * (cy - an)
    else:  # the sky gradient (in the old one pinned to the screen)
        oy = -(1 - vk * (1 - 0.015)) * (cy - an)
    return oy - (o[1] - cy)


def col_jumps(rec):
    return [r[1] for fr in rec for r in fr]


def pct(v, p):
    v = sorted(v)
    return v[min(len(v) - 1, int(len(v) * p))] if v else 0.0


def label(d, xy, t, fill=(250, 240, 215), bg=(0, 0, 0)):
    d.rectangle((xy[0], xy[1], xy[0] + 6 * len(t) + 6, xy[1] + 12), fill=bg)
    d.text((xy[0] + 3, xy[1]), t, fill=fill)


def plot(seg, cam, ops, rows, sink, vk, meas, title, W=560, H=250):
    """view offset through the openings against the frame, old (red) and new (blue), with the camera's y (grey); under it the measured colour change"""
    a, b = seg[0], seg[1]
    im = Image.new('RGB', (W, H + 90), PAPER); d = ImageDraw.Draw(im)
    d.text((6, 4), unicodedata.normalize('NFKD', title).encode('ascii', 'ignore').decode(), fill=INK)  # (the default font has no accents)
    L, T, R, B = 46, 22, W - 10, H - 18
    d.rectangle((L, T, R, B), outline=(180, 170, 160))
    vis = [i for i, o in enumerate(ops) if any(cam[k][1] < o[1] and o[1] + o[3] < cam[k][1] + ROOM_H and cam[k][0] - 10 < o[0] < cam[k][0] + 420 for k in range(a, b + 1))]
    lines = []
    for i in vis[:6]:
        o = ops[i]
        for f, w in ((0.015, 2), (0.3, 1)):
            lines.append((OLDC, w, [off_old(o, cam[k][1], f, rows, sink) for k in range(a, b + 1)]))
            lines.append((NEWC, w, [off_new(o, cam[k][1], f, rows, sink, vk) for k in range(a, b + 1)]))
    cy = [cam[k][1] for k in range(a, b + 1)]
    allv = [v for _, _, ys in lines for v in ys] + [c - cy[0] for c in cy]
    lo, hi = min(allv) - 4, max(allv) + 4
    X = lambda k: L + (R - L) * k / max(1, (b - a))
    Y = lambda v: B - (B - T) * (v - lo) / (hi - lo)
    for t in range(int(lo // 50) * 50, int(hi) + 1, 50):
        if lo <= t <= hi:
            d.line((L, Y(t), R, Y(t)), fill=(232, 226, 216)); d.text((4, Y(t) - 6), '%d' % t, fill=(120, 110, 100))
    d.line([(X(k), Y(c - cy[0])) for k, c in enumerate(cy)], fill=CAMC, width=1)
    for c, w, ys in lines:
        d.line([(X(k), Y(v)) for k, v in enumerate(ys)], fill=c, width=w)
    d.text((L + 4, B + 2), 'frames %d-%d (60 a second)   grey: camera y   red: before   blue: after   thick: sky, thin: near land (px)' % (a, b), fill=(90, 80, 70))
    # measured colour change a frame (Torchlight), the largest over the openings
    y0 = H + 4; d.text((6, y0), 'measured change a frame through the openings, Torchlight (mean abs. difference, worst opening; line: %.0f)' % JMAX, fill=INK)
    mo, mn = meas
    mx = max([max([0] + col_jumps(mo[k:k + 1])) for k in range(len(mo))] + [1])
    sc = 60 / max(mx, 8)
    for k in range(len(mo)):
        jo = max([0] + col_jumps(mo[k:k + 1])); jn = max([0] + col_jumps(mn[k:k + 1]))
        x = X(k)
        d.line((x, y0 + 80, x, y0 + 80 - jo * sc), fill=OLDC)
        d.line((x + 1, y0 + 80, x + 1, y0 + 80 - jn * sc), fill=NEWC)
    d.line((L, y0 + 80 - JMAX * sc, R, y0 + 80 - JMAX * sc), fill=(150, 150, 150))
    d.text((R - 150, y0 + 14), 'max %.0f before, %.1f after' % (mx, max([0] + col_jumps(mn))), fill=INK)
    return im


def strip(pg, n, seed, frames, torch):
    """crops round each window through a bot descent (the bot playing), one row per window"""
    pg.evaluate("([n,s])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS){H.S.hints[id]=1;if(H.S.learned)H.S.learned[id]=1;}window.__g=botGen(n,s,{});window.__f=0;window.__r=__g.next();if(H.GLP)H.GLP.pipe=false;}", [n, seed])
    fr = []
    for f in frames:
        info = pg.evaluate("""t=>{const H=__HK;while(__f<t&&!__r.done){H.tick(1);__f++;__r=__g.next();}H.render();H.render();
          const X=H.XF,cv=document.getElementById('game'),R=cv.getBoundingClientRect(),L=H.L;
          return L.windows.map(w=>[w.c,w.r,R.left+((w.c*32+16)*X.VZ-X.camD)/cv.width*R.width,R.top+((w.r*64+38)*X.VZ-X.camDY)/cv.height*R.height]).filter(w=>w[2]>16&&w[2]<R.width-16&&w[3]>24&&w[3]<R.height-24);}""", f)
        fr.append((info, Image.open(io.BytesIO(pg.screenshot())).convert('RGB')))
    return fr


GCROP = (250, 36, 690, 330)   # the part of the screen (CSS px) the gif shows: the prince on the lift and the hall's windows beside it


def gif_frames(pgs, n, seed, a, b, step):
    for pg in pgs:
        pg.evaluate("([n,s])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS){H.S.hints[id]=1;if(H.S.learned)H.S.learned[id]=1;}window.__g=botGen(n,s,{});window.__f=0;window.__r=__g.next();if(H.GLP)H.GLP.pipe=false;}", [n, seed])
    out = []
    for f in range(a, b + 1, step):
        tiles = []
        for pg in pgs:
            pg.evaluate("t=>{const H=__HK;while(__f<t&&!__r.done){H.tick(1);__f++;__r=__g.next();}H.render();}", f)
            tiles.append(Image.open(io.BytesIO(pg.screenshot())).convert('RGB').crop(GCROP))
        out.append(tiles)
    return out


def make_gif(br, srcs):
    """floor 7, the bot riding the lift down past the hall's windows: before | after, Torchlight over Classic, a crop at 1:1 (CSS px)"""
    gpgs = [page(br, srcs[t], m, 1) for m in ('torch', 'classic') for t in ('before', 'after')]
    gf = gif_frames(gpgs, 7, 1, 905, 1013, 3)
    errs = [pg.errs[:2] for pg in gpgs if pg.errs]
    tw, th = GCROP[2] - GCROP[0], GCROP[3] - GCROP[1]
    frames = []
    for tiles in gf:
        fimg = Image.new('RGB', (2 * tw + 4, 2 * th + 4), INK)
        dd = ImageDraw.Draw(fimg)
        for j, tl in enumerate(tiles):
            x, y = (j % 2) * (tw + 4), (j // 2) * (th + 4)
            fimg.paste(tl, (x, y))
            label(dd, (x + 2, y + 2), '%s, %s' % (('Torchlight', 'Classic')[j // 2], ('before (25d)', 'after (25e)')[j % 2]))
        frames.append(fimg.convert('P', palette=Image.ADAPTIVE, colors=64))
    g = os.path.join(OUTD, 'r25e_descent.gif')
    frames[0].save(g, save_all=True, append_images=frames[1:], duration=50, loop=0, optimize=True)
    print('wrote', g, os.path.getsize(g) // 1024, 'KB', 'errors', errs)


if __name__ == '__main__':
    tmp = tempfile.mkdtemp()
    srcs = {'before': old_src(tmp), 'after': NEW}
    if '--gif' in sys.argv:
        with sync_playwright() as p:
            br = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
            make_gif(br, srcs)
            br.close()
        sys.exit(0)
    res = {'floors': [], 'stats': {}}
    with sync_playwright() as p:
        br = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
        rec = page(br, NEW, 'classic', 1)
        vk = rec.evaluate("()=>__HK.BG_VK")
        pages = {(t, m): page(br, s, m) for t, s in srcs.items() for m in ('classic', 'torch')}
        stats = {}
        plots = []
        for n, seed in FLOORS:
            R = rec.evaluate(RECORD, [n, seed])
            cam, ops = R['cam'], R['ops']
            fl = {'n': n, 'seed': seed, 'theme': R['theme'], 'segs': {}}
            for kind in ('down', 'up', 'level'):
                for sg in segments(cam, ops, kind):
                    path = [cam[k][:2] for k in range(sg[0], sg[1] + 1)]
                    meas = {}
                    for (t, m), pg in pages.items():
                        pg.evaluate(SETUP, [n, seed])
                        meas[(t, m)] = pg.evaluate(REPLAY, [path, [o[:4] for o in ops], m == 'torch'])
                        js = col_jumps(meas[(t, m)])
                        stats.setdefault((kind, t, m), []).extend(js)
                        if kind != 'level':  # the frames that move straight up or down (lifts, climbs, plain falls)
                            for k, fr in enumerate(meas[(t, m)]):
                                if k and abs(path[k][0] - path[k - 1][0]) < 0.05 and abs(path[k][1] - path[k - 1][1]) > 0.3:
                                    stats.setdefault((kind + '|', t, m), []).extend(q[1] for q in fr)
                    # computed view motion through the openings a frame (sky and near land), old and new
                    for t, fn in (('before', lambda o, c, f: off_old(o, c, f, R['rows'], R['sink'])), ('after', lambda o, c, f: off_new(o, c, f, R['rows'], R['sink'], vk))):
                        for k in range(sg[0] + 1, sg[1] + 1):
                            for o in ops:
                                if cam[k][1] < o[1] and o[1] + o[3] < cam[k][1] + ROOM_H and cam[k][0] - 10 < o[0] < cam[k][0] + 420:
                                    for f in (0.015, 0.3):
                                        stats.setdefault((kind, t, 'px'), []).append(abs(fn(o, cam[k][1], f) - fn(o, cam[k - 1][1], f)))
                    sts = sorted(set(cam[k][2] for k in range(sg[0], sg[1] + 1)))
                    fl['segs'].setdefault(kind, []).append({'frames': [sg[0], sg[1]], 'travel': round(sg[2]), 'openings': sg[3], 'states': sts,
                        'jump_max': {'%s %s' % k2: round(max([0] + col_jumps(v)), 1) for k2, v in meas.items()}})
                    if kind == 'down' and not any(q[0] == n for q in plots):
                        plots.append((n, plot(sg, cam, ops, R['rows'], R['sink'], vk, (meas[('before', 'torch')], meas[('after', 'torch')]),
                                              'Floor %d, %s: descent (%s), camera %+d px' % (n, R['theme'], ', '.join(s for s in sts if s not in ('stand', 'run', 'land', 'turn')) or 'drop', round(cam[sg[1]][1] - cam[sg[0]][1])))))
            print('floor', n, R['theme'], {k: len(v) for k, v in fl['segs'].items()}, flush=True)
            res['floors'].append(fl)
        # pictures: window strips and the gif, floor 7 seed 1, the lift ride down past the hall's windows (frames found in the recording)
        strips = {}
        SF = list(range(930, 1011, 4))
        for (t, m), pg in pages.items():
            strips[(t, m)] = strip(pg, 7, 1, SF, m == 'torch')
        errs = [(k, pg.errs[:2]) for k, pg in pages.items() if pg.errs] + ([('rec', rec.errs[:2])] if rec.errs else [])
        make_gif(br, srcs)
        br.close()
    # statistics
    print('per-frame jumps through the openings (classic, torch: the view\'s mean absolute pixel difference, 0-255; px: the computed view, view units)')
    bad = False
    for kind in ('down', 'down|', 'up', 'up|', 'level'):
        for m in (('classic', 'torch') if '|' in kind else ('classic', 'torch', 'px')):
            row = []
            for t in ('before', 'after'):
                v = stats.get((kind, t, m), [])
                row.append('%s n=%d p50 %.2f p95 %.2f max %.2f' % (t, len(v), pct(v, .5), pct(v, .95), max(v) if v else 0))
                res['stats']['%s %s %s' % (kind, t, m)] = {'n': len(v), 'p50': round(pct(v, .5), 3), 'p95': round(pct(v, .95), 3), 'max': round(max(v) if v else 0, 3)}
            print('  %-6s %-7s | %s' % (kind, m, ' | '.join(row)))
    da = stats.get(('down', 'after', 'px'), [0]) + stats.get(('up', 'after', 'px'), [0])
    if max(da) > 1.0:
        bad = True
    print('errors', errs)
    json.dump(res, open(os.path.join(HERE, 'r25e.json'), 'w'), indent=1)
    # the sheet: plots, then window strips
    os.makedirs(OUTD, exist_ok=True)
    pw = plots[0][1].width; ph = plots[0][1].height
    cols = 3
    prow = (len(plots) + cols - 1) // cols
    CW, CH = 56, 100
    srows = []
    for (t, m) in (('before', 'torch'), ('after', 'torch'), ('before', 'classic'), ('after', 'classic')):
        fr = strips[(t, m)]
        keys = []
        for info, _ in fr:
            for w in info:
                if (w[0], w[1]) not in keys:
                    keys.append((w[0], w[1]))
        for kk in keys[:2]:
            row = Image.new('RGB', (len(fr) * (CW + 2) + 150, CH), INK)
            ImageDraw.Draw(row).text((4, 40), '%s, %s' % ('Torchlight' if m == 'torch' else 'Classic', t), fill=(250, 240, 215))
            for i, (info, im) in enumerate(fr):
                w = next((w for w in info if (w[0], w[1]) == kk), None)
                if w:
                    x, y = int(w[2] * 2), int(w[3] * 2)
                    row.paste(im.crop((x - CW // 2, y - CH // 2, x + CW // 2, y + CH // 2)), (150 + i * (CW + 2), 0))
            srows.append(row)
    SW = max(cols * (pw + 8), max(r.width for r in srows))
    sheet = Image.new('RGB', (SW, 30 + prow * (ph + 8) + 24 + len(srows) * (CH + 4) + 8), PAPER)
    d = ImageDraw.Draw(sheet)
    d.text((8, 8), 'Round 25e: the view through the openings against the camera, through descents. Before (red): pinned to the screen, it slides past every opening at the camera\'s speed. After (blue): each opening looks out from its own storey; only the parallax is left.', fill=INK)
    for i, (_, im) in enumerate(plots):
        sheet.paste(im, (8 + (i % cols) * (pw + 8), 30 + (i // cols) * (ph + 8)))
    y = 30 + prow * (ph + 8) + 4
    d.text((8, y), 'Floor 7, the lift down past the hall\'s windows, the bot riding (frames %d-%d, every 4th): two windows, before over after, Torchlight then Classic' % (SF[0], SF[-1]), fill=INK)
    y += 20
    for r in srows:
        sheet.paste(r, (8, y)); y += CH + 4
    out = os.path.join(OUTD, 'r25e_backdrop.png')
    sheet.save(out)
    print('wrote', out, sheet.size)
    sys.exit(1 if bad else 0)
