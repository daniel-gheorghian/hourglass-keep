# egyptr12.py [new.html] [old.html] [outdir]: round 12's pictures for egypt_themes.html: the portcullis, the roof block, the sand-filled
# shaft under a slab and the plugs, before (old.html, default ../_r11.html, made with git show d50648e:dev/hourglass-keep.html) and after,
# in the game at the phone's resolution (crops of the 1704 px canvas, 1:1; the enlarged rows at 3x, smoothed), both modes; the stones'
# textures; each theme's slab at gate size; the roof block in three themes, worn and clean; GIFs of the pour, of the prince jumping a
# fallen block, of the sand shaft giving way and of the chase. Run from dev/tools.
import ast, base64, io, os, sys
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
NEW = os.path.abspath(a[0] if len(a) > 0 else os.path.join(HERE, '..', 'hourglass-keep.html'))
OLD = os.path.abspath(a[1] if len(a) > 1 else os.path.join(HERE, '..', '_r11.html'))
OUT = a[2] if len(a) > 2 else os.path.join(HERE, 'egypt_themes')
PC = {n.targets[0].id: n.value.value for n in ast.parse(open(os.path.join(HERE, 'egyptprop.py')).read()).body if isinstance(n, ast.Assign) and isinstance(n.value, ast.Constant) and isinstance(n.targets[0], ast.Name)}
F = lambda ns: [[n, s] for n in ns for s in (801, 802, 803)]
WHITE = (240, 230, 210)
GATE = r"""([q,open])=>{const H=__HK;H.EGP.traps=true;H.EGP.plug=true;__P.load(q.n,q.seed);const L=H.L;__P.stand(q.pc,q.r,q.face);
  const o=L.dyn.find(o=>o.c===q.c&&o.r===q.r);o.f.open=open;o.f.tm=open>0?99:0;o.f.heldAt=-9;__P.draw();o.f.open=open;__P.draw();return __P.scr(q.c*32+16,(q.r+1)*64-34);}"""
STONEF = r"""([q,state,wear,look])=>{const H=__HK;H.EGP.traps=true;H.EGP.wear=wear<0?undefined:wear;__P.load(q.n,q.seed);const L=H.L;
  if(look){const T=H.THEMES.find(t=>t.look===look);if(T){L.theme=T;H.clearRooms();}}
  __P.stand(q.pc,q.r,q.face);const C=L.cols,o=L.dyn.find(o=>o.c===q.c&&o.r===q.r);
  if(state==='lying'){o.f.s=3;L.rubble.add(q.r*C+q.c);H.clearRooms();}
  let rr=q.r-1;while(rr>=0&&L.base[rr*C+q.c]!==2)rr--;const cy=(rr+1)*64,fy=(q.r+1)*64-4,lift=state==='lying'?0:Math.max(0,fy-cy-60);if(lift){H.P.state='dead';H.cam.y-=lift;H.cam.gy-=lift;} // (the ceiling in view: the camera holds where it is put while he is 'dead', out of the crop)
  __P.draw();__P.draw();H.EGP.wear=undefined;return {cam:H.cam.y,c:__P.scr(q.c*32+16,cy+12),f:__P.scr(q.c*32+16,fy-26),m:__P.scr(q.c*32+16,(cy+fy)/2),h:(fy-cy)};}"""
SHEETS = r"""([kinds,looks])=>{const H=__HK,S=2,out=[];for(const k of kinds){const c=H.stoneTex(k,72,72);out.push(['s',k,c.toDataURL('image/png')]);}
  for(const lk of looks){const c=H.stoneTex(H.SLAB_STONE[lk],24,72,lk);out.push(['m',lk,c.toDataURL('image/png')]);}return out;}"""


def page(b, src, mode):
    pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=2)
    pg.errs = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e)))
    pg.goto('file://' + src)
    pg.wait_for_timeout(700)
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true)")
    pg.evaluate("m=>{__HK.S.set.lightMode=m;if(__HK.GLP)__HK.GLP.pipe=false;}", mode)
    pg.evaluate(PC['JS'])
    pg.add_script_tag(path=os.path.join(HERE, 'bot.js'))
    return pg


def shot(pg):
    return Image.open(io.BytesIO(pg.screenshot())).convert('RGB')


def crop(im, xy, cw, ch):
    x0 = int(min(max(0, xy[0] * 2 - cw / 2), im.width - cw)); y0 = int(min(max(0, xy[1] * 2 - ch / 2), im.height - ch))
    return im.crop((x0, y0, x0 + cw, y0 + ch))


def label(im, txt, xy=(4, 3)):
    ImageDraw.Draw(im).text(xy, txt, fill=WHITE)
    return im


def grid(tiles, cols, pad=2):
    w, h = tiles[0].size
    rows = (len(tiles) + cols - 1) // cols
    g = Image.new('RGB', (cols * w + (cols - 1) * pad, rows * h + (rows - 1) * pad), (20, 16, 24))
    for i, t in enumerate(tiles):
        g.paste(t, ((i % cols) * (w + pad), (i // cols) * (h + pad)))
    return g


def stack(ims, pad=6):
    w = max(i.width for i in ims)
    g = Image.new('RGB', (w, sum(i.height for i in ims) + pad * (len(ims) - 1)), (20, 16, 24))
    y = 0
    for i in ims:
        g.paste(i, (0, y)); y += i.height + pad
    return g


def gif(frames, fn, ms):
    frames[0].save(os.path.join(OUT, fn), save_all=True, append_images=frames[1:], duration=ms, loop=0, optimize=True)


if __name__ == '__main__':
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
        errs = []
        P = {(t, m): page(b, s, m) for t, s in (('before', OLD), ('after', NEW)) for m in ('torch', 'classic')}
        pn = P[('after', 'torch')]
        # ---- the portcullis: raised, half-way, closed, before and after, both modes; the closed slab enlarged 3x
        gq = pn.evaluate(PC['FINDF'], [F([6, 7, 26, 27]), ['gate'], 1, 2])[0]
        rows, big = [], []
        for m in ('torch', 'classic'):
            for t in ('before', 'after'):
                pg = P[(t, m)]; tl = []
                for op, nm in ((1, 'raised'), (0.5, 'half-way'), (0, 'closed')):
                    xy = pg.evaluate(GATE, [gq, op]); im = shot(pg); tl.append(label(crop(im, xy, 220, 230), '%s %s, %s' % (t, m, nm)))
                    if op == 0:
                        big.append(label(crop(im, xy, 96, 110).resize((288, 330), Image.LANCZOS), '%s %s 3x' % (t, m)))
                rows.append(grid(tl, 3))
        stack([stack(rows, 2), grid(big, 4)]).save(os.path.join(OUT, 'r12_gate_persp.png'))
        # ---- the stones and each theme's carved slab, as generated (2x)
        looks = pn.evaluate("__HK.THEMES.map(t=>t.look)")
        kinds = ['granite', 'syenite', 'quartzite', 'sandstone', 'limestone', 'greywacke', 'mudbrick', 'kershef']
        tex = pn.evaluate(SHEETS, [kinds, looks])
        sw = [label(Image.open(io.BytesIO(base64.b64decode(d.split(',')[1]))).convert('RGB').resize((144, 144), Image.LANCZOS), k) for t, k, d in tex if t == 's']
        ms = [label(Image.open(io.BytesIO(base64.b64decode(d.split(',')[1]))).convert('RGB').resize((48, 144), Image.LANCZOS), k[:5]) for t, k, d in tex if t == 'm']
        stack([grid(sw, 8), grid(ms, 12)]).save(os.path.join(OUT, 'r12_stones.png'))
        # ---- each theme's slab at gate size, closed, in the game (Torchlight above, Classic below)
        tl = []
        for m in ('torch', 'classic'):
            pg = P[('after', m)]
            for lk in looks:
                fl = pg.evaluate("lk=>__HK.floorsOf(lk,180)", lk)
                qs = pg.evaluate(PC['FINDF'], [F([f + i for f in fl[:4] for i in range(4)]), ['gate'], 1, 2])
                if not qs:
                    print('no gate', lk); continue
                xy = pg.evaluate(GATE, [qs[0], 0]); tl.append(label(crop(shot(pg), xy, 150, 190), lk))
        grid(tl, 12).save(os.path.join(OUT, 'r12_gate_themes.png'))
        # ---- the roof block: hanging and lying, before and after, both modes
        sq = pn.evaluate(PC['FINDF'], [F([2, 3, 4, 41, 42, 43]), ['stone'], 1, 3])[0]
        rows = []
        for m in ('torch', 'classic'):
            for t in ('before', 'after'):
                pg = P[(t, m)]; tl = []
                for st in ('hang', 'lying'):
                    r = pg.evaluate(STONEF, [sq, st, -1, None]); tl.append(label(crop(shot(pg), r['c'] if st == 'hang' else r['f'], 260, 300), '%s %s, %s' % (t, m, st)))
                rows.append(grid(tl, 2))
        grid(rows, 2, 6).save(os.path.join(OUT, 'r12_roof_persp.png'))
        # ---- the same block in four themes, clean and worn (Torchlight)
        tl = []
        for lk in ('west', 'napata', 'deffufa', 'aksum'):
            for w in (0, 3):
                for st in ('hang', 'lying'):
                    r = pn.evaluate(STONEF, [sq, st, w, lk]); tl.append(label(crop(shot(pn), r['c'] if st == 'hang' else r['f'], 200, 260), '%s %s %s' % (lk, 'worn' if w else 'clean', st)))
        grid(tl, 8).save(os.path.join(OUT, 'r12_roof_themes.png'))
        # ---- the pour: idle trickle, shifting, letting go, falling, landing, settling (Torchlight)
        r = pn.evaluate(STONEF, [sq, 'hang', -1, None]); xy = r['m']; ch = int(min(780, (r['f'][1] - r['c'][1]) * 2 + 200)); fr = []
        for k in range(70):
            if k == 8:
                pn.evaluate("q=>{const o=__HK.L.dyn.find(o=>o.c===q.c&&o.r===q.r);o.f.s=1;o.f.tm=0;}", sq)
            pn.evaluate("cy=>{const H=__HK;H.tick(2);H.cam.y=cy;H.cam.gy=cy;H.P.inv=1e9;H.render();}", r['cam'])
            fr.append(crop(shot(pn), xy, 280, ch).resize((210, ch * 3 // 4), Image.LANCZOS))
        gif(fr, 'r12_roof_pour.gif', 66)
        # ---- the prince jumping a fallen block (Torchlight)
        r = pn.evaluate(STONEF, [sq, 'lying', -1, None]); fr = []
        pn.evaluate("q=>{const H=__HK;H.setKey('kb',q.face>0?'r':'l',true);}", sq)
        for k in range(46):
            xy = pn.evaluate("q=>{const H=__HK,P=H.P;if(P.state==='run'&&Math.abs(P.x-(q.c*32+16))<60&&!window.__jp){window.__jp=1;H.setKey('kb','j',true);}H.tick(2);H.setKey('kb','j',false);P.inv=1e9;H.render();return __P.scr(q.c*32+16,(q.r+1)*64-30);}", sq)
            fr.append(crop(shot(pn), xy, 360, 260))
        pn.evaluate("()=>{__HK.setKey('kb','r',false);__HK.setKey('kb','l',false);window.__jp=0;}")
        print('jump', pn.evaluate("q=>{const P=__HK.P;return [P.x-(q.c*32+16),P.state,P.hp]}", sq))
        gif(fr, 'r12_roof_jump.gif', 66)
        # ---- the sand-filled shaft under a slab: shifting, giving way, the puff, settling (Torchlight)
        lq = pn.evaluate(PC['FINDF'], [F([10, 11, 30, 31, 45, 46, 47]), ['loose'], 1, 3])[0]
        r = pn.evaluate(STONEF, [lq, 'x', -1, None]); xy = pn.evaluate("q=>__P.scr(q.c*32+16,(q.r+1)*64+20)", lq); fr = []
        for k in range(56):
            if k == 4:
                pn.evaluate("q=>{const o=__HK.L.dyn.find(o=>o.c===q.c&&o.r===q.r);o.f.s=1;o.f.tm=0;}", lq)
            pn.evaluate("()=>{const H=__HK;H.tick(2);H.P.inv=1e9;H.render();}")
            fr.append(crop(shot(pn), xy, 260, 300))
        gif(fr, 'r12_sandfloor.gif', 66)
        # ---- the plugs: before and after, both modes; the chase (Torchlight)
        for pg in P.values():
            pg.evaluate("()=>{__HK.GLFX.storm2=false;__HK.GLFX.storm=false;}")
        cq = pn.evaluate(PC['CHASEF'], [F([41, 42, 43, 44, 45, 46, 47, 48])])[0]
        tl = []
        for m in ('torch', 'classic'):
            for t in ('before', 'after'):
                pg = P[(t, m)]; xy = pg.evaluate(PC['SHOW'], [cq, {'traps': True, 'plug': True}, 'chase']); tl.append(label(crop(shot(pg), [xy[0] - 50, xy[1] - 10], 600, 340), '%s %s' % (t, m)))
        grid(tl, 2).save(os.path.join(OUT, 'r12_plug_persp.png'))
        xy = pn.evaluate(PC['SHOW'], [cq, {'traps': True, 'plug': True}, 'chase']); fr = []
        pn.evaluate("()=>{const H=__HK;H.setKey('kb','r',true);}")
        for k in range(40):
            xy = pn.evaluate("()=>{const H=__HK;H.tick(2);H.P.inv=1e9;H.render();return __P.scr(H.P.x-40,H.P.y-30);}")
            fr.append(crop(shot(pn), xy, 360, 240))
        pn.evaluate("()=>__HK.setKey('kb','r',false)")
        gif(fr, 'r12_plug.gif', 66)
        for pg in P.values():
            errs += pg.errs
        print('errors', errs[:4])
        b.close()
