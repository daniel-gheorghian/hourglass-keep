# egyptr10.py [new.html] [old.html] [outdir]: round 10's pictures for egypt_themes.html: the prince and the robbers at the phone's
# own resolution (852x393 CSS px, the game's 1704 px canvas as on the iPhone), round 9 (old.html, default ../_r9.html) against round 10
# (new.html), and v62's figure (hk_v62_release.html): 1x crops in the game in both modes (no resampling), sheets at 3x, a run and a
# fight GIF at 1x. Run from dev/tools.
import base64, io, os, sys
from playwright.sync_api import sync_playwright
from PIL import Image
import egyptr7 as R7
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
NEW = os.path.abspath(a[0] if len(a) > 0 else os.path.join(HERE, '..', 'hourglass-keep.html'))
OLD = os.path.abspath(a[1] if len(a) > 1 else os.path.join(HERE, '..', '_r9.html'))
V62 = os.path.join(HERE, 'hk_v62_release.html')
OUT = a[2] if len(a) > 2 else os.path.join(HERE, 'egypt_themes')
# the prince by a torch on floor 5 (v62 has no setHero: its own prince)
SPOT = r"""([n])=>{const H=__HK;if(H.setHero)H.setHero('P');for(const sd of [941,942,943,944]){const L=__P.load(n,sd);for(let c=Math.floor(L.start.x/32)+3;c<L.cols-10;c++){const r=L.start.r;if(H.solidBelow(c,r)&&H.solidBelow(c+3,r)&&!L.feat[r*L.cols+c]&&L.torches.some(t=>!t.broken&&t.r===r&&Math.abs(t.c-c)<=4)){__P.stand(c,r,1);H.render();H.render();H.render();return __P.scr(H.P.x,H.P.y-30);}}}return null;}"""
# the bot plays a floor with its guards until the prince is in a fight
FIGHT0 = r"""([n,seed])=>{const H=__HK;if(H.setHero)H.setHero('P');window.__g=botGen(n,seed,{fight:true});for(let k=0;k<60*400;k++){const r=__g.next();if(r.done)return 'done';H.tick(1);const p=H.P;if(p.foe&&p.foe.alive&&Math.abs(p.foe.x-p.x)<40&&p.state==='garde'){p.inv=1e9;H.render();return __P.scr((p.x+p.foe.x)/2,p.y-30);}}return null;}"""
FIGHTN = r"""()=>{const H=__HK,p=H.P;for(let k=0;k<3;k++){const r=__g.next();if(r.done)break;H.tick(1);}p.inv=1e9;if(p.foe)p.foe.hp=Math.max(p.foe.hp,2);H.banner=null;H.render();return __P.scr(p.foe?(p.x+p.foe.x)/2:p.x,p.y-30);}"""
SHEET = r"""([rows,S])=>{const H=__HK,P=H.PS,poses=[['stand',P.stand,0],['run',P.stand,0],['jump',P.jumpR,0],['hang',P.hang,0],['guard',P.garde,1],['lunge',P.lunge,1]];
  const W=40,Hh=64,c=document.createElement('canvas');c.width=poses.length*W*S;c.height=rows.length*Hh*S;const g=c.getContext('2d');g.fillStyle='#2a2430';g.fillRect(0,0,c.width,c.height);g.setTransform(S,0,0,S,0,0);
  rows.forEach((k,j)=>{let pal;if(typeof k==='number')pal=H.guardPal({tier:k,cap:k===3});else{H.setHero(k==='old'?null:k);pal=Object.assign({},H.PAL_HERO);}
    g.fillStyle='#3a3240';g.fillRect(0,j*Hh+Hh-6,c.width,6);poses.forEach(([pn,q,sw],i)=>{if(pn==='run')q=H.mk({lean:0.2,hF:0.55,hB:-0.55,kF:0.3,kB:1.1,aF:-0.5,aB:0.5,eF:0.7,eB:0.7});
      H.drawFigureHD(g,i*W+W/2,j*Hh+Hh-6,1,q,pal,{hasSword:true,sword:!!sw,time:1.3,lt:{dir:1,col:'255,200,140',k:0.5}});});});
  H.setHero('P');return c.toDataURL('image/png');}"""


def page(b, src, mode):
    pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=2)  # (the game's canvas is 1704 px wide on the phone (dpr 3) and here alike: screenshots are its pixels 1:1)
    pg.errs = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e)))
    pg.goto('file://' + src)
    pg.wait_for_timeout(700)
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.body.classList.remove('panelOpen')")
    pg.evaluate("m=>{__HK.S.set.lightMode=m;}", mode)
    pg.evaluate(R7.JS)
    pg.add_script_tag(path=os.path.join(HERE, 'bot.js'))
    return pg


def crop(pg, xy, cw, ch):  # xy in CSS px; the crop in device px, 1:1
    im = Image.open(io.BytesIO(pg.screenshot())).convert('RGB')
    x0 = int(min(max(0, xy[0] * 2 - cw / 2), im.width - cw)); y0 = int(min(max(0, xy[1] * 2 - ch / 2), im.height - ch))
    return im.crop((x0, y0, x0 + cw, y0 + ch))


def png(d):
    return Image.open(io.BytesIO(base64.b64decode(d.split(',')[1]))).convert('RGB')


if __name__ == '__main__':
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
        errs = []
        for tag, src in (('r9', OLD), ('r10', NEW), ('v62', V62)):
            for mode in ('torch', 'classic'):
                pg = page(b, src, mode)
                if tag == 'r10' and mode == 'torch':
                    print('canvas', pg.evaluate("()=>[...document.querySelectorAll('canvas')].map(c=>c.width+'x'+c.height).join(' ')"))
                xy = pg.evaluate(SPOT, [5])
                if xy:
                    crop(pg, xy, 300, 270).save(os.path.join(OUT, 'r10_1x_%s_%s.png' % (tag, mode)))
                if tag != 'v62':
                    xy = pg.evaluate(FIGHT0, [6, 4106])
                    if xy and xy != 'done':
                        crop(pg, xy, 420, 270).save(os.path.join(OUT, 'r10_1x_fight_%s_%s.png' % (tag, mode)))
                if tag == 'r10' and mode == 'torch':
                    fr = []
                    for k in range(40):
                        xy = pg.evaluate(FIGHTN)
                        fr.append(crop(pg, xy, 420, 270))
                    fr[0].save(os.path.join(OUT, 'r10_fight.gif'), save_all=True, append_images=fr[1:], duration=50, loop=0, optimize=True)
                    fr = []
                    pg.evaluate("()=>{const H=__HK;H.setHero('P');const L=__P.load(9,951);__P.stand(Math.floor(L.start.x/32)+2,L.start.r,1);H.setKey('kb','r',true);}")
                    for k in range(26):
                        xy = pg.evaluate("()=>{const H=__HK;H.tick(4);H.P.inv=1e9;H.banner=null;H.render();return __P.scr(H.P.x,H.P.y-30);}")
                        fr.append(crop(pg, xy, 420, 270))
                    pg.evaluate("()=>__HK.setKey('kb','r',false)")
                    fr[0].save(os.path.join(OUT, 'r10_run.gif'), save_all=True, append_images=fr[1:], duration=67, loop=0, optimize=True)
                if mode == 'torch' and tag != 'v62':
                    png(pg.evaluate(SHEET, [['old', 'P', 0, 1, 3], 3])).save(os.path.join(OUT, 'r10_sheet3x_%s.png' % tag))
                    png(pg.evaluate(SHEET, [['P', 1], 3])).save(os.path.join(OUT, 'r10_sheet3x_small_%s.png' % tag))
                errs += pg.errs
                pg.close()
        print('errors', errs[:3])
        b.close()
