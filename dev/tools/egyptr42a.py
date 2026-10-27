# egyptr42a.py old.html new.html [outdir] [measure] [floors=n:s,...]: round 42a's pictures and numbers (owner: "Kick shaft: great idea with
# the chimney pose. Research and let's implement"). The bot climbs a kick shaft (its own walljump action from the shaft's foot, as in play);
# every frame of the climb is the same in both builds (look only), so the same frame index is a phase of the climb in both.
# r42a_chimney.png: one row per phase (the jump in, each plant, push, flight, the arrival, the slide to the lip, the hang, the climb out),
#   columns old | new for Classic and Torchlight, crops round the shaft at 3x; then the phases side by side at phone size (dsf 3).
# r42a_chimney.gif: a whole climb in real time, new build, Classic | Torchlight, 3x.
# measure: the pixels of him cut by the shaft's walls (drawn past a wall's face at mid-depth: x < X beside a left wall, x > X+TW-HX beside a
#   right wall), every frame of the bot's climbs, by state, for both builds (a hang's or climb's ledge side is the approved hide: not counted).
# Run from dev/tools (Torchlight is software WebGL in headless Chromium unless HK_GPU=1).
import io, os, sys, json
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
H = [os.path.abspath(x) for x in a if x.endswith('.html')]
OLD, NEW = (H + [os.path.join(HERE, '..', 'hourglass-keep.html')] * 2)[:2] if len(H) != 1 else (H[0], H[0])
OUTD = next((x for x in a if not x.endswith('.html') and '=' not in x and x not in ('measure', 'quick', 'nogif', 'gifonly')), os.path.join(HERE, 'egypt_themes'))
FL = [tuple(int(v) for v in q.split(':')) for q in next((x[7:] for x in a if x.startswith('floors=')), '11:1,9:1,14:1,7:1,13:1').split(',')]
INK = (20, 16, 24)
BW, BH, ZK = 64, 100, 3
GPU = ['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'] if os.environ.get('HK_GPU') else []
MODES = [('Classic', 'classic'), ('Torchlight', 'torch')]

# the bot's walljump action from the shaft's foot; window.__G steps it one game tick at a time (S: every hint learned, guards away)
LOAD = r'''([n,s,i,tch])=>{const H=__HK;for(const id in H.HINTS){H.S.hints[id]=1;H.S.learned[id]=1;}const L=H.load(n,s,true);H.banner=null;
  const a=L.path.filter(a=>a.a==='walljump')[i];let rf=-1;for(let r=0;r<L.rows;r++){const f=H.F(a.from,r);if(f&&f.t==='shaftfoot')rf=r;}
  for(const e of H.G)e.x=-9999;H.mode='play';let q=12345;Math.random=()=>{q=(q*16807)%2147483647;return q/2147483647;};
  window.__A={c:a.from,rf,k:a.k,dir:a.dir||1};window.__G=botGen(n,s,{path:[a],at:{c:a.from,r:rf,face:a.dir||1}});window.__G.next();window.__f=0;
  if(tch){H.L.torches.length=0;H.L.torches.push({c:a.from,r:rf-a.k});H.clearRooms();} // (a lamp up the shaft: his shadow on its back wall)
  return window.__A;}'''
STEP = r'''(k)=>{const H=__HK;for(let i=0;i<k;i++){H.tick(1);const r=window.__G.next();window.__f++;if(r.done)return [window.__f,'done',H.P.state];}return [window.__f,H.P.state,H.P.plant?1:0,H.P.jumpKind];}'''
SHOW = r'''()=>{const H=__HK,A=window.__A;H.banner=null;if(!window.__pn)window.__pn=performance.now.bind(performance);let T=1e6+H.gameTime*1000;H.setClock(()=>T);
  const fx=A.c*32+12,fy=Math.round(H.P.y-30);H.cam.x=fx-H.viewW/2;H.cam.y=fy-192*0.55;H.cam.gy=fy;if(H.GLP){H.GLP.pipe=false;H.GLP.rs=1;window.__HKnoauto=true;}
  window.__HKfreeze=true;for(let i=0;i<3;i++)H.render();const X=H.XF,cv=[...document.querySelectorAll('canvas')].find(c=>c.getBoundingClientRect().width>0),R=cv.getBoundingClientRect(),k=X.VZ/cv.width*R.width;
  H.setClock(window.__pn);
  return [R.left-X.camD/cv.width*R.width,R.top-X.camDY/cv.height*R.height,k,fx,fy];}'''


def page(b, html, mode, dsf=3):
    pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=dsf)
    pg.errs = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e)))
    pg.goto('file://' + html)
    pg.wait_for_timeout(700)
    pg.add_script_tag(path=os.path.join(HERE, 'bot.js'))
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.body.classList.remove('panelOpen')")
    pg.evaluate("m=>{__HK.S.set.lightMode=m;window.__HKfreeze=true;}", mode)
    pg.dsf = dsf
    return pg


def shot(pg, zk=ZK, yc=None):
    q = pg.evaluate(SHOW)
    im = Image.open(io.BytesIO(pg.screenshot())).convert('RGB')
    d = pg.dsf
    ox, oy, k, fx, fy = q[0] * d, q[1] * d, q[2] * d, q[3], q[4]
    yc = fy if yc is None else yc
    x0, y0 = ox + (fx - BW / 2) * k, oy + (yc - BH * 0.5) * k
    c = im.crop((int(x0), int(y0), int(x0 + BW * k), int(y0 + BH * k)))
    return c if zk is None else c.resize((BW * zk, BH * zk), Image.LANCZOS)


def label(im, t):
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 8 + 6 * len(t), 13), fill=(0, 0, 0))
    d.text((4, 1), t, fill=(250, 240, 215))


MEASURE = r'''([n,s])=>{const H=__HK;const cv=document.createElement('canvas');cv.width=cv.height=300;const g=cv.getContext('2d');const SC=3,TW=32,HX=8,TH=64;
 let on=-1,sh=null;const tot={frames:0,cut:0,cutFrames:0,max:0,by:{}};
 const res=runBot(n,s,{stop:(H)=>{const P=H.P,L=H.L;const c=Math.floor(P.x/32);
   if(on<0){const a=L.path.find(a=>a.a==='walljump'&&a.from===c&&P.state==='air');if(a){on=1;sh=a;}}
   if(on>0){const x=P.x+(P.rdx||0),y=P.y+(P.rdy||0),face=P.dF||P.face,cc=sh.from,lg=P.hideMode?P.hideLg:null;
     g.setTransform(1,0,0,1,0,0);g.clearRect(0,0,300,300);g.setTransform(SC,0,0,SC,-SC*(x-50),-SC*(y-80));
     H.drawActor(g,P,x,y,face,P.pose,H.PAL_HERO,{yo:P.yo,hasSword:true,sword:false,time:0});
     const d=g.getImageData(0,0,300,300).data;let cut=0;
     for(let py=0;py<300;py++){const wy=y-80+py/SC,r=Math.floor(wy/TH);const lw=H.B(cc-1,r)===H.WALL&&!(lg&&lg.s>0),rw=H.B(cc+1,r)===H.WALL&&!(lg&&lg.s<0);
       for(let px=0;px<300;px++){if(d[(py*300+px)*4+3]<128)continue;const wx=x-50+px/SC;if((lw&&wx<cc*TW)||(rw&&wx>(cc+1)*TW-HX))cut++;}}
     cut/=SC*SC;const st=P.state+(P.plant?':plant':P.state==='air'&&P.jumpKind?':'+P.jumpKind:'');
     tot.frames++;tot.cut+=cut;if(cut>=1)tot.cutFrames++;tot.max=Math.max(tot.max,cut);const b=tot.by[st]||(tot.by[st]=[0,0,0,0]);b[0]++;b[1]+=cut;b[2]=Math.max(b[2],cut);if(cut>=1)b[3]++;
     if(P.state==='stand'&&Math.floor((P.y-1)/64)<Math.floor((sh._y||1e9))){on=-1;sh=null;}else if(!sh._y)sh._y=P.y-1;}
   return false;}});
 return {res,tot};}'''


def measure(b):
    out = {}
    for tag, html in (('old', OLD), ('new', NEW)):
        pg = page(b, html, 'classic', 1)
        G = {'frames': 0, 'cut': 0, 'cutFrames': 0, 'max': 0, 'by': {}}
        for n, s in FL:
            r = pg.evaluate(MEASURE, [n, s]); t = r['tot']
            print(tag, 'floor', n, 'seed', s, 'bot', r['res'].get('ok'), 'frames', t['frames'], 'cut px*frames %.0f' % t['cut'], 'frames with a cut', t['cutFrames'], 'max %.1f' % t['max'], flush=True)
            for k in ('frames', 'cut', 'cutFrames'): G[k] += t[k]
            G['max'] = max(G['max'], t['max'])
            for k, v in t['by'].items():
                q = G['by'].setdefault(k, [0, 0, 0, 0]); q[0] += v[0]; q[1] += v[1]; q[2] = max(q[2], v[2]); q[3] += v[3]
        print(tag, 'ALL frames', G['frames'], 'cut px*frames %.0f' % G['cut'], 'frames with a cut', G['cutFrames'], 'max %.1f px' % G['max'])
        for k, v in sorted(G['by'].items()):
            print('   %-12s frames %4d  with a cut %4d  mean %6.2f px  max %6.1f px' % (k, v[0], v[3], v[1] / v[0], v[2]))
        out[tag] = G
        pg.close()
    json.dump(out, open(os.path.join(OUTD, 'r42a.json'), 'w'), indent=1)


# the phases: frame indices into the bot's climb of floor FL[0]'s first shaft, found from the old build's states
PH = r'''()=>{const H=__HK,P=H.P;const o=[];let ps='',f=0,kick=0;
  for(;f<400;f++){H.tick(1);const r=window.__G.next();if(r.done)break;const st=P.state+(P.plant?':plant':P.state==='air'&&P.jumpKind?':'+P.jumpKind:'');if(st!==ps){o.push([f+1,st]);ps=st;}if(P.state==='stand'&&f>20)break;}
  return o;}'''

if __name__ == '__main__':
    os.makedirs(OUTD, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(args=GPU)
        if 'quick' in a:
            MODES[:] = MODES[:1]
        if 'measure' in a:
            measure(b); b.close(); sys.exit(0)
        n, s = FL[0]
        pg = page(b, OLD, 'classic', 1)
        pg.evaluate(LOAD, [n, s, 0, 0])
        tr = pg.evaluate(PH)
        pg.close()
        print('states', tr)
        # each phase: [label, frame]
        idx = {}
        for f, st in tr: idx.setdefault(st, []).append(f)
        ph = []
        first = lambda st, i=0, d=0: idx[st][i] + d if st in idx and len(idx[st]) > i else None
        cand = [('the jump in', first('air:stand', 0, 3)), ('first plant (one wall)', first('air:plant', 0, 3)), ('kick: push', first('air:kick', 0, 1)),
                ('kick: push 2', first('air:kick', 0, 4)), ('flight', first('air:kick', 0, 9)), ('flight, near the wall', first('air:kick', 0, 15)),
                ('arriving', first('air:plant', 1, 1)), ('braced', first('air:plant', 1, 5)), ('kick 2: push', first('air:kick', 1, 2)),
                ('kick 2: flight', first('air:kick', 1, 9)), ('plant at the top', first('air:plant', 2, 2)), ('sliding to the lip', first('air:plant', 2, 10)),
                ('hang', first('hang', 0, 0)), ('climb', first('climb', 0, 10)), ('climb, over', first('climb', 0, 30))]
        ph = [(t, f) for t, f in cand if f]
        print('phases', ph)
        cols, errs = {}, []
        for mt, m in ([] if 'gifonly' in a else MODES):
            for tag, html in (('old', OLD), ('new', NEW)):
                pg = page(b, html, m)
                pg.evaluate(LOAD, [n, s, 0, 0])
                got, f0 = [], 0
                for t, f in ph:
                    pg.evaluate(STEP, f - f0); f0 = f
                    got.append((shot(pg), shot(pg, None)))
                cols[(m, tag)] = got
                errs += [(m, tag, e) for e in pg.errs[:3]]
                pg.close()
                print('done', m, tag, flush=True)
        # his lamp shadow: Torchlight with a lamp up the shaft, a few phases, before | 42a
        SHP = [x for x in ph if x[0] in ('first plant (one wall)', 'kick: push', 'flight', 'braced', 'kick 2: flight', 'sliding to the lip')]
        if 'gifonly' not in a and len(MODES) > 1:
            for tag, html in (('old', OLD), ('new', NEW)):
                pg = page(b, html, 'torch')
                pg.evaluate(LOAD, [n, s, 0, 1])
                got, f0 = [], 0
                for t, f in SHP:
                    pg.evaluate(STEP, f - f0); f0 = f
                    got.append(shot(pg))
                cols[('shadow', tag)] = got
                errs += [('shadow', tag, e) for e in pg.errs[:3]]
                pg.close()
        keys = [(m, t) for _, m in MODES for t in ('old', 'new')]
        if 'gifonly' in a:
            keys = []
        names = {('classic', 'old'): 'Classic, before', ('classic', 'new'): 'Classic, 42a', ('torch', 'old'): 'Torchlight, before', ('torch', 'new'): 'Torchlight, 42a'}
        cw, chh = BW * ZK, BH * ZK
        # 3x: phases across, one row per build and mode
        rows = []
        per = 8
        for i0 in range(0, len(ph), per):
            for k in keys:
                row = Image.new('RGB', (per * (cw + 4) + 4, chh + 20), INK)
                for j, (t, f) in enumerate(ph[i0:i0 + per]):
                    c = cols[k][i0 + j][0].copy()
                    label(c, t)
                    row.paste(c, (4 + j * (cw + 4), 18))
                ImageDraw.Draw(row).text((6, 3), names[k] + ('  (floor %d seed %d, shaft at column %d)' % (n, s, 0) if False else ''), fill=(250, 240, 215))
                rows.append(row)
        if ('shadow', 'new') in cols:
            for tag in ('old', 'new'):
                row = Image.new('RGB', (per * (cw + 4) + 4, chh + 20), INK)
                for j, (t, f) in enumerate(SHP):
                    c = cols[('shadow', tag)][j].copy()
                    label(c, t)
                    row.paste(c, (4 + j * (cw + 4), 18))
                ImageDraw.Draw(row).text((6, 3), 'Torchlight with a lamp up the shaft (his shadow on its back wall), ' + ('before' if tag == 'old' else '42a'), fill=(250, 240, 215))
                rows.append(row)
        for k in keys:
            ims = [x[1] for x in cols[k]]
            w, h = ims[0].size
            row = Image.new('RGB', (len(ims) * (w + 4) + 130, h + 4), INK)
            ImageDraw.Draw(row).text((4, 4), names[k] + ', phone', fill=(250, 240, 215))
            for i, im in enumerate(ims):
                row.paste(im, (130 + i * (w + 4), 2))
            rows.append(row)
        W = max([r.width for r in rows] + [1])
        sheet = Image.new('RGB', (W, sum(r.height + 4 for r in rows)), INK)
        y = 0
        for r in rows:
            sheet.paste(r, (0, y)); y += r.height + 4
        out = os.path.join(OUTD, 'r42a_chimney.png')
        if keys:
            sheet.save(out, optimize=True)
            print('wrote', out, sheet.size)
        if 'nogif' in a:
            b.close(); sys.exit(0)
        fr = {}
        for mt, m in MODES:
            pg = page(b, NEW, m, 2)
            pg.evaluate(LOAD, [n, s, 0, 0])
            L = []
            g0 = max(0, ph[0][1] - 10)
            pg.evaluate(STEP, g0)
            for i in range(g0, ph[-1][1] + 6):
                L.append(shot(pg))
                pg.evaluate(STEP, 1)
            fr[m] = L
            errs += [(m, 'gif', e) for e in pg.errs[:3]]
            pg.close()
        frames = []
        for a1, a2 in zip(fr['classic'], fr['torch']):
            im = Image.new('RGB', (2 * cw + 6, chh), INK)
            im.paste(a1, (0, 0)); im.paste(a2, (cw + 6, 0)); frames.append(im)
        frames += [frames[-1]] * 10
        gif = os.path.join(OUTD, 'r42a_chimney.gif')
        frames[0].save(gif, save_all=True, append_images=frames[1:], duration=17, loop=0, optimize=True)
        print('wrote', gif, len(frames), 'frames')
        if errs:
            print('errors', errs)
        b.close()
