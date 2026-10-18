# egyptr8.py [file.html] [outdir]: round 8's pictures for egypt_themes.html: the three timekeeper concepts (A Nut's sky clock, built
# in; B the barque passing the twelve gates; C the diagonal star clock) at a large size, at HUD and at gate-clock size, full, half and
# nearly out; the sky clock running and in the rewind (GIF); in the game (checkpoint, HUD, a gate's clock, the rewind); and the
# rebalanced glass jars. Writes r8.json. Run from dev/tools.
import base64, io, json, os, sys
from playwright.sync_api import sync_playwright
from PIL import Image
import egyptr7 as R7
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
SRC = a[0] if len(a) > 0 else os.path.join(HERE, '..', 'hourglass-keep.html')
OUT = a[1] if len(a) > 1 else os.path.join(HERE, 'egypt_themes')
CLOCK = r'''([kind,f,s,rev,t])=>{const H=__HK,c=document.createElement('canvas'),Z=s*10;c.width=Math.round(Z*2.2);c.height=Math.round(Z*2);const g=c.getContext('2d');g.fillStyle='#120e18';g.fillRect(0,0,c.width,c.height);
  g.translate(c.width/2,c.height/2);g.scale(Z/10,Z/10);if(kind==='A')H.nutClock(g,f,{s:1,t,rev,glow:true});else H.conceptClock2(g,kind,f,1);return c.toDataURL('image/png');}'''
GATE = r'''()=>{const H=__HK;for(const n of [6,7,10,11,14,18]){for(const sd of [821,822,823]){const L=__P.load(n,sd);const o=L.dyn.find(o=>o.f.t==='gate'&&o.f.dur>0&&!o.f.latch&&H.solidBelow(o.c-2,o.r));if(!o)continue;
  __P.stand(o.c-2,o.r,1);o.f.tm=o.f.dur*0.55;o.f.open=1;o.f.heldAt=-9;H.render();H.render();H.render();return __P.scr(o.c*32+16,(o.r+1)*64-50);}}return null;}'''
REW = r'''()=>{const H=__HK;const L=__P.load(13,824);H.S.sands=3;H.mode='play';for(let k=0;k<240;k++){H.P.inv=1e9;H.tick(1);}H.P.inv=0;H.hurt(9,'fall');H.tick(50);H.startRewind();H.tick(14);H.render();H.render();return 1;}'''


HAIR = r"""()=>{const H=__HK,P=H.PS,opts=[['fillet','own hair, linen fillet (built in)'],['wig','short rounded wig'],['lock','close crop, side lock'],['long','long, tied back']];
  const S=3,W=44,Hh=64,c=document.createElement('canvas');c.width=opts.length*W*S;c.height=Hh*S;const g=c.getContext('2d');g.fillStyle='#2a2430';g.fillRect(0,0,c.width,c.height);g.setTransform(S,0,0,S,0,0);
  H.setHero('P');opts.forEach(([k],i)=>{const pal=Object.assign({},H.PAL_HERO,{hairStyle:k});H.drawFigureHD(g,i*W+W/2,Hh-6,1,P.stand,pal,{hasSword:true,time:1.3,lt:{dir:1,col:'255,200,140',k:0.5}});});return c.toDataURL('image/png');}"""
SPOT = r"""([n])=>{const H=__HK;H.setHero('P');for(const sd of [941,942,943,944]){const L=__P.load(n,sd);for(let c=Math.floor(L.start.x/32)+3;c<L.cols-10;c++){const r=L.start.r;if(H.solidBelow(c,r)&&H.solidBelow(c+3,r)&&!L.feat[r*L.cols+c]&&L.torches.some(t=>!t.broken&&t.r===r&&Math.abs(t.c-c)<=4)){__P.stand(c,r,1);H.render();H.render();H.render();return __P.scr(H.P.x,H.P.y-30);}}}return null;}"""


def png(d):
    return Image.open(io.BytesIO(base64.b64decode(d.split(',')[1]))).convert('RGB')


with sync_playwright() as p:
    b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
    R7.SRC = SRC
    pt, pc = R7.page(b, 'torch'), R7.page(b, 'classic')
    for kind in ('A', 'B', 'C'):
        for f in (1.0, 0.5, 0.1):
            png(pt.evaluate(CLOCK, [kind, f, 4, False, 1.0])).save(os.path.join(OUT, 'r8_clock_%s_%d.png' % (kind, int(f * 10))))
        png(pt.evaluate(CLOCK, [kind, 0.6, 0.86, False, 1.0])).resize((57, 51), Image.NEAREST).save(os.path.join(OUT, 'r8_clock_%s_hud.png' % kind))
        png(pt.evaluate(CLOCK, [kind, 0.6, 0.64, False, 1.0])).resize((42, 39), Image.NEAREST).save(os.path.join(OUT, 'r8_clock_%s_gate.png' % kind))
    fr = [png(pt.evaluate(CLOCK, ['A', 1 - k / 23, 4, False, k * 0.08])) for k in range(24)] + [png(pt.evaluate(CLOCK, ['A', k / 15, 4, True, k * 0.08])) for k in range(16)]
    fr[0].save(os.path.join(OUT, 'r8_clock_run.gif'), save_all=True, append_images=fr[1:], duration=90, loop=0, optimize=True)
    for lab, pg in (('torch', pt), ('classic', pc)):
        xy = pg.evaluate(R7.CP)
        if xy:
            R7.crop(Image.open(io.BytesIO(pg.screenshot())).convert('RGB'), xy, 360, 260).save(os.path.join(OUT, 'r8_clock_game_%s.jpg' % lab), quality=90)
        xy = pg.evaluate(GATE)
        if xy:
            R7.crop(Image.open(io.BytesIO(pg.screenshot())).convert('RGB'), xy, 360, 260).save(os.path.join(OUT, 'r8_gate_%s.jpg' % lab), quality=90)
        pg.evaluate(REW)
        Image.open(io.BytesIO(pg.screenshot())).convert('RGB').resize((852, 393), Image.LANCZOS).save(os.path.join(OUT, 'r8_rewind_%s.jpg' % lab), quality=86)
    pt.evaluate("()=>{const H=__HK;const L=__P.load(13,971);__P.stand(Math.floor(L.start.x/32)+3,L.start.r,1);H.P.hp=2;H.S.sands=2;H.render();H.render();}")
    Image.open(io.BytesIO(pt.screenshot())).convert('RGB').crop((0, 0, 1704, 120)).save(os.path.join(OUT, 'r8_hud.png'))
    png(pt.evaluate(R7.JARS, [1, 0, 3])).save(os.path.join(OUT, 'r8_jars.png'))
    fr = [png(pt.evaluate(R7.JARS, [1 - k / 19 if k > 3 else 1, min(0.9, k * 0.06), k * 0.4])) for k in range(20)]
    fr[0].save(os.path.join(OUT, 'r8_jars_drink.gif'), save_all=True, append_images=fr[1:], duration=110, loop=0, optimize=True)
    for lab, pg in (('torch', pt), ('classic', pc)):
        xy = pg.evaluate(R7.ITEM)
        if xy:
            R7.crop(Image.open(io.BytesIO(pg.screenshot())).convert('RGB'), xy, 360, 240).save(os.path.join(OUT, 'r8_jar_game_%s.jpg' % lab), quality=90)
    # the prince (round 8): v62, round 7 and round 8 side by side; the hair options; running; on the darkest themes' floors
    png(pt.evaluate(R7.FIGS, [['old', 'R7', 'P']])).save(os.path.join(OUT, 'r8_prince_compare.png'))
    png(pt.evaluate(HAIR)).save(os.path.join(OUT, 'r8_prince_hair.png'))
    frames = []
    for k in range(22):
        if k == 0:
            pt.evaluate("()=>{const H=__HK;H.setHero('P');const L=__P.load(9,951);__P.stand(Math.floor(L.start.x/32)+2,L.start.r,1);H.setKey('kb','r',true);}")
        xy = pt.evaluate("()=>{const H=__HK;H.tick(4);H.P.inv=1e9;H.banner=null;H.render();return __P.scr(H.P.x,H.P.y-30);}")
        frames.append(R7.crop(Image.open(io.BytesIO(pt.screenshot())).convert('RGB'), xy, 480, 300).resize((360, 225), Image.LANCZOS))
    pt.evaluate("()=>__HK.setKey('kb','r',false)")
    frames[0].save(os.path.join(OUT, 'r8_prince_run.gif'), save_all=True, append_images=frames[1:], duration=67, loop=0, optimize=True)
    for look in ('osiris', 'nun', 'hawara', 'meroe'):
        for lab, pg in (('torch', pt), ('classic', pc)):
            n = pg.evaluate("l=>__HK.floorsOf(l)[0]", look)
            xy = pg.evaluate(SPOT, [n])
            if xy:
                R7.crop(Image.open(io.BytesIO(pg.screenshot())).convert('RGB'), xy, 300, 240).save(os.path.join(OUT, 'r8_prince_on_%s_%s.jpg' % (look, lab)), quality=90)
    errs = (pt.errs + pc.errs)[:10]
    b.close()
json.dump({'errors': errs}, open(os.path.join(OUT, 'r8.json'), 'w'))
print('errors', errs[:3])
