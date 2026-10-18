# egyptprince.py [file.html] [outdir]: the pictures of the prince in Egyptian dress for egypt_themes.html (round 6): for each variant
# (HERO_VAR A, B, C) a pose sheet drawn by the game's own drawFigureHD at 3x (stand, run, jump, hang, climb, guard, lunge, fallen),
# a running GIF and a standing shot in the game in Torchlight and Classic; and the recommended one (A) standing on every theme's
# floor in Torchlight, at phone size, to check how he reads. Also the Green Hall's and Meroë's new tints (after; egyptshot.py's
# shots of v62 were kept as tint_before_*). Writes prince.json beside them. Run from dev/tools.
import base64, io, json, os, sys
from playwright.sync_api import sync_playwright
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
SRC = a[0] if len(a) > 0 else os.path.join(HERE, '..', 'hourglass-keep.html')
OUT = a[1] if len(a) > 1 else os.path.join(HERE, 'egypt_themes')
SHEET = r'''([v])=>{const H=__HK;H.setHero(v);const P=H.PS,names=[['stand',P.stand,0],['jump',P.jumpR,0],['hang',P.hang,0],['climb',P.pull,0],['guard',P.garde,1],['lunge',P.lunge,1],['fallen',P.dead,0]];
  const S=3,W=40,Hh=64,c=document.createElement('canvas');c.width=names.length*W*S;c.height=Hh*S;const g=c.getContext('2d');g.fillStyle='#2a2430';g.fillRect(0,0,c.width,c.height);
  g.fillStyle='#3a3240';g.fillRect(0,(Hh-6)*S,c.width,6*S);g.setTransform(S,0,0,S,0,0);
  names.forEach(([nm,p,sw],i)=>{let q=p;if(!q){q=Object.assign({},P.stand);const r=H.PS.run||null;}
    try{H.drawFigureHD(g,i*W+W/2,Hh-6,1,q||P.stand,H.PAL_HERO,{hasSword:true,sword:!!sw,time:1.3,lt:{dir:1,col:'255,200,140',k:0.5}});}catch(e){g.fillStyle='#f00';g.fillRect(i*W+5,5,5,5);}});
  return c.toDataURL('image/png');}'''
JS = r'''window.__P={load(n,seed){const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS){H.S.hints[id]=1;H.S.learned[id]=1;}H.load(n,seed,true);H.banner=null;return H.L;},
  stand(c,r,face){const H=__HK,P=H.P;P.inv=1e9;P.x=c*32+16;P.y=(r+1)*64-4;P.fallY=P.y;P.vx=P.vy=0;P.state='stand';P.face=face;H.cam.snap=true;H.tick(2);P.x=c*32+16;P.y=(r+1)*64-4;P.state='stand';P.face=face;H.cam.snap=true;H.tick(1);H.banner=null;H.mode='play';},
  scr(x,y){const H=__HK,X=H.XF,cv=[...document.querySelectorAll('canvas')].find(q=>q.getBoundingClientRect().width>0),R=cv.getBoundingClientRect();return [R.left+(x*X.VZ-X.camD)/cv.width*R.width,R.top+(y*X.VZ-X.camDY)/cv.height*R.height];}};'''
SPOT = r'''([n,v])=>{const H=__HK;H.setHero(v);for(const sd of [941,942,943,944]){const L=__P.load(n,sd);for(let c=Math.floor(L.start.x/32)+3;c<L.cols-10;c++){const r=L.start.r;if(H.solidBelow(c,r)&&H.solidBelow(c+3,r)&&!L.feat[r*L.cols+c]&&L.torches.some(t=>!t.broken&&t.r===r&&Math.abs(t.c-c)<=4)){__P.stand(c,r,1);H.GLP&&(H.GLP.pipe=false);H.render();H.render();H.render();return __P.scr(H.P.x,H.P.y-30);}}}return null;}'''
RUN = r'''([n,v,k])=>{const H=__HK;if(k===0){H.setHero(v);const L=__P.load(n,951);__P.stand(Math.floor(L.start.x/32)+2,L.start.r,1);H.setKey('kb','r',true);}
  H.tick(4);H.P.inv=1e9;H.banner=null;H.render();return __P.scr(H.P.x,H.P.y-30);}'''


def newpage(b, mode):
    pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=2)
    pg.errs = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e)))
    pg.goto('file://' + os.path.abspath(SRC))
    pg.wait_for_timeout(700)
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.body.classList.remove('panelOpen')")
    pg.evaluate("m=>{__HK.S.set.lightMode=m;}", mode)
    pg.evaluate(JS)
    return pg


def crop(im, xy, cw, ch):
    x0 = int(min(max(0, xy[0] * 2 - cw / 2), im.width - cw)); y0 = int(min(max(0, xy[1] * 2 - ch / 2), im.height - ch))
    return im.crop((x0, y0, x0 + cw, y0 + ch))


man = {'variants': [], 'themes': [], 'tint': []}
errs = []
with sync_playwright() as p:
    b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
    pt, pc = newpage(b, 'torch'), newpage(b, 'classic')
    for v in ('A', 'B', 'C'):
        d = pt.evaluate(SHEET, [v])
        Image.open(io.BytesIO(base64.b64decode(d.split(',')[1]))).convert('RGB').save(os.path.join(OUT, 'prince_%s_sheet.png' % v))
        ent = {'v': v, 'sheet': 'prince_%s_sheet.png' % v, 'shots': {}}
        for lab, pg in (('torch', pt), ('classic', pc)):
            for n in (5, 13):
                xy = pg.evaluate(SPOT, [n, v])
                if not xy:
                    continue
                im = Image.open(io.BytesIO(pg.screenshot())).convert('RGB')
                stem = 'prince_%s_%d_%s' % (v, n, lab)
                crop(im, xy, 420, 300).save(os.path.join(OUT, stem + '.jpg'), quality=90)
                ent['shots'][stem] = n
        frames = []
        for k in range(22):
            xy = pt.evaluate(RUN, [9, v, k])
            im = Image.open(io.BytesIO(pt.screenshot())).convert('RGB')
            frames.append(crop(im, xy, 480, 300).resize((360, 225), Image.LANCZOS))
        pt.evaluate("()=>__HK.setKey('kb','r',false)")
        gif = 'prince_%s_run.gif' % v
        frames[0].save(os.path.join(OUT, gif), save_all=True, append_images=frames[1:], duration=67, loop=0, optimize=True)
        ent['gif'] = gif
        man['variants'].append(ent)
        print('variant', v, flush=True)
    looks = pt.evaluate("__HK.THEMES.map(t=>[t.look,t.name,__HK.floorsOf(t.look)[0]])")
    for look, name, n in looks:
        xy = pt.evaluate(SPOT, [n, 'A'])
        if not xy:
            continue
        im = Image.open(io.BytesIO(pt.screenshot())).convert('RGB')
        fn = 'prince_on_%s.jpg' % look
        crop(im, xy, 300, 240).save(os.path.join(OUT, fn), quality=90)
        man['themes'].append({'look': look, 'name': name, 'n': n, 'img': fn})
    errs += pt.errs + pc.errs
    b.close()
man['errors'] = errs[:20]
json.dump(man, open(os.path.join(OUT, 'prince.json'), 'w'), indent=1)
print('errors', errs[:5])
