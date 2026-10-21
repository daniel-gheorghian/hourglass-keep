# egyptr26c.py [new.html] [old.html] [--quick]: round 26c's pictures and numbers (owner: "when jumping the stride is too large. It works for
# large gaps but for smaller gaps looks silly. I'd adjust the stride with the actual distance he jumps"), into egypt_themes/:
#   r26c_stride.png  1. the inventory: every jump the bot makes on floors 1-27 (seeds 1 and 2; --quick: seed 1 only), grouped by kind and
#                       outcome: how often, the distance flown (take-off to landing or grab, px) and the air time, the distance the jump is
#                       for (jumpSpan: D, and the blend s), and as drawn the widest split of the thighs and the widest the feet get apart
#                       over the flight, before | after;
#                    2. onion skins, before | after, of running jumps over one, two and three tiles of pit and the low leap over one tile
#                       (a real floor each, the prince set 80 px back and run at the lip: the game times the take-off), every 4th frame
#                       of the flight, with the distance flown, the gap, D, s, the split and the feet;
#   r26c_jumps.gif   in game (Torchlight, the phone's resolution, 3/4 size), before | after, the one-tile and three-tile jumps at half speed.
#   r26c.json        the numbers.
# HK_R26C_CACHE=file keeps the bot's measurements between runs (while working on the pictures).
# old.html defaults to round 26b's source (git show 0c44572:dev/hourglass-keep.html). Run from dev/tools. CMU mocap (mocap.cs.cmu.edu, NSF
# EIA-0196217).
import io, os, subprocess, sys, tempfile, shutil, base64, json, math, collections, statistics as st
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright
import egyptr12 as R12

HERE = os.path.dirname(os.path.abspath(__file__))
args = [x for x in sys.argv[1:] if not x.startswith('--')]
QUICK = '--quick' in sys.argv
NEW = os.path.abspath(args[0] if args else os.path.join(HERE, '..', 'hourglass-keep.html'))
OLD = args[1] if len(args) > 1 else None
OUTD = os.path.join(HERE, 'egypt_themes')
INK = (20, 16, 24)
TXT = (250, 240, 215)
DIM = (170, 160, 140)
# the examples: (label, floor, seed, take-off x of a jump the bot made there, its feet's y, facing, the gap in tiles)
EX = [('one tile of pit', 3, 1, 764.0, 636, 1, 1),
      ('two tiles of pit', 2, 2, 568.6, 444, 1, 2),
      ('three tiles of pit', 10, 1, 5080.4, 1212, 1, 3),
      ('the low leap over one tile', 4, 1, 4440.6, 1404, 1, 1)]

# every jump the bot makes: kind, low, outcome, take-off/landing, air time, jumpSpan's numbers, the widest split and feet over the flight
MEAS = r"""([n,sd])=>{const J=[];let cur=null;const H=__HK;
 const r=runBot(n,sd,{fight:false,stop:H=>{const p=H.P;
  if(!cur&&p.state==='air'&&(p.jumpKind==='run'||p.jumpKind==='stand'))cur={n,sd,kind:p.jumpKind,low:p.lowJump,jx:p.jx,jy:p.jy,t0:H.gameTime,jS:p.jS,jD:p.jD,jF:p.jF,jN:p.jN,msp:0,mft:0,kick:false};
  if(cur){if(p.jumpKind==='kick'||p.jumpKind==='wall'||p.plant)cur.kick=true;
   if(p.state==='air'){const q=p.pose,sp=q.hF-q.hB,s=H.skel(q),fd=Math.hypot(s.fF[0]-s.fB[0],s.fF[1]-s.fB[1]);if(sp>cur.msp)cur.msp=sp;if(fd>cur.mft)cur.mft=fd;}
   else{cur.end=p.state;cur.T=H.gameTime-cur.t0;cur.dx=Math.abs(p.x-cur.jx);cur.dy=p.y-cur.jy;J.push(cur);cur=null;}}
  return false;}});return {ok:r.ok,J};}"""
# the prince set 80 px back from the take-off, run at the lip: Jump pressed early, the game launches him at the hazard's edge
SETUP = r"""([n,sd,jx,jy,face])=>{const H=__HK;__P.load(n,sd);H.GFX().hd=true;const P=H.P;P.inv=1e9;P.x=jx-face*80;P.y=jy;P.fallY=jy;P.vx=P.vy=0;P.state='stand';P.face=face;
  H.cam.snap=true;H.tick(1);P.x=jx-face*80;P.y=jy;P.state='stand';P.face=face;H.cam.snap=true;H.tick(1);H.banner=null;return [P.x,P.y];}"""
STEP = r"""([i,face])=>{const H=__HK,P=H.P,k=face>0?'r':'l';if(i===0)H.setKey('kb',k,true);if(i===10)H.setKey('kb','j',true);if(i===11)H.setKey('kb','j',false);
  if(P.state==='land'||(P.state==='stand'&&i>30)||P.state==='hang')H.setKey('kb',k,false);H.tick(1);H.banner=null;
  return {x:P.x,y:P.y,st:P.state,kind:P.jumpKind,low:P.lowJump,jx:P.jx,face:P.face,p:Object.assign({},P.pose),jS:P.jS,jD:P.jD,jF:P.jF,jN:P.jN,t:P.t};}"""
# an onion skin: the tiles round the jump (a plain diagram: stone, floor's top, the pit), the figure every 4th frame of the flight
ONION = r"""([fr,S,face,jx,jy])=>{const H=__HK,L=H.L;H.GFX().hd=true;const air=fr.filter(f=>f.st==='air');const pre=fr.filter(f=>f.st==='run').slice(-1),post=fr.filter(f=>f.st==='land').slice(0,1);
  const all=[...pre,...air,...post];let x0=Math.min(...all.map(f=>f.x))-36,x1=Math.max(...all.map(f=>f.x))+36;const y0=jy-104,y1=jy+40;
  const W=Math.round(x1-x0),Hh=Math.round(y1-y0),cv=document.createElement('canvas');cv.width=W*S;cv.height=Hh*S;const c=cv.getContext('2d');c.scale(S,S);c.translate(-x0,-y0);
  c.fillStyle='#e9dfcc';c.fillRect(x0,y0,W,Hh);
  const r=Math.floor((jy-1)/64);for(let cc=Math.floor(x0/32);cc<=Math.floor(x1/32);cc++)for(let rr=r-2;rr<=r+1;rr++){const b=H.L.base[rr*L.cols+cc],X=cc*32,Y=rr*64;
    if(b===2){c.fillStyle='#8a7a62';c.fillRect(X,Y,32,64);}else if(b===1){c.fillStyle='#b9a888';c.fillRect(X,Y+60,32,4);c.fillStyle='#8a7a62';c.fillRect(X,Y+64,32,6);}
    else if(rr===r&&!H.solidBelow(cc,rr)){c.fillStyle='#3a3028';c.fillRect(X,Y+60,32,44);}}
  const pick=[...pre];air.forEach((f,i)=>{if(i%4===0||i===air.length-1)pick.push(f);});pick.push(...post);
  pick.forEach((f,i)=>{c.globalAlpha=0.25+0.75*(i+1)/pick.length;H.figDraw(c,f.x,f.y,f.face,Object.assign(H.mk({}),f.p),H.PAL_HERO,{hasSword:true,time:0});});
  c.globalAlpha=1;c.strokeStyle='#c0392b';c.lineWidth=1/S*2;c.beginPath();c.moveTo(jx,jy+3);c.lineTo(jx,jy+9);c.stroke();
  return [cv.toDataURL('image/png'),W*S,Hh*S];}"""


def old_src(tmp):
    if OLD:
        return os.path.abspath(OLD)
    fn = os.path.join(tmp, '_r26b.html')
    open(fn, 'w', encoding='utf-8').write(subprocess.run(['git', 'show', '0c44572:dev/hourglass-keep.html'], cwd=HERE, capture_output=True, text=True, check=True).stdout)
    return fn


def img(u):
    return Image.open(io.BytesIO(base64.b64decode(u.split(',')[1]))).convert('RGB')


def label(im, t, xy=(4, 2), col=TXT, bg=(0, 0, 0)):
    d = ImageDraw.Draw(im)
    for k, line in enumerate(t.split('\n')):
        y = xy[1] + 14 * k
        d.rectangle((xy[0] - 2, y - 1, xy[0] + 6 * len(line) + 4, y + 12), fill=bg)
        d.text((xy[0], y), line, fill=col)
    return im


def page(b, src):
    pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=2)
    pg.errs = []
    pg.on('pageerror', lambda e, pg=pg: pg.errs.append(str(e)))
    pg.goto('file://' + src)
    pg.wait_for_timeout(600)
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true)")
    pg.evaluate(R12.PC['JS'])
    pg.add_script_tag(path=os.path.join(HERE, 'bot.js'))
    return pg


def measure(b, src):
    J = []
    for n in range(1, 28):
        for sd in ((1,) if QUICK else (1, 2)):
            pg = page(b, src)
            r = pg.evaluate(MEAS, [n, sd])
            J += r['J']
            if pg.errs:
                print('errors', n, sd, pg.errs[:2])
            pg.close()
    return J


def cat(j):
    if j['kick']:
        return None
    dy = j['dy']
    lv = 'level' if abs(dy) < 8 else ('down a storey' if dy > 0 else 'up')
    if j['end'] == 'hang':
        lv = 'to a ledge a storey up' if abs(dy) < 8 else 'to the far ledge'
    if j['end'] == 'swing':
        lv = 'to a swing bar'
    k = ('running' if j['kind'] == 'run' else 'standing') + (' low leap' if j['low'] else ' jump')
    g = ''
    if j['kind'] == 'run' and j['end'] == 'land' and abs(dy) < 8:
        N = j['jN']
        g = ', no pit or trap in front' if N is None or N > 1e8 else (', one tile' if N < 60 else ', two tiles' if N < 95 else ', three tiles')
    return '%s %s%s' % (k, lv, g)


def table(JB, JA):
    groups = collections.OrderedDict()
    key = lambda j: (j['n'], j['sd'], round(j['jx'], 1), round(j['jy']))
    CA = {key(j): cat(j) for j in JA}   # the same jumps in both builds (the arcs are unchanged): sorted by the after build's jumpSpan
    for t, J in (('before', JB), ('after', JA)):
        for j in J:
            c = CA.get(key(j))
            if c:
                groups.setdefault(c, {'before': [], 'after': []})[t].append(j)
    rows = []
    for c in sorted(groups, key=lambda c: (c.startswith('standing'), c)):
        B, A = groups[c]['before'], groups[c]['after']
        if not A:
            continue
        m = lambda L, k: st.median(x[k] for x in L)
        rng = lambda L, k, f=1.0: ('%.0f' % (min(x[k] for x in L) * f)) + ('' if round(min(x[k] for x in L) * f) == round(max(x[k] for x in L) * f) else '-%.0f' % (max(x[k] for x in L) * f))
        rng1 = lambda L, k: ('%.1f' % min(x[k] for x in L)) + ('' if abs(min(x[k] for x in L) - max(x[k] for x in L)) < 0.05 else '-%.1f' % max(x[k] for x in L))
        Dv = [x['jD'] for x in A if x.get('jD') is not None]
        Sv = [x['jS'] for x in A if x.get('jS') is not None]
        rows.append({'what': c, 'n': len(A), 'dx': round(m(A, 'dx'), 1), 'T': round(m(A, 'T'), 2),
                     'D': ('%.0f-%.0f' % (min(Dv), max(Dv))) if Dv and A[0]['kind'] == 'run' else '-',
                     's': ('%.2f-%.2f' % (min(Sv), max(Sv))) if Sv and A[0]['kind'] == 'run' else '-',
                     'split': '%s > %s' % (rng(B, 'msp', 180 / math.pi), rng(A, 'msp', 180 / math.pi)),
                     'feet': '%s > %s' % (rng1(B, 'mft'), rng1(A, 'mft'))})
    return rows


def table_img(rows, W):
    lh = 16
    im = Image.new('RGB', (W, lh * (len(rows) + 3)), INK)
    d = ImageDraw.Draw(im)
    X = [6, 330, 380, 470, 540, 620, 720, 880]
    H = ('jump, bot on floors 1-27', 'n', 'flown px', 'air s', 'D px', 's', 'split deg, before > after', 'feet apart px, before > after')
    for x, h in zip(X, H):
        d.text((x, 4), h, fill=TXT)
    y = 4 + lh + 2
    for r in rows:
        for x, k in zip(X, ('what', 'n', 'dx', 'T', 'D', 's', 'split', 'feet')):
            d.text((x, y), str(r[k]), fill=TXT if k in ('what', 'split', 'feet') else DIM)
        y += lh
    d.text((6, y + 2), 'flown: take-off to landing or grab (the game\'s px; a tile is 32). D: what the jump is for (jumpSpan: the arc to the first floor, '
           'or a pit\'s far lip + 12); s = (D - 48) / (the level arc - 48). Split, feet: widest over the flight as drawn (P.pose).', fill=DIM)
    return im


def play(pg, ex):
    _, n, sd, jx, jy, face, _ = ex
    pg.evaluate(SETUP, [n, sd, jx, jy, face])
    fr = []
    for i in range(140):
        f = pg.evaluate(STEP, [i, face])
        fr.append(f)
        if f['st'] in ('stand', 'hang') and any(q['st'] == 'air' for q in fr) and i > 30:
            break
    return fr


def info(fr):
    air = [f for f in fr if f['st'] == 'air']
    a0 = air[0]
    end = next(f for f in fr[fr.index(a0):] if f['st'] != 'air')
    sk = lambda p: None
    msp = max(f['p']['hF'] - f['p']['hB'] for f in air)
    return {'dx': abs(end['x'] - a0['jx']), 'T': len(air) / 60.0, 'D': a0['jD'], 's': a0['jS'], 'need': a0['jN'], 'fly': a0['jF'], 'low': a0['low'],
            'kind': a0['kind'], 'msp': math.degrees(msp), 'jx': a0['jx']}


FEET = r"""(fr)=>{const H=__HK;let m=0;for(const f of fr){if(f.st!=='air')continue;const s=H.skel(Object.assign(H.mk({}),f.p));m=Math.max(m,Math.hypot(s.fF[0]-s.fB[0],s.fF[1]-s.fB[1]));}return m;}"""


def onion(pages, b):
    rows, nums = [], []
    for ex in EX:
        cells = []
        for t in ('before', 'after'):
            pg = pages[t]
            fr = play(pg, ex)
            I = info(fr)
            I['feet'] = pg.evaluate(FEET, fr)
            u, w, h = pg.evaluate(ONION, [fr, 3, ex[5], I['jx'], ex[4]])
            im = img(u)
            s = '-' if I['s'] is None else '%.2f' % I['s']
            D = '-' if I['D'] is None else '%.0f' % I['D']
            label(im, '%s, %s: %s %s, flown %.1f px in %.2f s\nD %s px, s %s; widest split %.0f deg, feet %.1f px apart' % (
                ex[0], t, 'low leap' if I['low'] else 'running jump', '(%d tile%s)' % (ex[6], 's' if ex[6] > 1 else ''), I['dx'], I['T'], D, s, I['msp'], I['feet']))
            cells.append(im)
            nums.append({'ex': ex[0], 'build': t, **I})
        Wd = sum(c.width for c in cells) + 8
        row = Image.new('RGB', (Wd, max(c.height for c in cells)), INK)
        x = 0
        for c in cells:
            row.paste(c, (x, 0))
            x += c.width + 8
        rows.append(row)
    return rows, nums


def gif(b, srcs):
    frames = {}
    for t, s in srcs.items():
        pg = R12.page(b, s, 'torch')
        seq = []
        for ex in (EX[0], EX[2]):   # a short and a long jump (the GIF under 5 MB)
            _, n, sd, jx, jy, face, _ = ex
            pg.evaluate(SETUP, [n, sd, jx, jy, face])
            pg.evaluate("()=>{__HK.intro=0;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);}")
            started = False
            for i in range(120):
                f = pg.evaluate(STEP, [i, face])
                started = started or f['st'] == 'air'
                if i % 2 == 0 and i >= 8:
                    pg.evaluate('()=>__P.draw()')
                    xy = pg.evaluate('([x,y])=>__P.scr(x,y)', [f['x'] + face * 16, f['y'] - 22])   # on him, the floor in view
                    im = R12.crop(R12.shot(pg), xy, 440, 260)
                    label(im, '%s, %s (half speed)' % (ex[0], t))
                    seq.append(im)
                if started and f['st'] in ('stand',) and i > 40:
                    break
            for k in range(6):
                seq.append(seq[-1])
        if pg.errs:
            print('errors', t, pg.errs[:3])
        pg.close()
        frames[t] = seq
    n = min(len(frames['before']), len(frames['after']))
    out = []
    for i in range(n):
        a, c = frames['before'][i], frames['after'][i]
        im = Image.new('RGB', (a.width + c.width + 6, a.height), INK)
        im.paste(a, (0, 0))
        im.paste(c, (a.width + 6, 0))
        out.append(im.resize((im.width * 3 // 4, im.height * 3 // 4), Image.LANCZOS).quantize(colors=64, method=Image.MEDIANCUT, dither=Image.NONE))
    fn = os.path.join(OUTD, 'r26c_jumps.gif')
    out[0].save(fn, save_all=True, append_images=out[1:], duration=66, loop=0, optimize=True)
    return fn, len(out)


if __name__ == '__main__':
    tmp = tempfile.mkdtemp()
    try:
        srcs = {'before': old_src(tmp), 'after': NEW}
        with sync_playwright() as p:
            b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
            cache = os.environ.get('HK_R26C_CACHE')
            if cache and os.path.exists(cache):
                JB, JA = json.load(open(cache))
            else:
                JB, JA = measure(b, srcs['before']), measure(b, srcs['after'])
                if cache:
                    json.dump([JB, JA], open(cache, 'w'))
            rows = table(JB, JA)
            pages = {t: page(b, s) for t, s in srcs.items()}
            orows, nums = onion(pages, b)
            for t, pg in pages.items():
                if pg.errs:
                    print('errors', t, pg.errs[:3])
                pg.close()
            gfn, gn = gif(b, srcs)
            b.close()
        W = max(r.width for r in orows)
        head = Image.new('RGB', (W, 46), INK)
        d = ImageDraw.Draw(head)
        d.text((6, 4), 'Round 26c: the stride for the distance (owner: "when jumping the stride is too large. It works for large gaps but for smaller gaps looks silly. '
               'I\'d adjust the stride with the actual distance he jumps").', fill=TXT)
        d.text((6, 22), 'Every running jump flies the same arc on a level floor (97.6 px, 0.53 s); v72 drew all of them with one held split. After: a flight from a '
               'running stride (09_01) to the leap (49_04), blended by what the jump is for.', fill=TXT)
        mid = Image.new('RGB', (W, 22), INK)
        ImageDraw.Draw(mid).text((6, 4), 'Onion skins, before | after: the prince set 80 px back on the floor the bot jumped from and run at the lip; every 4th frame of the '
                                 'flight (darker later); red tick: take-off.', fill=TXT)
        parts = [head, table_img(rows, W), mid] + orows
        sheet = Image.new('RGB', (W, sum(r.height + 8 for r in parts)), INK)
        y = 0
        for r in parts:
            sheet.paste(r, (0, y))
            y += r.height + 8
        sheet.save(os.path.join(OUTD, 'r26c_stride.png'), optimize=True)
        json.dump({'table': rows, 'examples': nums}, open(os.path.join(HERE, 'r26c.json'), 'w'), indent=1, default=float)
        print('wrote r26c_stride.png', sheet.size, gfn, gn, 'frames', round(os.path.getsize(gfn) / 1e6, 2), 'MB')
        for r in rows:
            print('%-58s n %4d flown %6.1f T %.2f D %-8s s %-10s split %-12s feet %s' % (r['what'], r['n'], r['dx'], r['T'], r['D'], r['s'], r['split'], r['feet']))
        for q in nums:
            print(q)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
