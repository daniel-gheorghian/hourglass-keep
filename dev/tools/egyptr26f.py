# egyptr26f.py [png|gif|all] [new.html] [old.html]: round 26f's pictures (owner: "the climb animation: the prince climbs the wall, he should
# instead disappear on the stairs ... propose some other way to exit and maybe enter the level"; chosen: exit D "into the light", entry E1
# "out of the dark door").
#   egypt_themes/r26f_exit.png: frame strips from the moment Up is pressed at the exit, 14 px off the doorway's middle: before (v72 to round
#     26e) over after, three themes (a lintel: The Waters of Nun, The Forges of Meroe; a round vault: The Ruined Labyrinth), Torchlight and
#     Classic, facing right and facing left (before, facing left he drifted onto the left jamb); then the entry, after only (before, the
#     entrance was drawn shut and he stood in front of it from the first frame).
#   egypt_themes/r26f_exit.gif: in game, the bot's own keys: he walks to the exit, climbs into the light, the card, the next floor's entry,
#     Torchlight then Classic.
# old.html defaults to the source before round 26f (git show 876bd7b:dev/hourglass-keep.html). Run from dev/tools.
import io, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
WHAT = a[0] if a and a[0] in ('png', 'gif', 'all') else 'all'
a = [x for x in a if x not in ('png', 'gif', 'all')]
NEW = os.path.abspath(a[0] if a else os.path.join(HERE, '..', 'hourglass-keep.html'))
OLD = a[1] if len(a) > 1 else None
OUTP = os.path.join(HERE, 'egypt_themes', 'r26f_exit.png')
OUTG = os.path.join(HERE, 'egypt_themes', 'r26f_exit.gif')
INK = (20, 16, 24)
TIMES = [0.2, 0.4, 0.55, 0.7, 0.85, 1.0, 1.15, 1.3, 1.45, 1.6]
ROWS = [(1, 'torch', 1), (1, 'classic', -1), (13, 'torch', -1), (13, 'classic', 1), (41, 'torch', 1), (41, 'classic', -1)]
ETIMES = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.66, 0.8, 1.2]
EROWS = [(13, 'torch'), (26, 'classic'), (41, 'torch'), (1, 'classic')]

GEO = r'''(()=>{const H=__HK,X=H.XF,cv=[...document.querySelectorAll('canvas')].find(c=>c.getBoundingClientRect().width>0),R=cv.getBoundingClientRect();
  return {VZ:X.VZ,camD:X.camD,camDY:X.camDY,sx:R.width/cv.width,sy:R.height/cv.height,left:R.left,top:R.top};})()'''
EXIT0 = r'''([n,mode,face])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS)H.S.hints[id]=1;H.S.set.lightMode=mode;
  H.load(n,4400+n,true);const L=H.L,d=L.door,P=H.P;H.banner=null;d.opening=true;d.open=1;
  P.inv=1e9;P.face=face;P.x=d.x-face*14;P.y=(d.r+1)*64-4;P.vx=P.vy=0;P.state='stand';P.t=0;H.tick(5);
  P.state='exit';P.t=0;P.exS=0;P.sword=false;H.mode='play';if(H.GLP){H.GLP.pipe=false;}return {th:H.themeName(n),dx:d.x,dr:d.r};}'''
STEP = r'''([k,cx,cy])=>{const H=__HK;for(let i=0;i<k;i++){if(H.mode==='play')H.tick(1);}
  document.querySelectorAll('.screen').forEach(e=>e.hidden=true);H.mode='play';
  H.cam.x=cx-H.viewW/2;H.cam.y=cy-64*1.6;H.cam.gy=H.cam.y;H.render();H.render();return {exS:H.P.exS||0,x:H.P.x};}'''
ENTRY0 = r'''([n,mode])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS)H.S.hints[id]=1;H.S.set.lightMode=mode;
  H.startLevel(n,-1,true);H.mode='play';if(H.GLP){H.GLP.pipe=false;}const L=H.L,sd=L.start.door===undefined?1:L.start.door;
  return {th:H.themeName(n),dx:sd*32+16,dr:L.start.r,face:L.start.face||1,sx:L.start.x};}'''


def old_src(tmp):
    if OLD:
        return os.path.abspath(OLD)
    fn = os.path.join(tmp, '_r26e.html')
    open(fn, 'w', encoding='utf-8').write(subprocess.run(['git', 'show', '876bd7b:dev/hourglass-keep.html'], cwd=HERE, capture_output=True, text=True, check=True).stdout)
    return fn


def page(b, src, scale=2):
    pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=scale)
    pg.errs = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e)))
    pg.goto('file://' + src)
    pg.wait_for_timeout(800)
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.body.classList.remove('panelOpen')")
    return pg


def shot(pg):
    return Image.open(io.BytesIO(pg.screenshot())).convert('RGB')


def crop(pg, im, wx, wy, w0, w1, h0, h1, out):
    g = pg.evaluate(GEO)
    W = lambda x, y: ((g['left'] + (x * g['VZ'] - g['camD']) * g['sx']) * 2, (g['top'] + (y * g['VZ'] - g['camDY']) * g['sy']) * 2)
    (x0, y0), (x1, y1) = W(wx + w0, wy + h0), W(wx + w1, wy + h1)
    return im.crop((int(x0), int(y0), int(x1), int(y1))).resize(out, Image.LANCZOS)


TW, TH = 120, 136


def exit_row(pg, n, mode, face):
    s = pg.evaluate(EXIT0, [n, mode, face]); pg.wait_for_timeout(100)
    wx, wy = s['dx'] + 8, (s['dr'] + 1) * 64 - 30
    tiles, last = [], 0
    for t in TIMES:
        k = round(t * 60) - last; last = round(t * 60)
        r = pg.evaluate(STEP, [k, s['dx'], (s['dr'] + 1) * 64 - 4])
        c = crop(pg, shot(pg), wx, wy, -36, 38, -54, 30, (TW, TH))
        ImageDraw.Draw(c).text((3, 2), '%.2fs' % t, fill=(255, 240, 170))
        tiles.append(c)
    return s['th'], tiles


def entry_row(pg, n, mode):
    s = pg.evaluate(ENTRY0, [n, mode]); pg.wait_for_timeout(100)
    wx, wy = (s['dx'] + s['sx']) / 2 + 8, (s['dr'] + 1) * 64 - 30
    tiles, last = [], 0
    for t in ETIMES:
        k = round(t * 60) - last; last = round(t * 60)
        pg.evaluate(STEP, [k, wx, (s['dr'] + 1) * 64 - 4])
        c = crop(pg, shot(pg), wx, wy, -48, 48, -54, 30, (TW + 18, TH))
        st = pg.evaluate("()=>__HK.P.state")
        ImageDraw.Draw(c).text((3, 2), '%.2fs %s' % (t, 'control' if st != 'enter' else ''), fill=(255, 240, 170))
        tiles.append(c)
    return s['th'], tiles


def make_png(b, old):
    pn, po = page(b, NEW), page(b, old)
    blocks = []
    for n, mode, face in ROWS:
        th, before = exit_row(po, n, mode, face)
        _, after = exit_row(pn, n, mode, face)
        blocks.append(('Floor %d, %s, %s, arriving facing %s' % (n, th, 'Torchlight' if mode == 'torch' else 'Classic', 'right' if face > 0 else 'left'), before, after))
    eb = []
    for n, mode in EROWS:
        th, tiles = entry_row(pn, n, mode)
        eb.append(('Floor %d, %s, %s: out of the dark door, the leaf drops behind him' % (n, th, 'Torchlight' if mode == 'torch' else 'Classic'), tiles))
    errs = pn.errs + po.errs
    LW = 64; W = LW + TW * len(TIMES); bh = 16 + 2 * (TH + 2)
    eh = 16 + TH + 2; ew = LW + (TW + 18) * len(ETIMES)
    W = max(W, ew)
    H = 30 + len(blocks) * bh + 34 + len(eb) * eh + 6
    out = Image.new('RGB', (W, H), INK); d = ImageDraw.Draw(out)
    d.text((6, 8), 'Round 26f: the exit, before (v72 to round 26e) | after, from the moment Up is pressed 14 px off the doorway\'s middle (s)', fill=(240, 220, 170))
    y = 30
    for lab, before, after in blocks:
        d.text((6, y + 2), lab, fill=(230, 200, 140)); y += 16
        for row, tag in ((before, 'before'), (after, 'after')):
            d.text((6, y + TH // 2 - 6), tag, fill=(200, 190, 210))
            for j, t in enumerate(row): out.paste(t, (LW + j * TW, y))
            y += TH + 2
    d.text((6, y + 12), 'The entry (after; before, the entrance was drawn shut and he stood in front of it from the first frame), s from the floor\'s start', fill=(240, 220, 170)); y += 34
    for lab, tiles in eb:
        d.text((6, y + 2), lab, fill=(230, 200, 140)); y += 16
        for j, t in enumerate(tiles): out.paste(t, (LW + j * (TW + 18), y))
        y += TH + 2
    out.save(OUTP, optimize=True)
    print('wrote', OUTP, out.size, os.path.getsize(OUTP), 'errors', errs[:3])


# in game: the bot walks him to the exit with the game's keys, Up at the door; the card; the next floor started as the card's button does
GIF0 = r'''([n,seed,mode,face])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS)H.S.hints[id]=1;H.S.set.lightMode=mode;
  H.load(n,seed,true);const L=H.L,d=L.door,P=H.P;H.banner=null;d.opening=true;d.open=1;H.intro=0;
  P.face=face;P.x=d.x-face*44;P.y=(d.r+1)*64-4;P.fallY=P.y;P.state='stand';P.t=0;H.cam.snap=true;H.mode='play';if(H.GLP)H.GLP.pipe=false;
  for(let i=0;i<20;i++)H.tick(1);return d.x;}'''
GSTEP = r'''([k,keys])=>{const H=__HK;for(const kk of ['l','r','u'])H.setKey('kb',kk,!!keys[kk]);for(let i=0;i<k;i++){if(H.mode==='play')H.tick(1);}H.render();
  return {mode:H.mode,st:H.P.state,x:H.P.x,dx:H.L.door.x};}'''


def make_gif(b):
    pg = page(b, NEW, 1)
    frames, durs = [], []
    box = (236, 86, 616, 316)

    def grab(ms):
        im = shot(pg).crop(box)
        frames.append(im.convert('P', palette=Image.ADAPTIVE, colors=64)); durs.append(ms)

    for n, seed, mode, face in ((13, 4413, 'torch', -1), (26, 4426, 'classic', 1)):
        pg.evaluate(GIF0, [n, seed, mode, face])
        keys = {'l': face < 0, 'r': face > 0}
        for i in range(60):  # walk to the door
            r = pg.evaluate(GSTEP, [4, keys])
            if abs(r['x'] - r['dx']) < 22: break
            grab(67)
        for i in range(30):  # he comes to a stop, then Up at the door
            r = pg.evaluate(GSTEP, [2, {}]); grab(33)
            if r['st'] == 'stand': break
        for i in range(10):
            r = pg.evaluate(GSTEP, [1, {'u': True}])
            if r['st'] == 'exit': break
        print('exit started' if r['st'] == 'exit' else 'NO EXIT: %s' % r)
        for i in range(38):
            r = pg.evaluate(GSTEP, [4, {}]); grab(67)
            if r['mode'] == 'card': break
        for i in range(3): grab(300)  # the card
        pg.evaluate("([n,mode])=>{const H=__HK;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);H.startLevel(n,-1,true);H.mode='play';H.render();}", [n + 1, mode])
        for i in range(21):
            pg.evaluate(GSTEP, [4, {}]); grab(67)
        for i in range(6):
            pg.evaluate(GSTEP, [4, {'r': True} if pg.evaluate("()=>__HK.L.start.face||1") > 0 else {'l': True}]); grab(67)
    frames[0].save(OUTG, save_all=True, append_images=frames[1:], duration=durs, loop=0, optimize=True, disposal=1)
    print('wrote', OUTG, len(frames), 'frames', os.path.getsize(OUTG), 'bytes', 'errors', pg.errs[:3])


if __name__ == '__main__':
    with tempfile.TemporaryDirectory() as tmp, sync_playwright() as p:
        b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
        if WHAT in ('png', 'all'): make_png(b, old_src(tmp))
        if WHAT in ('gif', 'all'): make_gif(b)
        b.close()
