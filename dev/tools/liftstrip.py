# liftstrip.py file.html out.png [kind] [torch|classic]: a frame strip of a ride on the first counterweight lift of `kind`
# (lift2d default): he stands on the platform, Down (Up for an up lift) is held through the whole ride and for a second after
# it ends; a frame every 0.3 s and four after the arrival, labelled with his state. Run from dev/tools.
import os, sys, base64
from playwright.sync_api import sync_playwright
a = sys.argv[1:]
SRC = next((x for x in a if x.endswith('.html')))
OUT = next((x for x in a if x.endswith('.png')))
KIND = next((x for x in a if (x.startswith('lift') or x.startswith('chn')) and '.' not in x), 'lift2d')
MODE = 'classic' if 'classic' in a else 'torch'
FIND = r'''([kind])=>{const H=__HK;for(let n=3;n<30;n++)for(let s=0;s<40;s++){const seed=5000+s*131+n*7,L=H.genLevel(n,seed,true);if(L.segs.some(q=>q.k==='turn-'+kind))return [n,seed];}return null;}'''
SETUP = r'''([n,seed,kind])=>{const H=__HK,L=H.load(n,seed,true);H.banner=null;for(const id in H.HINTS)H.S.hints[id]=1;const sg=L.segs.find(q=>q.k==='turn-'+kind);
  const f=L.lifts.find(q=>q.t==='lift'&&q.sc>=Math.min(sg.c0,sg.c1)&&q.sc<=Math.max(sg.c0,sg.c1)&&q.rT>=Math.min(sg.r0,sg.r1)&&q.rB<=Math.max(sg.r0,sg.r1));
  const P=H.P;P.inv=1e9;P.x=f.sc*32+16;P.y=f.y;P.fallY=P.y;P.state='stand';P.face=f.sT<0?1:-1;window.__f=f;window.__down=f.y===f.yT;
  H.cam.snap=true;H.tick(2);if(H.GLP)H.GLP.pipe=false;H.setKey('kb',window.__down?'d':'u',true);return true;}'''
STEP = r'''(k)=>{const H=__HK,f=window.__f;H.tick(k);H.render();H.render();
  const X=H.XF,cv=[...document.querySelectorAll('canvas')].find(c=>c.getBoundingClientRect().width>0),R=cv.getBoundingClientRect();
  const m=(x,y)=>[R.left+(x*X.VZ-X.camD)/cv.width*R.width,R.top+(y*X.VZ-X.camDY)/cv.height*R.height];
  const p=m(H.P.x,H.P.y);return {p,st:H.P.state,y:H.P.y|0,arr:Math.abs(f.y-(window.__down?f.yB:f.yT))<0.01};}'''
SHEET = r'''([tiles,cols])=>new Promise(res=>{const ims=tiles.map(t=>{const i=new Image();i.src=t.u;return i;});
  Promise.all(ims.map(i=>i.decode())).then(()=>{const cw=ims[0].width,ch=ims[0].height,rows=Math.ceil(ims.length/cols);
    const c=document.createElement('canvas');c.width=cw*cols;c.height=ch*rows;const g=c.getContext('2d');g.fillStyle='#000';g.fillRect(0,0,c.width,c.height);
    ims.forEach((im,i)=>{g.drawImage(im,(i%cols)*cw,Math.floor(i/cols)*ch);g.font='13px monospace';g.fillStyle='#ff0';g.fillText(tiles[i].l,(i%cols)*cw+4,Math.floor(i/cols)*ch+14);});res(c.toDataURL());});})'''
with sync_playwright() as p:
    b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
    pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=2); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://' + os.path.abspath(SRC)); pg.wait_for_timeout(300)
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true)")
    pg.evaluate("m=>{__HK.S.set.lightMode=m}", MODE)
    n, seed = pg.evaluate(FIND, [KIND]); pg.evaluate(SETUP, [n, seed, KIND])
    tiles = []; after = None; t = 0
    while t < 60 * 12:
        r = pg.evaluate(STEP, 18); t += 18
        if r['arr'] and after is None: after = 0
        x, y = r['p']; W, H = 150, 150
        png = pg.screenshot(clip={'x': max(0, x - W / 2), 'y': max(0, min(393 - H, y - 110)), 'width': W, 'height': H})
        tiles.append({'u': 'data:image/png;base64,' + base64.b64encode(png).decode(), 'l': '%.1fs %s' % (t / 60, r['st'])})
        if after is not None:
            after += 1
            if after > 4: break
    u = b.new_page().evaluate(SHEET, [tiles, 8])
    open(OUT, 'wb').write(base64.b64decode(u.split(',')[1])); print('n', n, 'seed', seed, KIND, MODE, 'frames', len(tiles), errs[:2]); b.close()
