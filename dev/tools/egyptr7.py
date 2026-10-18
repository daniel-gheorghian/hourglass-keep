# egyptr7.py [file.html] [outdir]: the pictures for round 7 on egypt_themes.html: the prince (v62's, round 6's A and the plain one now
# in the game) and the tomb robbers, drawn by the game's own drawFigureHD; a robber fight and the prince running (GIFs); the three
# timekeeper concepts at HUD and gate-clock size, the barque clock draining and in the rewind (GIF), and in the game; the glass
# jars (stills, a GIF of one being drunk) and on the floor; the faience hearts; the title and pause panels. Writes r7.json. Run from dev/tools.
import base64, io, json, os, sys
from playwright.sync_api import sync_playwright
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
SRC = a[0] if len(a) > 0 else os.path.join(HERE, '..', 'hourglass-keep.html')
OUT = a[1] if len(a) > 1 else os.path.join(HERE, 'egypt_themes')
LT = "{dir:1,col:'255,200,140',k:0.5}"
FIGS = r'''([rows])=>{const H=__HK,P=H.PS,poses=[['stand',P.stand,0],['jump',P.jumpR,0],['hang',P.hang,0],['guard',P.garde,1],['lunge',P.lunge,1],['fallen',P.dead,0]];
  const S=3,W=40,Hh=64,c=document.createElement('canvas');c.width=poses.length*W*S;c.height=rows.length*Hh*S;const g=c.getContext('2d');g.fillStyle='#2a2430';g.fillRect(0,0,c.width,c.height);g.setTransform(S,0,0,S,0,0);
  rows.forEach((k,j)=>{let pal;if(typeof k==='number')pal=H.guardPal({tier:k,cap:k===3});else{H.setHero(k==='old'?null:k);pal=Object.assign({},H.PAL_HERO);}
    g.fillStyle='#3a3240';g.fillRect(0,j*Hh+Hh-6,c.width,6);poses.forEach(([pn,q,sw],i)=>H.drawFigureHD(g,i*W+W/2,j*Hh+Hh-6,1,q,pal,{hasSword:true,sword:!!sw,time:1.3,lt:LT}));});
  H.setHero('P');return c.toDataURL('image/png');}'''.replace('LT', LT)
FIGHT = r'''([tier,k])=>{const H=__HK,P=H.PS,seq=[P.garde,P.garde,P.lunge,P.lunge,P.garde,P.parry,P.parry,P.garde],hs=[P.garde,P.parry,P.parry,P.garde,P.garde,P.lunge,P.lunge,P.garde];
  const S=3,c=document.createElement('canvas');c.width=150*S;c.height=70*S;const g=c.getContext('2d');g.fillStyle='#2a2430';g.fillRect(0,0,c.width,c.height);g.setTransform(S,0,0,S,0,0);g.fillStyle='#3a3240';g.fillRect(0,64,150,6);
  H.setHero('P');const i=Math.floor(k/3)%seq.length;H.drawFigureHD(g,55,64,1,seq[i],H.PAL_HERO,{hasSword:true,sword:true,time:k*0.05,lt:LT});
  H.drawFigureHD(g,95,64,-1,hs[i],H.guardPal({tier,cap:tier===3}),{hasSword:true,sword:true,time:k*0.05,lt:LT});return c.toDataURL('image/png');}'''.replace('LT', LT)
CLOCKS = r'''([kind,f,s,rev,t])=>{const H=__HK,c=document.createElement('canvas'),Z=s*10;c.width=Z*3;c.height=Z*3;const g=c.getContext('2d');g.fillStyle='#120e18';g.fillRect(0,0,c.width,c.height);
  g.translate(c.width/2,c.height/2);g.scale(Z/10,Z/10);if(kind==='A')H.barqueClock(g,f,{s:1,t,rev,glow:true});else H.conceptClock(g,kind,f,1);return c.toDataURL('image/png');}'''
JARS = r'''([fill,tilt,t])=>{const H=__HK,c=document.createElement('canvas');c.width=4*16*4;c.height=4*24;const g=c.getContext('2d');g.fillStyle='#120e18';g.fillRect(0,0,c.width,c.height);
  ['heal','big','life','poison'].forEach((ty,i)=>{g.save();g.setTransform(4,0,0,4,(i*16+8)*4,22*4);H.flaskBody(g,ty,t,fill,tilt);g.restore();});return c.toDataURL('image/png');}'''
HEARTS = r'''()=>{const H=__HK,c=document.createElement('canvas');c.width=6*10*5;c.height=14*5;const g=c.getContext('2d');g.fillStyle='#120e18';g.fillRect(0,0,c.width,c.height);g.setTransform(5,0,0,5,0,0);
  for(let i=0;i<6;i++)H.heart(g,2+i*10,2,i<4,i<4?'#2fae9e':'#2fae9e',i<4?'#b8f5e8':'rgba(70,190,170,.55)');return c.toDataURL('image/png');}'''
JS = r'''window.__P={load(n,seed){const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS){H.S.hints[id]=1;H.S.learned[id]=1;}H.load(n,seed,true);H.banner=null;return H.L;},
  stand(c,r,face){const H=__HK,P=H.P;P.inv=1e9;P.x=c*32+16;P.y=(r+1)*64-4;P.fallY=P.y;P.vx=P.vy=0;P.state='stand';P.face=face;H.cam.snap=true;H.tick(2);P.x=c*32+16;P.y=(r+1)*64-4;P.state='stand';P.face=face;H.cam.snap=true;H.tick(1);H.banner=null;H.mode='play';},
  scr(x,y){const H=__HK,X=H.XF,cv=[...document.querySelectorAll('canvas')].find(q=>q.getBoundingClientRect().width>0),R=cv.getBoundingClientRect();return [R.left+(x*X.VZ-X.camD)/cv.width*R.width,R.top+(y*X.VZ-X.camDY)/cv.height*R.height];}};'''
ITEM = r'''()=>{const H=__HK;for(const n of [3,6,9,12,15]){for(const sd of [961,962,963]){const L=__P.load(n,sd);const it=L.items.find(q=>!q.hidden&&H.solidBelow(Math.floor(q.x/32)-2,q.r));if(!it)continue;__P.stand(Math.floor(it.x/32)-2,it.r,1);H.render();H.render();H.render();return __P.scr(it.x,(it.r+1)*64-14);}}return null;}'''
CP = r'''()=>{const H=__HK;for(const n of [9,17,13]){const L=__P.load(n,821);const cp=L.cps.find(c=>H.solidBelow(Math.floor(c.x/32)+2,c.r));if(!cp)continue;__P.stand(Math.floor(cp.x/32)+2,cp.r,-1);cp.on=true;cp.onAt=H.gameTime-3.4;H.render();H.render();H.render();return __P.scr(cp.x,(cp.r+1)*64-36);}return null;}'''


def png(d):
    return Image.open(io.BytesIO(base64.b64decode(d.split(',')[1]))).convert('RGB')


def page(b, mode):
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


man = {}
with sync_playwright() as p:
    b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
    pt, pc = page(b, 'torch'), page(b, 'classic')
    png(pt.evaluate(FIGS, [['old', 'A', 'P']])).save(os.path.join(OUT, 'r7_prince_compare.png'))
    png(pt.evaluate(FIGS, [[0, 1, 2, 3]])).save(os.path.join(OUT, 'r7_robbers.png'))
    for tier in (1, 3):
        fr = [png(pt.evaluate(FIGHT, [tier, k])) for k in range(24)]
        fr[0].save(os.path.join(OUT, 'r7_fight_%d.gif' % tier), save_all=True, append_images=fr[1:], duration=90, loop=0, optimize=True)
    # the prince running, in the game
    frames = []
    for k in range(22):
        if k == 0:
            pt.evaluate("()=>{const H=__HK;H.setHero('P');const L=__P.load(9,951);__P.stand(Math.floor(L.start.x/32)+2,L.start.r,1);H.setKey('kb','r',true);}")
        xy = pt.evaluate("()=>{const H=__HK;H.tick(4);H.P.inv=1e9;H.banner=null;H.render();return __P.scr(H.P.x,H.P.y-30);}")
        frames.append(crop(Image.open(io.BytesIO(pt.screenshot())).convert('RGB'), xy, 480, 300).resize((360, 225), Image.LANCZOS))
    pt.evaluate("()=>__HK.setKey('kb','r',false)")
    frames[0].save(os.path.join(OUT, 'r7_prince_run.gif'), save_all=True, append_images=frames[1:], duration=67, loop=0, optimize=True)
    # the timekeepers: concepts at HUD size (x1 and enlarged) and gate-clock size, and the barque clock draining / in the rewind
    for kind in ('A', 'B', 'C'):
        for f in (1.0, 0.5, 0.1):
            png(pt.evaluate(CLOCKS, [kind, f, 4, False, 1.0])).save(os.path.join(OUT, 'r7_clock_%s_%d.png' % (kind, int(f * 10))))
        png(pt.evaluate(CLOCKS, [kind, 0.6, 0.86, False, 1.0])).resize((78, 78), Image.NEAREST).save(os.path.join(OUT, 'r7_clock_%s_hud.png' % kind))
        png(pt.evaluate(CLOCKS, [kind, 0.6, 0.64, False, 1.0])).resize((58, 58), Image.NEAREST).save(os.path.join(OUT, 'r7_clock_%s_gate.png' % kind))
    fr = [png(pt.evaluate(CLOCKS, ['A', 1 - k / 23, 4, False, k * 0.08])) for k in range(24)] + [png(pt.evaluate(CLOCKS, ['A', k / 15, 4, True, k * 0.08])) for k in range(16)]
    fr[0].save(os.path.join(OUT, 'r7_clock_run.gif'), save_all=True, append_images=fr[1:], duration=90, loop=0, optimize=True)
    for lab, pg in (('torch', pt), ('classic', pc)):
        xy = pg.evaluate(CP)
        if xy:
            crop(Image.open(io.BytesIO(pg.screenshot())).convert('RGB'), xy, 360, 260).save(os.path.join(OUT, 'r7_clock_game_%s.jpg' % lab), quality=90)
    # the jars: stills, a GIF of one being drunk (level falling, tilting), and on the floor in the game
    png(pt.evaluate(JARS, [1, 0, 3])).save(os.path.join(OUT, 'r7_jars.png'))
    fr = [png(pt.evaluate(JARS, [1 - k / 19 if k > 3 else 1, min(0.9, k * 0.06), k * 0.4])) for k in range(20)]
    fr[0].save(os.path.join(OUT, 'r7_jars_drink.gif'), save_all=True, append_images=fr[1:], duration=110, loop=0, optimize=True)
    for lab, pg in (('torch', pt), ('classic', pc)):
        xy = pg.evaluate(ITEM)
        if xy:
            crop(Image.open(io.BytesIO(pg.screenshot())).convert('RGB'), xy, 360, 240).save(os.path.join(OUT, 'r7_jar_game_%s.jpg' % lab), quality=90)
    png(pt.evaluate(HEARTS)).save(os.path.join(OUT, 'r7_hearts.png'))
    # the HUD and the panels
    pt.evaluate("()=>{const H=__HK;const L=__P.load(13,971);__P.stand(Math.floor(L.start.x/32)+3,L.start.r,1);H.P.hp=2;H.render();H.render();}")
    Image.open(io.BytesIO(pt.screenshot())).convert('RGB').crop((0, 0, 1704, 120)).save(os.path.join(OUT, 'r7_hud.png'))
    pt.evaluate("()=>{document.getElementById('title').hidden=false;}")
    pt.wait_for_timeout(300)
    pt.screenshot(path=os.path.join(OUT, 'r7_title.png'))
    pt.evaluate("()=>{document.getElementById('title').hidden=true;const q=document.getElementById('pause');q.hidden=false;document.getElementById('pTitle').textContent='Floor 13 · '+__HK.themeName(13);}")
    pt.wait_for_timeout(300)
    pt.screenshot(path=os.path.join(OUT, 'r7_pause.png'))
    man['errors'] = (pt.errs + pc.errs)[:10]
    b.close()
for f in ('r7_title.png', 'r7_pause.png'):
    Image.open(os.path.join(OUT, f)).convert('RGB').save(os.path.join(OUT, f[:-4] + '.jpg'), quality=86)
    os.remove(os.path.join(OUT, f))
json.dump(man, open(os.path.join(OUT, 'r7.json'), 'w'))
print('errors', man['errors'][:3])
