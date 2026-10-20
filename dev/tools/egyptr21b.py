# egyptr21b.py [new.html] [old.html] [outdir]: round 21b's pictures for egypt_themes.html, before (old.html, default the v68 release,
# hk_v68_release.html here or in the main checkout's dev/tools) and after:
#  r21b_rest.png      the sand under a row of cracked slabs at rest (a chain of five over a one-storey pit, three over a two-storey pit),
#                     Torchlight at GLP.rs 1 and 0.5 and Classic, crops of the 1704 px canvas; then the cut face at 2x; the sand lift's
#                     column of sand (its own grain now too) as it sinks
#  r21b_collapse.png  frame strips: the chain of five giving way (it counts down from below zero, one slab every 0.36 s) and three
#                     slabs of a deep pit set off from the left 0.2 s apart (as he runs over them), before and after, Torchlight and Classic
#  r21b_collapse.gif  the chain of five, before | after, Torchlight, 1:1
# Writes r21b.json (cases, page errors). Run from dev/tools.
import json, os, sys
from playwright.sync_api import sync_playwright
from PIL import Image
import egyptr12 as R12
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
NEW = os.path.abspath(a[0] if len(a) > 0 else os.path.join(HERE, '..', 'hourglass-keep.html'))
_old = os.path.join(HERE, 'hk_v68_release.html')
if not os.path.exists(_old):
    _old = os.path.join(HERE, '..', '..', '..', '..', '..', 'dev', 'tools', 'hk_v68_release.html')  # (from a worktree: the main checkout's)
OLD = os.path.abspath(a[1] if len(a) > 1 else _old)
OUT = a[2] if len(a) > 2 else os.path.join(HERE, 'egypt_themes')
R12.OUT = OUT
TAG = {'old': 'before (v68)', 'new': 'after (21b)'}
CHAIN = [5, 801, 26, 35, 5]   # floor, seed, first column, row, slabs: the chain of a side passage (armed by its plate two columns before it)
DEEP = [7, 802, 63, 22, 3]    # three slabs over a pit two storeys deep
# put the view on a row of slabs; mode 'rest' (nothing set off), 'chain' (armed by standing on its plate, the prince then put out of
# the way), 'run' (each slab set off 0.2 s after the one before it, from the left, as he sets them
# off running over them)
SET = r'''([q,mode,rs])=>{const H=__HK;H.EGP.traps=true;const [n,sd,c,r,w]=q;const L=__P.load(n,sd);
  {__P.stand(mode==='chain'?c-2:c-8,r,1);if(mode==='rest')for(const o of L.dyn)if(o.f.t==='loose'&&o.r===r&&o.c>=c&&o.c<c+w){o.f.s=0;o.f.tm=0;}H.P.x=-9999;H.P.y=-9999;}
  H.P.inv=1e9;window.__t0=H.gameTime+0.1;window.__q=q;window.__rs=rs;window.__mode=mode;window.__k=0;return 1;}'''
STEP = r'''(nt)=>{const H=__HK,[n,sd,c,r,w]=__q;
  for(let i=0;i<nt;i++){if(__mode==='run')for(const o of H.L.dyn)if(o.f.t==='loose'&&o.r===r&&o.c>=c&&o.c<c+w&&o.f.s===0&&H.gameTime-__t0>=0.2*(o.c-c)){o.f.s=1;o.f.tm=0;}H.tick(1);}H.P.x=-9999;H.P.y=-9999;H.P.inv=1e9;H.banner=null;
  H.cam.x=(c+w/2)*32-H.viewW/2;H.cam.y=r*64-40;H.cam.gy=H.cam.y;if(H.GLP){H.GLP.rs=__rs;H.GLP.pipe=false;}H.render();H.render();
  const L=H.L,st=L.dyn.filter(o=>o.f.t==='loose'&&o.r===r&&o.c>=c&&o.c<c+w).map(o=>[o.f.s,+o.f.tm.toFixed(2)]);
  return {xy:__P.scr((c+w/2)*32,(r+1)*64+(w>4?20:30)),st,t:+H.gameTime.toFixed(2)};}'''


import egyptr16 as R16
SANDL = r'''([q,rs,nt])=>{const H=__HK;H.EGP.traps=true;const L=__P.load(q.n,q.seed);__P.stand(q.c+q.sT,q.r,-q.sT);const f=L.lifts.find(f=>f.sand&&f.sc===q.c);
  const P=H.P;P.x=f.sc*32+16;P.y=f.yT;P.state='stand';for(let i=0;i<nt;i++)H.tick(1);P.inv=1e9;H.banner=null;if(H.GLP){H.GLP.rs=rs;H.GLP.pipe=false;}H.render();H.render();return __P.scr(f.sc*32+16,(f.y+f.yT)/2+40);}'''


def shotq(pg, q, mode, rs, nt, cw, ch):
    pg.evaluate(SET, [q, mode, rs])
    r = pg.evaluate(STEP, nt)
    return R12.crop(R12.shot(pg), r['xy'], cw, ch), r


def strip(pg, q, mode, rs, steps, nt, cw, ch):
    pg.evaluate(SET, [q, mode, rs]); fr = []; info = []
    for k in range(steps):
        r = pg.evaluate(STEP, nt); fr.append(R12.crop(R12.shot(pg), r['xy'], cw, ch)); info.append(r)
    return fr, info


if __name__ == '__main__':
    J = {'errors': {}, 'cases': {'chain': CHAIN, 'deep': DEEP}}
    os.makedirs(OUT, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
        P = {(v, m): R12.page(b, src, m) for v, src in (('old', OLD), ('new', NEW)) for m in ('torch', 'classic')}
        # ---- 1. at rest
        rows = []
        for q in (CHAIN, DEEP):
            t = []
            for m, rs in (('torch', 1), ('torch', 0.5), ('classic', 1)):
                for v in ('old', 'new'):
                    im, _ = shotq(P[(v, m)], q, 'rest', rs, 2, 300, 300 if q is DEEP else 220)
                    t.append(R12.label(im, '%s, %s%s' % (TAG[v], m, ' rs .5' if rs < 1 else '')))
            rows.append(R12.grid(t, 6))
        t = []
        for m in ('torch', 'classic'):
            for v in ('old', 'new'):
                im, _ = shotq(P[(v, m)], CHAIN, 'rest', 1, 2, 160, 110)
                t.append(R12.label(im.resize((320, 220), Image.LANCZOS), '%s, %s 2x' % (TAG[v], m)))
        rows.append(R12.grid(t, 4))
        sl = P[('new', 'torch')].evaluate(R16.FINDS); J['cases']['sandlift'] = sl; t = []
        for m in ('torch', 'classic'):
            for v in ('old', 'new'):
                xy = P[(v, m)].evaluate(SANDL, [sl, 1, 40])
                t.append(R12.label(R12.crop(R12.shot(P[(v, m)]), xy, 160, 300), '%s, %s, sand lift' % (TAG[v][:6], m)))
        rows.append(R12.grid(t, 4))
        R12.stack(rows).save(os.path.join(OUT, 'r21b_rest.png'))
        # ---- 2. the collapse, frame strips
        rows = []
        for q, mode, n0, nt, steps in ((CHAIN, 'chain', 0, 6, 50), (DEEP, 'run', 0, 6, 40)):
            for m in ('torch', 'classic'):
                for v in ('old', 'new'):
                    fr, info = strip(P[(v, m)], q, mode, 1, steps, nt, 300, 230 if q is CHAIN else 300)
                    if q is CHAIN:
                        i0 = next((i for i, r in enumerate(info) if any(s[0] == 1 and s[1] > 0 for s in r['st'])), 0)
                        pick = list(range(max(0, i0 - 1), min(len(fr), i0 + 1 + 6 * 4), 4))[:7]
                    else:
                        i0 = next((i for i, r in enumerate(info) if any(s[0] == 1 and s[1] > 0 for s in r['st'])), 0)
                        pick = list(range(max(0, i0 - 1), min(len(fr), i0 + 13), 2))[:7]
                    J['cases']['%s %s %s' % (mode, m, v)] = [info[i]['st'] for i in pick]
                    rows.append(R12.grid([R12.label(fr[i], '%s %s t=%.2f' % (TAG[v][:6], m[:5], info[i]['t'] - info[pick[0]]['t'])) for i in pick], 7))
        R12.stack(rows).save(os.path.join(OUT, 'r21b_collapse.png'))
        # ---- 3. the gif: the chain, Torchlight, before | after
        F = {}
        for v in ('old', 'new'):
            fr, info = strip(P[(v, 'torch')], CHAIN, 'chain', 1, 100, 3, 300, 230)
            i0 = next((i for i, r in enumerate(info) if any(s[0] == 1 and s[1] > 0 for s in r['st'])), 0)
            F[v] = [R12.label(f.resize((240, 184), Image.LANCZOS), TAG[v]) for f in fr[max(0, i0 - 4):i0 + 52]]
        n = min(len(F['old']), len(F['new']))
        gif = []
        for i in range(n):
            g = Image.new('RGB', (484, 184), (20, 16, 24)); g.paste(F['old'][i], (0, 0)); g.paste(F['new'][i], (244, 0)); gif.append(g.quantize(128))
        gif[0].save(os.path.join(OUT, 'r21b_collapse.gif'), save_all=True, append_images=gif[1:], duration=50, loop=0, optimize=True)
        for k, pg in P.items():
            J['errors']['%s %s' % k] = pg.errs[:3]
        json.dump(J, open(os.path.join(HERE, 'r21b.json'), 'w'), indent=1)
        print('errors', J['errors']); b.close()
