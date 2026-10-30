# egyptr49b.py old.html new.html [outdir]: round 49b's pictures (owner after the round 49 research: "rely only on subtle graphic hints").
#   r49b_tells_3x.png     each tell (reach, edge, stakes, flask, low, chim) after 1.2 s standing still: old | new, Torchlight and Classic, 3x
#   r49b_tells_phone.png  the reach and the low tunnel at phone size (852 x 393), old | new, Torchlight
#   r49b_reach.gif        the reach easing in, held, then Up pressed (the jump up takes over at once), new, Torchlight, 3x crop
#   r49b_grit_3x.png      the grit over a slab's plate, old | new at three moments, both modes, 3x
#   r49b_grit_phone.png   the same at phone size, Torchlight
#   r49b_grit.gif         4 s of the grit (new, Torchlight, 3x crop), then the slab let go: the grit stops
#   r49b_swing.png        the swing's beat: his angle against time, a press each way after each turn from a still hang (swingtest's cue
#                         run, then a press at each bottom the way he comes back: armed through the turn), each turn's beat marked by its loudness (armed: brighter), the pumps and the ready chime; r49b_swing.txt the log
# Run from dev/tools (any copy of dev/). GPU flags for Torchlight (HK_GPU=0 for software).
import io, os, sys, json
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright
a = sys.argv[1:]
OLD, NEW = os.path.abspath(a[0]), os.path.abspath(a[1])
OUT = os.path.abspath(a[2]) if len(a) > 2 else os.path.dirname(os.path.abspath(__file__))
GPU = [] if os.environ.get('HK_GPU') == '0' else ['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist', '--force_high_performance_gpu']
VW, VH, DSF = 852, 393, 3

PREP = r'''(mode)=>{const H=__HK;window.__HKfreeze=true;window.__HKnoauto=true;H.S.set.lightMode=mode;H.S.set.cross=false;if(H.GLFX)H.GLFX.sheen=false;
  for(const id in H.HINTS){H.S.hints[id]=1;if(H.S.learned)H.S.learned[id]=1;}
  document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.body.classList.remove('panelOpen');
  const st=document.createElement('style');st.textContent='.ctl,#pause,#pauseBtn,#pad{display:none!important}';document.head.appendChild(st);return 1;}'''
# a spot for each tell (the new build's tellKind; the chimney from a kick shaft's foot)
FIND = r'''([lo,hi])=>{const H=__HK,TW=32,S=r=>(r+1)*64-4,out={};
 for(let n=lo;n<=hi;n++){const sd=4400+n;const L=H.load(n,sd,false);const P=H.P;
  for(let r=1;r<L.rows-1;r++)for(let c=2;c<L.cols-2;c++){if(H.B(c,r)===H.WALL||!H.solidBelow(c,r)||H.F(c,r))continue;
   if(L.guards.some(g=>Math.abs(g.c-c)<8&&g.r===r))continue;
   for(const fc of [1,-1]){P.x=c*TW+16+fc*8;P.y=S(r);P.face=fc;const k=H.tellKind();if(k&&!out[k])out[k]=[n,sd,c,r,fc];}}
  if(!out.chim)for(const q of L.path)if(q.a==='walljump'){let rf=-1;for(let r=0;r<L.rows;r++){const f=H.F(q.from,r);if(f&&f.t==='shaftfoot')rf=r;}if(rf>0&&H.chimFoot(q.from,rf)){out.chim=[n,sd,q.from,rf,q.dir||1];break;}}}
 return out;}'''
# stand him there and let 1.2 s pass (or, in the chimney, go in with Up and wait in the first stance)
SETUP = r'''([k,n,sd,c,r,fc,T])=>{const H=__HK,TW=32,S=r=>(r+1)*64-4;const L=H.load(n,sd,false);H.banner=null;H.mode='play';H.intro=0;
  for(const e of H.G)e.x=-9999;for(const e of H.SN)e.x=-9999;for(const q of ['l','r','u','d','j','g'])H.setKey('kb',q,false);
  const P=H.P;P.x=c*TW+16+(k==='chim'?0:fc*8);P.y=S(r);P.fallY=P.y;P.face=fc;P.state='stand';P.vx=P.vy=0;P.inv=1e9;P.t=0;H.cam.snap=true;H.tick(1);
  if(k==='chim'){H.setKey('kb','u',true);H.tick(1);H.setKey('kb','u',false);let f=0;while(f<240&&!(P.lock&&P.plant&&P.plant.y==null))f++,H.tick(1);}
  H.tick(Math.round(T*60));return [P.x,P.y,P.state,H.TELL?H.TELL.k:null,H.TELL?+H.TELL.w.toFixed(2):null];}'''
CAM = r'''([fx,fy,gt])=>{const H=__HK;if(gt!=null){H.setClock(()=>1e6);H.setGT(gt);}H.clearRooms();H.cam.x=fx-H.viewW/2;H.cam.y=fy-192*0.55;H.cam.gy=H.cam.y;
  if(H.GLP){H.GLP.pipe=false;H.GLP.rs=1;}for(let i=0;i<3;i++)H.render();
  const XF=H.XF,cv=[...document.querySelectorAll('canvas')].find(c=>c.getBoundingClientRect().width>0),R=cv.getBoundingClientRect(),k=XF.VZ/cv.width*R.width;
  return [R.left-XF.camD/cv.width*R.width,R.top-XF.camDY/cv.height*R.height,k];}'''
GRITF = r'''([lo,hi])=>{const H=__HK;for(let n=lo;n<=hi;n++)for(const sd of [700000+97*n+13,4400+n]){H.load(n,sd,false);const g=H.gritList();if(g.length)return [n,sd,g[0].c,g[0].r0,g[0].r1];}return null;}'''
GRITS = r'''([n,sd,drop])=>{const H=__HK;H.load(n,sd,false);H.banner=null;H.mode='play';H.intro=0;const P=H.P;P.x=-999;P.y=-999;P.state='dead';
  for(const e of H.G)e.x=-9999;for(const e of H.SN)e.x=-9999;if(drop&&H.gritList)H.gritList()[0].o.f.s=2;return 1;}'''


def label(im, t):
    d = ImageDraw.Draw(im); d.rectangle((0, 0, 8 + 6 * len(t), 13), fill=(0, 0, 0)); d.text((4, 1), t, fill=(250, 240, 215)); return im


def crop(pg, fx, fy, bw, bh, gt=None, whole=False):
    q = pg.evaluate(CAM, [fx, fy, gt]); im = Image.open(io.BytesIO(pg.screenshot())).convert('RGB')
    if whole: return im.resize((VW, VH), Image.LANCZOS)
    k = q[2] * DSF; x0, y0 = q[0] * DSF + (fx - bw / 2) * k, q[1] * DSF + (fy - bh / 2) * k
    return im.crop((int(x0), int(y0), int(x0 + bw * k), int(y0 + bh * k))).resize((bw * 3, bh * 3), Image.LANCZOS)


def grid(rows, gap=8, bg=(20, 16, 24)):
    w = sum(i.width for i in rows[0]) + gap * (len(rows[0]) - 1); h = sum(r[0].height for r in rows) + gap * (len(rows) - 1)
    im = Image.new('RGB', (w, h), bg); y = 0
    for r in rows:
        x = 0
        for c in r: im.paste(c, (x, y)); x += c.width + gap
        y += r[0].height + gap
    return im


KINDS = ['reach', 'edge', 'stakes', 'flask', 'low', 'chim']
with sync_playwright() as p:
    b = p.chromium.launch(args=GPU); pages = {}; errs = []
    for nm, src in (('old', OLD), ('new', NEW)):
        for mode in ('torch', 'classic'):
            pg = b.new_page(viewport={'width': VW, 'height': VH}, device_scale_factor=DSF); pg.on('pageerror', lambda e: errs.append(str(e)))
            pg.goto('file://' + src); pg.wait_for_timeout(700); pg.evaluate(PREP, mode); pages[(nm, mode)] = pg
    NP = pages[('new', 'torch')]
    cases = NP.evaluate(FIND, [3, 16]); print('cases', cases, flush=True)
    info = {}
    # the tells, 3x
    BW, BH = 150, 96; rows = []
    for k in KINDS:
        if k not in cases: continue
        n, sd, c, r, fc = cases[k]; row = []
        for mode in ('torch', 'classic'):
            for nm in ('old', 'new'):
                pg = pages[(nm, mode)]; st = pg.evaluate(SETUP, [k, n, sd, c, r, fc, 1.2]); info[k + '/' + nm + '/' + mode] = st
                im = crop(pg, st[0], st[1] - 34, BW, BH); row.append(label(im, '%s %s fl%d %s' % (k, 'v89+48/49a' if nm == 'old' else 'round 49b', n, mode)))
        rows.append(row); print(k, info[k + '/new/torch'], flush=True)
    grid(rows).save(os.path.join(OUT, 'r49b_tells_3x.png'))
    # phone size
    ph = []
    for k in ('reach', 'low'):
        if k not in cases: continue
        n, sd, c, r, fc = cases[k]; row = []
        for nm in ('old', 'new'):
            pg = pages[(nm, 'torch')]; st = pg.evaluate(SETUP, [k, n, sd, c, r, fc, 1.2]); row.append(label(crop(pg, st[0], st[1] - 40, 0, 0, whole=True), '%s %s' % (k, 'before' if nm == 'old' else 'round 49b')))
        ph.append(row)
    grid(ph, 6).save(os.path.join(OUT, 'r49b_tells_phone.png'))
    # the reach: easing in, held, then Up
    if 'reach' in cases:
        n, sd, c, r, fc = cases['reach']; pg = NP; st = pg.evaluate(SETUP, ['reach', n, sd, c, r, fc, 0]); fr = []
        for i in range(70):
            if i == 55: pg.evaluate("()=>{__HK.setKey('kb','u',true);}")
            if i == 57: pg.evaluate("()=>{__HK.setKey('kb','u',false);}")
            q = pg.evaluate("()=>{__HK.tick(2);const T=__HK.TELL;return [__HK.P.state,T.k,+T.w.toFixed(2),+__HK.P.t.toFixed(2)];}")
            fr.append(label(crop(pg, st[0], st[1] - 40, 120, 90), '%s %s w%.2f' % (q[0], q[1], q[2])).resize((240, 180), Image.LANCZOS))
        fr[0].save(os.path.join(OUT, 'r49b_reach.gif'), save_all=True, append_images=fr[1:], duration=33, loop=0)
    # the grit
    g = NP.evaluate(GRITF, [3, 20]); print('grit', g, flush=True)
    if g:
        n, sd, c, r0, r1 = g; fx, fy = c * 32 + 16, (r0 + r1 + 2) / 2 * 64 - 4; rows = []
        for mode in ('torch', 'classic'):
            row = []
            for nm in ('old', 'new'):
                pg = pages[(nm, mode)]; pg.evaluate(GRITS, [n, sd, False])
                for gt in (10.37, 11.1, 12.6):
                    row.append(label(crop(pg, fx, fy, 110, 190, gt), '%s %s t%.1f' % ('before' if nm == 'old' else '49b', mode, gt)))
            rows.append(row)
        grid(rows).save(os.path.join(OUT, 'r49b_grit_3x.png'))
        ph = []
        for nm in ('old', 'new'):
            pg = pages[(nm, 'torch')]; pg.evaluate(GRITS, [n, sd, False]); ph.append(label(crop(pg, fx, fy, 0, 0, 11.1, whole=True), 'grit %s' % ('before' if nm == 'old' else 'round 49b')))
        grid([ph], 6).save(os.path.join(OUT, 'r49b_grit_phone.png'))
        pg = NP; pg.evaluate(GRITS, [n, sd, False]); fr = []
        for i in range(150):
            if i == 120: pg.evaluate(GRITS, [n, sd, True])
            fr.append(label(crop(pg, fx, fy, 70, 180, 20 + i / 30), 'grit t%.2f%s' % (i / 30, ' slab gone' if i >= 120 else '')).resize((140, 360), Image.LANCZOS))
        fr[0].save(os.path.join(OUT, 'r49b_grit.gif'), save_all=True, append_images=fr[1:], duration=33, loop=0)
    # the swing's beat (new): swingtest's cue run from a still hang, the sounds logged
    SW = r'''(n)=>{const H=__HK;let L=null,o=null,SD=0;for(let sd=1;sd<=25&&!o;sd++){SD=7100+sd;L=H.load(n,SD,true);H.banner=null;o=L.dyn.find(q=>q.f.t==='bar');}
     if(!o)return null;const f=o.f,D=L.base[o.r*L.cols+o.c+2]===L.base[o.r*L.cols+o.c]?1:-1,FW=D>0?'r':'l',BK=D>0?'l':'r',P=H.P;H.mode='play';
     const snd=[],pl=H.Snd.play.bind(H.Snd);H.Snd.play=nm=>{snd.push([H.gameTime,nm,nm==='swbeat'?[+H.SWB.k.toFixed(3),H.SWB.arm]:null]);return pl(nm);};
     for(const q of ['l','r','j','d','u','g'])H.setKey('kb',q,false);P.x=f.x;P.y=f.y+57;P.vx=0;P.vy=0;P.state='air';P.autoGrab=true;P.face=D;P.fallY=P.y;P.inv=1e9;f.ps=0;f.pw=0;H.tick(1);
     P.swTh=0;P.swOm=0;H.SWB.log=[];const t0=H.gameTime,tr=[];let k=0,want=0,last=0,due=[[1,1]];
     let lth=0,bw=0,bk=0;
     while(k<540){const om=P.swOm,sg=Math.abs(om)>0.05?Math.sign(om):0;if(k<200){if(sg&&sg!==last){last=sg;due.push([k+12,sg]);}while(due.length&&due[0][0]<=k)want=due.shift()[1];}
       else if(k<400){const th=P.swTh;if(lth&&Math.sign(th)!==Math.sign(lth)&&sg){bw=-sg;bk=k+8;}lth=th;want=k<bk?bw:0;} // (then a press at each bottom, the way he will come back: armed through the turn)
       else want=0;H.setKey('kb',FW,want>0);H.setKey('kb',BK,want<0);H.tick(1);k++;tr.push([+(H.gameTime-t0).toFixed(3),+P.swTh.toFixed(4),P.swArm,want,P.swRdy?1:0]);}
     for(const q of ['l','r'])H.setKey('kb',q,false);H.Snd.play=pl;const lg=H.SWB.log;H.SWB.log=null;
     return {n,seed:SD,t0,tr,beats:lg.map(q=>[+(q[0]-t0).toFixed(3),+q[1].toFixed(3),q[2]]),snd:snd.map(q=>[+(q[0]-t0).toFixed(3),q[1],q[2]])};}'''
    sw = None
    for n in range(6, 20):
        sw = NP.evaluate(SW, n)
        if sw: break
    if sw:
        W, H, ml = 1100, 420, 50; im = Image.new('RGB', (W, H), (250, 248, 242)); d = ImageDraw.Draw(im); T = sw['tr'][-1][0]
        X = lambda t: ml + (W - ml - 20) * t / T; Y = lambda th: 150 - th * 110
        d.line((ml, Y(0), W - 20, Y(0)), fill=(200, 196, 190))
        for i in range(-1, 2): d.text((4, Y(i * 0.6) - 6), '%+.1f' % (i * 0.6), fill=(90, 90, 90))
        pts = [(X(q[0]), Y(q[1])) for q in sw['tr']]; d.line(pts, fill=(40, 60, 120), width=2)
        for q in sw['tr']:
            if q[3]: d.line((X(q[0]), 300 + (0 if q[3] > 0 else 8), X(q[0]), 306 + (0 if q[3] > 0 else 8)), fill=(120, 120, 120))
        for t, nm, ex in sw['snd']:
            x = X(t)
            if nm == 'swbeat':
                kk, arm = ex; vol = 0.022 + 0.012 * kk + 0.006 * arm; h = int(vol / 0.05 * 90); col = (214, 120, 30) if arm else (150, 110, 70)
                d.rectangle((x - 3, 400 - h, x + 3, 400), fill=col)
            elif nm == 'swpump': d.line((x, 318, x, 400), fill=(60, 150, 90), width=2)
            elif nm == 'swready': d.rectangle((x - 3, 400 - 90, x + 3, 400), outline=(200, 40, 40), width=2)
        d.text((ml, 8), 'round 49b, the swing\'s beat: floor %d seed %d, 0-3.3 s a press 0.2 s after each turn from a still hang; 3.3-6.7 s a press at each bottom the way he will come back (armed through the turn); then none' % (sw['n'], sw['seed']), fill=(0, 0, 0))
        d.text((ml, 22), 'blue: his angle (rad); grey ticks: the arrow held (upper forward, lower back); bars: each turn\'s beat by its volume (orange: a pump armed), green: a pump, red box: the ready chime (0.05)', fill=(0, 0, 0))
        im.save(os.path.join(OUT, 'r49b_swing.png'))
        with open(os.path.join(OUT, 'r49b_swing.txt'), 'w') as fh:
            fh.write('# t (s from the hang), name, [SWB.k, armed] for swbeat\n')
            for q in sw['snd']: fh.write('%.3f %s %s\n' % (q[0], q[1], q[2] or ''))
            fh.write('# beats: t, amplitude, armed\n')
            for q in sw['beats']: fh.write('%.3f %.3f %d\n' % tuple(q))
        print('swing', sw['n'], sw['seed'], 'beats', len(sw['beats']), 'armed', sum(q[2] for q in sw['beats']), 'sounds', sorted(set(q[1] for q in sw['snd'])), flush=True)
    json.dump({'cases': cases, 'info': info, 'grit': g}, open(os.path.join(OUT, 'r49b.json'), 'w'), indent=1)
    print('errors', errs[:5])
    b.close()
