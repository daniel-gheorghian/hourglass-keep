#!/usr/bin/env python3
# egyptr48b.py old.html new.html [outdir] [quick]: round 48b's pictures, the kick shaft as a locked chimney. The new build played frame by frame
# by a scripted thumb (a running Jump at the shaft's wall, a rest in each locked stance, one press of Up a kick, Up at the top for the Y; or
# Down in a stance); the old build (v89) climbed by its own rule (Jump on each wall, the hang and the climb at the top), on the same shafts:
# floor 11 seed 1 (two storeys) and floor 7 seed 1 (three). Writes into outdir (default ../../.claude/research/r48chimney3):
#   r48b_keys_<shaft>.png    the new climb's key poses at 3x, Classic and Torchlight rows (the jump in, each stance, each kick, the Y's
#                            gather, push, the lip, the landing, standing)
#   r48b_old_<shaft>.png     the old climb's poses at 3x, both modes, for comparison
#   r48b_down_<shaft>.png    Down at the top stance: he lets go at once and falls (a fall's damage), 3x, both modes
#   r48b_phone_<shaft>.png   the new key poses at phone size
#   r48b_climb_<shaft>.gif   old | new, Classic over Torchlight, real time (30 fps), phone size x2
import io, os, sys
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
a = [x for x in sys.argv[1:] if x != 'quick']
OLD = os.path.abspath(a[0] if len(a) > 0 else os.path.join(HERE, 'hk_v89_release.html'))
NEW = os.path.abspath(a[1] if len(a) > 1 else os.path.join(HERE, '..', 'hourglass-keep.html'))
OUT = os.path.abspath(a[2] if len(a) > 2 else os.path.join(HERE, '..', '..', '.claude', 'research', 'r48chimney3'))
QUICK = 'quick' in sys.argv
GPU = ['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist', '--force_high_performance_gpu']
INK = (20, 16, 24)
BW, BH, ZK = 112, 150, 3
MODES = [('Classic', 'classic'), ('Torchlight', 'torch')]

# a shaft (walljump index i): him at its foot, or `back` cells of floor before it (a run in), facing its way
LOAD = r'''([n,s,i,back])=>{const H=__HK;for(const id in H.HINTS){H.S.hints[id]=1;H.S.learned[id]=1;}const L=H.load(n,s,true);H.banner=null;
  const a=L.path.filter(a=>a.a==='walljump')[i];let rf=-1;for(let r=0;r<L.rows;r++){const f=H.F(a.from,r);if(f&&f.t==='shaftfoot')rf=r;}
  H.mode='play';let q=12345;Math.random=()=>{q=(q*16807)%2147483647;return q/2147483647;};
  const dir=a.dir||1,P=H.P;P.x=(a.from-dir*back)*32+16;P.y=(rf+1)*64-4;P.fallY=P.y;P.face=dir;P.state='stand';P.vx=0;P.vy=0;
  window.__A={c:a.from,rf,k:a.k,dir,y0:(rf+1)*64-4,f1:-9,f:0};return window.__A;}'''
SHOW = r'''([cx,cy])=>{const H=__HK;H.banner=null;if(!window.__pn)window.__pn=performance.now.bind(performance);let T=1e6+H.gameTime*1000;H.setClock(()=>T);
  H.cam.x=cx-H.viewW/2;H.cam.y=cy-192*0.55;H.cam.gy=cy;if(H.GLP){H.GLP.pipe=false;H.GLP.rs=1;window.__HKnoauto=true;}
  window.__HKfreeze=true;for(let i=0;i<3;i++)H.render();const X=H.XF,cv=[...document.querySelectorAll('canvas')].find(c=>c.getBoundingClientRect().width>0),R=cv.getBoundingClientRect(),k=X.VZ/cv.width*R.width;
  H.setClock(window.__pn);return [R.left-X.camD/cv.width*R.width,R.top-X.camDY/cv.height*R.height,k];}'''
# one frame of the new build under the scripted thumb
TICK = r'''([keys,press])=>{const H=__HK;for(const q of ['l','r','u','d','j','g'])H.setKey('kb',q,keys.includes(q));if(press)H.setKey('kb',press,true);
  H.tick(1);if(press)H.setKey('kb',press,false);const P=H.P,A=window.__A;
  return {st:P.state,pl:!!P.plant,yp:!!(P.plant&&P.plant.y!=null),lock:!!P.lock,n:P.lock?P.lock.n:-9,jk:P.jumpKind||'',h:A.y0-P.y,x:P.x,y:P.y,hp:P.hp};}'''
# one frame of the old build climbing by its own rule (v89's bot: Jump at the foot, Jump on each wall while below the lip, Up on the hang)
OLDTICK = r'''()=>{const H=__HK,A=window.__A,P0=H.P,topYs=(A.rf-A.k+1)*64-4;for(const q of ['l','r','u','d','j','g'])H.setKey('kb',q,false);
  let pr=null;if(A.f===2)pr='j';else{const wt=H.wallTouch();if(P0.state==='air'&&wt&&P0.vy>-170&&A.f-A.f1>3&&(P0.y-57>topYs+2||wt===-A.dir)){pr='j';A.f1=A.f;}}
  if(P0.state==='hang')H.setKey('kb','u',true);if(pr){H.setKey('kb',pr,true);if(pr==='j'&&A.f===2)A.f1=A.f;}
  H.tick(1);if(pr)H.setKey('kb',pr,false);A.f++;const P=H.P;return {st:P.state,pl:!!P.plant,jk:P.jumpKind||'',h:A.y0-P.y,x:P.x,y:P.y,hp:P.hp};}'''


def page(b, html, mode, dsf=3):
    pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=dsf)
    pg.errs = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e)))
    pg.goto('file://' + html); pg.wait_for_timeout(700)
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.body.classList.remove('panelOpen')")
    pg.evaluate("m=>{__HK.S.set.lightMode=m;window.__HKfreeze=true;}", mode)
    pg.dsf = dsf
    return pg


def shot(pg, A, s, zk=ZK):
    cx = A['c'] * 32 + 16 + A['dir'] * 22
    cy = min(A['y0'] - 20, max(s['y'] - 30, A['y0'] - 64 * A['k'] - 20))
    q = pg.evaluate(SHOW, [cx, cy])
    im = Image.open(io.BytesIO(pg.screenshot())).convert('RGB'); d = pg.dsf
    ox, oy, k = q[0] * d, q[1] * d, q[2] * d
    x0, y0 = ox + (cx - BW / 2) * k, oy + (cy - BH * 0.5) * k
    c = im.crop((int(x0), int(y0), int(x0 + BW * k), int(y0 + BH * k)))
    return c if zk is None else c.resize((BW * zk, BH * zk), Image.LANCZOS)


class Thumb:
    """the scripted player: a decision a frame from his state (a run in from `back` cells, `rest` frames in each stance, then one Up)"""
    def __init__(s, A, back, rest, down_at=None):
        s.A, s.back, s.rest, s.down_at = A, back, rest, down_at
        s.dk = 'r' if A['dir'] > 0 else 'l'; s.f = 0; s.started = False; s.pf = None; s.pn = -9; s.pressed = False
    def keys(s, st):
        A = s.A
        if not s.started:
            if not s.back: s.started = True; return '', 'j'
            if st and st['st'] == 'air': s.started = True; return '', None
            if st and (st['x'] - (A['c'] * 32 + 16 - 14 * A['dir'])) * A['dir'] >= 0: return s.dk, 'j'
            return s.dk, None
        if st['pl'] and st['lock'] and not st['yp']:
            if st['n'] != s.pn: s.pf = s.f; s.pn = st['n']; s.pressed = False
            if s.f - s.pf >= s.rest:
                if s.down_at == st['n']: return 'd', None
                if not s.pressed: s.pressed = True; return '', 'u'
        return '', None


def play(pg, A, back, rest, down_at=None, every=None, tail=24, old=False):
    """the climb; returns (events, frames) with every `every`-th frame shot"""
    t = Thumb(A, back, rest, down_at); st = None; ev = []; ims = []; ps = ''; done = None
    for f in range(700):
        if old: st = pg.evaluate(OLDTICK)
        else: k, p = t.keys(st); t.f += 1; st = pg.evaluate(TICK, [k, p])
        tag = st['st'] + (':yprep' if st.get('yp') else ':plant' if st['pl'] else ':' + st['jk'] if st['st'] == 'air' and st['jk'] else '')
        if tag != ps: ev.append((f, tag, round(st['h'], 1), st['hp'])); ps = tag
        if every and f % every == 0: ims.append((f, tag, shot(pg, A, st)))
        if done is None and (st['st'] == 'stand' and st['h'] > 60 or (down_at is not None and st['st'] in ('stand', 'landHurt', 'dead') and f > 40 and st['h'] < 4)): done = f
        if done is not None and f - done >= tail: break
    return ev, ims


def frames_at(pg, A, back, rest, want, down_at=None, old=False):
    t = Thumb(A, back, rest, down_at); st = None; out = {}
    for f in range(max(want) + 1):
        if old: st = pg.evaluate(OLDTICK)
        else: k, p = t.keys(st); t.f += 1; st = pg.evaluate(TICK, [k, p])
        if f in want: out[f] = (shot(pg, A, st), shot(pg, A, st, None))
    return out


def label(im, t):
    d = ImageDraw.Draw(im); d.rectangle((0, 0, 8 + 6 * len(t), 13), fill=(0, 0, 0)); d.text((4, 1), t, fill=(250, 240, 215))


def first(ev, tag, i=0, d=0):
    q = [e[0] for e in ev if e[1] == tag]
    return q[i] + d if len(q) > i else None


def pick_new(ev):
    out = [('jump in', first(ev, 'air:stand', 0, 8))]
    np = len([e for e in ev if e[1] == 'air:plant'])
    for i in range(np):
        out.append(('stance %d, locked' % (i + 1), first(ev, 'air:plant', i, 14)))
        if first(ev, 'air:kick', i) is not None:
            out.append(('Up: kick %d, push' % (i + 1), first(ev, 'air:kick', i, 3)))
            out.append(('kick %d, flight' % (i + 1), first(ev, 'air:kick', i, 11)))
    out += [('Up at the top: the Y', first(ev, 'air:yprep', 0, 8)), ('Y: push', first(ev, 'air:stand', 1, 5)), ('Y: over the lip', first(ev, 'air:stand', 1, 17)),
            ('Y: landing', first(ev, 'land', 0, 3)), ('standing', [e[0] for e in ev if e[1] == 'stand'][-1] + 10)]
    return [(a, f) for a, f in out if f is not None]


def pick_old(ev):
    out = [('jump', first(ev, 'air:stand', 0, 8))]
    for i in range(len([e for e in ev if e[1] == 'air:plant'])):
        out.append(('plant %d' % (i + 1), first(ev, 'air:plant', i, 4)))
        if first(ev, 'air:kick', i) is not None: out.append(('kick %d' % (i + 1), first(ev, 'air:kick', i, 8)))
    out += [('hang', first(ev, 'hang', 0, 6)), ('climb', first(ev, 'climb', 0, 14)), ('standing', first(ev, 'stand', 1, 10))]
    return [(a, f) for a, f in out if f is not None]


def pick_down(ev):
    np = len([e for e in ev if e[1] == 'air:plant'])
    out = [('top stance', first(ev, 'air:plant', np - 1, 12))]
    s = first(ev, 'air:slip', 0)
    for d in (1, 8, 16):
        out.append(('Down: let go +%d f' % d, s + d if s is not None else None))
    lt = next((e[0] for e in ev if e[1] in ('landHurt', 'land')), None)
    out += [('landing', lt + 3 if lt else None), ('after', lt + 30 if lt else None)]
    return [(a, f) for a, f in out if f is not None]


def sheet(rows, path):
    W = max(r.width for r in rows); im = Image.new('RGB', (W, sum(r.height + 4 for r in rows)), INK); y = 0
    for r in rows: im.paste(r, (0, y)); y += r.height + 4
    im.save(path, optimize=True); print('wrote', path, im.size, flush=True)


def strip(title, cells, per=9):
    cw, ch = cells[0][1].size; rows = []
    for i0 in range(0, len(cells), per):
        row = Image.new('RGB', (per * (cw + 4) + 4, ch + 20), INK)
        for j, (t, im) in enumerate(cells[i0:i0 + per]):
            c = im.copy(); label(c, t); row.paste(c, (4 + j * (cw + 4), 18))
        ImageDraw.Draw(row).text((6, 3), title + ('' if i0 == 0 else ' (cont.)'), fill=(250, 240, 215)); rows.append(row)
    return rows


def gif(fr, path, ms=33):
    """old | new side by side, Classic above Torchlight; the shorter climb holds its last frame"""
    n = max(len(v) for v in fr.values()); frames = []
    w, h = fr[('old', 'classic')][0].size
    for i in range(n):
        im = Image.new('RGB', (2 * w + 6, 2 * h + 6), INK)
        for (o, m), L in fr.items():
            im.paste(L[min(i, len(L) - 1)], ((w + 6) if o == 'new' else 0, (h + 6) if m == 'torch' else 0))
        d = ImageDraw.Draw(im); d.text((4, 2), 'v89', fill=(250, 240, 215)); d.text((w + 10, 2), 'round 48b', fill=(250, 240, 215))
        frames.append(im)
    frames += [frames[-1]] * 15
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=ms, loop=0, optimize=True); print('wrote', path, len(frames), 'frames', flush=True)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    SH = [(11, 1, 0, 'f11s1'), (7, 1, 0, 'f7s1')]
    if QUICK: SH = SH[:1]
    with sync_playwright() as p:
        b = p.chromium.launch(args=GPU)
        for n, s, i, tag in SH:
            pg = page(b, NEW, 'classic', 1); A = pg.evaluate(LOAD, [n, s, i, 2]); ev, _ = play(pg, A, 2, 20); errs = pg.errs; pg.close()
            print(tag, 'k', A['k'], 'new climb', ev, errs[:2], flush=True)
            pg = page(b, OLD, 'classic', 1); A = pg.evaluate(LOAD, [n, s, i, 0]); evo, _ = play(pg, A, 0, 0, old=True); pg.close()
            print(tag, 'old climb', evo, flush=True)
            pg = page(b, NEW, 'classic', 1); A = pg.evaluate(LOAD, [n, s, i, 0]); evd, _ = play(pg, A, 0, 20, down_at=A['k'] - 1); pg.close()
            print(tag, 'down', evd, flush=True)
            kp, ko, kd = pick_new(ev), pick_old(evo), pick_down(evd)
            rows, rowso, rowsd, phone = [], [], [], []
            for mt, m in MODES:
                pg = page(b, NEW, m); A = pg.evaluate(LOAD, [n, s, i, 2]); got = frames_at(pg, A, 2, 20, {f: t for t, f in kp}); pg.close()
                rows += strip('%s, floor %d seed %d, a %d-storey shaft, round 48b: the locked chimney (one Up a kick, the Y at the top)' % (mt, n, s, A['k']), [(t, got[f][0]) for t, f in kp])
                phone += strip('%s, phone size' % mt, [(t, got[f][1]) for t, f in kp], per=10)
                pg = page(b, OLD, m); A = pg.evaluate(LOAD, [n, s, i, 0]); got = frames_at(pg, A, 0, 0, {f: t for t, f in ko}, old=True); pg.close()
                rowso += strip('%s, floor %d seed %d, v89: Jump on each wall, the hang, the climb' % (mt, n, s), [(t, got[f][0]) for t, f in ko])
                pg = page(b, NEW, m); A = pg.evaluate(LOAD, [n, s, i, 0]); got = frames_at(pg, A, 0, 20, {f: t for t, f in kd}, down_at=A['k'] - 1); pg.close()
                rowsd += strip('%s, floor %d seed %d: Down at the top stance: he lets go at once and falls (a fall\'s damage)' % (mt, n, s), [(t, got[f][0]) for t, f in kd])
            sheet(rows, os.path.join(OUT, 'r48b_keys_%s.png' % tag))
            sheet(rowso, os.path.join(OUT, 'r48b_old_%s.png' % tag))
            sheet(rowsd, os.path.join(OUT, 'r48b_down_%s.png' % tag))
            sheet(phone, os.path.join(OUT, 'r48b_phone_%s.png' % tag))
            if QUICK: continue
            fr = {}
            for mt, m in MODES:
                pg = page(b, NEW, m, 2); A = pg.evaluate(LOAD, [n, s, i, 2]); _, ims = play(pg, A, 2, 20, every=2); fr[('new', m)] = [x[2].resize((BW * 2, BH * 2), Image.LANCZOS) for x in ims]; pg.close()
                pg = page(b, OLD, m, 2); A = pg.evaluate(LOAD, [n, s, i, 0]); _, ims = play(pg, A, 0, 0, every=2, old=True); fr[('old', m)] = [x[2].resize((BW * 2, BH * 2), Image.LANCZOS) for x in ims]; pg.close()
            gif(fr, os.path.join(OUT, 'r48b_climb_%s.gif' % tag))
        b.close()
