# egyptfx.py [file.html] [outdir]: the themes' own effects (LFX) for egypt_themes.html, in Torchlight: for each theme with one,
# a spot that shows it (an open arch for the water's caustics, a lamp for salt, glaze and heat, any floor for dust) as a short
# animated GIF (the prince standing there, 0.1 s a frame); and what it costs: ?prof's atmo and masks stages, per frame, with
# the theme's effects and with them switched off (LFX emptied for the run), on this Mac's GPU. Also each theme's backdrop as
# a strip (its layers over its sky, at dusk and in the light it first comes in). Writes fx.json beside them. Run from dev/tools.
import base64, io, json, os, sys
from playwright.sync_api import sync_playwright
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
SRC = a[0] if len(a) > 0 else os.path.join(HERE, '..', 'hourglass-keep.html')
OUT = a[1] if len(a) > 1 else os.path.join(HERE, 'egypt_themes')
os.makedirs(OUT, exist_ok=True)
FIND = r'''([t,want])=>{const H=__HK;window.__HKfreeze=true;
  for(let n=4*t+1;n<=4*t+4;n++)for(let sd=1;sd<=8;sd++){const L=H.load(n,600+sd,true);const C=L.cols,F=(c,r)=>c<0||c>=C||r<0||r>=L.rows?null:L.feat[r*C+c];
    for(let r=1;r<L.rows-1;r++)for(let c=10;c<C-10;c++){if(!H.solidBelow(c,r)||!H.solidBelow(c-1,r)||!H.solidBelow(c+1,r)||F(c,r)||F(c-1,r)||F(c+1,r))continue;
      let ok=false;
      if(want==='arch'){for(let cc=c-4;cc<=c+4;cc++)if(H.isOpenArch(cc,r-1)||H.isOpenArch(cc,r))ok=true;}
      else if(want==='lamp'){for(const q of L.torches)if(!q.broken&&q.r===r&&Math.abs(q.c-c)>=1&&Math.abs(q.c-c)<=2)ok=true;}
      else if(want==='beam'){for(const w of L.windows)if((w.r===r)&&Math.abs(w.c-c)<=3)ok=true;for(let cc=c-3;cc<=c+3;cc++)if(H.isOpenArch(cc,r))ok=true;}
      else ok=c%7===0;
      if(ok)return {n,seed:600+sd,c,r};}}
  return null;}'''
PLACE = r'''([n,seed,c,r])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS){H.S.hints[id]=1;H.S.learned[id]=1;}H.load(n,seed,true);const P=H.P;P.inv=1e9;
  P.x=c*32+16;P.y=(r+1)*64-4;P.fallY=P.y;P.vx=P.vy=0;P.state='stand';P.face=1;H.cam.snap=true;H.tick(2);P.x=c*32+16;P.state='stand';H.cam.snap=true;H.tick(1);H.banner=null;
  H.GLP&&(H.GLP.pipe=false);H.render();H.render();const X=H.XF,cv=[...document.querySelectorAll('canvas')].find(q=>q.getBoundingClientRect().width>0),R=cv.getBoundingClientRect();
  return {x:R.left+(P.x*X.VZ-X.camD)/cv.width*R.width,y:R.top+((P.y-30)*X.VZ-X.camDY)/cv.height*R.height,name:H.themeName(n)};}'''
STEP = r'''()=>{const H=__HK;H.tick(6);H.P.inv=1e9;H.banner=null;H.render();}'''
COST = r'''([n,frames,off])=>{const H=__HK,look=H.themeOf(n).look,sv=H.LFX[look];if(off)H.LFX[look]={};const PF=H.PF;
  for(let i=0;i<20;i++){H.tick(1);H.render();}const sum={};
  for(let i=0;i<frames;i++){H.tick(1);H.P.inv=1e9;PF.s();H.render();for(const k in PF.a)sum[k]=(sum[k]||0)+PF.a[k];}const o={};for(const k of ['masks','atmo','compose','lmap'])o[k]=(sum[k]||0)/frames;H.LFX[look]=sv;return o;}'''
STRIP = r'''([look,tod])=>{const H=__HK,art=H.BGART[look],ly=H.bgLayers(look,tod),W=ly[0].c.width,Hh=ly[0].c.height,c=document.createElement('canvas');c.width=W*2;c.height=Hh;const g=c.getContext('2d');
  const sky=H.progOf(1+20*tod)&&art.sky,gr=g.createLinearGradient(0,0,0,Hh);gr.addColorStop(0,sky[0]);gr.addColorStop(0.45,sky[1]);gr.addColorStop(0.72,sky[2]);gr.addColorStop(1,sky[3]);g.fillStyle=gr;g.fillRect(0,0,W*2,Hh);
  for(const q of ly){g.drawImage(q.c,0,0);g.drawImage(q.c,W,0);}return c.toDataURL('image/png');}'''
WANT = {'nun': 'arch', 'foggara': 'beam', 'blue': 'lamp', 'meroe': 'lamp', 'napata': 'lamp', 'shali': 'lamp', 'deffufa': 'lamp', 'wells': 'beam', 'hawara': 'lamp'}
man = {'fx': [], 'strips': {}}
with sync_playwright() as p:
    b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
    pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=2)
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://' + os.path.abspath(SRC))
    pp = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=2)  # (the cost runs: ?prof's timings, its overlay kept out of the pictures)
    pp.goto('file://' + os.path.abspath(SRC) + '?prof')
    for q_ in (pg, pp):
        q_.wait_for_timeout(500)
        q_.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true)")
        q_.evaluate("()=>{__HK.S.set.lightMode='torch';}")
    looks = pg.evaluate("__HK.THEMES.map(t=>t.look)")
    for t, look in enumerate(looks):
        for tod in sorted({0, (4 * t) // 20 % 3}):
            d = pg.evaluate(STRIP, [look, tod])
            fn = 'bg_%s_%d.png' % (look, tod)
            im = Image.open(io.BytesIO(base64.b64decode(d.split(',')[1]))).convert('RGB')
            im.save(os.path.join(OUT, fn.replace('.png', '.jpg')), quality=85)
            man['strips'].setdefault(look, []).append(fn.replace('.png', '.jpg'))
        if look not in WANT:
            continue
        q = pg.evaluate(FIND, [t, WANT[look]])
        if not q:
            print('no spot', look); continue
        r = pg.evaluate(PLACE, [q['n'], q['seed'], q['c'], q['r']])
        frames = []
        for i in range(18):
            pg.evaluate(STEP)
            png = pg.screenshot()
            im = Image.open(io.BytesIO(png)).convert('RGB')
            cw, ch = 720, 440
            x0 = int(min(max(0, r['x'] * 2 - cw / 2), im.width - cw)); y0 = int(min(max(0, r['y'] * 2 - ch / 2 - 40), im.height - ch))
            frames.append(im.crop((x0, y0, x0 + cw, y0 + ch)).resize((cw * 2 // 3, ch * 2 // 3), Image.LANCZOS))
        gif = 'fx_%s.gif' % look
        frames[0].save(os.path.join(OUT, gif), save_all=True, append_images=frames[1:], duration=100, loop=0, optimize=True)
        pp.evaluate(PLACE, [q['n'], q['seed'], q['c'], q['r']])
        on = pp.evaluate(COST, [q['n'], 240, False])
        pp.evaluate(PLACE, [q['n'], q['seed'], q['c'], q['r']])
        off = pp.evaluate(COST, [q['n'], 240, True])
        man['fx'].append({'look': look, 'name': r['name'], 'gif': gif, 'n': q['n'], 'seed': q['seed'], 'c': q['c'], 'r': q['r'], 'on': on, 'off': off})
        print(look, r['name'], 'on', {k: round(v, 3) for k, v in on.items()}, 'off', {k: round(v, 3) for k, v in off.items()}, flush=True)
    b.close()
man['errors'] = errs[:20]
json.dump(man, open(os.path.join(OUT, 'fx.json'), 'w'), indent=1)
print('errors', errs[:5])
