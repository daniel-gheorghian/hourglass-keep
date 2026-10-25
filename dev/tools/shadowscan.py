# shadowscan.py [file.html] [lo hi] [seeds] [kinds=a,b] [per=K] [ref=file.html] [out.png]: a figure's lamp shadow on what stands in front of
# the back wall (round 38a, owner: "Correct ... all of the faults"; round 37b did the slicer's jaws). Torchlight's lamp shadow (glShadow, the
# effect mask's r) was carved out of walls, floors, low ceilings and the jaws only, so the prince's shadow (and a guard's) was painted across a
# lowered portcullis, a lift's mouth slab, the stakes, a saw's blade, the sky clock, a flask, a fallen roof block or a lift's platform as if it
# were the wall. Now glMask also carves their outlines as drawn this frame (SHC). For every such thing on floors lo..hi (default 1-48: all twelve
# themes), seeds (default 1), up to K a kind a floor (default 2): the thing is set as it shows the fault (a slab down, the stakes out, a block
# lying), the prince stands beside it with a torch on the wall behind him (his shadow, pushed away from the lamp, falls on the thing), Torchlight
# is drawn with the shadow on and off (GLFX.shadow) and the thing's own pixels (inside its outline as recorded, 1.7 px in from its edge, as the
# mask is a quarter size and read blurred over a texel either side: the walls' edges are as soft) must not change: a thing is bad when more than 4 of them differ by more than 24 (sum of channels). In
# the same run each is drawn with the carve off (SHC.off: v82's look), which counts the things his shadow reaches. On a file without SHC (v82),
# the outlines are taken from the ref build (default: the source) in the same scene, and every thing reached is bad. Kinds: slab (portcullis,
# lift and sand lift mouth slabs, down), stakes, saw, pend, roof (a fallen block), clock (lit), flask, liftslab (a counterweight platform at its
# foot, a paternoster slab), rope (the same lifts' ropes at mid depth: the platform's two, the paternoster's upright runs), sandslab (the sand
# lift's slab at its top). Prints the counts per kind and 'shadowscan: ok'; a sheet of the worst
# cases (shadowscan.png: shadow on | off | carve off). Run from dev/tools.
import io, os, sys
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFilter, ImageChops
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
SRC = os.path.abspath(next((x for x in a if x.endswith('.html') and '=' not in x), os.path.join(HERE, '..', 'hourglass-keep.html')))
REF = os.path.abspath(next((x[4:] for x in a if x.startswith('ref=')), os.path.join(HERE, '..', 'hourglass-keep.html')))
NUM = [int(x) for x in a if x.isdigit()]
LO, HI = (NUM + [1, 48])[:2] if len(NUM) >= 2 else (1, 48)
SEEDS = [int(s) for s in next((x for x in a if ',' in x and '=' not in x), str(NUM[2]) if len(NUM) > 2 else '1').split(',')]
KINDS = next((x[6:] for x in a if x.startswith('kinds=')), 'slab,stakes,saw,pend,roof,clock,flask,liftslab,rope,sandslab').split(',')
PER = int(next((x[4:] for x in a if x.startswith('per=')), '2'))
OUT = next((x for x in a if x.endswith('.png')), os.path.join(HERE, 'shadowscan.png'))
ERODE = 7  # device px (3.5 css px, 1.7 world px at this view: the quarter-size mask read blurred over a texel either side)

# the things of a kind on the floor, and the scene: the thing set as it shows the fault, the prince beside it, a torch behind him
JS = r'''window.SHS=(()=>{const H=__HK,TW=32,SURF=r=>(r+1)*64-4,TS=7;
  function things(L,kind){const out=[],C=L.cols,dyn=t=>L.dyn.filter(o=>o.f.t===t),gx=(f,s)=>s<0?f.sc*TW-TS/2:(f.sc+1)*TW+TS/2;
    if(kind==='slab'){dyn('gate').forEach(o=>out.push({x:o.c*TW+16,r:o.r,ys:SURF(o.r),prep:()=>{o.f.open=0;}}));
      L.lifts.forEach(f=>{if(f.t!=='lift'||f.sand)return;for(let e=0;e<2;e++){const s=e?f.sB:f.sT;if(!s)continue;const rr=e?f.rB:f.rT;out.push({x:gx(f,s),r:rr,ys:SURF(rr),prep:()=>{if(e)f.gB=0;else f.gT=0;}});}});
      L.lifts.forEach(f=>{if(!f.sand||!f.ms)return;for(const s of f.ms){if(!s)continue;out.push({x:gx(f,s),r:f.rB,ys:SURF(f.rB),prep:()=>{f.y=f.yT;}});}});}
    if(kind==='stakes')dyn('spikes').forEach(o=>out.push({x:o.c*TW+16,r:o.r,ys:SURF(o.r),prep:()=>{o.f.ext=1;}}));
    if(kind==='saw')dyn('saw').forEach(o=>out.push({x:o.c*TW+16,r:o.r,ys:SURF(o.r),at:()=>H.sawX(o.f,H.gameTime)}));
    if(kind==='pend')dyn('pend').forEach(o=>out.push({x:o.c*TW+16,r:o.r,ys:SURF(o.r),at:()=>H.pendTip(o,o.f).x}));
    if(kind==='roof')dyn('stone').forEach(o=>out.push({x:o.c*TW+16,r:o.r,ys:SURF(o.r),prep:()=>{o.f.s=2;o.f.land=-100;L.rubble.add(o.r*C+o.c);}}));
    if(kind==='clock')L.cps.forEach(q=>out.push({x:q.x,r:q.r,ys:SURF(q.r),prep:()=>{for(const p of L.cps)p.on=false;q.on=true;q.onAt=-100;},at:()=>H.cpX(q)}));
    if(kind==='flask')L.items.forEach(q=>{if(!q.hidden&&!q.taken)out.push({x:q.x,r:q.r,ys:SURF(q.r)});});
    if(kind==='liftslab'||kind==='rope'){L.lifts.forEach(f=>{if(f.t==='lift'&&!f.sand)out.push({x:f.sc*TW+16,r:f.rB,ys:SURF(f.rB),prep:()=>{f.y=SURF(f.rB);}});});
      L.lifts.forEach(f=>{if(f.t!=='chain')return;out.push({x:f.c0*TW+16,r:f.rB,ys:SURF(f.rB),at:()=>{let b=null,d=1e9;for(let i=0;i<f.n;i++){const q=H.chainPos(f,i,H.gameTime),e=Math.abs(q.y-SURF(f.rB))+Math.abs(q.x-(f.c0*TW+16))*0.2;if(e<d){d=e;b=q;}}return b?b.x:f.c0*TW+16;}});});}
    if(kind==='sandslab')L.lifts.forEach(f=>{if(f.sand)out.push({x:f.sc*TW+16,r:f.rT,ys:SURF(f.rT),prep:()=>{f.y=f.yT;}});});
    return out;}
  function list(n,sd,kind){window.__HKfreeze=true;const L=H.load(n,sd,true);return things(L,kind).length;}
  function show(n,sd,kind,i,shadow,off){window.__HKfreeze=true;for(const id in H.HINTS)H.S.hints[id]=1;
    const L=H.load(n,sd,true),C=L.cols;H.banner=null;H.intro=0;const t=things(L,kind)[i];if(!t)return null;if(t.prep)t.prep();const x=t.at?t.at():t.x;
    const fl=c=>c>=0&&c<C&&L.base[t.r*C+c]!==2&&H.solidBelow(c,t.r);let s=1;
    {const l=Math.floor((x-40)/TW),r=Math.floor((x+40)/TW),okL=fl(l)&&fl(Math.floor((x-100)/TW)),okR=fl(r)&&fl(Math.floor((x+100)/TW));s=okL?-1:okR?1:fl(l)?-1:1;}
    const P=H.P;P.inv=1e9;P.state='stand';P.face=-s;P.x=x+s*40;P.y=t.ys;P.fallY=P.y;P.vx=P.vy=0;
    L.torches.length=0;const lc=Math.floor((P.x+s*60)/TW);L.torches.push({c:lc,r:t.r});
    H.GLFX.shadow=!!shadow;if(H.SHC)H.SHC.off=!!off;H.clearRooms();
    H.cam.x=x-H.viewW/2;H.cam.y=(t.r+1)*64-64*1.6;H.cam.gy=H.cam.y;H.mode='play';H.GLP&&(H.GLP.pipe=false);
    H.render();H.render();H.render();if(H.SHC)H.SHC.off=false;
    const X=H.XF,cv=[...document.querySelectorAll('canvas')].find(q=>q.getBoundingClientRect().width>0),R=cv.getBoundingClientRect();
    const m=p=>[R.left+(p[0]*X.VZ-X.camD)/cv.width*R.width,R.top+(p[1]*X.VZ-X.camDY)/cv.height*R.height];
    const kk=kind==='slab'?'slab':kind,shc=H.shcList?H.shcList().filter(e=>e.k===kk&&e.rings.some(rg=>rg.some(p=>Math.abs(p[0]-x)<48&&Math.abs(p[1]-t.ys)<90))).map(e=>({clip:[m([e.clip[0],e.clip[1]]),m([e.clip[2],e.clip[3]])],rings:e.rings.map(rg=>rg.map(m))})):null;
    return {mid:m([x,t.ys-24]),th:H.themeName(n),c:Math.floor(x/TW),r:t.r,side:s,shc};}
  return {things,list,show};})();'''


def page(b, src):
    pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=2)
    pg.errs = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e)))
    pg.goto('file://' + src); pg.wait_for_timeout(700)
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.body.classList.remove('panelOpen')")
    pg.evaluate("()=>{__HK.S.set.lightMode='torch';__HK.GLFX.sheen=false;}")  # (the wet floor's reflection: a mirror of what is lit, not a shadow)
    pg.evaluate(JS)
    pg.shc = pg.evaluate("()=>!!__HK.shcList")
    return pg


def mask(shc, w, h):  # the thing's pixels (device px), its outline eroded by ERODE
    mk = Image.new('L', (w, h), 0)
    for e in shc:
        sub = Image.new('L', (w, h), 0); d = ImageDraw.Draw(sub)
        for rg in e['rings']:
            d.polygon([(x * 2, y * 2) for x, y in rg], fill=255)
        (x0, y0), (x1, y1) = e['clip']
        cl = Image.new('L', (w, h), 0); ImageDraw.Draw(cl).rectangle([max(-1, x0 * 2), max(-1, y0 * 2), min(w + 1, x1 * 2), min(h + 1, y1 * 2)], fill=255)
        mk = ImageChops.lighter(mk, ImageChops.multiply(sub, cl))
    return mk.filter(ImageFilter.MinFilter(2 * ERODE + 1))


def changed(A, B, mk):  # pixels of the mask whose colour differs by more than 24 (sum of channels)
    d = ImageChops.difference(A, B).convert('RGB')
    r, g, bb = d.split()
    s = ImageChops.add(ImageChops.add(r, g), bb)
    hit = s.point(lambda v: 255 if v > 24 else 0)
    return ImageChops.multiply(hit, mk).histogram()[255], mk.histogram()[255]


def shot(pg):
    return Image.open(io.BytesIO(pg.screenshot())).convert('RGB')


if __name__ == '__main__':
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--enable-gpu', '--ignore-gpu-blocklist'])
        pg = page(b, SRC); rp = None if pg.shc else page(b, REF)
        tot, reach, bad, where, worst, empty = {}, {}, {}, [], [], 0
        for n in range(LO, HI + 1):
            for sd in SEEDS:
                for kind in KINDS:
                    cnt = pg.evaluate("([n,sd,k])=>SHS.list(n,sd,k)", [n, sd, kind])
                    idx = list(range(cnt)) if cnt <= PER else [int((i + 0.5) * cnt / PER) for i in range(PER)]
                    for i in idx:
                        r1 = pg.evaluate("([n,sd,k,i])=>SHS.show(n,sd,k,i,true,false)", [n, sd, kind, i])
                        if not r1: continue
                        A = shot(pg)
                        shc = r1['shc'] if pg.shc else rp.evaluate("([n,sd,k,i])=>SHS.show(n,sd,k,i,true,false)", [n, sd, kind, i])['shc']
                        if not shc:
                            empty += 1; continue
                        pg.evaluate("([n,sd,k,i])=>SHS.show(n,sd,k,i,false,false)", [n, sd, kind, i]); Bm = shot(pg)
                        mk = mask(shc, A.width, A.height)
                        nb, area = changed(A, Bm, mk)
                        if area < 20:
                            empty += 1; continue
                        if pg.shc:
                            pg.evaluate("([n,sd,k,i])=>SHS.show(n,sd,k,i,true,true)", [n, sd, kind, i]); Cm = shot(pg)
                            nr, _ = changed(Cm, Bm, mk)
                        else:
                            Cm, nr = A, nb
                        tot[kind] = tot.get(kind, 0) + 1
                        if nr > 4: reach[kind] = reach.get(kind, 0) + 1
                        if nb > 4:
                            bad[kind] = bad.get(kind, 0) + 1; where.append('%s %d/%d c%d r%d (%d of %d px)' % (kind, n, sd, r1['c'], r1['r'], nb, area))
                            if len(worst) < 12:
                                cx, cy = int(r1['mid'][0] * 2), int(r1['mid'][1] * 2); box = (cx - 150, cy - 130, cx + 150, cy + 80)
                                row = Image.new('RGB', (906, 226), (20, 16, 24))
                                for k, im in enumerate((A, Bm, Cm)):
                                    row.paste(im.crop(box), (k * 302, 16))
                                ImageDraw.Draw(row).text((4, 2), '%s %d/%d c%d,%d %s: shadow on | off | carve off (%d px)' % (kind, n, sd, r1['c'], r1['r'], r1['th'][:22], nb), fill=(255, 240, 160))
                                worst.append(row)
            print('floor %d done' % n, flush=True) if (n - LO) % 8 == 7 else None
        errs = pg.errs + (rp.errs if rp else [])
        print('floors %d-%d seeds %s%s: things framed %d (%d without an outline in view)' % (LO, HI, ','.join(map(str, SEEDS)), '' if pg.shc else ' [no SHC: outlines from %s]' % os.path.basename(REF), sum(tot.values()), empty))
        for k in KINDS:
            print('  %-9s framed %3d  his shadow reaches it (carve off) %3d  shadow on it %3d' % (k, tot.get(k, 0), reach.get(k, 0), bad.get(k, 0)))
        if where: print('bad:', '; '.join(where[:30]))
        nbad = sum(bad.values())
        print('shadowscan: %s (%d of %d things take his shadow, %d reached with the carve off)' % ('ok' if nbad == 0 and not errs else 'FAIL', nbad, sum(tot.values()), sum(reach.values())), 'errors', errs[:3])
        if worst:
            sh = Image.new('RGB', (906, 226 * len(worst)), (20, 16, 24))
            for k, row in enumerate(worst): sh.paste(row, (0, k * 226))
            sh.save(OUT); print('wrote', OUT)
        b.close()
