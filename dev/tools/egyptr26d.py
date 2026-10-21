# egyptr26d.py [new.html] [old.html]: round 26d's pictures (owner: "the domino sand effect needs to be more organic and less mechanically
# domino. On two columns of sand it works, on more than two it doesn't"), into egypt_themes/:
#   r26d_sand.png  frame strips, before | after, Torchlight and Classic, of sand wells under rows of two, three and five cracked slabs giving
#                  way: two slabs (floor 7 seed 801, a pit two storeys deep) and three (floor 7 seed 802, two storeys) set off from the left
#                  0.32 s apart (his running pace, RUN 100 px/s), five (floor 5 seed 801, one storey) the side passage's chain armed by its
#                  plate (the game's own countdown, 0.36 s apart); a frame every 0.1 s (five: 0.2 s) from the first trigger, at 0.6 of the
#                  2x screenshot
#   r26d_sand.gif  in game (Torchlight, the phone's resolution, half the 2x screenshot, from 1 s), before | after: the side passage on floor 5 seed 801 armed as its
#                  flask's tile arms it (the chain's countdown, armPassage), the prince running across the row of five as it gives way behind him
# --nogif: the strips only; --gifonly: the GIF only. old.html defaults to round 26c's source (git show bfe48b8:dev/hourglass-keep.html). Run from dev/tools.
import os, subprocess, sys, tempfile, shutil
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright
import egyptr12 as R12

HERE = os.path.dirname(os.path.abspath(__file__))
a = [x for x in sys.argv[1:] if not x.startswith('--')]
NEW = os.path.abspath(a[0] if a else os.path.join(HERE, '..', 'hourglass-keep.html'))
OLD = a[1] if len(a) > 1 else None
OUTD = os.environ.get('HK_R26D_OUT') or os.path.join(HERE, 'egypt_themes')
INK = (20, 16, 24)
TXT = (250, 240, 215)
# (label, floor, seed, first column, row, slabs, mode): 'run' sets each off 0.32 s after the one to its left; 'chain' arms the side passage
CASES = [('two slabs, two storeys deep', 7, 801, 347, 54, 2, 'run'),
         ('three slabs, two storeys deep', 7, 802, 63, 22, 3, 'run'),
         ('five slabs (a chain), one storey', 5, 801, 26, 35, 5, 'chain')]
SET = r'''([q,rs])=>{const H=__HK;H.EGP.traps=true;const [_,n,sd,c,r,w,mode]=q;const L=__P.load(n,sd);
  __P.stand(c-8,r,1);if(mode==='chain'){const p=L.dyn.find(o=>o.f.chain&&L.dyn.some(d=>o.f.chain.includes(d.f)&&d.r===r&&d.c>=c&&d.c<c+w));if(p){p.f.armed=1;p.f.chain.forEach((t,k)=>{t.s=1;t.tm=-(0.2+0.36*k);});}}
  H.P.x=-9999;H.P.y=-9999;H.P.inv=1e9;window.__q=q;window.__rs=rs;window.__t0=H.gameTime;window.__go=-1;return 1;}'''
STEP = r'''(nt)=>{const H=__HK,[_,n,sd,c,r,w,mode]=__q,os=H.L.dyn.filter(o=>o.f.t==='loose'&&o.r===r&&o.c>=c&&o.c<c+w).sort((p,q)=>p.c-q.c);
  for(let i=0;i<nt;i++){if(mode==='run')os.forEach((o,k)=>{if(o.f.s===0&&H.gameTime-__t0>=0.32*k){o.f.s=1;o.f.tm=0;}});H.tick(1);H.P.x=-9999;H.P.y=-9999;
    if(__go<0&&os.some(o=>o.f.s===1&&o.f.tm>=0))__go=H.gameTime;}
  H.P.inv=1e9;H.banner=null;H.cam.x=(c+w/2)*32-H.viewW/2;H.cam.y=r*64-40;H.cam.gy=H.cam.y;if(H.GLP){H.GLP.rs=__rs;H.GLP.pipe=false;}H.render();H.render();
  return {xy:__P.scr((c+w/2)*32,(r+1)*64+(w>4?14:44)),st:os.map(o=>[o.f.s,+o.f.tm.toFixed(2)]),go:__go<0?null:+(H.gameTime-__go).toFixed(2)};}'''


def old_src(tmp):
    if OLD:
        return os.path.abspath(OLD)
    fn = os.path.join(tmp, '_r26c.html')
    open(fn, 'w', encoding='utf-8').write(subprocess.run(['git', 'show', 'bfe48b8:dev/hourglass-keep.html'], cwd=HERE, capture_output=True, text=True, check=True).stdout)
    return fn


def label(im, t, xy=(4, 2)):
    d = ImageDraw.Draw(im)
    d.rectangle((xy[0] - 2, xy[1] - 1, xy[0] + 6 * len(t) + 4, xy[1] + 12), fill=(0, 0, 0))
    d.text(xy, t, fill=TXT)
    return im


def strip(pg, q, n_fr=10, every=0.1, cw=None, ch=None):
    cw = cw or q[5] * 132 + 120
    ch = ch or (330 if q[5] > 4 else 450)
    pg.evaluate(SET, [list(q), 1])
    fr = []
    for k in range(400):
        r = pg.evaluate(STEP, 1)
        if r['go'] is not None and r['go'] >= len(fr) * every - 1e-6:
            fr.append((R12.crop(R12.shot(pg), r['xy'], cw, ch), r))
            if len(fr) >= n_fr:
                break
    return fr


GIFSET = r'''([n,sd,c,r,w])=>{const H=__HK;H.EGP.traps=true;const L=__P.load(n,sd);H.GFX&&(H.GFX().hd=true);
  const p=L.dyn.find(o=>o.f.chain&&L.dyn.some(d=>o.f.chain.includes(d.f)&&d.r===r&&d.c>=c&&d.c<c+w));__P.stand(p.c,r,1);H.P.inv=1e9;
  p.f.armed=1;p.f.chain.forEach((t,k)=>{t.s=1;t.tm=-(1.8+0.36*k);}); // (as the flask's tile arms it, armPassage: he runs, the floor gives way behind him)
  window.__q=[n,sd,c,r,w];return [p.c,p.r];}'''
GIFSTEP = r'''(i)=>{const H=__HK,[n,sd,c,r,w]=__q;if(i===0)H.setKey('kb','r',true);H.tick(1);H.banner=null;H.P.inv=1e9;
  H.cam.x=(c+w/2)*32-H.viewW/2;H.cam.y=r*64-40;H.cam.gy=H.cam.y;
  const os=H.L.dyn.filter(o=>o.f.t==='loose'&&o.r===r&&o.c>=c&&o.c<c+w);return {x:H.P.x,y:H.P.y,st:H.P.state,done:os.every(o=>o.f.s===2&&o.f.tm>0.9)};}'''


def gif(b, srcs, q):
    frames = {}
    for t, s in srcs.items():
        pg = R12.page(b, s, 'torch')
        info = pg.evaluate(GIFSET, list(q[1:6]))
        seq = []
        for i in range(420):
            f = pg.evaluate(GIFSTEP, i)
            if i % 2 == 0 and i >= 60:   # (from 1 s: he is on the row; the first slab goes at 2.3 s)
                pg.evaluate('()=>__P.draw()')
                xy = pg.evaluate('([x,y])=>__P.scr(x,y)', [(q[3] + q[5] / 2) * 32, (q[4] + 1) * 64 + 22])
                seq.append(label(R12.crop(R12.shot(pg), xy, 760, 360), t))
            if f['done']:
                break
        if pg.errs:
            print('errors', t, pg.errs[:3])
        pg.close()
        frames[t] = seq
        print('gif', t, 'plate', info, len(seq), 'frames')
    n = min(len(frames['before']), len(frames['after']))
    out = []
    for i in range(n):
        A, B = frames['before'][i], frames['after'][i]
        im = Image.new('RGB', (A.width + B.width + 6, A.height), INK)
        im.paste(A, (0, 0)); im.paste(B, (A.width + 6, 0))
        out.append(im.resize((im.width // 2, im.height // 2), Image.LANCZOS).quantize(colors=64, method=Image.MEDIANCUT, dither=Image.NONE))
    fn = os.path.join(OUTD, 'r26d_sand.gif')
    out[0].save(fn, save_all=True, append_images=out[1:], duration=33, loop=0, optimize=True)
    return fn, len(out)


if __name__ == '__main__':
    tmp = tempfile.mkdtemp()
    try:
        srcs = {'before': old_src(tmp), 'after': NEW}
        os.makedirs(OUTD, exist_ok=True)
        with sync_playwright() as p:
            b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
            P = {(t, m): R12.page(b, s, m) for t, s in srcs.items() for m in ('torch', 'classic')}
            rows = []
            for q in (CASES if '--gifonly' not in sys.argv else []):
                for m in ('torch', 'classic'):
                    for t in ('before', 'after'):
                        fr = strip(P[(t, m)], q, n_fr=12, every=0.1 if q[5] < 5 else 0.2)
                        tiles = [label(im.resize((im.width * 3 // 5, im.height * 3 // 5), Image.LANCZOS), '%s %s, %d slabs, t=%.1f' % (t, m, q[5], r['go'])) for im, r in fr]
                        rows.append(R12.grid(tiles, 6))
            for k, pg in P.items():
                if pg.errs:
                    print('errors', k, pg.errs[:3])
                pg.close()
            gfn, gn = gif(b, srcs, CASES[2]) if '--nogif' not in sys.argv else (None, 0)
            b.close()
        if not rows:
            print('gif', gfn, gn, 'frames', round(os.path.getsize(gfn) / 1e6, 2), 'MB'); sys.exit(0)
        W = max(r.width for r in rows)
        head = Image.new('RGB', (W, 40), INK)
        d = ImageDraw.Draw(head)
        d.text((6, 4), 'Round 26d (owner: "the domino sand effect needs to be more organic and less mechanically domino. On two columns of sand it works, on more '
               'than two it doesn\'t"). Before | after, Torchlight and Classic, a frame every 0.1 s (five slabs: 0.2 s) from the first slab set off.', fill=TXT)
        d.text((6, 20), 'Rows: two slabs, three slabs (set off from the left 0.32 s apart, his running pace), five slabs (the side passage\'s chain, 0.36 s apart). '
               'Play timing is the same in both.', fill=TXT)
        sheet = R12.stack([head] + rows)
        sheet.save(os.path.join(OUTD, 'r26d_sand.png'), optimize=True)
        print('wrote', os.path.join(OUTD, 'r26d_sand.png'), sheet.size, gfn, gn, 'frames', gfn and round(os.path.getsize(gfn) / 1e6, 2), 'MB')
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
