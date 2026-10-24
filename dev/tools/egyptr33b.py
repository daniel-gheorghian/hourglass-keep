# egyptr33b.py [new.html] [old.html] [--measure]: round 33b's pictures and numbers (owner after v78: "the tiptoe animation: research this
# also against the PoP animation"), into egypt_themes/:
#   r33b_tiptoe.png  PoP 1989 (its own sprites, SDLPoP seqtbl.c step14 and testfoot at 12 fps) | v78 | round 33b: onion skins (later frames
#                    darker; the hit box's x dashed red, the drawn hip blue) and frame strips of one careful step, of Grab held across a row
#                    of stakes (the bot's way), and of a step at a drop's lip pressed again (PoP's test foot)
#   r33b_tiptoe.gif  Grab held across the stakes and the lip, v78 | round 33b, at half speed
#   r33b.json        (local) the numbers --measure prints: per build and scene, how far each foot slides while it is on the floor (px, summed
#                    over the frames its ball stays within 0.6 px of its lowest), each foot's highest lift (ball and heel), the hip's lowest (px under standing),
#                    the order the feet leave the floor, the arms' velocity correlation, the frames held still
# old.html defaults to v78's source (git show HEAD:dev/hourglass-keep.html when it is the parent, else hk_v78_release.html). The PoP sprites are
# read from ref/pop1/ (or HK_POP1): SDLPoP's KID images (fNNN_resMMM.png: frame NNN of frame_table_kid, image res MMM), local only.
# Run from dev/tools. CMU mocap (mocap.cs.cmu.edu, NSF EIA-0196217): 139_29.
import os, sys, json, math, glob, subprocess, tempfile, shutil
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright
import egyptr26c as E

HERE = os.path.dirname(os.path.abspath(__file__))
args = [x for x in sys.argv[1:] if not x.startswith('--')]
MEASURE = '--measure' in sys.argv
NEW = os.path.abspath(args[0] if args else os.path.join(HERE, '..', 'hourglass-keep.html'))
OLD = os.path.abspath(args[1]) if len(args) > 1 else None
POP = os.environ.get('HK_POP1', os.path.join(HERE, 'ref', 'pop1'))
OUTD = os.path.join(HERE, 'egypt_themes')
INK, TXT, DIM = E.INK, E.TXT, E.DIM
S = 3
EXPORT = 'window.__J33={livePose,footRot,FOOTP,rd:()=>RD};'

FIND = r"""([n,sd])=>{__P.load(n,sd);const H=__HK,L=H.L,C=L.cols,sp=[],ed=[];
 for(let r=1;r<L.rows;r++)for(let c=3;c<C-4;c++){const f=L.feat[r*C+c],p=L.feat[r*C+c-1],ok=cc=>H.solidBelow(cc,r)&&!L.feat[r*C+cc]&&L.base[r*C+cc]!==2&&L.base[(r-1)*C+cc]!==2;
   if(f&&f.t==='spikes'&&!(p&&p.t==='spikes')){let k=0;while(L.feat[r*C+c+k]&&L.feat[r*C+c+k].t==='spikes')k++;if(ok(c-1)&&ok(c-2)&&ok(c+k)&&ok(c+k+1))sp.push({c,r,k});}
   if(ok(c)&&ok(c-1)&&ok(c-2)&&!H.solidBelow(c+1,r)&&L.base[r*C+c+1]!==2&&L.base[(r-1)*C+c+1]!==2)ed.push({c,r});}
 return {sp,ed};}"""
SETUP = r"""([n,sd,x,y,face])=>{const H=__HK;__P.load(n,sd);H.GFX().hd=true;const P=H.P;P.inv=1e9;
  for(let k=0;k<2;k++){P.x=x;P.y=y;P.fallY=y;P.vx=P.vy=0;P.state='stand';P.t=0;P.face=face;H.cam.snap=true;H.tick(1);}H.banner=null;
  for(let k=0;k<40;k++){P.x=x;H.tick(1);}H.banner=null;return [P.x,P.y,P.state];}"""
# one game frame. mode 'tap': Grab held, the way tapped at frame 0 (and again at 'again'); 'hold': Grab and the way held for 'hold' frames
STEP = r"""([i,face,mode,hold,again])=>{const H=__HK,P=H.P,k=face>0?'r':'l';
  if(mode==='hold'){H.setKey('kb','g',i<hold);H.setKey('kb',k,i<hold);}
  else{H.setKey('kb','g',i<70);H.setKey('kb',k,i===0||i===again);}
  H.tick(1);H.banner=null;const lp=__J33.livePose(P,P.pose),s=H.skel(lp),ox=lp.ox||0,f=P.face;
  const W=q=>[P.x+f*(ox+q[0]),P.y-s.hipH+q[1]];
  const FP=(kn,fe,fp)=>{const fk=__J33.rd().fk,r=__J33.footRot(kn[0],kn[1],fe[0],fe[1],fp||0),ax=r[0],ay=r[1],c=r[2],s2=r[3],o=[];
    for(const j of [0,6,8]){const px=fe[0]+__J33.FOOTP[j]*fk-ax,py=fe[1]+__J33.FOOTP[j+1]-ay;o.push(W([ax+px*c-py*s2,ay+px*s2+py*c]));}return o;}; // heel, ball, toe
  return {i,gt:H.gameTime,st:P.state,t:P.t,x:P.x,y:P.y,face:f,ox,hipY:P.y-s.hipH,hipX:P.x+f*ox,hdY:W(s.hd)[1],ftF:FP(s.kF,s.fF,lp.fpF),ftB:FP(s.kB,s.fB,lp.fpB),p:Object.assign({},lp)};}"""
DRAW = r"""([fr,S,x0,y0,W,Hh,mode,jy])=>{const H=__HK,L=H.L;H.GFX().hd=true;const cv=document.createElement('canvas');cv.width=W*S;cv.height=Hh*S;const c=cv.getContext('2d');c.scale(S,S);c.translate(-x0,-y0);
  c.fillStyle='#e9dfcc';c.fillRect(x0,y0,W,Hh);
  const r=Math.floor((jy-1)/64);for(let cc=Math.floor(x0/32);cc<=Math.floor((x0+W)/32);cc++)for(let rr=r-2;rr<=r+1;rr++){const b=L.base[rr*L.cols+cc],X=cc*32,Y=rr*64;
    if(b===2){c.fillStyle='#8a7a62';c.fillRect(X,Y,32,64);}else if(b===1){c.fillStyle='#b9a888';c.fillRect(X,Y+60,32,4);c.fillStyle='#8a7a62';c.fillRect(X,Y+64,32,6);}
    else if(rr===r&&!H.solidBelow(cc,rr)){c.fillStyle='#3a3028';c.fillRect(X,Y+60,32,44);}
    const f=L.feat[rr*L.cols+cc];if(rr===r&&f&&f.t==='spikes'){const m=cc%2?-1:1;c.strokeStyle='#5a4630';c.lineWidth=1.1;
      for(const [bx,d,hh,ln] of [[25,0.78,10,3],[7,0.66,16,-1.9],[19,0.48,21,0.6],[12.5,0.26,11,-0.8]]){const x=X+16+m*(bx-16)-d*4+2;c.beginPath();c.moveTo(x,Y+60);c.lineTo(x+m*ln,Y+60-hh);c.stroke();}}}
  for(let g=1;g<=7;g++){c.strokeStyle='rgba(60,50,40,.16)';c.lineWidth=0.3;c.beginPath();c.moveTo(x0,jy-g*8);c.lineTo(x0+W,jy-g*8);c.stroke();}
  const n=fr.length;fr.forEach((f,i)=>{const p=Object.assign(H.mk({}),f.p),o={hasSword:true,time:f.gt,yo:0};
    if(mode==='onion')c.globalAlpha=0.2+0.8*(i+1)/n;H.figDraw(c,f.x,f.y,f.face,p,H.PAL_HERO,o);});c.globalAlpha=1;
  if(mode==='onion'){c.lineWidth=0.6;c.strokeStyle='#2e6bd8';c.beginPath();fr.forEach((f,i)=>{if(i)c.lineTo(f.hipX,f.hipY);else c.moveTo(f.hipX,f.hipY);});c.stroke();
    c.setLineDash([2,1.5]);c.strokeStyle='#c0392b';c.beginPath();fr.forEach((f,i)=>{if(i)c.lineTo(f.x,f.y+3);else c.moveTo(f.x,f.y+3);});c.stroke();c.setLineDash([]);}
  return cv.toDataURL('image/png');}"""


def prep(src, tmp, tag):
    s = open(src, encoding='utf-8').read()
    i = s.find('window.__HK={')
    fn = os.path.join(tmp, '_r33b_%s.html' % tag)
    open(fn, 'w', encoding='utf-8').write(s[:i] + EXPORT + s[i:])
    return fn


def old_src(tmp):
    if OLD:
        return OLD
    fn = os.path.join(tmp, '_v78.html')
    r = subprocess.run(['git', 'log', '-1', '--format=%s', 'HEAD'], cwd=HERE, capture_output=True, text=True)
    ref = 'HEAD' if r.stdout.startswith('v78') else None
    if ref:
        open(fn, 'w', encoding='utf-8').write(subprocess.run(['git', 'show', ref + ':dev/hourglass-keep.html'], cwd=HERE, capture_output=True, text=True, check=True).stdout)
        return fn
    for c in (os.path.join(HERE, 'hk_v78_release.html'), os.path.join(HERE, '..', '..', '..', '..', '..', 'dev', 'tools', 'hk_v78_release.html')):
        if os.path.exists(c):
            return os.path.abspath(c)
    r = subprocess.run(['git', 'log', '--format=%H %s'], cwd=HERE, capture_output=True, text=True).stdout.split('\n')
    h = next(q.split()[0] for q in r if q.split(' ', 1)[-1].startswith('v78:'))
    open(fn, 'w', encoding='utf-8').write(subprocess.run(['git', 'show', h + ':dev/hourglass-keep.html'], cwd=HERE, capture_output=True, text=True, check=True).stdout)
    return fn


def scenes(pg):
    """the floors used: the first row of stakes walled by plain floor on floors 3.., and the first drop's lip"""
    sp = ed = None
    for n in range(3, 20):
        r = pg.evaluate(FIND, [n, 1])
        if sp is None and r['sp']:
            sp = (n, 1, r['sp'][0])
        if ed is None and r['ed']:
            ed = (n, 1, r['ed'][0])
        if sp and ed:
            break
    n, sd, q = sp
    y = (q['r'] + 1) * 64 - 4
    x = (q['c'] - 1) * 32 + 16
    m, sd2, e = ed
    return [('single', 'one careful step (Grab held, the way tapped once): floor %d seed %d' % (n, sd), n, sd, x, y, 'tap', 0, -1, 30),
            ('hold', 'Grab and the way held across %d tile%s of stakes (the bot\'s way): floor %d seed %d' % (q['k'], 's' if q['k'] > 1 else '', n, sd), n, sd, x - 6, y, 'hold', 64, -1, 76),
            ('edge', 'at a drop: the way tapped to the lip, then again (PoP\'s test foot): floor %d seed %d' % (m, sd2), m, sd2, e['c'] * 32 + 21, (e['r'] + 1) * 64 - 4, 'tap', 0, 24, 50)]


def record(pg, sc):
    key, lab, n, sd, x, y, mode, hold, again, nf = sc
    pg.evaluate(SETUP, [n, sd, x, y, 1])
    return [pg.evaluate(STEP, [i, 1, mode, hold, again]) for i in range(nf)]


def draw(pg, fr, x0, y0, W, H, mode, jy):
    return E.img(pg.evaluate(DRAW, [fr, S, x0, y0, W, H, mode, jy]))


# ---- PoP 1989: SDLPoP seqtbl.c's sequences (frame, dx before it in units of 320/140 px); frame_table_kid's dx is 0 in these frames
POPSEQ = {'step14': [(121, 0), (122, 1), (123, 1), (124, 3), (125, 4), (126, 3), (127, 2), (128, 0), (129, 0), (130, 0), (131, 0), (132, 0)],
          'testfoot': [(121, 0), (122, 1), (123, 0), (124, 2), (125, 4), (126, 3), (86, -4), (116, -4), (117, -2), (118, 0), (119, 0)]}


def pop_frames(name, h):
    files = {int(os.path.basename(f)[1:4]): f for f in glob.glob(os.path.join(POP, 'f*_res*.png'))}
    k = h / 41.0
    ux = 320 / 140 * k / 1.2
    out, X = [], 0
    for f, dx in POPSEQ[name]:
        X += dx
        if f not in files:
            return None
        sp = Image.open(files[f]).convert('RGBA').transpose(Image.FLIP_LEFT_RIGHT)   # (the kid's frames face left; anchored by the front edge)
        big = sp.resize((max(1, int(sp.width * k / 1.2)), max(1, int(sp.height * k))), Image.NEAREST)
        out.append((f, big, X * ux))
    return out


def pop_onion(name, h):
    fr = pop_frames(name, h)
    if not fr:
        im = Image.new('RGB', (300, h + 20), INK)
        E.label(im, 'PoP 1989: no sprites in ' + POP)
        return im
    x0 = min(x - b.width for _, b, x in fr)
    W = int(max(x for _, b, x in fr) - x0 + 30)
    out = Image.new('RGBA', (W, h + 24), (233, 223, 204, 255))
    base = h + 14
    for i, (f, big, x) in enumerate(fr):
        a = big.getchannel('A').point(lambda v, q=0.2 + 0.8 * (i + 1) / len(fr): int(v * q))
        b2 = big.copy()
        b2.putalpha(a)
        out.alpha_composite(b2, (int(10 + x - x0 - big.width), int(base - big.height)))
    ImageDraw.Draw(out).line([(0, base), (W, base)], fill=(140, 120, 100, 255))
    return out.convert('RGB')


def pop_strip(name, h):
    fr = pop_frames(name, h)
    if not fr:
        return Image.new('RGB', (10, 10), INK)
    cw = int(max(b.width for _, b, _ in fr)) + 8
    out = Image.new('RGB', (cw * len(fr), h + 30), (233, 223, 204))
    d = ImageDraw.Draw(out)
    for i, (f, big, x) in enumerate(fr):
        out.paste(big, (i * cw + cw - 4 - big.width, h + 16 - big.height), big)
        d.text((i * cw + 2, 2), 'f%d' % f, fill=(40, 30, 20))
        d.line([(i * cw, h + 16), (i * cw + cw - 2, h + 16)], fill=(140, 120, 100))
    return out


def panel(pg, fr, jy, every=2):
    sel = [q for k, q in enumerate(fr) if k % every == 0]
    x0 = min(q['x'] for q in fr) - 30
    x1 = max(q['x'] for q in fr) + 36
    return draw(pg, sel, x0, jy - 80, x1 - x0, 96, 'onion', jy)


def strip(pg, fr, jy, every=1, per=30):
    cells = []
    for q in fr[::every]:
        im = draw(pg, [q], q['x'] - 24, jy - 66, 48, 74, 'cell', jy)
        ImageDraw.Draw(im).text((2, 1), '%d %s' % (q['i'], q['st'][:5]), fill=(40, 30, 20))
        cells.append(im)
    cw, ch = cells[0].size
    rows = (len(cells) + per - 1) // per
    out = Image.new('RGB', (per * (cw + 1), rows * (ch + 1)), INK)
    for k, c in enumerate(cells):
        out.paste(c, ((k % per) * (cw + 1), (k // per) * (ch + 1)))
    return out


# ---------------- the numbers ----------------
def corr(a, b):
    da = [a[i] - a[i - 1] for i in range(1, len(a))]
    db = [b[i] - b[i - 1] for i in range(1, len(b))]
    if len(da) < 2:
        return 0.0
    ma, mb = sum(da) / len(da), sum(db) / len(db)
    sa = math.sqrt(sum((x - ma) ** 2 for x in da))
    sb = math.sqrt(sum((y - mb) ** 2 for y in db))
    return sum((x - ma) * (y - mb) for x, y in zip(da, db)) / (sa * sb) if sa and sb else 0.0


def numbers(fr):
    y = fr[0]['y']
    st = [q for q in fr if q['st'] in ('step', 'stand', 'edgeWalk')]
    base = {k: min(y - q[k][1][1] for q in fr) for k in ('ftF', 'ftB')}     # the ball's lowest = on the floor
    o = {}
    order = []
    for k in ('ftF', 'ftB'):
        slide, down0, lift, heel, up = 0.0, None, 0.0, 0.0, False
        for q in fr:
            bh = y - q[k][1][1] - base[k]
            lift = max(lift, bh)
            heel = max(heel, y - q[k][0][1] - base[k])
            down = bh < 0.6
            if down and down0 is not None:
                slide += abs(q[k][1][0] - down0)
            down0 = q[k][1][0] if down else None
            if bh > 1.0 and not up:
                order.append((q['i'], k))
            up = bh > 1.0 if not up else not down
        o[k[2] + ' slide'] = round(slide, 1)
        o[k[2] + ' lift'] = round(lift, 1)
        o[k[2] + ' heel'] = round(heel, 1)
    o['order'] = ''.join('F' if k == 'ftF' else 'B' for _, k in sorted(order))
    hip0 = y - fr[0]['hipY']
    o['hip dip'] = round(hip0 - min(y - q['hipY'] for q in st), 1)
    o['head dip'] = round((y - fr[0]['hdY']) - min(y - q['hdY'] for q in st), 1)
    o['arm corr'] = round(corr([q['p']['aF'] for q in st], [q['p']['aB'] for q in st]), 2)
    A = ['lean', 'head', 'aF', 'eF', 'aB', 'eB', 'hF', 'kF', 'hB', 'kB']
    mv = [q for q in fr if q['st'] == 'step']
    o['held'] = '%d/%d' % (sum(1 for i in range(1, len(mv)) if max(abs(math.degrees(mv[i]['p'][a] - mv[i - 1]['p'][a])) for a in A) < 0.5), max(0, len(mv) - 1))
    o['steps'] = sum(1 for i in range(1, len(fr)) if fr[i]['st'] == 'step' and fr[i - 1]['st'] != 'step') + (1 if fr[0]['st'] == 'step' else 0)
    o['x'] = round(fr[-1]['x'] - fr[0]['x'], 1)
    return o


def main():
    os.makedirs(OUTD, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix='r33b', dir=HERE)
    J, rec = {}, {}
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            pgs = {}
            SC = None
            for tag, src in (('v78', old_src(tmp)), ('r33b', NEW)):
                pg = E.page(b, prep(src, tmp, tag))
                pgs[tag] = pg
                if SC is None:
                    SC = scenes(pg)
                J[tag], rec[tag] = {}, {}
                for sc in SC:
                    fr = record(pg, sc)
                    rec[tag][sc[0]] = fr
                    J[tag][sc[0]] = numbers(fr)
                if pg.errs:
                    print(tag, 'errors', pg.errs[:3])
            json.dump(J, open(os.path.join(OUTD, 'r33b.json'), 'w'), indent=1)
            for sc in SC:
                for tag in ('v78', 'r33b'):
                    print('%-6s %-4s %s' % (sc[0], tag, json.dumps(J[tag][sc[0]])))
            if MEASURE:
                return
            # ---- the picture ----
            rows = []
            hP = 51 * S
            rows.append(('PoP 1989, SDLPoP seqtbl.c step14 (frames 121-132, 12 fps; step11 "corresponds directly to filmed sequence", SEQTABLE.S) and testfoot (121-126, 86, 116-119)',
                         None, [pop_onion('step14', hP), pop_strip('step14', hP // 2 + 20), pop_onion('testfoot', hP), pop_strip('testfoot', hP // 2 + 20)]))
            for sc in SC:
                key, lab, n, sd, x, y = sc[:6]
                ims = []
                for tag in ('v78', 'r33b'):
                    pgs[tag].evaluate("([n,sd])=>{__P.load(n,sd);__HK.GFX().hd=true;}", [n, sd])
                    ims.append(panel(pgs[tag], rec[tag][key], y))
                rows.append((lab + ': onion skins, every 2nd frame, v78 | round 33b', None, ims))
                for tag in ('v78', 'r33b'):
                    pgs[tag].evaluate("([n,sd])=>{__P.load(n,sd);__HK.GFX().hd=true;}", [n, sd])
                    fr = rec[tag][key]
                    rows.append(('%s, %s: every frame (60 fps)  %s' % (lab.split(':')[0], tag, json.dumps(J[tag][key])), strip(pgs[tag], fr[:60 if key != 'hold' else 60], y), None))
            W = 0
            blocks = []
            for lab, im, ims in rows:
                if ims:
                    Hh = max(i.height for i in ims)
                    Wd = sum(i.width for i in ims) + 12 * len(ims)
                    blk = Image.new('RGB', (Wd, Hh), INK)
                    xx = 0
                    for i in ims:
                        blk.paste(i, (xx, 0))
                        xx += i.width + 12
                    im = blk
                blocks.append((lab, im))
                W = max(W, im.width)
            Ht = sum(im.height + 22 for _, im in blocks) + 30
            out = Image.new('RGB', (W, Ht), INK)
            d = ImageDraw.Draw(out)
            d.text((6, 6), 'Round 33b: the careful step (owner: "the tiptoe animation: research this also against the PoP animation"): PoP\'s step-to on the clip\'s body (CMU 139_29), feet planted by IK, toe first, the test foot at a lip', fill=TXT)
            yy = 30
            for lab, im in blocks:
                d.text((6, yy + 2), lab, fill=DIM)
                out.paste(im, (0, yy + 18))
                yy += im.height + 22
            out.save(os.path.join(OUTD, 'r33b_tiptoe.png'), optimize=True)
            # ---- the gif: Grab held across the stakes, and the lip, v78 | round 33b, half speed ----
            views = []
            for sc in SC[1:]:
                key, y = sc[0], sc[5]
                fa = {t: rec[t][key] for t in ('v78', 'r33b')}
                x0 = int(min(q['x'] for t in fa for q in fa[t]) - 30)
                x1 = int(max(q['x'] for t in fa for q in fa[t]) + 34)
                views.append((sc, fa, x0, x1, y))
            n = max(len(f[t]) for _, f, _, _, _ in views for t in f)
            frames = []
            for i in range(n):
                tiles = []
                for sc, fa, x0, x1, y in views:
                    for t in ('v78', 'r33b'):
                        pgs[t].evaluate("([n,sd])=>{__P.load(n,sd);__HK.GFX().hd=true;}", [sc[2], sc[3]])
                        q = fa[t][min(i, len(fa[t]) - 1)]
                        im = draw(pgs[t], [q], x0, y - 74, x1 - x0, 86, 'cell', y).resize(((x1 - x0) * 2, 86 * 2))
                        ImageDraw.Draw(im).text((4, 2), ('v78' if t == 'v78' else 'round 33b') + '  ' + sc[1].split(':')[0], fill=(40, 30, 20))
                        tiles.append(im)
                Wg = max(tiles[0].width, tiles[2].width) * 2 + 6
                Hg = tiles[0].height + tiles[2].height + 6
                g = Image.new('RGB', (Wg, Hg), INK)
                g.paste(tiles[0], (0, 0))
                g.paste(tiles[1], (Wg // 2 + 3, 0))
                g.paste(tiles[2], (0, tiles[0].height + 6))
                g.paste(tiles[3], (Wg // 2 + 3, tiles[0].height + 6))
                frames.append(g.convert('P', palette=Image.ADAPTIVE, colors=128))
            frames[0].save(os.path.join(OUTD, 'r33b_tiptoe.gif'), save_all=True, append_images=frames[1:], duration=33, loop=0)
            print('wrote', os.path.join(OUTD, 'r33b_tiptoe.png'), os.path.join(OUTD, 'r33b_tiptoe.gif'))
            b.close()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == '__main__':
    main()
