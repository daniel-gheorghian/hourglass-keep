# egyptr20b.py [new.html] [old.html] [outdir]: round 20b's pictures and numbers for egypt_themes.html, before (old.html, default the v67 release,
# hk_v67_release.html here or in the main checkout's dev/tools) and after:
#  r20b_prince.png  the prince on all fours with his blade drawn low (crouch + Grab), in the game (crops of the 1704 px canvas, both modes, and
#                   Torchlight at GLP.rs 0.5), then the figure drawn alone at 6x: crawling, the low blade, the blade in the fight's poses, on a
#                   pale floor's colour and a dark wall's
#  r20b_slab.png    a granite portcullis that is down near two lamps, Torchlight at rs 0.5 (the owner's phone): a strip of consecutive frames at
#                   30 fps before and after, and a chart of the mean brightness of its narrow face and its broad face frame by frame
#  r20b_blade.png   Classic: a slicer's blades in a sky beam, their shadow down the beam, before, round 20a (its build as a 4th argument) and after
# The slabs are found by replaying round 20a's key light (the nearest lamp within 1.6 times its flickering radius) on floors 5 to 12, seeds
# 1 to 3, and taking the ones where it changes side within 30 frames. Writes r20b.json (cases, flips per build, errors). Run from dev/tools.
import io, json, os, sys
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw
import egyptr12 as R12
import egyptr20a as R20
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
NEW = os.path.abspath(a[0] if len(a) > 0 else os.path.join(HERE, '..', 'hourglass-keep.html'))
_old = os.path.join(HERE, 'hk_v67_release.html')
if not os.path.exists(_old):
    _old = os.path.join(HERE, '..', '..', '..', '..', '..', 'dev', 'tools', 'hk_v67_release.html')  # (from a worktree: the main checkout's)
OLD = os.path.abspath(a[1] if len(a) > 1 else _old)
OUT = a[2] if len(a) > 2 else os.path.join(HERE, 'egypt_themes')
R20A = os.path.abspath(a[3]) if len(a) > 3 else None  # (round 20a's build, git show 22af63e:dev/hourglass-keep.html: the hard shadow wedge, for the blade sheet)
R12.OUT = OUT
TAG = {'old': 'before (v67)', 'new': 'after (20b)'}
# ---- 1: the prince on all fours, the blade drawn low
CRAWL = r'''([n,sd,ph,sw,rs])=>{const H=__HK;const L=__P.load(n,sd);let pc=-1,r=-1;
 for(let rr=1;rr<L.rows&&pc<0;rr++)for(let c=12;c<L.cols-12;c++){let ok=true;for(let k=-3;k<=4;k++)if(!H.solidBelow(c+k,rr)||L.feat[rr*L.cols+c+k])ok=false;if(ok){pc=c;r=rr;break;}}
 __P.stand(pc,r,1);const P=H.P;for(let i=0;i<30;i++){P.state='crouch';P.ph=ph;P.lowSword=sw;H.tick(1);P.x=pc*32+16;}
 P.state='crouch';P.ph=ph;P.lowSword=sw;if(H.GLP)H.GLP.rs=rs;__P.draw();return __P.scr(pc*32+24,(r+1)*64-16);}'''
FIG = r'''([kind,bg,S])=>{const H=__HK,mk=H.mk,cr=ph=>{const a=ph*6.2832,s=Math.sin(a);return mk({lean:1.36,head:-0.95,hF:0.28+0.22*s,kF:1.78+0.1*s,hB:0.1-0.22*s,kB:1.66-0.1*s,aF:0.06-0.28*s,eF:-0.25,aB:-0.02+0.28*s,eB:-0.2,kn:1});};
 let p,sw=false,W=46,Hh=32,x=18,y=29;
 if(kind==='crawl')p=cr(0.5);else if(kind==='low'){p=cr(0.1);p.aF=0.55;p.eF=-0.45;p.sw=0.03;sw=true;}else if(kind==='poke'){p=cr(0);p.aF=1.45;p.eF=0;p.sw=0.03;sw=true;}
 else{p=H.PS[kind];sw=true;W=46;Hh=40;x=10;y=46;}
 const cv=document.createElement('canvas');cv.width=W*S;cv.height=Hh*S;const c=cv.getContext('2d');c.fillStyle=bg;c.fillRect(0,0,cv.width,cv.height);c.scale(S,S);
 H.figDraw(c,x,y,1,p,H.PAL_HERO,{sword:sw,hasSword:true,time:0,lt:{dir:1,col:'255,220,170',k:0.5}});return cv.toDataURL('image/png');}'''
# ---- 2: the slab's key light, as round 20a chose it, replayed frame by frame on the new build's light list (to find the cases)
FINDSLAB = r'''([n,sd,N])=>{const H=__HK,L=__P.load(n,sd),out=[];
 const old=(x,y)=>{let best=null,bd=1e9;for(const q of H.frameLights){if(q.kind==='fill'||q.kind==='trap'||q.kind==='sky')continue;const d=Math.hypot(q.x-x,q.y-(y-26));if(d<bd&&d<q.r*1.6){bd=d;best=q;}}return best?Math.sign(best.x-x)||1:-1;};
 for(const o of L.dyn){if(o.f.t!=='gate'||o.c<12||o.c>L.cols-12)continue;const c=o.c,r=o.r;let pc=-1;for(const d of [-5,5,-6,6,-4,4])if(H.solidBelow(c+d,r)&&!L.feat[r*L.cols+c+d]){pc=c+d;break;}if(pc<0)continue;
   __P.stand(pc,r,1);const x=c*32+16-8+8,y=r*64+32;let f1=0,f2=0,p1=null,p2=null;
   for(let i=0;i<N;i++){H.tick(2);const P=H.P;P.x=pc*32+16;P.y=(r+1)*64-4;P.state='stand';P.vx=P.vy=0;o.f.open=0;o.f.tm=0;H.cam.x=c*32+16-H.viewW/2;H.cam.y=r*64-110;H.cam.gy=H.cam.y;H.render();
     const d1=old(x,y),d2=H.keyLight(x,y).dir;if(p1!==null&&d1!==p1)f1++;if(p2!==null&&d2!==p2)f2++;p1=d1;p2=d2;}
   out.push({n,sd,c,r,pc,flipsOld:f1,flipsNew:f2,name:H.themeName(n)});}
 return out;}'''
# consecutive frames of one slab at 30 fps (two game steps a frame), the mean brightness of its narrow face and its broad face per frame
# (Rec. 601 luma of the composited canvases over two boxes inside the faces), and crops of the first frames
SLAB = r'''([q,rs,N,K])=>{const H=__HK,L=__P.load(q.n,q.sd),o=L.dyn.find(o=>o.f.t==='gate'&&o.c===q.c&&o.r===q.r);__P.stand(q.pc,q.r,1);
 const X=q.c*32,Y=q.r*64,cvs=()=>[...document.querySelectorAll('canvas')].filter(c=>c.getBoundingClientRect().width>0&&c.width>800),g=document.createElement('canvas'),gx=g.getContext('2d',{willReadFrequently:true});
 const nar=[],brd=[],img=[];
 for(let i=0;i<N;i++){H.tick(2);const P=H.P;P.x=q.pc*32+16;P.y=(q.r+1)*64-4;P.state='stand';P.vx=P.vy=0;o.f.open=0;o.f.tm=0;if(H.GLP)H.GLP.rs=rs;
   H.cam.x=X+16-H.viewW/2;H.cam.y=Y-110;H.cam.gy=H.cam.y;H.render();const XF=H.XF,cs=cvs(),W=cs[0].width;
   const px=(wx,wy)=>[Math.round(wx*XF.VZ-XF.camD),Math.round(wy*XF.VZ-XF.camDY)];
   const [bx0,by0]=px(X-20,Y-14),[bx1,by1]=px(X+52,Y+60),bw=bx1-bx0,bh=by1-by0;g.width=bw;g.height=bh;gx.clearRect(0,0,bw,bh);for(const c of cs)if(c.width===W)gx.drawImage(c,bx0,by0,bw,bh,0,0,bw,bh);
   const d=gx.getImageData(0,0,bw,bh).data,mean=(x0,y0,x1,y1)=>{const [a0,b0]=px(x0,y0),[a1,b1]=px(x1,y1);let s=0,n=0;for(let y=b0-by0;y<b1-by0;y++)for(let x=a0-bx0;x<a1-bx0;x++){const k=(y*bw+x)*4;s+=0.299*d[k]+0.587*d[k+1]+0.114*d[k+2];n++;}return n?s/n:0;};
   nar.push(+mean(X+6.5,Y+18,X+9.5,Y+48).toFixed(2));brd.push(+mean(X+15,Y+16,X+25,Y+44).toFixed(2));if(i<K)img.push(g.toDataURL('image/png'));}
 return {nar,brd,img};}'''


def dataimg(d):
    import base64
    return Image.open(io.BytesIO(base64.b64decode(d.split(',')[1]))).convert('RGB')


def chart(series, w=560, h=150, lo=None, hi=None, title=''):
    # series: [(label, values, colour)]; a plain line chart, frames along x, mean brightness (0..255 luma) up
    vals = [v for _, s, _ in series for v in s]
    lo = min(vals) - 4 if lo is None else lo
    hi = max(vals) + 4 if hi is None else hi
    im = Image.new('RGB', (w, h), (26, 22, 30)); dr = ImageDraw.Draw(im)
    L, Rr, T, B = 34, 8, 16, 18
    n = max(len(s) for _, s, _ in series)
    X = lambda i: L + (w - L - Rr) * i / max(1, n - 1)
    Y = lambda v: T + (h - T - B) * (1 - (v - lo) / max(1e-6, hi - lo))
    for k in range(5):
        v = lo + (hi - lo) * k / 4; dr.line([(L, Y(v)), (w - Rr, Y(v))], fill=(52, 46, 58)); dr.text((2, Y(v) - 6), '%d' % round(v), fill=(150, 140, 130))
    for i in range(0, n, 10):
        dr.text((X(i) - 4, h - B + 4), str(i), fill=(150, 140, 130))
    for j, (lab, s, col) in enumerate(series):
        dr.line([(X(i), Y(v)) for i, v in enumerate(s)], fill=col, width=2)
        dr.text((L + 6 + j * 170, 2), lab, fill=col)
    dr.text((w - 8 - 7 * len(title), 2), title, fill=(230, 220, 205))
    return im


def jumps(s):
    return round(sum(abs(s[i] - s[i - 1]) for i in range(1, len(s))) / max(1, len(s) - 1), 2)


if __name__ == '__main__':
    J = {'errors': [], 'slabs': [], 'num': []}
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
        P = {(v, m): R12.page(b, src, m) for v, src in (('old', OLD), ('new', NEW)) for m in ('torch', 'classic')}
        if R20A:
            P[('r20a', 'classic')] = R12.page(b, R20A, 'classic'); TAG['r20a'] = 'round 20a'
        for pg in P.values():
            pg.evaluate("()=>{__HK.EGP.traps=true;}")
        # ---- 1. the prince on all fours
        rows = []
        for n, ph in ((7, 0.5), (3, 0.1)):
            t = []
            for m, rs in (('torch', 1), ('torch', 0.5), ('classic', 1)):
                for v in ('old', 'new'):
                    xy = P[(v, m)].evaluate(CRAWL, [n, 1, ph, True, rs])
                    t.append(R12.label(R12.crop(R12.shot(P[(v, m)]), (xy[0] + 8, xy[1]), 250, 130), '%s, floor %d, %s%s' % (TAG[v], n, m, ', rs .5' if rs < 1 else '')))
            rows.append(R12.grid(t, 6))
        figs = []
        for kind in ('crawl', 'low', 'poke'):
            for v in ('old', 'new'):
                figs.append(R12.label(dataimg(P[(v, 'classic')].evaluate(FIG, [kind, '#c9a06c', 6])), '%s, %s, 6x' % (TAG[v], kind), (4, 3)))
        rows.append(R12.grid(figs, 6))
        figs = []
        for kind in ('garde', 'lunge', 'windup'):
            for bg in ('#c9a06c', '#2a2018'):
                for v in ('old', 'new'):
                    figs.append(R12.label(dataimg(P[(v, 'classic')].evaluate(FIG, [kind, bg, 4])), '%s, %s' % (TAG[v], kind), (4, 3)))
        rows.append(R12.grid(figs, 12))
        R12.stack(rows).save(os.path.join(OUT, 'r20b_prince.png'))
        print('prince done', flush=True)
        # ---- 2. the slab: find the flipping ones
        found = []
        pn = P[('new', 'classic')]
        for n in range(5, 13):
            for sd in (1, 2, 3):
                for q in pn.evaluate(FINDSLAB, [n, sd, 30]):
                    J['slabs'].append(q)
                    if q['flipsOld']:
                        found.append(q)
        found.sort(key=lambda q: -q['flipsOld'])
        print('slabs', len(J['slabs']), 'flipping before', len(found), 'after', sum(1 for q in J['slabs'] if q['flipsNew']), flush=True)
        cases = found[:2]
        rows = []
        for q in cases:
            res = {}
            for v in ('old', 'new'):
                for rs in (0.5, 1):
                    res[(v, rs)] = P[(v, 'torch')].evaluate(SLAB, [q, rs, 60, 10 if rs == 0.5 else 0])
            num = {'n': q['n'], 'sd': q['sd'], 'c': q['c'], 'name': q['name']}
            for (v, rs), r in res.items():
                num['%s_rs%s' % (v, rs)] = {'narrow': jumps(r['nar']), 'broad': jumps(r['brd']), 'nmin': min(r['nar']), 'nmax': max(r['nar']), 'bmin': min(r['brd']), 'bmax': max(r['brd'])}
            J['num'].append(num); print(num, flush=True)
            strip = []
            for v in ('old', 'new'):
                ims = [dataimg(d) for d in res[(v, 0.5)]['img']]
                strip.append(R12.label(R12.grid(ims, len(ims), 1), '%s, %s, floor %d, Torchlight rs .5, 10 frames at 30 fps' % (TAG[v], q['name'][:24], q['n'])))
            allv = [x for r in res.values() for x in r['nar'] + r['brd']]
            lo, hi = min(allv) - 4, max(allv) + 4
            ch = [chart([('narrow face', res[(v, 0.5)]['nar'], (255, 170, 80)), ('broad face', res[(v, 0.5)]['brd'], (120, 170, 255))], lo=lo, hi=hi, title=TAG[v] + ', rs .5') for v in ('old', 'new')]
            rows.append(R12.stack([R12.stack(strip, 2), R12.grid(ch, 2)], 2))
        if rows:
            R12.stack(rows).save(os.path.join(OUT, 'r20b_slab.png'))
        # ---- 3. Classic: a slicer's shadow down a beam (round 20a's cases)
        F = P[('new', 'torch')].evaluate(R20.FIND, [3, 30, [1, 2, 3, 4]])
        jaw, seen = [], set()
        for q in F['jaw']:
            if q['name'] not in seen:
                seen.add(q['name']); jaw.append(q)
            if len(jaw) == 2:
                break
        t = []
        for q in jaw:
            q.update(pc=-1, x=q['c'] * 32 + 16, y=q['r'] * 64 + 10)
            for v in ('old', 'r20a', 'new') if R20A else ('old', 'new'):
                t.append(R20.tile(P[(v, 'classic')], q, 1, 300, 320, '%s, Classic, %s' % (q['name'][:20], TAG[v])))
        R12.grid(t, 6 if R20A else 4).save(os.path.join(OUT, 'r20b_blade.png'))
        for pg in P.values():
            J['errors'] += pg.errs
        json.dump(J, open(os.path.join(OUT, 'r20b.json'), 'w'), indent=1)
        print('errors', J['errors'][:4])
        b.close()
