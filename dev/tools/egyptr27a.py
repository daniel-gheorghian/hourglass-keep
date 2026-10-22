# egyptr27a.py [new.html] [old.html] [--quick]: round 27a's pictures and numbers (owner: "The running jump of the prince: the stride is better
# now, but I think the height is wrong: he moves up too much"), into egypt_themes/:
#   r27a_jump.png  1. the inventory: every jump the bot makes on floors 1-27 (seed 1), grouped by kind and outcome: how often, how high the
#                     hit box rises (P.y, the arc: the same before and after), and as drawn how high the hip, the crown and the lowest foot
#                     rise over the take-off floor, before > after, and the drawn arc's share k of the real one (P.jK);
#                  2. onion skins, before (v73) | after, of running jumps over one, two and three tiles of pit, a saw and the low leap over one
#                     tile (a real floor each, the prince set 80 px back and run at the lip: the game times the take-off), every 4th frame of
#                     the flight, with the hit box's path (dashed red: P.y, the arc), the drawn hip's (blue) and crown's (green) paths;
#                  3. in game at the top of the flight, before | after, Torchlight and Classic: the phone's pixels (1x) and the figure at 3x.
#   r27a_jump.gif  in game, before | after, half speed: the one-tile jump (Torchlight) and the three-tile jump (Classic).
#   r27a.json      the numbers.
# HK_R27A_CACHE=file keeps the bot's measurements between runs. old.html defaults to v73's source (git show bfffe0c:dev/hourglass-keep.html).
# Run from dev/tools. CMU mocap (mocap.cs.cmu.edu, NSF EIA-0196217).
import io, os, subprocess, sys, tempfile, shutil, json, math, collections, statistics as st
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright
import egyptr12 as R12
import egyptr26c as E

HERE = os.path.dirname(os.path.abspath(__file__))
args = [x for x in sys.argv[1:] if not x.startswith('--')]
QUICK = '--quick' in sys.argv
NEW = os.path.abspath(args[0] if args else os.path.join(HERE, '..', 'hourglass-keep.html'))
OLD = args[1] if len(args) > 1 else None
OUTD = os.path.join(HERE, 'egypt_themes')
INK, TXT, DIM = E.INK, E.TXT, E.DIM
# (label, floor, seed, take-off x of a jump the bot made there, its feet's y, facing, the gap in tiles)
EX = [('one tile of pit', 3, 1, 764.0, 636, 1, 1),
      ('two tiles of pit', 2, 2, 568.6, 444, 1, 2),
      ('three tiles of pit', 9, 1, 4680.0, 1916, -1, 3),
      ('a saw', 7, 1, 1594.8, 828, 1, 1),
      ('the low leap over one tile', 4, 1, 4440.6, 1404, 1, 1)]
# as egyptr26c's STEP, but Jump is pressed where the bot pressed it (the take-off x it measured; a saw is not a pit, so the game launches at once)
STEP = r"""([i,face,jx])=>{const H=__HK,P=H.P,k=face>0?'r':'l';if(i===0){H.setKey('kb',k,true);window.__jp=0;}
  if(!window.__jp&&P.state==='run'&&(P.x-jx)*face>-3.2){H.setKey('kb','j',true);window.__jp=1;}else if(window.__jp===1){H.setKey('kb','j',false);window.__jp=2;}
  if(P.state==='land'||(P.state==='stand'&&i>30)||P.state==='hang')H.setKey('kb',k,false);H.tick(1);H.banner=null;
  return {x:P.x,y:P.y,st:P.state,kind:P.jumpKind,low:P.lowJump,jx:P.jx,face:P.face,p:Object.assign({},P.pose),jS:P.jS,jD:P.jD,jF:P.jF,jN:P.jN,t:P.t,yo:P.yo||0,jK:P.jK,jy:P.jy};}"""

MEAS = r"""([n,sd])=>{const J=[];let cur=null;const H=__HK;
 const r=runBot(n,sd,{fight:false,stop:H=>{const p=H.P;
  if(!cur&&p.state==='air'&&(p.jumpKind==='run'||p.jumpKind==='stand'))cur={n,sd,kind:p.jumpKind,low:p.lowJump,jx:p.jx,jy:p.jy,t0:H.gameTime,jS:p.jS,jN:p.jN,jK:p.jK,box:0,hip:-1e9,hip0:null,crown:-1e9,cr0:null,foot:-1e9,kick:false,dyo:0,yo:0};
  if(cur){if(p.jumpKind==='kick'||p.jumpKind==='wall'||p.plant)cur.kick=true;
   if(p.state==='air'){const s=H.skel(p.pose),hip=p.y-s.hipH+(p.yo||0),h=cur.jy-hip,c=cur.jy-(hip+s.hd[1]-H.LEN.hd*1.25),f=cur.jy-(hip+Math.max(s.fF[1],s.fB[1]));
     if(cur.hip0===null){cur.hip0=h;cur.cr0=c;}cur.box=Math.max(cur.box,cur.jy-p.y);cur.hip=Math.max(cur.hip,h);cur.crown=Math.max(cur.crown,c);cur.foot=Math.max(cur.foot,f);
     cur.dyo=Math.max(cur.dyo,Math.abs((p.yo||0)-cur.yo));cur.yo=p.yo||0;}
   else{cur.end=p.state;cur.dx=Math.abs(p.x-cur.jx);cur.dy=p.y-cur.jy;cur.yoEnd=p.yo||0;J.push(cur);cur=null;}}
  return false;}});return {ok:r.ok,J};}"""

GEO = r"""([fr,jy])=>{const H=__HK,o=[];for(const f of fr){const p=Object.assign(H.mk({}),f.p),s=H.skel(p),hip=f.y-s.hipH+(f.yo||0);
 o.push({x:f.x,st:f.st,box:jy-f.y,hip:jy-hip,crown:jy-(hip+s.hd[1]-H.LEN.hd*1.25),foot:jy-(hip+Math.max(s.fF[1],s.fB[1])),yo:f.yo||0});}return o;}"""

# an onion skin as egyptr26c's, the figure drawn with its offset yo, and the paths of the hit box's feet, the hip and the crown
ONION = r"""([fr,S,face,jx,jy])=>{const H=__HK,L=H.L;H.GFX().hd=true;const air=fr.filter(f=>f.st==='air');const pre=fr.filter(f=>f.st==='run').slice(-1),post=fr.filter(f=>f.st==='land').slice(0,1);
  const all=[...pre,...air,...post];let x0=Math.min(...all.map(f=>f.x))-36,x1=Math.max(...all.map(f=>f.x))+36;x1=Math.max(x1,x0+176);const y0=jy-112,y1=jy+40;
  const W=Math.round(x1-x0),Hh=Math.round(y1-y0),cv=document.createElement('canvas');cv.width=W*S;cv.height=Hh*S;const c=cv.getContext('2d');c.scale(S,S);c.translate(-x0,-y0);
  c.fillStyle='#e9dfcc';c.fillRect(x0,y0,W,Hh);
  const r=Math.floor((jy-1)/64);for(let cc=Math.floor(x0/32);cc<=Math.floor(x1/32);cc++)for(let rr=r-2;rr<=r+1;rr++){const b=H.L.base[rr*L.cols+cc],X=cc*32,Y=rr*64;
    if(b===2){c.fillStyle='#8a7a62';c.fillRect(X,Y,32,64);}else if(b===1){c.fillStyle='#b9a888';c.fillRect(X,Y+60,32,4);c.fillStyle='#8a7a62';c.fillRect(X,Y+64,32,6);}
    else if(rr===r&&!H.solidBelow(cc,rr)){c.fillStyle='#3a3028';c.fillRect(X,Y+60,32,44);}
    const f=rr===r?L.feat[rr*L.cols+cc]:null;if(f&&f.t==='spikes'){c.fillStyle='#6a4a20';for(const q of [7,12.5,19,25])c.fillRect(X+q-0.6,Y+60-18,1.2,18);}
    if(f&&f.t==='saw'){c.strokeStyle='#6a6a78';c.lineWidth=1;c.beginPath();c.arc((f.x0+f.x1)/2,Y+62,14,Math.PI,0);c.stroke();}}
  for(let g=0;g<=6;g++){c.strokeStyle='rgba(60,50,40,.18)';c.lineWidth=0.3;c.beginPath();c.moveTo(x0,jy-g*8);c.lineTo(x1,jy-g*8);c.stroke();}
  const pick=[...pre];air.forEach((f,i)=>{if(i%4===0||i===air.length-1)pick.push(f);});pick.push(...post);
  pick.forEach((f,i)=>{c.globalAlpha=0.25+0.75*(i+1)/pick.length;H.figDraw(c,f.x,f.y,f.face,Object.assign(H.mk({}),f.p),H.PAL_HERO,{hasSword:true,time:0,yo:f.yo||0});});
  c.globalAlpha=1;const geo=all.map(f=>{const p=Object.assign(H.mk({}),f.p),s=H.skel(p),hip=f.y-s.hipH+(f.yo||0);return [f.x,f.y,hip,hip+s.hd[1]-H.LEN.hd*1.25];});
  const path=(k,col,dash)=>{c.strokeStyle=col;c.lineWidth=1.6/S*2;c.setLineDash(dash?[3,2]:[]);c.beginPath();geo.forEach((g,i)=>{const x=g[0]+(k===1?0:face*0);if(i)c.lineTo(x,g[k]);else c.moveTo(x,g[k]);});c.stroke();c.setLineDash([]);};
  path(1,'#c0392b',true);path(2,'#2e6bd8',false);path(3,'#1f9a55',false);
  c.strokeStyle='#c0392b';c.lineWidth=1/S*2;c.beginPath();c.moveTo(jx,jy+3);c.lineTo(jx,jy+9);c.stroke();
  return [cv.toDataURL('image/png'),W*S,Hh*S];}"""


def old_src(tmp):
    if OLD:
        return os.path.abspath(OLD)
    fn = os.path.join(tmp, '_v73.html')
    open(fn, 'w', encoding='utf-8').write(subprocess.run(['git', 'show', 'bfffe0c:dev/hourglass-keep.html'], cwd=HERE, capture_output=True, text=True, check=True).stdout)
    return fn


def play(pg, ex):
    _, n, sd, jx, jy, face, _ = ex
    pg.evaluate(E.SETUP, [n, sd, jx, jy, face])
    fr = []
    for i in range(140):
        f = pg.evaluate(STEP, [i, face, jx])
        fr.append(f)
        if f['st'] in ('stand', 'hang') and any(q['st'] == 'air' for q in fr) and i > 30:
            break
    return fr


def measure(b, src):
    J = []
    for n in range(1, 28 if not QUICK else 8):
        pg = E.page(b, src)
        r = pg.evaluate(MEAS, [n, 1])
        J += r['J']
        if pg.errs or not r['ok']:
            print('bot', n, r['ok'], pg.errs[:2])
        pg.close()
    return J


def cat(j):
    if j['kick']:
        return None
    dy = j['dy']
    lv = 'level' if abs(dy) < 8 else ('down a storey' if dy > 0 else 'up')
    if j['end'] == 'hang':
        lv = 'to a ledge a storey up' if abs(dy) < 8 else 'short, caught the far lip'
    if j['end'] == 'swing':
        lv = 'to a swing bar'
    k = ('running' if j['kind'] == 'run' else 'standing') + (' low leap' if j['low'] else ' jump')
    g = ''
    if j['kind'] == 'run' and j['end'] == 'land' and abs(dy) < 8:
        N = j['jN']
        g = ', no pit or trap' if N is None or N > 1e8 else (', one tile (pit or trap)' if N < 60 else ', two tiles' if N < 95 else ', three tiles')
    return '%s %s%s' % (k, lv, g)


def table(JB, JA):
    key = lambda j: (j['n'], j['sd'], round(j['jx'], 1), round(j['jy']))
    BK = {key(j): j for j in JB}
    groups = collections.OrderedDict()
    for j in JA:
        c = cat(j)
        if c and key(j) in BK:
            groups.setdefault(c, []).append((BK[key(j)], j))
    rows = []
    for c in sorted(groups, key=lambda c: (c.startswith('standing'), c)):
        G = groups[c]
        m = lambda f: st.median(f(x) for x in G)
        rise = lambda j, a, b: j[a] - j[b]
        ks = [x[1]['jK'] if x[1]['jK'] is not None else 1 for x in G]
        rows.append({'what': c, 'n': len(G), 'box': round(m(lambda x: x[1]['box']), 1),
                     'hip': '%.1f > %.1f' % (m(lambda x: rise(x[0], 'hip', 'hip0')), m(lambda x: rise(x[1], 'hip', 'hip0'))),
                     'crown': '%.1f > %.1f' % (m(lambda x: rise(x[0], 'crown', 'cr0')), m(lambda x: rise(x[1], 'crown', 'cr0'))),
                     'foot': '%.1f > %.1f' % (m(lambda x: x[0]['foot']), m(lambda x: x[1]['foot'])),
                     'k': ('%.2f' % min(ks)) + ('' if abs(min(ks) - max(ks)) < 0.005 else '-%.2f' % max(ks)),
                     'same': all(abs(x[0]['dx'] - x[1]['dx']) < 0.01 and abs(x[0]['dy'] - x[1]['dy']) < 0.01 and x[0]['end'] == x[1]['end'] for x in G),
                     'dyo': round(max(x[1]['dyo'] for x in G), 2), 'yoEnd': round(max(abs(x[1]['yoEnd']) for x in G), 3)})
    return rows


def table_img(rows, W):
    lh = 16
    im = Image.new('RGB', (W, lh * (len(rows) + 4)), INK)
    d = ImageDraw.Draw(im)
    X = [6, 330, 375, 450, 590, 730, 870, 960]
    H = ('jump, bot on floors 1-27', 'n', 'box px', 'hip rises, bef > aft', 'crown rises', 'lowest foot over floor', 'k', 'flight same')
    for x, h in zip(X, H):
        d.text((x, 4), h, fill=TXT)
    y = 4 + lh + 2
    for r in rows:
        for x, k in zip(X, ('what', 'n', 'box', 'hip', 'crown', 'foot', 'k', 'same')):
            d.text((x, y), str(r[k]), fill=TXT if k in ('what', 'hip', 'crown') else DIM)
        y += lh
    d.text((6, y + 2), 'box: how high the hit box (P.y, the arc: unchanged) rises over the take-off floor. Hip, crown: how much the drawn hip and crown rise over '
           'the flight (medians, the game\'s px; he is 51.5 px tall). Lowest foot: its highest point over the floor.', fill=DIM)
    d.text((6, y + 18), 'k: the drawn arc over the real one (P.jK, 1 = drawn on the arc). Flight same: distance, drop and how it ends identical before and '
           'after (the bot, the arc and the hit box are untouched).', fill=DIM)
    return im


def onion(pages):
    rows, nums = [], []
    for ex in EX:
        cells = []
        for t in ('before', 'after'):
            pg = pages[t]
            fr = play(pg, ex)
            g = pg.evaluate(GEO, [fr, ex[4]])
            air = [q for q in g if q['st'] == 'air']
            a0 = next(f for f in fr if f['st'] == 'air')
            u, w, h = pg.evaluate(ONION, [fr, 3, ex[5], a0['jx'], ex[4]])
            im = E.img(u)
            I = {'box': max(q['box'] for q in air), 'hip': max(q['hip'] for q in air) - air[0]['hip'], 'crown': max(q['crown'] for q in air) - air[0]['crown'],
                 'foot': max(q['foot'] for q in air), 'k': a0.get('jK') if t == 'after' else 1, 's': a0['jS'],
                 'dyo': max(abs(air[i]['yo'] - air[i - 1]['yo']) for i in range(1, len(air))), 'end': fr[-1]['st']}
            E.label(im, '%s, %s: box rises %.1f px; drawn hip %.1f, crown %.1f; lowest foot %.1f px up\ns %.2f, k %.2f' % (
                ex[0], 'before (v73)' if t == 'before' else 'after', I['box'], I['hip'], I['crown'], I['foot'], I['s'] or 0, I['k'] if I['k'] is not None else 1))
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


def ingame(b, srcs):
    """the top of the flight in game, before | after, both modes: the phone's pixels and the figure at 3x"""
    out = []
    for mode in ('torch', 'classic'):
        for ex in (EX[0], EX[2]):
            cells = []
            for t, s in srcs.items():
                pg = R12.page(b, s, mode)
                _, n, sd, jx, jy, face, _ = ex
                pg.evaluate(E.SETUP, [n, sd, jx, jy, face])
                pg.evaluate("()=>{__HK.intro=0;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);}")
                top, i = None, 0
                while i < 140:
                    f = pg.evaluate(STEP, [i, face, jx])
                    i += 1
                    if f['st'] == 'air' and f['jy'] - f['y'] > 23.5:   # the arc's top
                        top = f
                        break
                pg.evaluate('()=>__P.draw()')
                # a region 120 x 96 of the game's px round him (the take-off floor at its foot): 1x is the game's own pixels, 3x three device
                # pixels to one (both from the phone-sized screenshot, LANCZOS)
                g = pg.evaluate("()=>{const X=__HK.XF,cv=[...document.querySelectorAll('canvas')].find(q=>q.getBoundingClientRect().width>0);return X.VZ/cv.width*cv.getBoundingClientRect().width*2;}")
                c0 = pg.evaluate('([x,y])=>__P.scr(x,y)', [top['x'] - 60, jy - 84])
                im = R12.shot(pg)
                box = (int(c0[0] * 2), int(c0[1] * 2), int(c0[0] * 2 + 120 * g), int(c0[1] * 2 + 96 * g))
                a = im.crop(box).resize((120, 96), Image.LANCZOS)
                big = im.crop(box).resize((360, 288), Image.LANCZOS)
                lab = '%s, %s, %s' % (ex[0], 'before (v73)' if t == 'before' else 'after', 'Torchlight' if mode == 'torch' else 'Classic')
                a2 = Image.new('RGB', (190, 288), INK)
                a2.paste(a, (4, 150))
                E.label(a2, lab.replace(', ', ',\n', 1) + '\n1x (the game\'s px)', (4, 4))
                E.label(big, '3x')
                a = a2
                c = Image.new('RGB', (a.width + big.width + 4, max(a.height, big.height)), INK)
                c.paste(a, (0, 0))
                c.paste(big, (a.width + 4, 0))
                cells.append(c)
                if pg.errs:
                    print('errors', t, mode, pg.errs[:2])
                pg.close()
            row = Image.new('RGB', (sum(c.width for c in cells) + 8, cells[0].height), INK)
            row.paste(cells[0], (0, 0))
            row.paste(cells[1], (cells[0].width + 8, 0))
            out.append(row)
    return out


def gif(b, srcs):
    frames = {}
    for t, s in srcs.items():
        seq = []
        for ex, mode in ((EX[0], 'torch'), (EX[2], 'classic')):
            pg = R12.page(b, s, mode)
            _, n, sd, jx, jy, face, _ = ex
            pg.evaluate(E.SETUP, [n, sd, jx, jy, face])
            pg.evaluate("()=>{__HK.intro=0;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);}")
            started = False
            for i in range(120):
                f = pg.evaluate(STEP, [i, face, jx])
                started = started or f['st'] == 'air'
                if i % 2 == 0 and i >= 8:
                    pg.evaluate('()=>__P.draw()')
                    xy = pg.evaluate('([x,y])=>__P.scr(x,y)', [f['x'] + face * 16, jy - 34])
                    im = R12.crop(R12.shot(pg), xy, 440, 260)
                    E.label(im, '%s, %s, %s (half speed)' % (ex[0], 'before (v73)' if t == 'before' else 'after', 'Torchlight' if mode == 'torch' else 'Classic'))
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
    fn = os.path.join(OUTD, 'r27a_jump.gif')
    out[0].save(fn, save_all=True, append_images=out[1:], duration=66, loop=0, optimize=True)
    return fn, len(out)


if __name__ == '__main__':
    tmp = tempfile.mkdtemp()
    try:
        srcs = {'before': old_src(tmp), 'after': NEW}
        with sync_playwright() as p:
            b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
            cache = os.environ.get('HK_R27A_CACHE')
            if cache and os.path.exists(cache):
                JB, JA = json.load(open(cache))
            else:
                JB, JA = measure(b, srcs['before']), measure(b, srcs['after'])
                if cache:
                    json.dump([JB, JA], open(cache, 'w'))
            rows = table(JB, JA)
            pages = {t: E.page(b, s) for t, s in srcs.items()}
            orows, nums = onion(pages)
            for t, pg in pages.items():
                if pg.errs:
                    print('errors', t, pg.errs[:3])
                pg.close()
            grows = ingame(b, srcs)
            gfn, gn = gif(b, srcs)
            b.close()
        W = max(max(r.width for r in orows), max(r.width for r in grows), 1100)
        head = Image.new('RGB', (W, 46), INK)
        d = ImageDraw.Draw(head)
        d.text((6, 4), 'Round 27a: the running jump\'s height (owner: "the stride is better now, but I think the height is wrong: he moves up too much").', fill=TXT)
        d.text((6, 22), 'The arc rises 25.8 px (half his height) and the figure followed it; now he is drawn on a lower arc of the same shape, 8 px (a stretched '
               'stride) to 14 px (the full leap; PoP1: 14 px of a 63 px storey), unless what he clears or catches needs more.', fill=TXT)
        mid = Image.new('RGB', (W, 22), INK)
        ImageDraw.Draw(mid).text((6, 4), 'Onion skins, before | after (every 4th frame of the flight, darker later; red tick: take-off; dashed red: the hit box\'s feet, '
                                 'the arc; blue: the drawn hip; green: the drawn crown; grey lines every 8 px over the take-off floor).', fill=TXT)
        mid2 = Image.new('RGB', (W, 22), INK)
        ImageDraw.Draw(mid2).text((6, 4), 'In game at the top of the arc, before | after, Torchlight then Classic: a crop of the phone\'s pixels and the figure at 3x.', fill=TXT)
        parts = [head, table_img(rows, W), mid] + orows + [mid2] + grows
        sheet = Image.new('RGB', (W, sum(r.height + 8 for r in parts)), INK)
        y = 0
        for r in parts:
            sheet.paste(r, (0, y))
            y += r.height + 8
        sheet.save(os.path.join(OUTD, 'r27a_jump.png'), optimize=True)
        json.dump({'table': rows, 'examples': nums}, open(os.path.join(HERE, 'r27a.json'), 'w'), indent=1, default=float)
        print('wrote r27a_jump.png', sheet.size, gfn, gn, 'frames', round(os.path.getsize(gfn) / 1e6, 2), 'MB')
        for r in rows:
            print('%-52s n %4d box %5.1f hip %-14s crown %-14s foot %-14s k %-10s same %s dyo %.2f yoEnd %.3f' % (r['what'], r['n'], r['box'], r['hip'], r['crown'], r['foot'], r['k'], r['same'], r['dyo'], r['yoEnd']))
        for q in nums:
            print(q)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
