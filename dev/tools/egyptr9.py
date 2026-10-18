# egyptr9.py [file.html] [outdir]: round 9's pictures for egypt_themes.html: the prince of round 8 and round 9 side by side (the
# chest before and after is r9_prince_before/after, drawn before and after the change), the hair options on the figure at 3x and in the
# game at game size in both modes, and a running GIF. Run from dev/tools.
import io, json, os, sys
from playwright.sync_api import sync_playwright
from PIL import Image
import egyptr7 as R7
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
SRC = a[0] if len(a) > 0 else os.path.join(HERE, '..', 'hourglass-keep.html')
OUT = a[1] if len(a) > 1 else os.path.join(HERE, 'egypt_themes')
HAIRS = ['crop', 'curls', 'bob']
SHEET = r"""([hs])=>{const H=__HK,P=H.PS,S=3,W=44,Hh=64,c=document.createElement('canvas');c.width=hs.length*W*S;c.height=Hh*S;const g=c.getContext('2d');g.fillStyle='#2a2430';g.fillRect(0,0,c.width,c.height);g.setTransform(S,0,0,S,0,0);
  H.setHero('P');hs.forEach((k,i)=>{H.drawFigureHD(g,i*W+W/2,Hh-6,1,P.stand,Object.assign({},H.PAL_HERO,{hairStyle:k}),{hasSword:true,time:1.3,lt:{dir:1,col:'255,200,140',k:0.5}});});return c.toDataURL('image/png');}"""
SPOT = r"""([n,hs])=>{const H=__HK;H.setHero('P');H.PAL_HERO.hairStyle=hs;for(const sd of [941,942,943,944]){const L=__P.load(n,sd);for(let c=Math.floor(L.start.x/32)+3;c<L.cols-10;c++){const r=L.start.r;if(H.solidBelow(c,r)&&H.solidBelow(c+3,r)&&!L.feat[r*L.cols+c]&&L.torches.some(t=>!t.broken&&t.r===r&&Math.abs(t.c-c)<=4)){__P.stand(c,r,1);H.render();H.render();H.render();return __P.scr(H.P.x,H.P.y-30);}}}return null;}"""
if __name__ == '__main__':
    import base64
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
        R7.SRC = SRC
        pt, pc = R7.page(b, 'torch'), R7.page(b, 'classic')
        d = pt.evaluate(SHEET, [HAIRS])
        Image.open(io.BytesIO(base64.b64decode(d.split(',')[1]))).convert('RGB').save(os.path.join(OUT, 'r9_hair_sheet.png'))
        for hs in HAIRS:
            for lab, pg in (('torch', pt), ('classic', pc)):
                xy = pg.evaluate(SPOT, [5, hs])
                if xy:
                    R7.crop(Image.open(io.BytesIO(pg.screenshot())).convert('RGB'), xy, 220, 200).save(os.path.join(OUT, 'r9_hair_%s_%s.jpg' % (hs, lab)), quality=92)
        for pg in (pt, pc):
            pg.evaluate("()=>__HK.setHero('P')")
        d = pt.evaluate(R7.FIGS, [['P']])
        frames = []
        for k in range(22):
            if k == 0:
                pt.evaluate("()=>{const H=__HK;H.setHero('P');const L=__P.load(9,951);__P.stand(Math.floor(L.start.x/32)+2,L.start.r,1);H.setKey('kb','r',true);}")
            xy = pt.evaluate("()=>{const H=__HK;H.tick(4);H.P.inv=1e9;H.banner=null;H.render();return __P.scr(H.P.x,H.P.y-30);}")
            frames.append(R7.crop(Image.open(io.BytesIO(pt.screenshot())).convert('RGB'), xy, 480, 300).resize((360, 225), Image.LANCZOS))
        pt.evaluate("()=>__HK.setKey('kb','r',false)")
        frames[0].save(os.path.join(OUT, 'r9_prince_run.gif'), save_all=True, append_images=frames[1:], duration=67, loop=0, optimize=True)
        print('errors', (pt.errs + pc.errs)[:3])
        b.close()
