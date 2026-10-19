# egyptr16.py [new.html] [outdir]: round 16a's pictures for egypt_themes.html, in the game at the phone's resolution (crops of the
# 1704 px canvas), Torchlight and Classic side by side: the prince stepping over a fallen roof block (r16_block.gif), a cracked slab
# over a corridor crumbling (r16_crumble.gif), a cracked slab over a sand-filled well draining (r16_drain.gif), the sand lift
# (r16_lift.gif), all at 1:1; key frames of the four at 2x (r16_2x.png); and the slab's two kinds and the sand lift in three more
# themes at 1:1 (r16_themes.png). Run from dev/tools.
import os, sys
from playwright.sync_api import sync_playwright
from PIL import Image
import egyptr12 as R12
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
NEW = os.path.abspath(a[0] if len(a) > 0 else os.path.join(HERE, '..', 'hourglass-keep.html'))
OUT = a[1] if len(a) > 1 else os.path.join(HERE, 'egypt_themes')
# a cracked slab of kind k ('well2': over a sand well two storeys deep, 'corr': over a corridor), with floor to run up on
FINDL = r'''([k])=>{const H=__HK;for(let n=4;n<=30;n++)for(const sd of [801,802,803]){const L=__P.load(n,sd);
  for(const o of L.dyn){const f=o.f;if(f.t!=='loose'||f.plank||f.sturdy||f.drop)continue;const w=H.looseWell(o),kk=w?'well'+w:'corr';
    if(kk!==k||!H.solidBelow(o.c-3,o.r)||!H.solidBelow(o.c-2,o.r)||H.L.feat[o.r*L.cols+o.c+1]||!H.solidBelow(o.c+1,o.r)||!H.solidBelow(o.c+2,o.r))continue;return {n,seed:sd,c:o.c,r:o.r};}}return null;}'''
FINDS = r'''()=>{const H=__HK;for(let n=5;n<=30;n++)for(let s=0;s<60;s++){const seed=60000+s*137+n*19,L=H.genLevel(n,seed,true);const f=L.lifts.find(q=>q.sand&&q.k===3);if(f)return {n,seed,c:f.sc,r:f.rT,sT:f.sT};}return null;}'''
FINDB = r'''()=>{const H=__HK;for(const n of [3,2,4,6])for(const sd of [801,802,803]){const L=__P.load(n,sd);const o=L.dyn.find(o=>o.f.t==='stone'&&H.solidBelow(o.c-4,o.r)&&H.solidBelow(o.c+3,o.r));if(o)return {n,seed:sd,c:o.c,r:o.r};}return null;}'''
# setup per kind; look: another theme's look (or null)
SETUP = r'''([kind,q,look])=>{const H=__HK;H.EGP.traps=true;const L=__P.load(q.n,q.seed);if(look){const T=H.THEMES.find(t=>t.look===look);if(T){L.theme=T;H.clearRooms();}}
  if(kind==='block'){const o=L.dyn.find(o=>o.c===q.c&&o.r===q.r);o.f.s=3;L.rubble.add(q.r*L.cols+q.c);H.clearRooms();__P.stand(q.c-4,q.r,1);}
  else if(kind==='lift')__P.stand(q.c+q.sT,q.r,-q.sT);else __P.stand(q.c-3,q.r,1);
  window.__k=0;return 1;}'''
STEP = r'''([kind,q])=>{const H=__HK,P=H.P,k=window.__k++;let key='r',on;
  if(kind==='block')on=P.x<q.c*32+16+46;else if(kind==='lift'){key=q.sT<0?'r':'l';on=P.state!=='lift'&&P.y<(q.r+1)*64&&Math.abs(P.x-(q.c*32+16))>4;}else on=P.x<q.c*32+16+76;
  H.setKey('kb',key,!!on&&k>2);H.tick(2);P.inv=1e9;H.banner=null;if(H.GLP)H.GLP.pipe=false;H.render();H.render();
  const y=kind==='block'?(q.r+1)*64-28:kind==='lift'?P.y-14:kind==='well2'?(q.r+1)*64+44:(q.r+1)*64+46;
  let info=0;if(kind==='block')info=-(P.rdy||0);else if(kind==='lift'){const f=H.L.lifts.find(f=>f.sc===q.c&&f.rT===q.r);info=f.y-f.yT;}
  else{const o=H.L.dyn.find(o=>o.c===q.c&&o.r===q.r);info=o.f.s*10+o.f.tm;}
  return __P.scr(kind==='lift'?q.c*32+16:q.c*32+16+6,y).concat([info]);}'''
SIZE = {'block': (260, 210), 'well2': (230, 400), 'corr': (250, 400), 'lift': (230, 440)}
NFR = {'block': 80, 'well2': 90, 'corr': 90, 'lift': 110}
# the key frames for the 2x sheet, from what each frame shows (block: how high he is drawn on it; slab: state*10 + its clock; lift: how far down)
KEYF = {'block': [lambda v: v > 9.5, lambda v: 1 < v < 7], 'well2': [lambda v: 10.3 <= v < 20, lambda v: v >= 20.2], 'corr': [lambda v: 10.35 <= v < 20, lambda v: v >= 20.16], 'lift': [lambda v: v > 30, lambda v: v > 120]}


def side(ims, pad=4):
    w = sum(i.width for i in ims) + pad * (len(ims) - 1); g = Image.new('RGB', (w, max(i.height for i in ims)), (20, 16, 24)); x = 0
    for i in ims:
        g.paste(i, (x, 0)); x += i.width + pad
    return g


def seq(pg, kind, q, look=None):
    pg.evaluate(SETUP, [kind, q, look]); fr = []; inf = []; seen = False
    for k in range(NFR[kind]):
        r = pg.evaluate(STEP, [kind, q]); fr.append(R12.crop(R12.shot(pg), r[:2], *SIZE[kind])); inf.append(r[2])
    pg.evaluate("()=>{for(const k of 'lrudjg')__HK.setKey('kb',k,false);}")
    key = []
    for cond in KEYF[kind]:
        i = next((j for j, v in enumerate(inf) if cond(v) and (kind != 'block' or not key or j > key[0])), len(fr) - 1); key.append(i)
    s0 = max(0, next((j for j, v in enumerate(inf) if v > (9.99 if kind in ('well2', 'corr') else 0.5)), 0) - 12) # (from a moment before it starts)
    s1 = min(len(fr), max(key) + (30 if kind != 'lift' else 40))
    print(kind, look, 'frames', s0, s1, 'key', key, [round(inf[i], 2) for i in key])
    return fr[s0:s1], [k - s0 for k in key]


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
        P = {m: R12.page(b, NEW, m) for m in ('torch', 'classic')}
        pt = P['torch']
        Q = {'block': pt.evaluate(FINDB), 'well2': pt.evaluate(FINDL, ['well2']), 'corr': pt.evaluate(FINDL, ['corr']), 'lift': pt.evaluate(FINDS)}
        print(Q)
        NAME = {'block': 'r16_block.gif', 'well2': 'r16_drain.gif', 'corr': 'r16_crumble.gif', 'lift': 'r16_lift.gif'}
        rows2x = []
        for kind in ('block', 'well2', 'corr', 'lift'):
            S = {m: seq(P[m], kind, Q[kind]) for m in ('torch', 'classic')}; key = S['torch'][1]; S = {m: S[m][0] for m in S}
            frames = [side([R12.label(t.copy(), 'Torchlight 1:1'), R12.label(c.copy(), 'Classic 1:1')]) for t, c in zip(S['torch'], S['classic'])]
            frames[0].save(os.path.join(OUT, NAME[kind]), save_all=True, append_images=frames[1:], duration=33, loop=0, optimize=True)
            rows2x.append(side([R12.label(S[m][i].resize((S[m][i].width * 2, S[m][i].height * 2), Image.LANCZOS), '%s 2x' % m) for i in key for m in ('torch', 'classic')], 6))
        R12.stack(rows2x).save(os.path.join(OUT, 'r16_2x.png'))
        # three more themes, Torchlight 1:1: each kind at one of its key frames
        tl = []
        for look in ('west', 'meroe', 'aksum'):
            row = []
            for kind in ('block', 'well2', 'corr', 'lift'):
                fr, key = seq(pt, kind, Q[kind], look); row.append(R12.label(fr[key[0] if kind == 'block' else key[1]], look))
            tl.append(side(row, 6))
        R12.stack(tl).save(os.path.join(OUT, 'r16_themes.png'))
        print('errors', P['torch'].errs[:3], P['classic'].errs[:3]); b.close()
