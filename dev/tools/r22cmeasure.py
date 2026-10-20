# r22cmeasure.py: round 22c's landmark measures of the standing prince (imported by egyptr22c.py; run alone it prints them for v69,
# round 22b and the current source). Each build is copied with two hooks: its skeleton exported (window.__FS) and window.__NOARM, which
# leaves the arms out, so the silhouette with and without arms gives the arms' own pixels. Landmarks, in px of the figure (y up from the
# hip, the trochanter, at 0):
#   chin       the head path's chin point (hd - 1.15 r along the head's axis), plus the outline's half width (0.6)
#   crown      the silhouette's top; sole its bottom
#   notch      the suprasternal notch: the neck's front edge at its deepest (the row where the armless silhouette's front edge is furthest
#              back between the chin and the chest), where the neck meets the chest
#   acromion   the visible top of the shoulder: the highest pixel of the arms' own silhouette (the deltoid's cap over the acromion)
#   joint      the shoulder joint (the skeleton's sh: the arm's pivot)
#   C7         the back's kink at the base of the neck: the point of the armless silhouette's back edge, between the skull and the joint,
#              furthest from the straight line joining its ends (the nape under the skull and the back at the joint)
#   neck depth the armless silhouette's width across the neck 0.3 px under the chin point (under the jaw, above C7; outline included)
import os, re, json, tempfile, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
EXPORT = "window.__FS={skel,LEN,PS,mk,figDraw,PAL_HERO,guardPal,GFX,NJ:(typeof NJ!=='undefined'?NJ:null)};"
S = 10
MEASURE = r'''()=>{const F=__FS;F.GFX().hd=true;const p=F.mk(F.PS.stand),s=F.skel(p),W=60,H=80,X=30,Y=70,S=%d;
 const draw=(noarm,noneck,mono)=>{window.__NOARM=noarm;window.__NONECK=noneck;const cv=document.createElement('canvas');cv.width=W*S;cv.height=H*S;const c=cv.getContext('2d');c.scale(S,S);
   F.figDraw(c,X,Y,1,p,F.PAL_HERO,{sword:false,hasSword:false,time:0,mono:mono?'#000':undefined,lt:{dir:1,col:'255,220,170',k:0.6}});window.__NOARM=0;window.__NONECK=0;return c.getImageData(0,0,cv.width,cv.height).data;};
 const w=W*S,h=H*S,A=draw(0,0,1),N=draw(1,0,1),C1=draw(0,0,0),C0=draw(0,1,0),hipY=(Y-s.hipH)*S,up=yy=>+((hipY-yy)/S).toFixed(3),on=(D,x,y)=>D[(y*w+x)*4+3]>127;
 let crown=1e9,sole=-1;for(let y=0;y<h;y++)for(let x=0;x<w;x++)if(on(A,x,y)){if(y<crown)crown=y;sole=y;}
 let arm=1e9;for(let y=0;y<h&&arm>1e8;y++)for(let x=0;x<w;x++)if(on(A,x,y)&&!on(N,x,y)){arm=y;break;}
 const front=y=>{for(let x=w-1;x>=0;x--)if(on(N,x,y))return x;return -1;},back=y=>{for(let x=0;x<w;x++)if(on(N,x,y))return x;return -1;};
 const L=F.LEN,r=L.hd,ha=p.lean+p.head,hx=Math.sin(ha),hy=-Math.cos(ha),chinY=(Y-s.hipH+s.hd[1]+hy*(-1.15*r)+hx*0.1*r+0.6)*S;
 const shY=(Y-s.hipH+s.sh[1])*S,ax=(X+s.sh[0])*S,hdY=(Y-s.hipH+s.hd[1])*S;
 // the neck as it reads: the lowest rows where drawing the neck changes the picture along the silhouette's front edge (the pit of the neck)
 // and its back edge (C7), within 1.5 px of the edge
 let nf=-1,nbk=-1;for(let y=Math.round(hdY);y<shY+6*S;y++){let cf=0,cb=0;const fe=front(y),be=back(y);for(let x=0;x<w;x++){const k=(y*w+x)*4,d=Math.abs(C1[k]-C0[k])+Math.abs(C1[k+1]-C0[k+1])+Math.abs(C1[k+2]-C0[k+2]);if(d>24){if(x>ax&&x>fe-1.5*S)cf++;else if(x<ax&&x<be+1.5*S)cb++;}}if(cf>2)nf=y;if(cb>2)nbk=y;}
 // the nape: under the skull, where the back edge stops curving forward onto the neck's line
 let nape=Math.round(hdY);for(let y=Math.round(hdY+0.4*r*S);y<chinY+2*S;y++){if(back(y+S/2)-back(y)<0.25*S){nape=y;break;}}
 if(nf<0)nf=arm; // (the neck's front hidden behind the shoulder: it ends at the shoulder's top)
 const my=Math.round(chinY-0.3*S),nw=(front(my)-back(my))/S,cy=Math.round(hipY+(shY-hipY)*0.72);
 const dq=F.NJ?F.NJ.dq:0.7,chinG=up(chinY)+0.6,acrG=up(shY)-dq+2.6; // (geometric: the chin point and the deltoid's cap over the joint, no outline)
 return {chinG:+chinG.toFixed(3),acrG:+acrG.toFixed(3),dq,LEN:L,crown:up(crown),sole:up(sole+1),chin:up(chinY),notch:up(nf),c7:up(nbk),nape:up(nape),acromion:up(arm),joint:up(shY),
   neckW:+nw.toFixed(2),chest:+((front(cy)-back(cy))/S).toFixed(2),head:+(up(crown)-up(chinY)).toFixed(2)};}''' % S


def hooked(src_text, tag, tmp):
    """a copy of a build with the measuring hooks; returns its file name"""
    s = src_text
    i = s.find('window.__HK={')
    assert i > 0
    s = s[:i] + EXPORT + s[i:]
    a = 'const arm=(sh,e,h,base,shade,a,G)=>{'
    assert a in s
    s = s.replace(a, a + 'if(window.__NOARM)return;', 1)
    for q in ('BT(NP,nk,nw,', 'BS(NP);'):
        if q in s:
            s = s.replace(q, 'if(!window.__NONECK)' + q, 1)
    q = "ctx.fillStyle=D('skin');ctx.fill(NP);"
    if q in s:  # (round 22c's neck)
        s = s.replace(q, 'if(!window.__NONECK){' + q, 1).replace('ctx.fill(NKP(O._lx,O._ly,2.3));}}}', 'ctx.fill(NKP(O._lx,O._ly,2.3));}}}}', 1)
    b = 'BS(FA.path);BS(FA.hp);'
    assert b in s
    s = s.replace(b, 'if(!window.__NOARM){BS(FA.path);BS(FA.hp);}', 1)
    fn = os.path.join(tmp, '_r22c_%s.html' % tag)
    open(fn, 'w', encoding='utf-8').write(s)
    return fn


def derive(m):
    """the scale-free ratios"""
    d = dict(m)
    d['chin_acr'] = m['chinG'] - m['acrG']
    d['chin_notch'] = m['chinG'] - m['notch']
    d['chin_joint'] = m['chin'] - m['joint']
    d['acr_joint'] = m['acrG'] - m['joint']
    d['c7_under_chin'] = m['chinG'] - m['c7']
    d['R_c7_trunk'] = d['c7_under_chin'] / m['notch']
    d['R_back_trunk'] = (m['nape'] - m['c7']) / m['notch']
    d['neck_back'] = m['nape'] - m['c7']
    d['neckDepth'] = m['neckW']
    d['height'] = m['crown'] - m['sole']
    d['heads'] = d['height'] / m['head']
    d['R_neck_trunk'] = d['chin_acr'] / m['acrG']            # chin-acromion / acromion-trochanter
    d['R_notch_trunk'] = d['chin_notch'] / m['notch']            # chin-suprasternale / suprasternale-trochanter
    d['R_neckD_chest'] = d['neckDepth'] / m['chest']
    d['R_neckD_head'] = d['neckDepth'] / m['head']                # neck depth / head height (chin to crown)
    d['R_len_width'] = d['chin_notch'] / d['neckDepth']
    d['R_trunk_leg'] = m['acrG'] / (-m['sole'])
    return d


# ANSUR II (US Army 2012, public data), the men aged 17-20 (n 422, means as derived in round 22b from the public file); chin from stature
# less the head's height (tragion to the top of the head plus tragion to menton, about 228 mm). Neck depth: the neck's circumference over pi
# (a near round neck): 381/pi.
ANSUR = {'stature': 1753, 'chin': 1525, 'cervicale': 1510, 'acromion': 1431, 'suprasternale': 1432, 'trochanter': 900, 'neckC': 381, 'neckCb': 419,
         'chest': 236, 'headL': 199, 'headH': 228, 'tragionTop': 132}


def ansur_ratios():
    A = ANSUR
    nd = A['neckC'] / 3.14159
    return {'R_neck_trunk': (A['chin'] - A['acromion']) / (A['acromion'] - A['trochanter']),
            'R_notch_trunk': (A['chin'] - A['suprasternale']) / (A['suprasternale'] - A['trochanter']),
            'R_neckD_chest': nd / A['chest'], 'R_neckD_head': nd / A['headH'], 'R_len_width': (A['chin'] - A['suprasternale']) / nd,
            'R_trunk_leg': (A['acromion'] - A['trochanter']) / A['trochanter'], 'neckD_mm': nd,
            'R_c7_trunk': (A['chin'] - A['cervicale']) / (A['suprasternale'] - A['trochanter']),
            'R_back_trunk': (A['stature'] - A['tragionTop'] - 25 - A['cervicale']) / (A['suprasternale'] - A['trochanter'])}  # (the nape: the mastoid's level, about 25 mm under tragion; an estimate)


def measure(browser, builds, tmp):
    """builds: [(tag, html text)] -> {tag: measures}"""
    out = {}
    for tag, txt in builds:
        fn = hooked(txt, tag, tmp)
        pg = browser.new_page()
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto('file://' + fn)
        pg.wait_for_timeout(500)
        raw = pg.evaluate(MEASURE)
        out[tag] = derive(raw)
        out[tag]['errors'] = errs
        pg.close()
    return out


if __name__ == '__main__':
    import sys
    from playwright.sync_api import sync_playwright
    files = sys.argv[1:] or [os.path.join(HERE, '..', '..', '..', '..', '..', 'dev', 'tools', 'hk_v69_release.html'), os.path.join(HERE, '..', 'hourglass-keep.html')]
    tmp = tempfile.mkdtemp(prefix='r22c', dir=HERE)
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            R = measure(b, [(os.path.basename(f), open(f, encoding='utf-8').read()) for f in files], tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print('ANSUR', {k: round(v, 3) for k, v in ansur_ratios().items()})
    for k, v in R.items():
        print(k, json.dumps({a: (round(b, 3) if isinstance(b, float) else b) for a, b in v.items()}))
