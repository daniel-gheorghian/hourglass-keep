# egyptr32.py [new.html] [old.html] [--measure]: round 32's pictures and numbers (owner: "The current one is too stiff too mechanical"; after
# the research: "Do everything; keep the motion capture body and borrow PoP's structure"), into egypt_themes/:
#   r32_jump.png   for the running jump over one tile and over two tiles of pit and the standing jump over one tile: PoP 1989 (its own sprites,
#                  SDLPoP's seqtbl.c sequences) | v77 | round 32 as onion skins (every 3rd game frame, later frames darker, the hit box's feet
#                  dashed red, the drawn hip blue), then each build's frame strip (every 2nd frame from the last strides to the settle)
#   r32_jump.gif   the three jumps in game, v77 | round 32, at half speed
#   r32.json       (in egypt_themes/, local) the numbers (--measure prints them): the arms' velocity correlation in the air, the lead knee at contact and just after,
#                  the hip's drop after landing, scissoring (40 take-offs at every run phase: do the thighs cross in the air), frames held
#                  (every angle moving under 0.5 degrees a frame), vx through the landing with the way held and let go
# old.html defaults to hk_v77_release.html. The PoP sprites are read from ref/pop1/ (or HK_POP1): SDLPoP's KID images (res401+, named
# fNNN_resMMM.png), local only. Run from dev/tools. CMU mocap (mocap.cs.cmu.edu, NSF EIA-0196217): 127_21, 13_11, 09_01.
import io, os, sys, tempfile, shutil, base64, json, math, glob
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright
import egyptr26c as E

HERE = os.path.dirname(os.path.abspath(__file__))
args = [x for x in sys.argv[1:] if not x.startswith('--')]
MEASURE = '--measure' in sys.argv
NEW = os.path.abspath(args[0] if args else os.path.join(HERE, '..', 'hourglass-keep.html'))
OLD = os.path.abspath(args[1] if len(args) > 1 else os.path.join(HERE, 'hk_v77_release.html'))
POP = os.environ.get('HK_POP1', os.path.join(HERE, 'ref', 'pop1'))
OUTD = os.path.join(HERE, 'egypt_themes')
INK, TXT, DIM = E.INK, E.TXT, E.DIM
S = 3
# (key, label, floor, seed, start x, feet y, facing, Jump pressed at x (running) or frame (standing), PoP's sequence)
SC = [('run1', 'running jump, one tile of pit (floor 3 seed 1)', 3, 1, 664.0, 636, 1, 724.0, 'runjump'),
      ('run2', 'running jump, two tiles of pit (floor 2 seed 2)', 2, 2, 418.6, 444, 1, 528.6, 'runjump'),
      ('stand1', 'standing jump, one tile of pit (floor 3 seed 1)', 3, 1, 764.0, 636, 1, 12, 'standjump')]

SETUP = r"""([n,sd,x,jy,face])=>{const H=__HK;__P.load(n,sd);H.GFX().hd=true;const P=H.P;P.inv=1e9;window.__jp=0;
  for(let k=0;k<2;k++){P.x=x;P.y=jy;P.fallY=jy;P.vx=P.vy=0;P.state='stand';P.t=0;P.face=face;H.cam.snap=true;H.tick(1);}H.banner=null;
  for(let k=0;k<30;k++){P.x=x;H.tick(1);}H.banner=null;return [P.x,P.y,P.state];}"""
# one game frame: the keys by the scenario (running: the way held, Jump tapped at px; hold false: let go once falling), then the drawn state
STEP = r"""([i,run,face,px,hold])=>{const H=__HK,P=H.P,k=face>0?'r':'l';
  if(run){if(i===0)H.setKey('kb',k,true);if(!window.__jp&&P.state==='run'&&(P.x-px)*face>0){H.setKey('kb','j',true);window.__jp=1;}else if(window.__jp===1){H.setKey('kb','j',false);window.__jp=2;}
    if(!hold&&P.state==='air'&&P.vy>120)H.setKey('kb',k,false);}
  else{if(i===px)H.setKey('kb','j',true);if(i===px+1)H.setKey('kb','j',false);}
  const x0=P.x;H.tick(1);H.banner=null;const lk=P.lk||{},lp=__J32.livePose(P,P.pose),s=H.skel(lp);
  return {i,gt:H.gameTime,st:P.state,x:P.x,y:P.y,vx:P.vx,dx:P.x-x0,vy:P.vy,yo:P.yo||0,face:P.face,jy:P.jy,ox:lp.ox||0,mir:!!P.jMir,
    hipY:P.y-s.hipH+(P.yo||0),hdY:P.y-s.hipH+(P.yo||0)+s.hd[1],sq:lk.sq||1,cw:lk.cw||0,cwy:lk.cwy||0,p:Object.assign({},lp)};}"""
DRAW = r"""([fr,S,x0,y0,W,Hh,mode,jy])=>{const H=__HK,L=H.L;H.GFX().hd=true;const cv=document.createElement('canvas');cv.width=W*S;cv.height=Hh*S;const c=cv.getContext('2d');c.scale(S,S);c.translate(-x0,-y0);
  c.fillStyle='#e9dfcc';c.fillRect(x0,y0,W,Hh);
  const r=Math.floor((jy-1)/64);for(let cc=Math.floor(x0/32);cc<=Math.floor((x0+W)/32);cc++)for(let rr=r-2;rr<=r+1;rr++){const b=L.base[rr*L.cols+cc],X=cc*32,Y=rr*64;
    if(b===2){c.fillStyle='#8a7a62';c.fillRect(X,Y,32,64);}else if(b===1){c.fillStyle='#b9a888';c.fillRect(X,Y+60,32,4);c.fillStyle='#8a7a62';c.fillRect(X,Y+64,32,6);}
    else if(rr===r&&!H.solidBelow(cc,rr)){c.fillStyle='#3a3028';c.fillRect(X,Y+60,32,44);}}
  for(let g=1;g<=7;g++){c.strokeStyle='rgba(60,50,40,.16)';c.lineWidth=0.3;c.beginPath();c.moveTo(x0,jy-g*8);c.lineTo(x0+W,jy-g*8);c.stroke();}
  const n=fr.length;fr.forEach((f,i)=>{const p=Object.assign(H.mk({}),f.p),o={hasSword:true,time:f.gt,yo:f.yo,sq:Math.abs(f.sq-1)>0.004?f.sq:undefined,vx:f.cw,vy:f.cwy};
    if(mode==='onion')c.globalAlpha=0.22+0.78*(i+1)/n;H.figDraw(c,f.x,f.y,f.face,p,H.PAL_HERO,o);});c.globalAlpha=1;
  if(mode==='onion'){c.lineWidth=0.6;c.strokeStyle='#2e6bd8';c.beginPath();fr.forEach((f,i)=>{const X=f.x+f.face*(f.ox||0);if(i)c.lineTo(X,f.hipY);else c.moveTo(X,f.hipY);});c.stroke();
    c.setLineDash([2,1.5]);c.strokeStyle='#c0392b';c.beginPath();fr.forEach((f,i)=>{if(i)c.lineTo(f.x,f.y);else c.moveTo(f.x,f.y);});c.stroke();c.setLineDash([]);}
  return cv.toDataURL('image/png');}"""


def prep(src, tmp, tag):
    s = open(src, encoding='utf-8').read()
    i = s.find('window.__HK={')
    fn = os.path.join(tmp, '_r32_%s.html' % tag)
    open(fn, 'w', encoding='utf-8').write(s[:i] + 'window.__J32={livePose};' + s[i:])
    return fn


def record(pg, sc, hold=True, x=None):
    key, lab, n, sd, x0, jy, face, px, popseq = sc
    run = key.startswith('run')
    pg.evaluate(SETUP, [n, sd, x if x is not None else x0, jy, face])
    fr = []
    for i in range(200):
        fr.append(pg.evaluate(STEP, [i, run, face, px, hold]))
        sts = [q['st'] for q in fr]
        if 'air' in sts and sum(1 for q in fr[sts.index('air'):] if q['st'] != 'air') >= 36:
            break
    return fr


def window(fr, pre, post):
    sts = [q['st'] for q in fr]
    i0 = sts.index('jumpPrep') if 'jumpPrep' in sts else sts.index('air')
    il = max(i for i, s in enumerate(sts) if s == 'air') + 1
    ia = sts.index('air')
    out = fr[max(0, i0 - pre):il + post]
    for q in out:
        q['rel'] = q['i'] - fr[ia]['i']
    return out


def draw(pg, fr, x0, y0, W, H, mode, jy):
    return E.img(pg.evaluate(DRAW, [fr, S, x0, y0, W, H, mode, jy]))


# ---- PoP 1989: SDLPoP's frame table rows (seg006.c frame_table_kid) and sequences (seqtbl.c), as the research's popsheet.py
FT = {7: (6, 0x40 | 10), 8: (7, 0xC0 | 5), 9: (8, 0x40 | 4), 10: (9, 0x40 | 7), 11: (10, 0x40 | 11), 12: (11, 0x40 | 3), 13: (12, 0xC0 | 3), 14: (13, 0x40 | 7),
      15: (14, 0x40 | 3), 16: (15, 0xC0 | 3), 17: (16, 0x40 | 4), 18: (17, 0x40 | 6), 19: (18, 0x40 | 8), 20: (19, 0x80 | 9), 21: (20, 11), 22: (21, 0x80 | 11),
      23: (22, 17), 24: (23, 7), 25: (24, 5), 26: (25, 0xC0 | 1), 27: (26, 0xC0 | 6), 28: (27, 0x40 | 3), 29: (28, 0x40 | 8), 30: (29, 0x40 | 2),
      31: (30, 0x40 | 2), 32: (31, 0xC0 | 2), 33: (32, 0xC0 | 2), 34: (33, 0x40 | 3), 35: (34, 0x40 | 8), 36: (35, 0xC0 | 14), 37: (36, 0xC0 | 1),
      38: (37, 0x40 | 5), 39: (38, 0x80 | 14), 40: (39, 11), 41: (40, 0x80 | 11), 42: (41, 0x80 | 10), 43: (42, 1), 44: (43, 0xC0 | 4)}
SEQ = {'standjump': [(15, 0, 0), (16, 0, 0), (17, 0, 0), (18, 2, 0), (19, 2, 0), (20, 2, 0), (21, 2, 0), (22, 2, 0), (23, 7, 0), (24, 9, 0), (25, 5, -6),
                     (26, 1, 6), (27, 4, 0), (28, -3, 0), (29, 5, 0), (30, 0, 0), (31, 0, 0), (32, 0, 0), (33, 0, 0), (15, 1, 0)],
       'runjump': [(11, 4, 0), (12, 5, 0), (13, 2, 0), (14, 3, 0), (34, 0, 0), (35, 5, 0), (36, 6, 0), (37, 3, 0), (38, 5, 0), (39, 7, 0), (40, 12, -3),
                   (41, 8, -9), (42, 8, -2), (43, 4, 11), (44, 4, 3), (7, 5, 0), (8, 5, 0), (9, 1, 0), (10, 2, 0)]}


def pop_onion(name, h):
    """PoP's own frames at 12 fps, overlaid as he moves (every frame; later ones darker), scaled to a figure h px tall"""
    files = {int(os.path.basename(f)[1:4]): f for f in glob.glob(os.path.join(POP, 'f*_res*.png'))}
    if not files:
        im = Image.new('RGB', (300, h + 20), INK)
        E.label(im, 'PoP 1989: no sprites in ' + POP)
        return im
    k = h / 41.0
    ux = 320 / 140 * k / 1.2   # a PoP x unit (SDLPoP: 140 units across 320 px), in this picture's px; a PoP pixel is 1.2 times taller than wide
    pos, X, Y = [], 0, 0
    for f, dx, dy in SEQ[name]:
        X += dx
        Y += dy
        img, fl = FT[f]
        sp = Image.open(files[f]).convert('RGBA').transpose(Image.FLIP_LEFT_RIGHT)   # (the kid's frames face left)
        pos.append((sp, X * ux, Y * k))
    W = int(max(p[1] + p[0].width * k / 1.2 for p in pos) + 20)
    out = Image.new('RGBA', (W, h + 24), (233, 223, 204, 255))
    base = h + 14
    n = len(pos)
    for i, (sp, x, y) in enumerate(pos):
        big = sp.resize((max(1, int(sp.width * k / 1.2)), max(1, int(sp.height * k))), Image.NEAREST)
        a = big.getchannel('A').point(lambda v, q=0.25 + 0.75 * (i + 1) / n: int(v * q))
        big.putalpha(a)
        out.alpha_composite(big, (int(10 + x), int(base + y - big.height)))
    d = ImageDraw.Draw(out)
    d.line([(0, base), (W, base)], fill=(140, 120, 100, 255))
    return out.convert('RGB')


def panel(pg, fr, jy, every=3):
    sel = [q for k, q in enumerate(fr) if k % every == 0 or q['st'] != fr[max(0, k - 1)]['st']]
    x0 = min(q['x'] for q in fr) - 30
    x1 = max(q['x'] for q in fr) + 34
    return draw(pg, sel, x0, jy - 80, x1 - x0, 96, 'onion', jy)


def strip(pg, fr, jy, every=2, per=26):
    cells = []
    for q in fr[::every]:
        im = draw(pg, [q], q['x'] - 26, jy - 70, 52, 80, 'cell', jy)
        d = ImageDraw.Draw(im)
        d.text((2, 1), '%+d %s' % (q['rel'], q['st'][:5]), fill=(40, 30, 20))
        cells.append(im)
    cw, ch = cells[0].size
    rows = (len(cells) + per - 1) // per
    out = Image.new('RGB', (per * (cw + 1), rows * (ch + 1)), INK)
    for k, c in enumerate(cells):
        out.paste(c, ((k % per) * (cw + 1), (k // per) * (ch + 1)))
    return out


# ---------------- the numbers ----------------
def deg(v):
    return math.degrees(v)


def corr(a, b):
    da = [a[i] - a[i - 1] for i in range(1, len(a))]
    db = [b[i] - b[i - 1] for i in range(1, len(b))]
    ma, mb = sum(da) / len(da), sum(db) / len(db)
    sa = math.sqrt(sum((x - ma) ** 2 for x in da))
    sb = math.sqrt(sum((y - mb) ** 2 for y in db))
    return sum((x - ma) * (y - mb) for x, y in zip(da, db)) / (sa * sb) if sa and sb else 0.0


def numbers(fr, rel=None):
    air = [q for q in fr if q['st'] == 'air']
    ia = fr.index(air[0])
    il = fr.index(air[-1]) + 1
    A = ['lean', 'head', 'aF', 'eF', 'aB', 'eB', 'hF', 'kF', 'hB', 'kB']
    held = sum(1 for i in range(1, len(air)) if max(abs(deg(air[i]['p'][k] - air[i - 1]['p'][k])) for k in A) < 0.5)
    mir = air[0]['mir']
    lk = 'kB' if mir else 'kF'
    jy = air[0]['jy']
    hip = [jy - q['hipY'] for q in fr]
    after = fr[il:il + 40]
    o = {'arm_corr': round(corr([q['p']['aF'] for q in air], [q['p']['aB'] for q in air]), 2),
         'held': '%d/%d' % (held, len(air) - 1),
         'knee_last_air': round(deg(air[-1]['p'][lk])), 'knee_contact': round(deg(fr[il]['p'][lk])), 'knee_3f': round(deg(fr[il + 3]['p'][lk])),
         'head_drop': round(max(jy - q['hdY'] for q in fr[:3]) - min(jy - q['hdY'] for q in fr[il:il + 40]), 1),
         'hip_contact': round(hip[il], 1), 'hip_min': round(min(hip[il:il + 40]), 1), 'hip_drop': round(25.2 - min(hip[il:il + 40]), 1),
         'vx_land': [round(abs(q['vx'])) for q in after[:8]], 'states_after': [q['st'] for q in after[:12:3]],
         'drawn_dx_takeoff': [round(fr[i]['dx'] + fr[i]['face'] * (fr[i]['ox'] - fr[i - 1]['ox']), 2) for i in range(ia - 2, ia + 4)]}
    return o


SCISSOR = r"""([n,sd,jy,face,px,x0])=>{const H=__HK,k=face>0?'r':'l';const res=[];
  for(let j=0;j<40;j++){__P.load(n,sd);const P=H.P;H.GFX().hd=true;P.inv=1e9;const x=x0-j*1.1;
    for(let q=0;q<2;q++){P.x=x;P.y=jy;P.fallY=jy;P.vx=P.vy=0;P.state='stand';P.t=0;P.face=face;H.cam.snap=true;H.tick(1);}H.banner=null;for(let q=0;q<20;q++){P.x=x;H.tick(1);}H.banner=null;
    let jp=0,air=0,flips=0,last=null,ph=null;H.setKey('kb',k,true);
    for(let i=0;i<200;i++){if(!jp&&P.state==='run'&&(P.x-px)*face>0){H.setKey('kb','j',true);jp=1;}else if(jp===1){H.setKey('kb','j',false);jp=2;}
      const st0=P.state,ph0=P.ph;H.tick(1);H.banner=null;if(P.state==='air'){if(st0==='run')ph=((ph0%1)+1)%1;air++;const sg=Math.sign(P.pose.hF-P.pose.hB);if(last!==null&&sg!==last&&air<22)flips++;last=sg;}
      else if(air>0)break;}
    H.setKey('kb',k,false);res.push({ph,flips});}
  return res;}"""


def scissor(pg):
    r = pg.evaluate(SCISSOR, [2, 2, 444, 1, 528.6, 450.0])
    return sum(1 for q in r if q['flips'] > 0), len(r)


def main():
    os.makedirs(OUTD, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix='r32', dir=HERE)
    J = {}
    rec = {}
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            pgs = {}
            for tag, src in (('v77', OLD), ('r32', NEW)):
                pg = E.page(b, prep(src, tmp, tag))
                pgs[tag] = pg
                rec[tag] = {}
                J[tag] = {}
                for sc in SC:
                    fr = record(pg, sc)
                    rec[tag][sc[0]] = fr
                    J[tag][sc[0]] = numbers(fr)
                rel = record(pg, SC[1], hold=False)
                rec[tag]['run2rel'] = rel
                J[tag]['run2rel'] = numbers(rel)
                J[tag]['scissor'] = '%d/%d' % scissor(pg)
                if pg.errs:
                    print(tag, 'errors', pg.errs[:3])
            json.dump(J, open(os.path.join(OUTD, 'r32.json'), 'w'), indent=1)
            for k in ('run1', 'run2', 'run2rel', 'stand1'):
                for tag in ('v77', 'r32'):
                    print('%-7s %-4s %s' % (k, tag, json.dumps(J[tag][k])))
            print('scissor (take-offs over 40 run phases whose thighs cross in the air): v77 %s, r32 %s' % (J['v77']['scissor'], J['r32']['scissor']))
            if MEASURE:
                return
            # ---- the picture ----
            rows = []
            for sc in SC:
                key, lab = sc[0], sc[1]
                jy = sc[5]
                imgs = [pop_onion(sc[8], 51 * S)]
                frs = {}
                for tag in ('v77', 'r32'):
                    s = SC[[q[0] for q in SC].index(key)]
                    pgs[tag].evaluate("([n,sd])=>{__P.load(n,sd);__HK.GFX().hd=true;}", [s[2], s[3]])
                    fr = window(rec[tag][key], 14 if key.startswith('run') else 4, 26)
                    frs[tag] = fr
                    imgs.append(panel(pgs[tag], fr, jy))
                H = max(i.height for i in imgs)
                W = sum(i.width for i in imgs) + 20
                row = Image.new('RGB', (W, H + 22), INK)
                x = 0
                for t, im in zip(('PoP 1989 (SDLPoP seqtbl.c %s, 12 fps)' % sc[8], 'v77', 'round 32'), imgs):
                    row.paste(im, (x, 20))
                    ImageDraw.Draw(row).text((x + 4, 4), t, fill=TXT)
                    x += im.width + 10
                rows.append((lab, row))
                for tag in ('v77', 'r32'):
                    st = strip(pgs[tag], frs[tag], jy)
                    rows.append(('%s, %s: every 2nd game frame (numbered from take-off)' % (lab, 'v77' if tag == 'v77' else 'round 32'), st))
            W = max(r.width for _, r in rows)
            Ht = sum(r.height + 20 for _, r in rows) + 30
            out = Image.new('RGB', (W, Ht), INK)
            d = ImageDraw.Draw(out)
            d.text((6, 6), 'Round 32: the jumps (owner: "too stiff too mechanical"; "keep the motion capture body and borrow PoP\'s structure"): gather and push-off, dive, squash, run on', fill=TXT)
            y = 30
            for lab, r in rows:
                d.text((6, y + 2), lab, fill=DIM)
                out.paste(r, (0, y + 18))
                y += r.height + 20
            out.save(os.path.join(OUTD, 'r32_jump.png'), optimize=True)
            # ---- the gif: the three jumps, v77 | round 32, a fixed view each, half speed ----
            views = []
            for sc in SC:
                key, jy = sc[0], sc[5]
                fa = {t: window(rec[t][key], 14 if key.startswith('run') else 4, 30) for t in ('v77', 'r32')}
                x0 = int(min(q['x'] for t in fa for q in fa[t]) - 30)
                x1 = int(max(q['x'] for t in fa for q in fa[t]) + 30)
                views.append((sc, fa, x0, x1, jy))
            n = max(len(f[t]) for _, f, _, _, _ in views for t in f)
            frames = []
            for i in range(n):
                tiles = []
                for sc, fa, x0, x1, jy in views:
                    for t in ('v77', 'r32'):
                        pgs[t].evaluate("([n,sd])=>{__P.load(n,sd);__HK.GFX().hd=true;}", [sc[2], sc[3]])
                        q = fa[t][min(i, len(fa[t]) - 1)]
                        im = draw(pgs[t], [q], x0, jy - 80, x1 - x0, 96, 'cell', jy).resize(((x1 - x0) * 2, 96 * 2))
                        ImageDraw.Draw(im).text((4, 2), ('v77' if t == 'v77' else 'round 32') + '  ' + sc[1], fill=(40, 30, 20))
                        tiles.append(im)
                Wg = max(tiles[0].width, tiles[2].width, tiles[4].width) * 2 + 6
                Hg = sum(tiles[k].height for k in (0, 2, 4)) + 12
                g = Image.new('RGB', (Wg, Hg), INK)
                yy = 0
                for k in (0, 2, 4):
                    g.paste(tiles[k], (0, yy))
                    g.paste(tiles[k + 1], (Wg // 2 + 3, yy))
                    yy += tiles[k].height + 6
                frames.append(g.convert('P', palette=Image.ADAPTIVE, colors=128))
            frames[0].save(os.path.join(OUTD, 'r32_jump.gif'), save_all=True, append_images=frames[1:], duration=33, loop=0)
            print('wrote', os.path.join(OUTD, 'r32_jump.png'), os.path.join(OUTD, 'r32_jump.gif'))
            b.close()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == '__main__':
    main()
