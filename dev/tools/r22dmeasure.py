# r22dmeasure.py [build.html ...]: round 22d's measures. The rule (owner, round 22d): the prince's proportions follow the 1989 Prince of
# Persia kid (DOS). This measures the kid from his sprite frames (ref/pop_kid.png and .json, from the PrinceJS project's assets/gfx,
# https://github.com/oklemenz/PrinceJS; frame names kid-N are the original's frame numbers, as named in SDLPoP's src/types.h enum
# (frame_15_stand, frame_7..14_run, frame_121..132_stepping, frame_109_crouch, frame_87..99_hanging, frame_135..149_climbing,
# frame_150_parry, frame_151..153_strike, frame_158_stand_with_sword, frame_191..205_drink) and our figure the same way, and prints both.
#
# DOS pixels: 320x200 shown on a 4:3 screen, so a pixel is 1.2 times taller than wide. Every horizontal measure of the kid is divided by
# 1.2 to put it in rows (vertical pixels); vertical measures are used as they are. All of the kid's numbers are then in rows, and his
# ratios are taken to his standing height (frame 15: 41 rows, crown to sole) and to his head (crown to chin, 7 rows).
#
# The kid's landmarks are read by eye from the frames (row and column of the pixel edges, listed in KID_LM with the frame each comes from)
# and his depth profile is measured: the silhouette's width at each row of the standing frames 15, 121 and 132 (arm included, as it
# hangs inside the silhouette), averaged.
# Ours: the standing figure drawn at 10x (r22cmeasure's hooked build: the skeleton exported; landmarks chin, acromion top, pit of the neck,
# C7, the neck's depth), plus: the head's depth, the silhouette's width at the same fractions of height as the kid's rows, the fingertip
# (the arm's lowest pixel), elbow, wrist and knee from the skeleton, the crotch (the top of the gap between the legs, drawn astride, as the
# kid's is read from his stride frames; the kilt left out, as his trousers' split is read) and the foot's length on the floor.
import os, json, sys, tempfile, shutil, math
import r22cmeasure as M
HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, 'ref')
PAR = 1.2  # the DOS pixel's height over its width on a 4:3 screen

# The kid's landmarks, in rows from the crown's top edge (frame 15: crown 0, sole 41), pixel edges. Lengths along a limb in rows, with the
# horizontal part divided by PAR.
KID_H = 41.0
KID_LM = {
    'crown': (0.0, 'kid-15: hair, row 0 top edge'),
    'chin': (7.0, 'kid-15: the jaw, row 6 bottom edge (the head is the same bitmap in every upright frame)'),
    'neck_front': (1.0, 'kid-15, 1, 12, 132: one row of throat skin (row 7) between the chin and the shirt'),
    'shoulder_line': (7.0, 'kid-15, 132: the shirt over the trapezius starts at row 7, level with the chin, behind the neck'),
    'acromion': (8.0, 'kid-15, 132: the arm\'s skin (the deltoid) starts at row 8'),
    'shoulder_joint': (9.5, 'kid-10, 12: the arm\'s pivot, about 1.5 rows under the deltoid\'s top'),
    'elbow': (16.5, 'kid-10: the bent arm, elbow at row 16-17'),
    'wrist': (21.5, 'kid-15: the arm narrows to the hand at rows 21-22'),
    'fingertip': (25.0, 'kid-15: the hand\'s lowest skin, row 24 bottom edge'),
    'waist': (16.5, 'guard-29: the sash, rows 16-17 of 40 (the kid\'s shirt and trousers are one white; the guards\' sash marks it)'),
    'crotch': (22.8, 'kid-12, 152: the straight back leg from the split (rows 25, 23) to the sole, 18.0 and 17.6 rows along the leg; '
                     'kid-158/150 fight stance split at row 22 of 36; baggy trousers hang ~1 row under the true crotch'),
    'knee': (29.7, 'kid-12, 158: knee to sole along the shin 10.8 and 8.2 rows (mean 9.5), plus 1.8 for the bent knee\'s cap'),
    'sole': (41.0, 'kid-15: the foot\'s row 40 bottom edge'),
}
KID_W = {  # widths in DOS pixels (divide by PAR for rows)
    'head_depth': (8, 'kid-15 row 4: hair at the back to the brow, cols 2-9'),
    'neck_depth': (4, 'kid-15, 121, 132 row 7: throat to the shirt\'s collar at the back'),
    'foot': (7, 'kid-15 row 40: heel to toe'),
    'upper_arm': (4, 'kid-15 rows 9-12: the hanging arm, cols 6-9'),
    'forearm': (3, 'kid-15 rows 13-20'),
}


def kid_profile():
    """the standing frames' silhouette width (rows, /PAR) at each row's fraction of height, averaged over frames 15, 121 and 132"""
    from PIL import Image
    im = Image.open(os.path.join(REF, 'pop_kid.png')).convert('RGBA')
    J = json.load(open(os.path.join(REF, 'pop_kid.json')))['frames']
    prof = {}
    for n in ('15', '121', '132'):
        f = J['kid-' + n]['frame']
        h = f['h']
        for y in range(h):
            xs = [x for x in range(f['w']) if im.getpixel((f['x'] + x, f['y'] + y))[3]]
            if xs:
                fr = round((y + 0.5) / h, 2)
                prof.setdefault(fr, []).append((xs[-1] - xs[0] + 1) / PAR)
    return {k: sum(v) / len(v) for k, v in sorted(prof.items())}


def kid():
    H = KID_H
    L = {k: v[0] for k, v in KID_LM.items()}
    head = L['chin'] - L['crown']
    up = lambda k: H - L[k]  # height over the sole
    d = {'height': H, 'head': head, 'heads': H / head}
    for k in ('chin', 'shoulder_line', 'acromion', 'shoulder_joint', 'elbow', 'wrist', 'fingertip', 'waist', 'crotch', 'knee'):
        d['h_' + k] = up(k) / H
    d['chin_acr_H'] = (L['acromion'] - L['chin']) / H
    d['chin_acr_head'] = (L['acromion'] - L['chin']) / head
    d['neck_front_H'] = L['neck_front'] / H
    d['trunk_H'] = (L['crotch'] - L['acromion']) / H           # acromion to crotch
    d['upper_arm_H'] = (L['elbow'] - L['shoulder_joint']) / H   # (vertical, the arm hanging: kid-10's bent arm gives 8.2 rows along it)
    d['arm_H'] = (L['fingertip'] - L['shoulder_joint']) / H
    d['leg_H'] = up('crotch') / H
    for k, v in KID_W.items():
        d[k + '_H'] = v[0] / PAR / H
        d[k + '_head'] = v[0] / PAR / head
    P = kid_profile()
    for name, a, b in (('chest', 0.25, 0.36), ('belly', 0.40, 0.55), ('hips', 0.60, 0.68), ('knees', 0.72, 0.80)):
        v = [w for f, w in P.items() if a <= f <= b]
        d[name + '_H'] = sum(v) / len(v) / H
    d['profile'] = P
    return d


OURS = r'''()=>{const F=__FS;F.GFX().hd=true;const S=10,W=60,H=80,X=30,Y=70;
 const fig=(p,noarm,nok)=>{window.__NOARM=noarm;window.__NOKILT=nok;const cv=document.createElement('canvas');cv.width=W*S;cv.height=H*S;const c=cv.getContext('2d');c.scale(S,S);
   F.figDraw(c,X,Y,1,p,F.PAL_HERO,{sword:false,hasSword:false,time:0,mono:'#000'});window.__NOARM=0;window.__NOKILT=0;return c.getImageData(0,0,cv.width,cv.height).data;};
 const w=W*S,h=H*S,on=(D,x,y)=>D[(y*w+x)*4+3]>127,p=F.mk(F.PS.stand),s=F.skel(p),A=fig(p,0),N=fig(p,1),hipY=(Y-s.hipH)*S,up=yy=>(hipY-yy)/S;
 let crown=1e9,sole=-1;for(let y=0;y<h;y++)for(let x=0;x<w;x++)if(on(A,x,y)){if(y<crown)crown=y;sole=y;}
 const wid=(D,y)=>{let a=-1,b=-1;for(let x=0;x<w;x++)if(on(D,x,y)){if(a<0)a=x;b=x;}return a<0?0:(b-a+1)/S;};
 const prof={};for(let i=0;i<100;i++){const f=(i+0.5)/100,y=Math.round(crown+f*(sole+1-crown));prof[f.toFixed(3)]=wid(A,y);}
 let fing=-1;for(let y=0;y<h;y++)for(let x=0;x<w;x++)if(on(A,x,y)&&!on(N,x,y)&&y>hipY-6*S)fing=y;
 const L=F.LEN,r=L.hd,ha=p.lean+p.head,hy=-Math.cos(ha),chinY=(Y-s.hipH+s.hd[1]+hy*(-1.15*r)+0.6)*S;
 let hdep=0;for(let y=crown;y<chinY;y++)hdep=Math.max(hdep,wid(N,y));
 let foot=wid(A,sole),neckD=wid(N,Math.round(chinY+0.5*S)); // (the neck's depth 0.5 px under the chin's outline, as the kid's row under his chin)
 // astride: the legs 43 degrees each side, straight (as the kid's stride frames 12 and 152); the crotch is the top of the gap between them
 const q=F.mk({hF:0.75,kF:0,hB:-0.75,kB:0,aF:0.08,aB:-0.06}),sq=F.skel(q),B=fig(q,1,1),hq=(Y-sq.hipH)*S;let crotch=null;
 for(let y=Math.round(hq-4*S);y<h;y++){let a=-1,b=-1,gap=false;for(let x=0;x<w;x++)if(on(B,x,y)){if(a<0)a=x;else if(b>=0&&x>b+1)gap=true;b=x;}if(gap){crotch=(hq-y)/S;break;}}
 const k0=Math.hypot(sq.fF[0],sq.fF[1]);
 return {crown:up(crown),sole:up(sole+1),profile:prof,fingertip:up(fing+1),elbow:-s.eF[1],wrist:-(s.eF[1]+(s.hF[1]-s.eF[1])*0.86),knee:-s.kF[1],
   headDepth:hdep,foot,neckD,crotchAstride:crotch,legAstride:k0,legStand:s.fF[1],LEN:L};}'''


def ours(browser, builds, tmp):
    base = M.measure(browser, builds, tmp)
    for tag, txt in builds:
        q = "celAt(ctx,kp,C('pants')"
        assert q in txt
        fn = M.hooked(txt.replace(q, 'if(!window.__NOKILT)' + q, 1), tag + 'd', tmp)
        pg = browser.new_page()
        pg.goto('file://' + fn)
        pg.wait_for_timeout(400)
        o = pg.evaluate(OURS)
        pg.close()
        m = base[tag]
        H = o['crown'] - o['sole']
        hd = m['head']
        lo = -o['sole']
        d = {'height': H, 'head': hd, 'heads': H / hd}
        # (heights over the sole as a share of the height; the crotch standing: the hip less the split's distance down the leg, legs 43 degrees apart)
        cr = o['crotchAstride'] / math.cos(0.75) if o['crotchAstride'] is not None else 0  # (the split's distance from the hip along the leg, as the kid's)
        for k, v in (('chin', m['chin']), ('shoulder_line', m['c7']), ('acromion', m['acromion']), ('shoulder_joint', m['joint']), ('elbow', o['elbow']),
                     ('wrist', o['wrist']), ('fingertip', o['fingertip']), ('crotch', cr), ('knee', o['knee'])):
            d['h_' + k] = (v + lo) / H
        d['chin_acr_H'] = (m['chin'] - m['acromion']) / H
        d['chin_acr_head'] = (m['chin'] - m['acromion']) / hd
        d['neck_front_H'] = (m['chin'] - m['notch']) / H
        d['trunk_H'] = (m['acromion'] - cr) / H
        d['upper_arm_H'] = (m['joint'] - o['elbow']) / H
        d['arm_H'] = (m['joint'] - o['fingertip']) / H
        d['leg_H'] = (cr + lo) / H
        d['head_depth_H'] = o['headDepth'] / H
        d['head_depth_head'] = o['headDepth'] / hd
        d['neck_depth_H'] = o['neckD'] / H
        d['neck_depth_head'] = o['neckD'] / hd
        d['foot_H'] = o['foot'] / H
        P = {float(k): v for k, v in o['profile'].items()}
        for name, a, b in (('chest', 0.25, 0.36), ('belly', 0.40, 0.55), ('hips', 0.60, 0.68), ('knees', 0.72, 0.80)):
            v = [w for f, w in P.items() if a <= f <= b]
            d[name + '_H'] = sum(v) / len(v) / H
        d['profile'] = P
        d['raw'] = {k: v for k, v in o.items() if k != 'profile'}
        d['r22c'] = {k: v for k, v in m.items() if not isinstance(v, (dict, list))}
        base[tag] = d
    return base


ROWS = [('heads', 'height in heads'), ('h_chin', 'chin height / H'), ('chin_acr_head', 'chin to acromion top / head'), ('chin_acr_H', 'chin to acromion / H'),
        ('neck_front_H', 'chin to pit of the neck / H'), ('h_shoulder_line', 'shoulder line (C7) / H'), ('h_acromion', 'acromion top / H'),
        ('h_shoulder_joint', 'shoulder joint / H'), ('h_elbow', 'elbow / H'), ('h_wrist', 'wrist / H'), ('h_fingertip', 'fingertip / H'),
        ('h_crotch', 'crotch / H'), ('h_knee', 'knee / H'), ('trunk_H', 'acromion to crotch / H'), ('arm_H', 'shoulder joint to fingertip / H'),
        ('head_depth_head', 'head depth / head height'), ('neck_depth_H', 'neck depth / H'), ('neck_depth_head', 'neck depth / head'),
        ('chest_H', 'depth at chest (0.25-0.36 H) / H'), ('belly_H', 'depth at waist (0.40-0.55) / H'), ('hips_H', 'depth at hips (0.60-0.68) / H'),
        ('knees_H', 'depth at knees (0.72-0.80) / H'), ('foot_H', 'foot length / H')]


def table(K, R):
    out = ['%-36s %8s ' % ('measure', 'PoP kid') + ' '.join('%10s' % t for t in R)]
    for k, name in ROWS:
        out.append('%-36s %8s ' % (name, ('%.3f' % K[k]) if k in K else '-') + ' '.join('%10s' % (('%.3f' % R[t][k]) if k in R[t] else '-') for t in R))
    return '\n'.join(out)


if __name__ == '__main__':
    from playwright.sync_api import sync_playwright
    files = sys.argv[1:] or [os.path.join(HERE, '..', '..', '..', '..', '..', 'dev', 'tools', 'hk_v69_release.html'), os.path.join(HERE, '..', 'hourglass-keep.html')]
    tmp = tempfile.mkdtemp(prefix='r22d', dir=HERE)
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            R = ours(b, [(os.path.basename(f), open(f, encoding='utf-8').read()) for f in files], tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(table(kid(), R))
