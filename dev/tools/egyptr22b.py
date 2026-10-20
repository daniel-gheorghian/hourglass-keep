# egyptr22b.py [new.html] [old.html] [r22.html] [outdir]: round 22b's pictures for egypt_themes.html, the prince's proportions after the
# research (ANSUR II's youths, the canons, other games), before (old.html, default the v69 release, hk_v69_release.html here or in the main
# checkout's dev/tools), round 22 (r22.html, default ../_r22.html, made with git show e62aa84:dev/hourglass-keep.html; skipped if missing) and
# after (new.html):
#  r22b_guide.png  standing at 10x, v69 | round 22 | after: lit from his back, and the silhouette with the research's marks: head heights
#                  counted down from the crown (h = chin to crown), the chin, the shoulder joint and the chin-to-shoulder measure in px and
#                  heads, C7, the wall line; beside them the research's target figure as a ruler (the after figure's crown and sole)
#  r22b_poses.png  every pose before | after at 4x (pairs side by side), lit from his back, and a robber
#  r22b_game.png   standing in the game: Torchlight at GLP.rs 1 and 0.5 and Classic, facing both ways (floors 7 and 14), before and after;
#                  the Torchlight crops again at 3x
#  r22b_moves.png  in the game, Torchlight and Classic, before and after: hanging on a wall's near face (only the hands show), climbing,
#                  crawling, swinging, a low leap under stone, the exit stairs
#  r22b_games.png  my own schematic profile silhouettes (not game art) of the proportions other games use, and Dawnward's before and after
# Writes r22b.json (measures, page errors). Run from dev/tools.
import base64, io, json, os, sys
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw
import egyptr12 as R12
import egyptr18 as E18
import egyptr19 as R19
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
NEW = os.path.abspath(a[0] if len(a) > 0 and a[0] else os.path.join(HERE, '..', 'hourglass-keep.html'))
_old = os.path.join(HERE, 'hk_v69_release.html')
if not os.path.exists(_old):
    _old = os.path.join(HERE, '..', '..', '..', '..', '..', 'dev', 'tools', 'hk_v69_release.html')  # (from a worktree: the main checkout's)
OLD = os.path.abspath(a[1] if len(a) > 1 and a[1] else _old)
R22 = os.path.abspath(a[2] if len(a) > 2 and a[2] else os.path.join(HERE, '..', '_r22.html'))
OUT = a[3] if len(a) > 3 else os.path.join(HERE, 'egypt_themes')
R12.OUT = OUT
TAG = {'old': 'before (v69)', 'r22': 'round 22', 'new': 'after (22b)'}
LEN0 = {'th': 12, 'sh': 12, 'to': 15, 'nk': 2.5, 'hd': 4.6}
FIG = r'''([p,S,W,Hh,x,y,dir,mono,pk])=>{const H=__HK;p=Object.assign(H.mk({}),p);const pal=pk==='rob'?H.guardPal({tier:1}):H.PAL_HERO;
 const cv=document.createElement('canvas');cv.width=W*S;cv.height=Hh*S;const c=cv.getContext('2d');c.fillStyle=mono?'#e8dcc8':'#5a4434';c.fillRect(0,0,cv.width,cv.height);c.scale(S,S);
 H.figDraw(c,x,y,1,p,pal,{sword:!!p._sw,hasSword:true,time:0,mono:mono||undefined,lt:{dir,col:'255,220,170',k:0.6}});
 return cv.toDataURL('image/png');}'''
# the landmarks of the standing figure (canvas px / S), from the build's own skeleton: the shoulder joint, the head's centre, the chin
GEO = r'''([p,x,y,L0])=>{const H=__HK,L=H.LEN||L0;p=Object.assign(H.mk({}),p);const ha=p.lean+p.head,sh=[L.to*Math.sin(p.lean),-L.to*Math.cos(p.lean)],
 hd=[sh[0]+(L.nk+L.hd)*Math.sin(ha),sh[1]-(L.nk+L.hd)*Math.cos(ha)],P=q=>[x+q[0],y-24+q[1]]; // (standing, the hip 24 px over the sole)
 const hx=Math.sin(ha),hy=-Math.cos(ha);return {L,sh:P(sh),hd:P(hd),chin:P([hd[0]+Math.cos(ha)*L.hd*0.1-hx*L.hd*1.15,hd[1]+Math.sin(ha)*L.hd*0.1-hy*L.hd*1.15]),hip:P([0,0])};}'''
POSES = r'''()=>{const H=__HK,o={};for(const k of ['stand','step','turn','crouch','land','jumpR','jumpS','jumpLow','fall','hang','reach','pull','press','kneel','garde','lunge','parry','windup','lowStrike','hurt','dead','kickTuck','slide'])o[k]=Object.assign({},H.PS[k]);
 for(const ph of [0,0.25,0.5,0.75])o['run '+ph]=Object.assign({},H.RP(ph));for(const t of [0.3,0.72,0.95])o['drink '+t]=Object.assign({},H.drinkFrame(t).p);
 for(const k of ['garde','lunge','parry','windup','lowStrike'])o[k]._sw=1;return o;}'''
STAND = r'''([n,sd,face,rs])=>{const H=__HK;const L=__P.load(n,sd);let pc=-1,r=-1;
 for(let rr=1;rr<L.rows&&pc<0;rr++)for(let c=12;c<L.cols-12;c++){let ok=true;for(let k=-3;k<=4;k++)if(!H.solidBelow(c+k,rr)||L.feat[rr*L.cols+c+k])ok=false;if(ok){pc=c;r=rr;break;}}
 __P.stand(pc,r,face);for(let i=0;i<40;i++){H.tick(1);H.P.x=pc*32+16;H.P.state='stand';}if(H.GLP)H.GLP.rs=rs;__P.draw();return __P.scr(pc*32+16,(r+1)*64-34);}'''
# the bot plays a floor until a moment (cond on __HK), then a few more frames; the crop's centre on him
MOMENT = r'''([n,sd,cond,more,rs])=>{const H=__HK;__P.load(n,sd);if(H.GLP)H.GLP.rs=rs;const f=new Function('H','return '+cond);let k=0;
 const r=runBot(n,sd,{fight:false,stop:h=>f(h)&&++k>more});H.banner=null;H.intro=0;for(const q of ['l','r','u','d','j','g'])H.setKey('kb',q,false);document.querySelectorAll('.screen').forEach(e=>e.hidden=true);__P.draw();
 return {ok:k>more,st:H.P.state,xy:__P.scr(H.P.x+(H.P.state==='exit'?H.P.exX||0:0),H.P.y+(H.P.state==='exit'?H.P.exY||0:0)-30),n,name:H.themeName(n)};}'''
FINDA = r'''(act)=>{for(let n=3;n<=40;n++)for(const sd of [1,2,3]){const L=__P.load(n,sd);if(L.path.some(a=>a.a===act))return [[n,sd]];}return [];}'''
MOVES = [         ('crawling', "H.P.state==='crouch'&&(H.L.feat[Math.floor((H.P.y-4)/64)*H.L.cols+Math.floor(H.P.x/32)]||{}).t==='low'", 12, 'crawl'),
         ('a low leap', "H.P.lowJump&&H.P.state==='air'", 6, [(6, 1), (9, 1), (12, 1), (15, 1), (7, 2), (4, 1)]),
         ('the exit stairs', "H.P.state==='exit'&&(H.P.exS||0)>1.2", 0, [(5, 1), (7, 1)])]
S = 10


def dataimg(d):
    return Image.open(io.BytesIO(base64.b64decode(d.split(',')[1]))).convert('RGB')


def rows_of(im):
    # the silhouette's top and bottom rows (dark on the light ground)
    px = im.load(); t = b = None
    for y in range(im.height):
        if any(sum(px[x, y]) < 200 for x in range(0, im.width, 2)):
            if t is None: t = y
            b = y
    return t, b


def back_edge(im, y):
    px = im.load()
    for x in range(im.width):
        if sum(px[x, y]) < 200: return x
    return None


def guide(im, g, crown, sole, tag):
    # the research's marks over a silhouette
    d = ImageDraw.Draw(im)
    chin = g['chin'][1] * S; h = chin - crown
    for i in range(0, 8):
        y = crown + i * h
        if y > im.height: break
        d.line([(0, y), (40, y)], fill=(200, 140, 20), width=2); d.text((2, y + 2), '%d' % i if i else 'crown', fill=(200, 140, 20))
    d.text((2, sole - 14), '%.1f heads' % ((sole - crown) / h), fill=(200, 140, 20))
    sy = g['sh'][1] * S
    d.line([(60, chin), (im.width, chin)], fill=(40, 110, 220), width=1); d.text((im.width - 60, chin - 13), 'chin', fill=(40, 110, 220))
    d.line([(60, sy), (im.width, sy)], fill=(200, 40, 40), width=1); d.text((im.width - 100, sy + 2), 'shoulder joint', fill=(200, 40, 40))
    x0 = im.width - 30
    d.line([(x0, chin), (x0, sy)], fill=(150, 60, 170), width=3)
    c = (sy - chin) / S
    d.text((x0 - 150, (chin + sy) / 2 - 6), '%.1f px = %.2f h' % (c, c / (h / S)), fill=(150, 60, 170))
    wall = min(e for e in (back_edge(im, y) for y in range(int(crown), int(sy))) if e is not None)
    d.line([(wall, 0), (wall, im.height)], fill=(40, 110, 220), width=1)
    return {'h': h / S, 'chin_sh': c, 'heads': (sole - crown) / h, 'height': (sole - crown) / S}


def ruler(Hh, crown, sole):
    # the research's figure as a ruler at the after figure's size: the body below the chin at 3.7 cm a px (ANSUR II, men 17-20), the head 10.4 px
    im = Image.new('RGB', (180, Hh * S), (232, 220, 200)); d = ImageDraw.Draw(im)
    px = (sole - crown) / S
    h = 10.4; marks = [('crown', 0), ('chin', h), ('C7 (0.07 h under the chin)', h + 0.07 * h), ('shoulder (acromion, the joint as drawn) 0.41 h', h + 0.41 * h), ('waist (omphalion)', px - 24.3 - 4.3), ('hip (trochanter)', px - 24.3),
                       ('knee', px - 13.2), ('sole', px)]
    d.line([(20, crown), (20, sole)], fill=(20, 16, 24), width=3)
    for name, y in marks:
        yy = crown + y * S
        d.line([(10, yy), (40, yy)], fill=(20, 16, 24), width=2); d.text((44, yy - 6), name, fill=(20, 16, 24))
    d.text((4, 4), 'research target', fill=(20, 16, 24))
    return im


def schematic(name, heads, neck, slope, sub, H=150):
    # a profile silhouette of my own, facing right: the head h = H/heads tall; the chin-to-shoulder-top gap neck*h; the front of the shoulder
    # falling by slope*h; the body below the shoulder in a youth's proportions (ANSUR II: crotch at 0.41 of it, knee at 0.7)
    im = Image.new('RGB', (110, H + 50), (232, 220, 200)); d = ImageDraw.Draw(im); ink = (20, 16, 24)
    h = H / heads; x0 = 52; top = 22
    chin = top + h; shy = chin + neck * h; B = top + H - shy; dp = max(0.62 * h, 0.17 * B)
    d.ellipse([x0 - 0.45 * h, top, x0 + 0.42 * h, top + h * 0.98], fill=ink)                        # the skull
    d.polygon([(x0 + 0.38 * h, top + 0.45 * h), (x0 + 0.52 * h, top + 0.6 * h), (x0 + 0.36 * h, top + 0.72 * h)], fill=ink)  # the nose
    if neck > 0.02:                                                                                     # the neck, leaning a little forward
        d.polygon([(x0 - 0.2 * h, chin - 0.35 * h), (x0 + 0.25 * h, chin - 0.2 * h), (x0 + 0.18 * h, shy + 0.15 * h), (x0 - 0.36 * h, shy + 0.2 * h)], fill=ink)
    d.polygon([(x0 - 0.3 * h, shy), (x0 + 0.2 * h, shy), (x0 + dp * 0.5, shy + slope * h * 0.5 + 0.04 * B), (x0 + dp * 0.5, shy + 0.15 * B),
               (x0 + dp * 0.38, shy + 0.3 * B), (x0 + dp * 0.36, shy + 0.41 * B), (x0 - dp * 0.5, shy + 0.41 * B), (x0 - dp * 0.55, shy + 0.36 * B),
               (x0 - dp * 0.35, shy + 0.28 * B), (x0 - dp * 0.5, shy + 0.14 * B), (x0 - dp * 0.42, shy + 0.03 * B)], fill=ink)   # the trunk
    lw = dp * 0.42
    d.polygon([(x0 - dp * 0.45, shy + 0.38 * B), (x0 + dp * 0.36, shy + 0.38 * B), (x0 + lw * 0.45, shy + 0.7 * B), (x0 + lw * 0.3, top + H - 3),
               (x0 + lw * 1.4, top + H - 2), (x0 + lw * 1.4, top + H), (x0 - lw * 0.6, top + H), (x0 - lw * 0.55, shy + 0.72 * B)], fill=ink)  # the legs
    d.text((3, H + 26), name[:19], fill=ink); d.text((3, 3), '%s, %.1f hd' % (sub[:11], heads), fill=ink)
    d.text((3, H + 36 - 1), 'neck %.2f h' % neck, fill=(150, 60, 170))
    return im


# my own estimates of each game's hero in profile, from published footage and art (heads tall, chin to shoulder top in heads, shoulder slope)
GAMES = [('Prince of Persia 89', 6.5, 0.35, 0.3, 'rotoscoped'), ('Another World', 7.0, 0.4, 0.3, 'rotoscoped'), ('Flashback', 7.0, 0.4, 0.3, 'rotoscoped'),
         ('Blackthorne', 6.5, 0.3, 0.2, 'rotoscoped'), ('Blasphemous', 6.0, 0.25, 0.2, 'hand pixels'), ('Lost Crown', 6.0, 0.35, 0.3, 'stylised 3D'),
         ('Dead Cells', 6.0, 0.3, 0.2, '3D to pixels'), ('Inside / Limbo', 5.0, 0.4, 0.4, 'child, shadow'), ('Abe (Oddworld)', 4.0, 0.6, 0.6, 'big head'),
         ('Celeste', 2.7, 0.0, 0.0, 'chibi'), ('Shovel Knight', 3.0, 0.0, 0.0, 'chibi'), ('Hollow Knight', 2.2, 0.05, 0.0, 'chibi'),
         ('Rayman', 3.0, 0.0, 0.0, 'limbless'), ('Cuphead', 3.0, 0.2, 0.3, 'rubber hose'),
         ('Dawnward v69', 4.9, 0.17, 0.2, 'before'), ('Dawnward 22b', 5.1, 0.41, 0.3, 'after')]

if __name__ == '__main__':
    J = {'errors': [], 'measure': {}, 'moves': {}}
    vers = [('old', OLD)] + ([('r22', R22)] if os.path.exists(R22) else []) + [('new', NEW)]
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
        P = {}
        for v, src in vers:
            for m in (('torch', 'classic') if v != 'r22' else ('classic',)):
                P[(v, m)] = R12.page(b, src, m)
        pn = P[('new', 'classic')]
        poses = pn.evaluate(POSES)
        # ---- 1. the guide sheet
        W, Hh, X, Y = 26, 60, 13, 57
        t = []
        for v, _ in vers:
            pg = P[(v, 'classic')]
            g = pg.evaluate(GEO, [poses['stand'], X, Y, LEN0])
            t.append(R12.label(dataimg(pg.evaluate(FIG, [poses['stand'], S, W, Hh, X, Y, -1, None, 'hero'])), '%s, lit from his back' % TAG[v]))
            sil = dataimg(pg.evaluate(FIG, [poses['stand'], S, W, Hh, X, Y, 1, '#120c18', 'hero']))
            crown, sole = rows_of(sil)
            J['measure'][v] = guide(sil, g, crown, sole + 1, TAG[v])
            ImageDraw.Draw(sil).text((60, 4), '%s: heads, chin to shoulder' % TAG[v], fill=(20, 16, 24))
            t.append(sil)
        c0, s0 = rows_of(dataimg(pn.evaluate(FIG, [poses['stand'], S, W, Hh, X, Y, 1, '#120c18', 'hero'])))
        t.append(ruler(Hh, c0, s0 + 1))
        g = Image.new('RGB', (sum(i.width for i in t) + 2 * len(t), Hh * S), (20, 16, 24)); xx = 0
        for i in t:
            g.paste(i, (xx, 0)); xx += i.width + 2
        g.save(os.path.join(OUT, 'r22b_guide.png'))
        print('guide', J['measure'], flush=True)
        # ---- 2. every pose, before | after
        tiles = []
        for k, q in list(poses.items()) + [('robber', 'rob')]:
            pair = []
            for v in ('old', 'new'):
                qq, pk = (poses['stand'], 'rob') if q == 'rob' else (q, 'hero')
                air = k in ('hang', 'pull', 'press', 'reach', 'slide', 'kneel')
                pair.append(dataimg(P[(v, 'classic')].evaluate(FIG, [qq, 4, 44, 72, 36 if k == 'dead' else 20, 60 if air else 68, -1, None, pk])))
            im = R12.grid(pair, 2, 1)
            tiles.append(R12.label(im, '%s: v69 | 22b' % k))
        R12.grid(tiles, 6).save(os.path.join(OUT, 'r22b_poses.png'))
        print('poses done', flush=True)
        # ---- 3. standing in the game
        t, big = [], []
        for n, face in ((7, 1), (14, -1)):
            for m, rs in (('torch', 1), ('torch', 0.5), ('classic', 1)):
                for v in ('old', 'new'):
                    xy = P[(v, m)].evaluate(STAND, [n, 1, face, rs])
                    im = R12.shot(P[(v, m)])
                    t.append(R12.label(R12.crop(im, xy, 150, 200), '%s, %s%s' % (TAG[v][:6], m, ' .5' if rs < 1 else '')))
                    if m == 'torch':
                        big.append(R12.label(R12.crop(im, (xy[0], xy[1] - 24), 70, 90).resize((210, 270), Image.LANCZOS), '%s %s 3x' % (TAG[v][:6], 'rs .5' if rs < 1 else 'rs 1')))
        R12.stack([R12.grid(t, 12), R12.grid(big, 8)]).save(os.path.join(OUT, 'r22b_game.png'))
        print('game done', flush=True)
        # ---- 4. moves in the game
        rows = []
        # hanging on a wall's near face (only the hands show over the ledge) and climbing onto it: round 19's stops
        hv = None
        for n, sd in R19.HANGS:
            if P[('new', 'torch')].evaluate(R19.STOP, [n, sd, False]):
                hv = (n, sd); break
        J['moves']['hanging'] = hv
        if hv:
            for seq, lab, dy in (([(30, None)], 'hanging on a near face', 10), ([(30, None), (1, 'u'), (12, None)], 'climbing onto it', -12)):
                t = []
                for m in ('torch', 'classic'):
                    for v in ('old', 'new'):
                        P[(v, m)].evaluate(R19.STOP, [hv[0], hv[1], False])
                        for k, key in seq:
                            xy, st = P[(v, m)].evaluate(R19.STEP, [k, key])
                        P[(v, m)].evaluate("()=>{__HK.intro=0;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);__P.draw();}")
                        t.append(R12.label(R12.crop(R12.shot(P[(v, m)]), (xy[0], xy[1] + dy), 240, 240), '%s, %s, %s' % (lab, m, TAG[v][:6])))
                rows.append(R12.grid(t, 4))
        for name, cond, more, floors in MOVES:
            got = None
            if isinstance(floors, str):
                floors = [tuple(q) for q in P[('new', 'torch')].evaluate(FINDA, floors)]
            for n, sd in floors:
                q = P[('new', 'torch')].evaluate(MOMENT, [n, sd, cond, more, 1])
                if q['ok']:
                    got = (n, sd); break
            J['moves'][name] = got
            if not got:
                print('no', name, flush=True); continue
            t = []
            for m in ('torch', 'classic'):
                for v in ('old', 'new'):
                    q = P[(v, m)].evaluate(MOMENT, [got[0], got[1], cond, more, 1])
                    t.append(R12.label(R12.crop(R12.shot(P[(v, m)]), q['xy'], 240, 240), '%s, %s, %s, %s' % (name, q['name'][:16], m, TAG[v][:6])))
            rows.append(R12.grid(t, 4))
        t = []
        for m in ('torch', 'classic'):
            for v in ('old', 'new'):
                q = P[(v, m)].evaluate(E18.SWING, [6, 0.85, 0.25])
                P[(v, m)].evaluate("()=>{__HK.intro=0;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);__P.draw();}")
                t.append(R12.label(R12.crop(R12.shot(P[(v, m)]), P[(v, m)].evaluate(E18.AT, [q['fx'], q['fy'] + 22]), 240, 240), 'swinging, %s, %s' % (m, TAG[v][:6])))
        rows.append(R12.grid(t, 4))
        R12.stack(rows).save(os.path.join(OUT, 'r22b_moves.png'))
        print('moves done', J['moves'], flush=True)
        for (v, m), pg in P.items():
            J['errors'] += ['%s %s: %s' % (v, m, e) for e in pg.errs]
    # ---- 5. the games, schematic
    R12.grid([schematic(*q) for q in GAMES], 8).save(os.path.join(OUT, 'r22b_games.png'))
    json.dump(J, open(os.path.join(OUT, 'r22b.json'), 'w'), indent=1)
    print('errors', J['errors'][:5])
