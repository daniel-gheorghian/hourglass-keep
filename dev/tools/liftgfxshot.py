# liftgfxshot.py file.html out.png [torch|classic] [only=i,j]: a contact sheet of lifts, both kinds, several floors, themes and
# wear levels, each at the top, mid-ride and at the bottom (counterweight) or at three clock times (chain-loop), with the
# prince on it, drawn by the game's own render() (Torchlight frames sent at once). Compares with any older html. No PIL: the
# tiles are cropped by Playwright and pasted into one sheet in a page. Run from dev/tools.
import os, sys, base64, json
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
SRC = next((x for x in a if x.endswith('.html')), os.path.join(HERE, '..', 'hourglass-keep.html'))
OUT = next((x for x in a if x.endswith('.png')), os.path.join(HERE, 'liftgfxshot.png'))
MODE = 'classic' if 'classic' in a else 'torch'
ONLY = next((x[5:] for x in a if x.startswith('only=')), None)
AT = [x[3:].split(':') for x in a if x.startswith('at=')]  # at=n:seed:liftindex (any number): those lifts instead of the fixed set
# (kind, floor from, which hit)
CASES = [('lift2d', 3, 0), ('lift3u', 9, 0), ('lift2u', 17, 0), ('lift3d', 26, 0), ('lift2d', 38, 0), ('lift2u', 50, 0),
         ('chn2d', 8, 0), ('chn3u', 20, 0), ('chn2u', 41, 0)]
FRACS = [0, 0.5, 1]
FACE = next((int(x[5:]) for x in a if x.startswith('face=')), 0)
DSF = next((float(x[4:]) for x in a if x.startswith('dsf=')), 2)
FR = next((x[3:] for x in a if x.startswith('fr=')), None)
if FR: FRACS = [float(v) for v in FR.split(',')]
if AT:
    CASES = [('#' + i, int(n), int(sd)) for n, sd, i in AT]
FIND = r'''([kind,n0,skip])=>{const H=__HK;if(kind[0]==='#')return [n0,skip];window.__HKfreeze=true;for(const id in H.HINTS)H.S.hints[id]=1;let k=0;
  for(let n=n0;n<n0+12;n++)for(let s=0;s<40;s++){const seed=5000+s*131+n*7,L=H.genLevel(n,seed,true);
    if(L.segs.some(q=>q.k==='turn-'+kind)){if(k++<skip)continue;return [n,seed];}}return null;}'''
PLACE = r'''([n,seed,kind,frac])=>{const H=__HK,L=H.load(n,seed,true);H.banner=null;const P=H.P;P.inv=1e9;
  const sg=kind[0]==='#'?null:L.segs.find(q=>q.k==='turn-'+kind);
  let lf=sg?null:L.lifts[+kind.slice(1)];if(sg)lf=L.lifts.find(q=>q.ca>=Math.min(sg.c0,sg.c1)-1&&q.cb<=Math.max(sg.c0,sg.c1)+1&&q.rT>=Math.min(sg.r0,sg.r1)&&q.rB<=Math.max(sg.r0,sg.r1));
  if(lf.t==='lift'){lf.y=lf.yT+(lf.yB-lf.yT)*frac;P.x=lf.sc*32+16;P.y=lf.y;P.fallY=P.y;P.face=window.__face||(lf.sT<0?1:-1);
    if(frac>0&&frac<1){P.state='lift';P.lift=lf;}else P.state='stand';
    L.base[lf.rT*L.cols+lf.sc]=frac===0?1:0;lf.gT=frac===0?1:0;lf.gB=frac===1?1:0;}
  else{H.tick(Math.round(frac*6*60));const q=H.chainPos(lf,0,H.gameTime);P.x=q.x;P.y=q.y;P.fallY=P.y;P.state='lift';P.lift=lf;P.slab=0;P.bx=q.x;P.by=q.y;P.bt=-9;}
  H.cam.snap=true;
  for(let k=0;k<24;k++){H.tick(1);if(lf.t==='lift'){lf.y=lf.yT+(lf.yB-lf.yT)*frac;P.x=lf.sc*32+16;P.y=lf.y;}} // (his look offsets ease in, as in play)
  if(H.GLP)H.GLP.pipe=false;window.__HKfreeze=true;H.render();H.render();H.render();
  const X=H.XF,cv=[...document.querySelectorAll('canvas')].find(c=>c.getBoundingClientRect().width>0),R=cv.getBoundingClientRect();
  const m=(x,y)=>[R.left+(x*X.VZ-X.camD)/cv.width*R.width,R.top+(y*X.VZ-X.camDY)/cv.height*R.height];
  const a=m(lf.ca*32-72,lf.rT*64-20),b=m((lf.cb+1)*32+72,lf.rB*64+64+8);
  return {a,b,th:H.themeName(n),wear:L.prog?L.prog.wear:0,wl:H.wearLevel(lf.sc*32+16,(lf.rT*64+lf.rB*64)/2+32)};}'''
SHEET = r'''([tiles,cols])=>new Promise(res=>{let W=0,Hs=[];const ims=tiles.map(t=>{const i=new Image();i.src=t.u;return i;});
  Promise.all(ims.map(i=>i.decode())).then(()=>{const cw=Math.max(...ims.map(i=>i.width)),rows=Math.ceil(ims.length/cols),rh=[];
    for(let r=0;r<rows;r++)rh.push(Math.max(...ims.slice(r*cols,r*cols+cols).map(i=>i.height)));
    const c=document.createElement('canvas');c.width=cw*cols;c.height=rh.reduce((a,b)=>a+b+0,0);const g=c.getContext('2d');g.fillStyle='#000';g.fillRect(0,0,c.width,c.height);
    let y=0;for(let r=0;r<rows;r++){for(let k=0;k<cols;k++){const i=r*cols+k;if(i>=ims.length)break;g.drawImage(ims[i],k*cw,y);g.font='12px monospace';g.fillStyle='#ff0';g.fillText(tiles[i].l,k*cw+4,y+13);}y+=rh[r];}
    res(c.toDataURL());});})'''
tiles = []
with sync_playwright() as p:
    b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
    for ci, (kind, n0, skip) in enumerate(CASES):
        if ONLY and str(ci) not in ONLY.split(','):
            continue
        for fr in FRACS:
            pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=DSF)
            errs = []
            pg.on('pageerror', lambda e: errs.append(str(e)))
            pg.goto('file://' + os.path.abspath(SRC)); pg.wait_for_timeout(300)
            pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true)")
            pg.evaluate("m=>{__HK.S.set.lightMode=m}", MODE)
            if FACE: pg.evaluate("f=>{window.__face=f}", FACE)
            f = pg.evaluate(FIND, [kind, n0, skip])
            if not f:
                print('none', kind, n0); pg.close(); break
            r = pg.evaluate(PLACE, [f[0], f[1], kind, fr])
            x0, y0 = max(0, r['a'][0]), max(0, r['a'][1]); x1, y1 = min(852, r['b'][0]), min(393, r['b'][1])
            png = pg.screenshot(clip={'x': x0, 'y': y0, 'width': x1 - x0, 'height': y1 - y0})
            lab = '%s n%d s%d %s w%d/%d %s f%.1f' % (kind, f[0], f[1], r['th'][:18], r['wear'], r['wl'], MODE, fr)
            tiles.append({'u': 'data:image/png;base64,' + base64.b64encode(png).decode(), 'l': lab})
            print(lab, errs[:2])
            pg.close()
    pg = b.new_page()
    u = pg.evaluate(SHEET, [tiles, 3])
    open(OUT, 'wb').write(base64.b64decode(u.split(',')[1]))
    b.close()
print('wrote', OUT)
