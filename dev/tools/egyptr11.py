# egyptr11.py [new.html] [old.html] [outdir]: round 11's pictures for egypt_themes.html: the prince's belt before (old.html, default
# ../_r10.html, made with git show 6241add:dev/hourglass-keep.html) and after, in the game at the phone's resolution (crops of the
# 1704 px canvas, 1:1), standing, running, in a jump, hanging and fighting, the bot playing; one sheet per mode. It also refreshes the
# in-game shots of the sections still current (the sky clock at the checkpoint, a gate's clock, the rewind, the HUD, a flask on the
# floor) so that they show the current figure. Run from dev/tools.
import ast, io, os, sys
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw
import egyptr7 as R7
import egyptr10 as R10
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
NEW = os.path.abspath(a[0] if len(a) > 0 else os.path.join(HERE, '..', 'hourglass-keep.html'))
OLD = os.path.abspath(a[1] if len(a) > 1 else os.path.join(HERE, '..', '_r10.html'))
OUT = a[2] if len(a) > 2 else os.path.join(HERE, 'egypt_themes')
R8C = {n.targets[0].id: n.value.value for n in ast.parse(open(os.path.join(HERE, 'egyptr8.py')).read()).body if isinstance(n, ast.Assign) and isinstance(n.value, ast.Constant)}
# the bot plays a floor until the prince is in the state asked for
BOT = r"""([runs,fight,cond])=>{const H=__HK,f=new Function('p','H','return '+cond);if(H.setHero)H.setHero('P');for(const [n,seed] of runs){window.__g=botGen(n,seed,{fight});
  for(let k=0;k<60*500;k++){const r=__g.next();if(r.done)break;H.tick(1);H.intro=0;H.banner=null;const p=H.P;p.inv=1e9;if(f(p,H)){document.querySelectorAll('.screen').forEach(e=>e.hidden=true);H.render();H.render();return __P.scr(p.foe&&fight?(p.x+p.foe.x)/2:p.x,p.y-(p.state==='climb'||p.state==='hang'?58:30));}}}return null;}"""
RUNS = [[3, 4103], [4, 4104], [5, 4105], [7, 4107], [9, 4109]]
POSES = [('stand', RUNS, False, "p.state==='stand'&&p.t>0.15&&H.P.x>H.L.start.x+96"), ('run', RUNS, False, "p.state==='run'&&p.t>0.35"), ('jump', RUNS, False, "p.state==='air'&&Math.abs(p.vy)<70&&Math.abs(p.vx)>40"),
         ('hang', RUNS, False, "(p.state==='hang'&&p.t>0.1)||(p.state==='climb'&&p.t>0.05&&p.t<0.2)"), ('fight', [[6, 4106], [9, 4109]], True, "p.foe&&p.foe.alive&&Math.abs(p.foe.x-p.x)<40&&p.state==='strike'&&p.t>0.12")]
W, Hh = 240, 230

if __name__ == '__main__':
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
        errs = []
        for mode in ('torch', 'classic'):
            sh = Image.new('RGB', (len(POSES) * W, 2 * Hh + 2), (20, 16, 24))
            for j, src in enumerate((OLD, NEW)):
                pg = R10.page(b, src, mode)
                for i, (nm, runs, fight, cond) in enumerate(POSES):
                    xy = pg.evaluate(BOT, [runs, fight, cond])
                    if xy:
                        sh.paste(R10.crop(pg, xy, W, Hh), (i * W, j * (Hh + 2)))
                    else:
                        print('no', nm, mode, j)
                errs += pg.errs
                if src == NEW:
                    # the current sections' in-game shots, with the current figure
                    xy = pg.evaluate(R7.CP)
                    if xy:
                        R10.crop(pg, xy, 360, 260).save(os.path.join(OUT, 'r8_clock_game_%s.jpg' % mode), quality=90)
                    xy = pg.evaluate(R8C['GATE'])
                    if xy:
                        R10.crop(pg, xy, 360, 260).save(os.path.join(OUT, 'r8_gate_%s.jpg' % mode), quality=90)
                    xy = pg.evaluate(R7.ITEM)
                    if xy:
                        R10.crop(pg, xy, 360, 240).save(os.path.join(OUT, 'r9_flask_game_%s.jpg' % mode), quality=90)
                    pg.evaluate(R8C['REW'])
                    Image.open(io.BytesIO(pg.screenshot())).convert('RGB').resize((852, 393), Image.LANCZOS).save(os.path.join(OUT, 'r8_rewind_%s.jpg' % mode), quality=86)
                    if mode == 'torch':
                        pg.evaluate("()=>{const H=__HK;const L=__P.load(13,971);__P.stand(Math.floor(L.start.x/32)+3,L.start.r,1);H.P.hp=2;H.S.sands=2;H.render();H.render();}")
                        Image.open(io.BytesIO(pg.screenshot())).convert('RGB').crop((0, 0, 1704, 120)).save(os.path.join(OUT, 'r8_hud.png'))
                pg.close()
            d = ImageDraw.Draw(sh)
            for i, (nm, *_) in enumerate(POSES):
                d.text((i * W + 6, 4), nm, fill=(240, 230, 210))
            d.text((W * len(POSES) - 70, 4), 'round 10', fill=(240, 230, 210)); d.text((W * len(POSES) - 70, Hh + 6), 'round 11', fill=(240, 230, 210))
            sh.save(os.path.join(OUT, 'r11_sash_%s.png' % mode))
        print('errors', errs[:3])
        b.close()
