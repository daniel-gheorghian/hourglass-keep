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
# lift's slab at its top). Round 42b adds what was still left out: bar (the swing bar, him swinging up beside it), rig (a counterweight lift's
# hoist beam, brace, hanger and sheave, him jumping up on the top landing), loop (the paternoster's level runs and wheels, him beside its
# top and its foot), lamp (a lamp's flame and a free lamp's stand, the caster beyond him), sand (a well's sand after its slab broke, him
# dropping beside it; a sand lift's column with the slab a storey up, him on the foot's landing), debris (a cracked slab or plank just
# fallen), vent (the flame at the roar) and dart (one in flight). Round 43 adds heap and drift (him 40 px off its middle, on or in it); round 46b
# measures those two by their drawn pixels (the frame with it less the frame without it, LAYER_DBG.hide; shadow, beams, mist, looks, caustics and
# bloom off in both), not by the SHC outline. Round 45 adds pool (a court's pool, him on its coping) and vine (a pergola's hanging vine). A kind the tested file does not record (an older build) takes its outlines
# from the ref build. Prints the counts per kind and 'shadowscan: ok'; a sheet of the worst
# cases (shadowscan.png: shadow on | off | carve off); SS_DUMP=prefix writes each bad thing's frame with the shadowed pixels in magenta. Run from dev/tools.
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
KINDS = next((x[6:] for x in a if x.startswith('kinds=')), 'slab,stakes,saw,pend,roof,clock,flask,liftslab,rope,sandslab,bar,rig,loop,lamp,sand,debris,vent,dart,heap,drift,pool,vine,jamb').split(',')
PER = int(next((x[4:] for x in a if x.startswith('per=')), '2'))
OUT = next((x for x in a if x.endswith('.png')), os.path.join(HERE, 'shadowscan.png'))
DRAWN = ('heap', 'drift')  # (round 46b: kinds measured by their drawn pixels, not by the outline the carve itself uses, which made the test circular: v87's
# hillSil missed B3's left end and every stone above the mound, and shadowscan, masking by that same outline, found 0 of 128)
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
    // (round 42b) place(P,s): where he is instead of standing 40 px off (s the side); tq: the caster's distance beyond him (default 60)
    if(kind==='bar')dyn('bar').forEach(o=>{const f=o.f;out.push({x:f.x,r:o.r,ys:SURF(o.r),tq:24,place:(P,s)=>{f.ps=0;f.pw=0;P.x=f.x;P.y=f.y+57;P.vx=P.vy=0;P.state='air';P.autoGrab=true;P.face=s;P.fallY=P.y;H.tick(1);
      if(P.state==='swing'){P.swTh=0.95;P.swOm=0;const b=H.barPos(f);P.x=b.x+P.face*34*Math.sin(P.swTh);P.y=b.y+34*Math.cos(P.swTh)+24.5;}}});});
    if(kind==='pool')(L.courts||[]).forEach(k=>k.pits.forEach(([a,b])=>out.push({x:(a+b+1)/2*TW,r:k.r,ys:SURF(k.r)}))); // (round 45: a court's pool, him on its coping)
    if(kind==='jamb')(L.courts||[]).forEach(k=>H.ctJambsOf(k).forEach(j=>out.push({x:j.x0+j.w/2,r:k.r,ys:SURF(k.r)}))); // (round 45c: a court's jambs)
    if(kind==='vine')(L.courts||[]).forEach(k=>{if(k.k==='perg')out.push({x:(k.c0+k.c1+1)/2*TW,r:k.r,ys:SURF(k.r)});});
    if(kind==='rig')L.lifts.forEach(f=>{if(f.t==='lift'&&!f.sand)out.push({x:f.sc*TW+12.5,r:f.rT,ys:SURF(f.rT),dy:-26});});
    if(kind==='loop')L.lifts.forEach(f=>{if(f.t!=='chain')return;for(const c of [f.c0,f.c1])for(const top of [1,0]){const rr=top?f.rT:f.rB;if(rr===undefined)continue;out.push({x:c*TW+16,r:rr,ys:top?f.yT:SURF(rr),at:()=>c*TW+16});}});
    if(kind==='lamp')L.torches.forEach(q=>{if(!q.broken)out.push({x:q.c*TW+16,r:q.r,ys:SURF(q.r),keep:q});});
    if(kind==='sand'){dyn('loose').forEach(o=>{const g=H.wellGroup(o);if(!g||g.os[0]!==o)return;const xa=o.c*TW,xb=xa+g.n*TW;
        out.push({x:(xa+xb)/2,r:o.r,ys:SURF(o.r),tq:50,prep:()=>{const f=o.f;f.s=2;f.tm=0.08;L.base[o.r*C+o.c]=2;},place:(P,s)=>{P.x=(s<0?xa:xb)+s*14;P.y=SURF(o.r)+40;P.state='fall';P.vy=60;}});});
      L.lifts.forEach(f=>{if(f.sand)out.push({x:f.sc*TW+16,r:f.rB,ys:SURF(f.rB),prep:()=>{f.y=SURF(f.rB)-72;}});});}
    if(kind==='debris')dyn('loose').forEach(o=>out.push({x:o.c*TW+16,r:o.r,ys:SURF(o.r),prep:()=>{const f=o.f;f.s=2;L.base[o.r*C+o.c]=2;const y0=SURF(o.r);
      L.debris.push({x:o.c*TW+16,y:y0+3,y0,vy:0,c:o.c,hitP:true,kind:f.plank?'plank':'slab',g:f.plank?undefined:1400,wl:!f.plank&&H.looseWell(o)});}}));
    if(kind==='vent')dyn('vent').forEach(o=>out.push({x:o.c*TW+16,r:o.r,ys:SURF(o.r),prep:()=>{const f=o.f;f.off=((0.86*f.per-H.gameTime)%f.per+f.per)%f.per;}}));
    if(kind==='dart')dyn('darter').forEach(o=>{const f=o.f,dir=f.dir||-1,xb=f.x-2*dir,mx=dir>0?xb+12.5:xb-8,dx=f.x+dir*90;
      out.push({x:dx,r:o.r,ys:SURF(o.r),prep:()=>{L.ext.darts.length=0;L.ext.darts.push({x:dx,y:f.y,r:o.r,x0:f.x0,dir,mx});}});});
    if(kind==='heap'||kind==='drift')(L.hills||[]).forEach(h=>{if(!!h.d===(kind==='drift'))out.push({x:(h.c+h.n/2)*TW,r:h.r,ys:SURF(h.r),tq:50,prep:()=>{L.winds.length=0;if(H.HILL_DBG)H.HILL_DBG.stream=false;}});}); // (round 43: him beside or on it, the lamp beyond him; round 46b: no wind's dust and no sand stream, air over it that takes the shadow on the wall)
    return out;}
  function list(n,sd,kind){window.__HKfreeze=true;const L=H.load(n,sd,true);return things(L,kind).length;}
  function show(n,sd,kind,i,shadow,off,hide,clean){window.__HKfreeze=true;for(const id in H.HINTS)H.S.hints[id]=1;
    const L=H.load(n,sd,true),C=L.cols;H.banner=null;H.intro=0;const t=things(L,kind)[i];if(!t)return null;if(t.prep)t.prep();const x=t.at?t.at():t.x;
    const fl=c=>c>=0&&c<C&&L.base[t.r*C+c]!==2&&H.solidBelow(c,t.r);let s=1;
    {const l=Math.floor((x-40)/TW),r=Math.floor((x+40)/TW),okL=fl(l)&&fl(Math.floor((x-100)/TW)),okR=fl(r)&&fl(Math.floor((x+100)/TW));s=okL?-1:okR?1:fl(l)?-1:1;}
    const P=H.P;P.inv=1e9;P.state='stand';P.face=-s;P.x=x+s*40;P.y=t.ys+(t.dy||0);P.fallY=P.y;P.vx=P.vy=0;if(t.place)t.place(P,s);
    L.torches.length=0;if(t.keep)L.torches.push(t.keep);const lc=Math.floor((P.x+s*(t.tq||60))/TW);L.torches.push({c:lc,r:t.r});
    H.GLFX.shadow=!!shadow;if(H.SHC)H.SHC.off=!!off;H.LAYER_DBG.hide=hide?new Set(hide):null;const G=H.GLFX;G.shafts=G.mist=G.caustics=G.lookfx=!clean;G.bloom=!clean&&kind!=='heap'&&kind!=='drift';/* (round 46b: the bloom held out, as layerscan's NOBLOOM: the shadow on the wall dims the glow that spreads onto a pale crest, light, not a draw-over) */H.clearRooms();
    H.cam.x=x-H.viewW/2;H.cam.y=(t.r+1)*64-64*1.6;H.cam.gy=H.cam.y;H.mode='play';H.GLP&&(H.GLP.pipe=false);
    H.render();H.render();H.render();if(H.SHC)H.SHC.off=false;H.LAYER_DBG.hide=null;G.shafts=G.mist=G.caustics=G.lookfx=G.bloom=true;
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


def changed(A, B, mk):  # pixels of the mask darker with the shadow on than off by more than 24 (sum of channels). (round 42b: darker only, as a
    # shadow only darkens: the GPU's multisampled edges of fine detail, a swing bar's rawhide turns, came out a few levels either way between two
    # renders, 6 px up and down on floor 32's bar)
    d = ImageChops.subtract(B, A).convert('RGB')
    r, g, bb = d.split()
    s = ImageChops.add(ImageChops.add(r, g), bb)
    hit = s.point(lambda v: 255 if v > 24 else 0)
    return ImageChops.multiply(hit, mk).histogram()[255], mk.histogram()[255]


def shot(pg):
    return Image.open(io.BytesIO(pg.screenshot())).convert('RGB')


if __name__ == '__main__':
    with sync_playwright() as p:
        b = p.chromium.launch(args=(['--use-angle=metal', '--force_high_performance_gpu'] if os.environ.get('HK_GPU') == '1' else []) + ['--enable-gpu', '--ignore-gpu-blocklist'])  # (HK_GPU=1: WebGL on the Radeon, as suite.py's heavy jobs)
        pg = page(b, SRC); rp = page(b, REF) if (not pg.shc or os.path.realpath(SRC) != os.path.realpath(REF)) else None
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
                        shc = r1['shc'] if pg.shc else None
                        if not shc and rp:  # (an older build that does not record this kind: the ref build's outlines in the same scene)
                            r2 = rp.evaluate("([n,sd,k,i])=>SHS.show(n,sd,k,i,true,false)", [n, sd, kind, i]); shc = r2 and r2['shc']; own = False
                        else: own = True
                        if not shc:
                            empty += 1; continue
                        pg.evaluate("([n,sd,k,i])=>SHS.show(n,sd,k,i,false,false)", [n, sd, kind, i]); Bm = shot(pg)
                        if kind in DRAWN:  # (round 46b) the thing as drawn: the frame with it less the frame without it, both with the shadow off, eroded as the outline's mask
                            pg.evaluate("([n,sd,k,i])=>SHS.show(n,sd,k,i,false,false,null,true)", [n, sd, kind, i]); Sm = shot(pg)  # (without the beams, mist, looks, caustics and bloom: their cut round it in the air would count as its pixels)
                            pg.evaluate("([n,sd,k,i])=>SHS.show(n,sd,k,i,false,false,[k],true)", [n, sd, kind, i]); Hm = shot(pg)
                            dd = ImageChops.difference(Sm, Hm).convert('RGB'); r_, g_, b_ = dd.split()
                            mk = ImageChops.add(ImageChops.add(r_, g_), b_).point(lambda v: 255 if v > 12 else 0).filter(ImageFilter.MinFilter(2 * ERODE + 1))
                        else:
                            mk = mask(shc, A.width, A.height)
                        nb, area = changed(A, Bm, mk)
                        if os.environ.get('SS_DUMP') and nb > 4:  # (the pixels that took his shadow, magenta, over the frame with it)
                            d = ImageChops.subtract(Bm, A).convert('RGB'); r_, g_, b_ = d.split(); hit = ImageChops.multiply(ImageChops.add(ImageChops.add(r_, g_), b_).point(lambda v: 255 if v > 24 else 0), mk)
                            vis = A.copy(); vis.paste((255, 0, 255), mask=hit.filter(ImageFilter.MaxFilter(3))); vis.save('%s_%s_%d_%d.png' % (os.environ['SS_DUMP'], kind, n, r1['c']))
                        if area < 20:
                            empty += 1; continue
                        if pg.shc and own:
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
