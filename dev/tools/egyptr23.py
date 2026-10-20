# egyptr23.py [what] [new.html] [old.html]: round 23's pictures (the prince rebuilt from motion capture), into egypt_themes/.
# The data used in this project was obtained from mocap.cs.cmu.edu. The database was created with funding from NSF EIA-0196217.
#   moves   r23_moves.png: each move, the clip's side view (stick figure, mocap.py) | the new figure | v69, at 4x
#   body    r23_body.png: the new figure at 10x and in game size beside the subject's projected skeleton, with the proportions table
#   game    r23_game.png: in the game, Torchlight at GLP.rs 1 and .5 and Classic
#   clips   r23_run_swing.gif (running over swinging) and r23_climb.gif (jumping up to grab, hanging, climbing): v69 | after, in game (Classic)
# what: one of those or 'all' (default). v69 is hk_v69_release.html here or in the main checkout's dev/tools. Run from dev/tools.
import base64, io, json, math, os, sys, tempfile, shutil
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont
import mocap
import r23poses as RP

HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
WHAT = a[0] if a else 'all'
NEW = os.path.abspath(a[1] if len(a) > 1 and a[1] else os.path.join(HERE, '..', 'hourglass-keep.html'))
_old = os.path.join(HERE, 'hk_v69_release.html')
if not os.path.exists(_old):
    _old = os.path.join(HERE, '..', '..', '..', '..', '..', 'dev', 'tools', 'hk_v69_release.html')
OLD = os.path.abspath(a[2] if len(a) > 2 and a[2] else _old)
OUT = os.path.join(HERE, 'egypt_themes')
INK = (20, 16, 24)
BG = (232, 220, 200)
EXPORT = 'window.__R23={skel,PS,mk,RP,crawlPose,drinkFrame,climbFrame,swingPose,figDraw,PAL_HERO,GFX,LEN,guardPal};'

# label, the game's pose, the clip and frame it was measured from
MOVES = [('stand', 'PS.stand'), ('run 0', 'run 0'), ('run .25', 'run 0.25'), ('run .5', 'run 0.5'), ('run .75', 'run 0.75'),
         ('walk 0', 'walk 0'), ('walk .5', 'walk 0.5'), ('skid (stop)', 'PS.skid'), ('turn', 'PS.turn'), ('step', 'PS.step'),
         ('crouch', 'PS.crouch'), ('land', 'PS.land'), ('jumpS', 'PS.jumpS'), ('jumpR', 'PS.jumpR'), ('jumpLow', 'PS.jumpLow'),
         ('jumpLowS', 'PS.jumpLowS'), ('reach', 'PS.reach'), ('hang', 'PS.hang'), ('pull', 'PS.pull'), ('press', 'PS.press'),
         ('kneelUp', 'PS.kneelUp'), ('kneel', 'PS.kneel'), ('fall', 'PS.fall'), ('slide', 'PS.slide'), ('kickPush', 'PS.kickPush'),
         ('kickTuck', 'PS.kickTuck'), ('kickReach', 'PS.kickReach'), ('swing front', 'swing 0.8,0'), ('swing back', 'swing -0.8,0'),
         ('swing bottom', 'swing 0,3'), ('garde', 'PS.garde'), ('windup', 'PS.windup'), ('lunge', 'PS.lunge'), ('parry', 'PS.parry'),
         ('lowStrike', 'PS.lowStrike'), ('hurt', 'PS.hurt'), ('dead', 'PS.dead'), ('crawl 0', 'crawl 0'), ('crawl .5', 'crawl 0.5'),
         ('drink grasp', 'drink 0.3'), ('drink sip', 'drink 0.72'), ('drink back', 'drink 0.99')]

FIG = r'''([spec,S,W,Hh,x,y,ver])=>{const F=window.__HK&&window.__HK.MCP&&ver==='new'?window.__HK:window.__R23;let p;const [k,v]=spec.split(' ');
 if(spec.startsWith('PS.'))p=F.PS[spec.slice(3)];else if(k==='run')p=F.RP(+v);else if(k==='walk')p=F.walkPose?F.walkPose(+v):F.RP(+v,0.6);
 else if(k==='crawl')p=F.crawlPose(+v);else if(k==='drink')p=F.drinkFrame(+v).p;else if(k==='swing'){const [th,om]=v.split(',').map(Number);p=F.swingPose(th,om,0);}
 p=Object.assign(F.mk({}),p);F.GFX().hd=true;
 const cv=document.createElement('canvas');cv.width=W*S;cv.height=Hh*S;const c=cv.getContext('2d');c.fillStyle='#e8dcc8';c.fillRect(0,0,cv.width,cv.height);c.scale(S,S);
 c.strokeStyle='rgba(0,0,0,.25)';c.lineWidth=0.25;c.beginPath();c.moveTo(0,y);c.lineTo(W,y);c.stroke();
 const sw=['garde','windup','lunge','parry','lowStrike'].some(q=>spec==='PS.'+q);
 F.figDraw(c,x,y,1,p,F.PAL_HERO,{sword:sw,hasSword:true,time:0,lt:{dir:1,col:'255,220,170',k:0.6}});return cv.toDataURL('image/png');}'''


def b64img(u):
    return Image.open(io.BytesIO(base64.b64decode(u.split(',')[1]))).convert('RGB')


def page(b, src, tag, tmp):
    s = open(src, encoding='utf-8').read()
    i = s.find('window.__HK={')
    fn = os.path.join(tmp, '_r23_%s.html' % tag)
    open(fn, 'w', encoding='utf-8').write(s[:i] + EXPORT + s[i:])
    pg = b.new_page()
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://' + fn)
    pg.wait_for_timeout(700)
    return pg, errs


def stick_for(spec):
    """the clip frame a move was measured from, as a stick figure (side view), PIL image"""
    J = json.load(open(os.path.join(HERE, 'r23body.json')))['src']
    k = spec.split(' ')
    name = spec[3:] if spec.startswith('PS.') else k[0]
    if spec.startswith('PS.'):
        s = J.get(name)
        if not s:
            return None, ''
        clip, fr = s['clip'], s['frame']
    elif k[0] in ('run', 'walk', 'crawl'):
        s = J[k[0]]
        i0 = {'run': (42, 88), 'walk': (80, 131), 'crawl': (760, 460)}[k[0]]
        clip, fr = s['clip'], int(i0[0] + i0[1] * float(k[1]))
    elif k[0] == 'drink':
        t = float(k[1])
        clip, fr = ('81_14', 1300) if t < 0.4 else ('79_38', {0.72: 220, 0.99: 360}.get(t, 220))
    elif k[0] == 'swing':
        th = float(k[1].split(',')[0])
        clip, fr = '43_02', {0.8: 348, -0.8: 228, 0.0: 288}.get(th, 288)
    else:
        return None, ''
    c = RP.clip(clip)
    f = RP.fwd_of(c, fr, span=(0, 240)) if name == 'dead' else (RP.fwd_of(c, 240, span=(100, 400)) if clip == '43_02' else RP.fwd_of(c, fr))
    Q = mocap.project(c.P(fr), f)
    im = Image.new('RGB', (140, 200), BG)
    dr = ImageDraw.Draw(im)
    fl = min(Q[q][1] for q in ('ankleL', 'ankleR', 'ballL', 'ballR', 'toeL', 'toeR'))
    H = ((Q['hipL'][0] + Q['hipR'][0]) / 2)
    sc = 100
    ox, oy = 70 - H * sc, 185 + fl * sc
    if Q['crown'][1] - fl > 1.9 or name in ('hang', 'reach', 'slide') or k[0] == 'swing':
        top = max(Q[q][1] for q in Q)
        oy = 12 + top * sc
    mocap.draw_stick(dr, Q, ox, oy, sc, 'r', w=2)
    return im, '%s f%s' % (clip, fr)


def moves(b):
    tmp = tempfile.mkdtemp(prefix='r23m', dir=HERE)
    try:
        pn, en = page(b, NEW, 'new', tmp)
        po, eo = page(b, OLD, 'old', tmp)
        S, W, Hh = 4, 70, 72
        cw, ch = 140 + W * S * 2 + 30, 300
        per = 3
        rows = (len(MOVES) + per - 1) // per
        sheet = Image.new('RGB', (cw * per, ch * rows + 40), (250, 246, 238))
        d = ImageDraw.Draw(sheet)
        d.text((8, 8), 'Round 23: each move as measured (CMU mocap, side view; red = near limbs) | the new prince | v69, 4x. '
               'Data: mocap.cs.cmu.edu (NSF EIA-0196217).', fill=INK)
        for n, (lab, spec) in enumerate(MOVES):
            x0, y0 = (n % per) * cw, 40 + (n // per) * ch
            st, cap = stick_for(spec)
            if st:
                sheet.paste(st.resize((140, 200)), (x0, y0 + 30))
            hang = any(q in spec for q in ('hang', 'reach', 'slide', 'swing', 'pull'))
            yy = 64 if not hang else 62
            for j, (pg, ver) in enumerate(((pn, 'new'), (po, 'old'))):
                im = b64img(pg.evaluate(FIG, [spec, S, W, Hh, 35, yy, ver]))
                sheet.paste(im, (x0 + 140 + 10 + j * (W * S + 10), y0 + 4))
            d.text((x0 + 4, y0 + 4), lab, fill=INK)
            d.text((x0 + 4, y0 + 236), cap, fill=(90, 80, 70))
        sheet.save(os.path.join(OUT, 'r23_moves.png'), optimize=True)
        print('r23_moves.png', sheet.size, 'errors', en[:3], eo[:3])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


MEAS = r'''()=>{const F=window.__HK,p=F.mk(F.PS.stand),s=F.skel(p),L=F.LEN,r=L.hd,ha=p.lean+p.head;
 const S=10,W=60,H=70,cv=document.createElement('canvas');cv.width=W*S;cv.height=H*S;const c=cv.getContext('2d');c.scale(S,S);
 F.figDraw(c,30,64,1,p,F.PAL_HERO,{hasSword:false,time:0,mono:'#000'});const d=c.getImageData(0,0,W*S,H*S).data;let t=1e9,b=-1;
 for(let y=0;y<H*S;y++)for(let x=0;x<W*S;x++)if(d[(y*W*S+x)*4+3]>127){if(y<t)t=y;if(y>b)b=y;}
 const crown=t/S-64,sole=(b+1)/S-64,hip=-s.hipH,chin=hip+s.hd[1]+1.15*r*Math.cos(ha);
 return {crown,sole,height:sole-crown,chin,head:chin-crown,heads:(sole-crown)/(chin-crown),hip,sh:hip+s.sh[1],knee:hip+s.kF[1],hand:hip+s.hF[1],elb:hip+s.eF[1],LEN:L};}'''
BIGF = r'''([S,W,Hh,x,y,pal,lit])=>{const F=window.__HK,p=F.mk(F.PS.stand);const cv=document.createElement('canvas');cv.width=W*S;cv.height=Hh*S;const c=cv.getContext('2d');
 c.fillStyle='#e8dcc8';c.fillRect(0,0,cv.width,cv.height);c.scale(S,S);const P=pal==='rob'?window.__R23.guardPal({tier:1}):F.PAL_HERO;
 F.figDraw(c,x,y,1,p,P,{hasSword:true,time:0,lt:lit?{dir:1,col:'255,220,170',k:0.6}:null});return cv.toDataURL('image/png');}'''


def body(b):
    tmp = tempfile.mkdtemp(prefix='r23b', dir=HERE)
    try:
        pn, en = page(b, NEW, 'new', tmp)
        M = pn.evaluate(MEAS)
        J = json.load(open(os.path.join(HERE, 'r23body.json')))
        S = 10
        big = b64img(pn.evaluate(BIGF, [S, 40, 62, 20, 58, 'hero', True]))
        rob = b64img(pn.evaluate(BIGF, [4, 40, 62, 20, 58, 'rob', True]))
        small = [b64img(pn.evaluate(BIGF, [k, 40, 62, 20, 58, 'hero', True])) for k in (1, 3)]
        c = RP.clip('79_38')
        Q = mocap.project(c.P(30), RP.fwd_of(c, 30))
        fl = min(Q[q][1] for q in ('ankleL', 'ankleR', 'ballL', 'ballR', 'toeL', 'toeR'))
        top = Q['crown'][1]
        sc = (big.height - 60) / (top - fl)
        st = Image.new('RGB', (300, big.height), BG)
        mocap.draw_stick(ImageDraw.Draw(st), Q, 150 - ((Q['hipL'][0] + Q['hipR'][0]) / 2) * sc, big.height - 22 + fl * sc, sc, 'r', w=4)
        ImageDraw.Draw(st).text((6, 6), 'CMU 79_38 f30 (side view)', fill=INK)
        W2 = big.width + st.width + 470
        im = Image.new('RGB', (W2, big.height + 40), (250, 246, 238))
        d = ImageDraw.Draw(im)
        d.text((8, 8), 'Round 23: the new prince at 10x | the CMU subject the standing pose comes from | in game (1x, 3x), a robber (4x), the proportions. '
               'Data: mocap.cs.cmu.edu (NSF EIA-0196217), ANSUR II.', fill=INK)
        im.paste(big, (0, 40))
        im.paste(st, (big.width, 40))
        x = big.width + st.width + 10
        im.paste(small[0], (x, 60))
        im.paste(small[1], (x + 50, 60))
        im.paste(rob, (x + 180, 60))
        B = J['body']
        Wd = J['widths']
        info = J['info']
        rows = [('standing height (sole to crown)', '%.1f px (v69 53.0)' % M['height']), ('heads tall (chin to crown %.1f px)' % M['head'], '%.2f' % M['heads']),
                ('scale below the chin', '%.2f cm a px' % info['cm_per_px']), ('hip joint over the floor', '%.1f px (%.2f of height)' % (-M['hip'], -M['hip'] / M['height'])),
                ('thigh / shank to the floor', '%.1f / %.1f px' % (B['th'], B['sh'])), ('hip joint to shoulder joint', '%.1f px' % B['to']),
                ('shoulder joint to chin', '%.1f px' % Wd['jc']), ('upper arm / forearm to the palm', '%.1f / %.1f px' % (B['ua'], B['fa'])),
                ('head radius (LEN.hd)', '%.2f px' % B['hd']), ('chest / waist / seat depth', '%.1f / %.1f / %.1f px' % (Wd['chest'], Wd['waist'], Wd['seat'])),
                ('neck depth (at its base)', '%.1f (%.1f) px' % (Wd['neck'], Wd['neckB'])), ('thigh / calf / upper arm across', '%.1f / %.1f / %.1f px' % (Wd['thigh'], Wd['calf'], Wd['arm'])),
                ('foot length', '%.1f px' % Wd['foot'])]
        y = 60 + max(small[1].height, rob.height) + 20
        for k, v in rows:
            d.text((x, y), k, fill=INK)
            d.text((x + 240, y), v, fill=INK)
            y += 18
        im.save(os.path.join(OUT, 'r23_body.png'), optimize=True)
        json.dump(M, open(os.path.join(HERE, 'r23measure.json'), 'w'), indent=1)
        print('r23_body.png', im.size, 'height %.2f heads %.2f head %.2f' % (M['height'], M['heads'], M['head']), en[:3])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def game(b):
    """in the game, v69 | after: standing and running (Torchlight rs 1 and .5, Classic), hanging and climbing, crawling, swinging, fighting"""
    import egyptr12 as R12, egyptr18 as E18, egyptr19 as R19, egyptr22b as B22, egyptr22c as C22
    R12.OUT = OUT
    tmp = tempfile.mkdtemp(prefix='r23g', dir=HERE)
    try:
        FILES = {}
        for k, f in (('v69', OLD), ('after', NEW)):
            fn = os.path.join(tmp, '_r23_game_%s.html' % k)
            shutil.copy(f, fn)
            FILES[k] = fn
        GP = {(k, mo): R12.page(b, FILES[k], mo) for k in FILES for mo in ('torch', 'classic')}
        rows, t = [], []
        for mo, rs in (('torch', 1), ('torch', 0.5), ('classic', 1)):
            for vv in ('v69', 'after'):
                pg = GP[(vv, mo)]
                xy = pg.evaluate(B22.STAND, [7, 1, 1, rs])
                t.append(R12.label(R12.crop(R12.shot(pg), (xy[0], xy[1] - 6), 220, 250), 'standing %s%s %s' % (mo, ' .5' if rs < 1 else '', vv)))
        for mo, rs in (('torch', 1), ('torch', 0.5), ('classic', 1)):
            for vv in ('v69', 'after'):
                q = GP[(vv, mo)].evaluate(B22.MOMENT, [6, 1, "H.P.state==='run'", 14, rs])
                t.append(R12.label(R12.crop(R12.shot(GP[(vv, mo)]), q['xy'], 220, 250), 'running %s%s %s' % (mo, ' .5' if rs < 1 else '', vv)))
        rows.append(R12.grid(t, 6))
        for pg in GP.values():
            pg.evaluate("()=>{if(__HK.GLP)__HK.GLP.rs=1;}")
        hv = None
        for n, sd in R19.HANGS:
            if GP[('after', 'torch')].evaluate(R19.STOP, [n, sd, False]):
                hv = (n, sd)
                break
        if hv:
            t = []
            for seq, lab, dy in (([(30, None)], 'hanging', 10), ([(30, None), (1, 'u'), (8, None)], 'pulling up', 0), ([(30, None), (1, 'u'), (16, None)], 'climbing', -12)):
                for mo in ('torch', 'classic'):
                    for vv in ('v69', 'after'):
                        pg = GP[(vv, mo)]
                        pg.evaluate(R19.STOP, [hv[0], hv[1], False])
                        for kk, key in seq:
                            xy, st = pg.evaluate(R19.STEP, [kk, key])
                        pg.evaluate("()=>{__HK.intro=0;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);__P.draw();}")
                        t.append(R12.label(R12.crop(R12.shot(pg), (xy[0], xy[1] + dy), 220, 250), '%s %s %s' % (lab, mo, vv)))
            rows.append(R12.grid(t, 6))
        t = []
        name, cond, more, floors = B22.MOVES[0]
        got = None
        for n, sd in [tuple(q) for q in GP[('after', 'torch')].evaluate(B22.FINDA, floors)]:
            if GP[('after', 'torch')].evaluate(B22.MOMENT, [n, sd, cond, more, 1])['ok']:
                got = (n, sd)
                break
        if got:
            for mo in ('torch', 'classic'):
                for vv in ('v69', 'after'):
                    q = GP[(vv, mo)].evaluate(B22.MOMENT, [got[0], got[1], cond, more, 1])
                    t.append(R12.label(R12.crop(R12.shot(GP[(vv, mo)]), q['xy'], 220, 250), 'crawling %s %s' % (mo, vv)))
        for mo in ('torch', 'classic'):
            for vv in ('v69', 'after'):
                pg = GP[(vv, mo)]
                q = pg.evaluate(E18.SWING, [6, 0.85, 0.25])
                pg.evaluate("()=>{__HK.intro=0;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);__P.draw();}")
                t.append(R12.label(R12.crop(R12.shot(pg), pg.evaluate(E18.AT, [q['fx'], q['fy'] + 22]), 220, 250), 'swinging %s %s' % (mo, vv)))
        rows.append(R12.grid(t, 8))
        t = []
        fgot = None
        for n, sd in ((6, 1), (7, 1), (12, 1), (5, 1)):
            if GP[('after', 'torch')].evaluate(C22.FIGHT, [n, sd, 25, 1])['ok']:
                fgot = (n, sd)
                break
        if fgot:
            for mo, rs in (('torch', 1), ('torch', 0.5), ('classic', 1)):
                for vv in ('v69', 'after'):
                    q = GP[(vv, mo)].evaluate(C22.FIGHT, [fgot[0], fgot[1], 25, rs])
                    t.append(R12.label(R12.crop(R12.shot(GP[(vv, mo)]), q['xy'], 280, 250), 'fight %s%s %s' % (mo, ' .5' if rs < 1 else '', vv)))
            rows.append(R12.grid(t, 6))
        im = R12.stack(rows)
        im.save(os.path.join(OUT, 'r23_game.png'), optimize=True)
        errs = [e for pg in GP.values() for e in pg.errs]
        print('r23_game.png', im.size, 'hang', hv, 'crawl', got, 'fight', fgot, 'errors', errs[:3])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


TICK = r'''([k,key,hold])=>{const H=__HK;if(key)H.setKey('kb',key,true);H.tick(k);if(key&&!hold)H.setKey('kb',key,false);H.banner=null;H.intro=0;
 document.querySelectorAll('.screen').forEach(e=>e.hidden=true);__P.draw();const P=H.P;return __P.scr(P.x,P.y-30);}'''


def clips(b):
    """short loops in game (Classic), v69 | after: running, jumping up to grab and climbing, swinging"""
    import egyptr12 as R12, egyptr18 as E18, egyptr19 as R19, egyptr22b as B22
    tmp = tempfile.mkdtemp(prefix='r23c', dir=HERE)
    try:
        FILES = {}
        for k, f in (('v69', OLD), ('after', NEW)):
            fn = os.path.join(tmp, '_r23_clip_%s.html' % k)
            shutil.copy(f, fn)
            FILES[k] = fn
        GP = {k: R12.page(b, FILES[k], 'classic') for k in FILES}
        CW, CH = 220, 240

        def save(frames, name, ms):
            fr = [f.convert('P', palette=Image.ADAPTIVE, colors=96) for f in frames]
            fr[0].save(os.path.join(OUT, name), save_all=True, append_images=fr[1:], duration=ms, loop=0, optimize=True)
            print(name, len(fr), '%.0f KB' % (os.path.getsize(os.path.join(OUT, name)) / 1024))

        def pair(ims, lab):
            g = Image.new('RGB', (CW * 2 + 4, CH), (20, 16, 24))
            for i, (im, l) in enumerate(zip(ims, ('v69', 'after (round 23)'))):
                g.paste(R12.label(im, '%s %s' % (lab, l)), (i * (CW + 4), 0))
            return g
        # running: the bot runs on floor 6 until he has run 14 frames, then the run is held on for 1.5 s, 2 game frames a picture
        seq = {}
        for k, pg in GP.items():
            q = pg.evaluate(B22.MOMENT, [6, 1, "H.P.state==='run'", 14, 1])
            key = 'r' if pg.evaluate('()=>__HK.P.face') > 0 else 'l'
            out = []
            for i in range(36):
                xy = pg.evaluate(TICK, [2, key, True])
                out.append(R12.crop(R12.shot(pg), (xy[0], xy[1] + 4), CW, CH))
            pg.evaluate("()=>{for(const q of ['l','r','u','d','j','g'])__HK.setKey('kb',q,false);}")
            seq[k] = out
        RUNF = [pair([seq['v69'][i], seq['after'][i]], 'running') for i in range(36)]
        # jumping up to grab a ledge, hanging, climbing onto it
        hv = None
        for n, sd in R19.HANGS:
            if GP['after'].evaluate(R19.STOP, [n, sd, False]):
                hv = (n, sd)
                break
        seq = {}
        for k, pg in GP.items():
            pg.evaluate(R19.STOP, [hv[0], hv[1], False])
            out = []
            xy0 = None
            for i in range(60):
                xy, st = pg.evaluate(R19.STEP, [2, 'u' if i == 22 else None])
                xy0 = xy0 or xy
                out.append(R12.crop(R12.shot(pg), (xy[0], xy[1] - 8), CW, CH))
            seq[k] = out
        save([pair([seq['v69'][i], seq['after'][i]], 'jump up, climb') for i in range(60)], 'r23_climb.gif', 66)
        # the swing: from a throw of 0.85 rad, 2.4 s
        seq = {}
        for k, pg in GP.items():
            q = pg.evaluate(E18.SWING, [6, 0.85, 0.25])
            at = pg.evaluate(E18.AT, [q['fx'], q['fy'] + 22])
            out = []
            for i in range(36):
                pg.evaluate(TICK, [4, None, False])
                out.append(R12.crop(R12.shot(pg), at, CW, CH))
            seq[k] = out
        SWF = [pair([seq['v69'][i], seq['after'][i]], 'swinging') for i in range(36)]
        both = []
        for a, c in zip(RUNF, SWF):
            g = Image.new('RGB', (a.width, a.height + c.height + 4), (20, 16, 24))
            g.paste(a, (0, 0))
            g.paste(c, (0, a.height + 4))
            both.append(g)
        save(both, 'r23_run_swing.gif', 66)
        print('clips errors', [e for pg in GP.values() for e in pg.errs][:3])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
        if WHAT in ('moves', 'all'):
            moves(b)
        if WHAT in ('body', 'all'):
            body(b)
        if WHAT in ('game', 'all'):
            game(b)
        if WHAT in ('clips', 'all'):
            clips(b)
        b.close()
