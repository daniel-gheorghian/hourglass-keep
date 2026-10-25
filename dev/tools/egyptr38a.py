# egyptr38a.py [part ...] [base=file.html] [new=file.html]: pictures and numbers for round 38a (owner: "Correct all Claude.md and all of
# the faults, then release"; the look faults found by dev/docs). Each part draws v82 (dev/tools/hk_v82_release.html) | round 38a (the
# source), both modes, cropped round the case and enlarged:
#   rope    the dungeon style's wall fitting under a ceiling (backCell): v61's iron chain | a short laid rope, knotted or a sling with a jar (r38a_rope.png)
#   shadow  a figure's lamp shadow on what stands in front of the back wall (glMask, SHC): the prince beside each kind with a lamp behind
#           him; Torchlight, shadow on and the difference to shadow off (r38a_shadow.png)
#   roof    a fallen roof block's relief (glRelFloors): Torchlight with the wall's art and with it flattened (EGP.noart), the difference; counts (r38a_roof.png)
#   grate   the fork's grating in a sky beam's footprint (fpMarkGrate on its bars): both modes; the mean level on it (r38a_grate.png)
#   blk     beam blockers: a lift's mouth slab in a beam, and views with more than four blockers by the beams; counts (r38a_blk.png)
#   cost    script and frame time (with gl.finish) of views carrying the new work, v82 against 38a (numbers only; view=n,sd,x,r adds a view)
# Run from dev/tools; 'cost' is not in the default list.
import io, os, sys, json
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageChops
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
BASE = next((x[5:] for x in a if x.startswith('base=')), os.path.join(HERE, 'hk_v82_release.html'))
NEW = next((x[4:] for x in a if x.startswith('new=')), os.path.join(HERE, '..', 'hourglass-keep.html'))
PARTS = [x for x in a if '=' not in x] or ['rope', 'shadow', 'roof', 'grate', 'blk']
sys.argv = sys.argv[:1]  # (shadowscan reads its own arguments when imported)
sys.path.insert(0, HERE)
from shadowscan import JS as SCENE, mask as shmask, changed as shchanged


def page(b, src, mode):
    pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=2)
    pg.errs = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e)))
    pg.goto('file://' + os.path.abspath(src)); pg.wait_for_timeout(700)
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.body.classList.remove('panelOpen')")
    pg.evaluate("m=>{__HK.S.set.lightMode=m;__HK.GLFX.sheen=false;}", mode)
    if SCENE:
        pg.evaluate(SCENE)
    return pg


def shot(pg):
    return Image.open(io.BytesIO(pg.screenshot())).convert('RGB')


def crop(im, cx, cy, w, h, k=1.0):  # css px centre and size; device scale 2
    c = im.crop((int(cx * 2 - w), int(cy * 2 - h), int(cx * 2 + w), int(cy * 2 + h)))
    return c.resize((int(c.width * k), int(c.height * k)), Image.LANCZOS) if k != 1 else c


def sheet(rows, labels, out, title):  # rows: lists of images of one size
    w, h = rows[0][0].size
    S = Image.new('RGB', (len(rows[0]) * (w + 4) + 4, len(rows) * (h + 18) + 22), (18, 14, 22))
    d = ImageDraw.Draw(S)
    d.text((6, 4), title, fill=(255, 240, 170))
    for i, row in enumerate(rows):
        for j, im in enumerate(row):
            S.paste(im, (4 + j * (w + 4), 22 + i * (h + 18) + 14))
        d.text((6, 22 + i * (h + 18)), labels[i], fill=(220, 220, 230))
    S.save(out); print('wrote', out)


# ---- rope: the dungeon style's wall fitting (hash2(gc*3+11, gr*5+7) % 13 == 1 under a ceiling)
FIND_ROPE = r'''([n,sd,skip])=>{const H=__HK;window.__HKfreeze=true;const L=H.load(n,sd,true),C=L.cols;if(L.theme.style!=='dungeon')return null;
  const h2=(a,b)=>{let h=(Math.imul(a|0,374761393)+Math.imul(b|0,668265263))|0;h=Math.imul(h^(h>>>13),1274126177);return (h^(h>>>16))>>>0;},bs=L.base0||L.base;let k=0;
  for(let r=1;r<L.rows-1;r++)for(let c=4;c<C-4;c++){if(bs[r*C+c]===2||bs[(r-1)*C+c]===0||h2(c*3+11,r*5+7)%13!==1)continue;
    if(bs[r*C+c+1]===2||L.feat[r*C+c]||L.feat[r*C+c+1])continue;if(k++<skip)continue;return [c,r,(h2(c*3+11,r*5+7)>>5)&1,H.themeName(n)];}
  return null;}'''
SHOW_AT = r'''([n,sd,c,r])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS)H.S.hints[id]=1;const L=H.load(n,sd,true);H.banner=null;H.intro=0;
  const P=H.P;P.inv=1e9;P.x=-999;H.clearRooms();H.cam.x=c*32+16-H.viewW/2;H.cam.y=(r+1)*64-64*1.6;H.cam.gy=H.cam.y;H.mode='play';H.GLP&&(H.GLP.pipe=false);
  H.render();H.render();H.render();const X=H.XF,cv=[...document.querySelectorAll('canvas')].find(q=>q.getBoundingClientRect().width>0),R=cv.getBoundingClientRect();
  const m=(x,y)=>[R.left+(x*X.VZ-X.camD)/cv.width*R.width,R.top+(y*X.VZ-X.camDY)/cv.height*R.height];return m(c*32+22,r*64+12);}'''


def part_rope(b):
    cases = []
    pg = page(b, NEW, 'torch')
    for n, sd, skip in [(2, 1, 0), (2, 1, 1), (2, 2, 0), (18, 1, 0), (18, 2, 0), (38, 1, 0), (38, 2, 0), (41, 1, 0)]:
        f = pg.evaluate(FIND_ROPE, [n, sd, skip])
        if f: cases.append((n, sd, f))
    pg.close()
    rows, labels = [], []
    for n, sd, (c, r, kn, th) in cases[:5]:
        row = []
        for src in (BASE, NEW):
            for mode in ('classic', 'torch'):
                pg = page(b, src, mode); m = pg.evaluate(SHOW_AT, [n, sd, c, r]); im = shot(pg)
                if pg.errs: print('errors', pg.errs[:2])
                row.append(crop(im, m[0], m[1], 70, 60, 1.5)); pg.close()
        rows.append(row); labels.append('floor %d seed %d cell %d,%d %s (%s): v82 Classic | v82 Torchlight | 38a Classic | 38a Torchlight' % (n, sd, c, r, th, 'knot' if kn else 'jar'))
    sheet(rows, labels, os.path.join(HERE, 'r38a_rope.png'), 'round 38a: the dungeon style\'s wall fitting under a ceiling: v61\'s iron chain | a laid rope in the theme\'s fibre')


# ---- shadow: one case of each kind (shadowscan.py's scenes: the prince beside it, a torch behind him), Torchlight
SHADOW_CASES = [('slab', 20, 1, 0, 'a granite portcullis'), ('slab', 5, 1, 6, 'a lift\'s mouth slab'), ('slab', 20, 1, 11, 'a sand lift\'s foot mouth'),
                ('stakes', 20, 1, 0, 'the stakes'), ('saw', 7, 1, 0, 'a saw\'s blade'), ('pend', 9, 1, 1, 'the pendulum'), ('roof', 2, 1, 0, 'a fallen roof block'),
                ('clock', 20, 1, 0, 'the sky clock'), ('flask', 20, 1, 0, 'a flask'), ('liftslab', 5, 1, 0, 'a lift\'s platform'), ('liftslab', 8, 1, 13, 'a paternoster\'s slab'),
                ('rope', 5, 1, 0, 'a lift platform\'s ropes'), ('rope', 8, 1, 13, 'a paternoster\'s ropes')]


def part_shadow(b):
    rows, labels = [], []
    for kind, n, sd, i, what in SHADOW_CASES:
        row, th, mid = [], '', None
        for src in (NEW, BASE):  # (the source first: the crop is centred on the thing's outline as it records it)
            pg = page(b, src, 'torch')
            r = pg.evaluate("([n,sd,k,i])=>SHS.show(n,sd,k,i,true,false)", [n, sd, kind, i])
            if not r: pg.close(); break
            if mid is None:
                pts = [p_ for e in (r['shc'] or []) for rg in e['rings'] for p_ in rg]
                mid = [(min(p_[0] for p_ in pts) + max(p_[0] for p_ in pts)) / 2, (min(p_[1] for p_ in pts) + max(p_[1] for p_ in pts)) / 2] if pts else r['mid']
                if kind in ('rope', 'pend'): mid = list(r['mid'])  # (a rope runs the shaft's height, the pendulum's arm from the ceiling: framed at the blade, his height)
            A = shot(pg); pg.evaluate("([n,sd,k,i])=>SHS.show(n,sd,k,i,false,false)", [n, sd, kind, i]); B = shot(pg)
            if pg.errs: print('errors', pg.errs[:2])
            pg.close(); th = r['th']
            d = ImageChops.difference(A, B).point(lambda v: min(255, v * 4))
            row = [crop(A, mid[0], mid[1], 110, 80, 1.2), crop(d, mid[0], mid[1], 110, 80, 1.2)] + row
        if len(row) == 4:
            rows.append(row); labels.append('%s, floor %d seed %d %s: v82 | his shadow there x4 | 38a | his shadow there x4' % (what, n, sd, th))
    sheet(rows, labels, os.path.join(HERE, 'r38a_shadow.png'), 'round 38a: a figure\'s lamp shadow on what stands in front of the back wall (Torchlight): v82 | 38a (glMask carves SHC)')


# ---- roof: a fallen roof block lying across the corridor, Torchlight with the back wall's art and with it flattened (EGP.noart 'atop'), a torch
# two cells off; its front, top and side (1.7 px in) must not change: the relief reads the room's picture and embossed the art behind it on the block
ROOF = r"""([n,sd,i,noart])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS)H.S.hints[id]=1;const L=H.load(n,sd,true),C=L.cols;H.banner=null;H.intro=0;
  const st=L.dyn.filter(o=>o.f.t==='stone'),o=st[i];if(!o)return st.length?{n:st.length}:null;o.f.s=2;o.f.land=-100;L.rubble.add(o.r*C+o.c);
  const P=H.P;P.inv=1e9;P.x=-999;L.torches.length=0;const lc=H.solidBelow(o.c-2,o.r)&&L.base[o.r*C+o.c-2]!==2?o.c-2:o.c+2;L.torches.push({c:lc,r:o.r});
  H.EGP.noart=noart?'atop':false;H.clearRooms();H.cam.x=o.c*32+16-H.viewW/2;H.cam.y=(o.r+1)*64-64*1.6;H.cam.gy=H.cam.y;H.mode='play';H.GLP&&(H.GLP.pipe=false);
  H.render();H.render();H.render();H.EGP.noart=false;const X=H.XF,cv=[...document.querySelectorAll('canvas')].find(q=>q.getBoundingClientRect().width>0),R=cv.getBoundingClientRect();
  const m=p=>[R.left+(p[0]*X.VZ-X.camD)/cv.width*R.width,R.top+(p[1]*X.VZ-X.camDY)/cv.height*R.height];
  const x0=o.c*32+16-8-11,yt=(o.r+1)*64-4+4-10,w=22,h=10,dx=16,dy=8;
  return {n:st.length,c:o.c,r:o.r,th:H.themeName(n),mid:m([x0+15,yt]),poly:[[x0,yt+h],[x0,yt],[x0+dx,yt-dy],[x0+w+dx,yt-dy],[x0+w+dx,yt+h-dy],[x0+w,yt+h]].map(m)};}"""


def roof_case(b, src, n, sd, i):
    out = []
    for noart in (False, True):
        pg = page(b, src, 'torch'); r = pg.evaluate(ROOF, [n, sd, i, noart]); im = shot(pg); pg.close()
        if not r or 'poly' not in r: return None
        out.append((r, im))
    (r, A), (_, B) = out
    mk = shmask([{'rings': [r['poly']], 'clip': [[-9999, -9999], [9999, 9999]]}], A.width, A.height)
    nb, area = shchanged(A, B, mk)
    return r, A, B, nb, area


def part_roof(b):
    rows, labels, stat = [], [], {}
    for n, sd in [(2, 1), (3, 1), (4, 1), (21, 1), (22, 1), (23, 1), (24, 1), (2, 2), (3, 2)]:
        pg = page(b, NEW, 'torch'); cnt = pg.evaluate(ROOF, [n, sd, 999, False]); pg.close()
        k = cnt['n'] if cnt else 0
        for i in range(0, k, max(1, k // 3)):
            row, lab = [], ''
            for tag, src in (('v82', BASE), ('38a', NEW)):
                c = roof_case(b, src, n, sd, i)
                if not c: continue
                r, A, B, nb, area = c; st = stat.setdefault(tag, [0, 0, 0]); st[0] += 1; st[1] += nb > 6; st[2] += nb
                d = ImageChops.difference(A, B).point(lambda v: min(255, v * 4))
                row += [crop(A, r['mid'][0], r['mid'][1], 90, 60, 1.5), crop(d, r['mid'][0], r['mid'][1], 90, 60, 1.5)]
                lab = 'floor %d seed %d block c%d r%d %s' % (n, sd, r['c'], r['r'], r['th'])
            if len(row) == 4 and len(rows) < 6:
                rows.append(row); labels.append(lab + ': v82 | v82 art less flattened x4 | 38a | 38a art less flattened x4')
    for tag, (t, bad, px) in stat.items():
        print('roof %s: %d fallen blocks framed, %d with the wall\'s art embossed on them (more than 6 px change by more than 24; %d px in all)' % (tag, t, bad, px))
    sheet(rows, labels, os.path.join(HERE, 'r38a_roof.png'), 'round 38a: a fallen roof block in Torchlight, the back wall\'s art embossed on it by the relief: v82 | 38a (glRelFloors, glRelRoof)')


# ---- grate: the fork's grating (a kind 4 fork's, rare and seldom in a beam) laid on a floor cell where a sky beam's footprint lands (as
# beamshot.py finds them: an opening whose beam from its middle lands on floor at c-1..c+1), the prince away; both modes
GRATE = r"""([n,skip,put])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS)H.S.hints[id]=1;let k=0;
  for(let sd=1;sd<60;sd++){const L=H.load(n,700+sd,true),C=L.cols;H.banner=null;H.intro=0;const sb=H.skyBeam();
    for(const o of H.ryOps()){if(o.sh&&o.sh.own)continue;if(o.x0<12*32||o.x1>(L.cols-12)*32)continue;
      const r=Math.round((o.fl+4)/64)-1,cy=(o.y0+o.y1)/2,lx=(o.x0+o.x1)/2+sb.dx/sb.dy*(o.fl-cy),c=Math.floor(lx/32);
      if(r<0||r>=L.rows||!H.solidBelow(c,r)||!H.solidBelow(c-1,r)||!H.solidBelow(c+1,r)||L.feat[r*C+c]||L.base[r*C+c]===2)continue;
      if(k++<skip)continue;
      if(put){const f={t:'grate',fork:4};L.feat[r*C+c]=f;L.dyn.push({c,r,f});}
      const P=H.P;P.inv=1e9;P.x=-999;H.clearRooms();H.cam.x=lx-H.viewW/2;H.cam.y=(r+1)*64-64*1.6;H.cam.gy=H.cam.y;H.mode='play';H.GLP&&(H.GLP.pipe=false);
      H.render();H.render();H.render();const X=H.XF,cv=[...document.querySelectorAll('canvas')].find(q=>q.getBoundingClientRect().width>0),R=cv.getBoundingClientRect();
      const m=(x,y)=>[R.left+(x*X.VZ-X.camD)/cv.width*R.width,R.top+(y*X.VZ-X.camDY)/cv.height*R.height];
      return {sd:700+sd,c,r,th:H.themeName(n),kind:o.kind,mid:m(c*32+16,(r+1)*64-4),tile:[[c*32-8,(r+1)*64],[c*32+24,(r+1)*64],[c*32+40,(r+1)*64-8],[c*32+8,(r+1)*64-8]].map(p=>m(p[0],p[1]))};}}
  return null;}"""


def part_grate(b):
    rows, labels = [], []
    for n, skip in [(34, 0), (31, 0), (7, 0), (45, 0)]:
        row, lab = [], ''
        for mode in ('torch', 'classic'):
            for tag, src in (('v82', BASE), ('38a', NEW)):
                pg = page(b, src, mode); r = pg.evaluate(GRATE, [n, skip, True]); im = shot(pg)
                if not r: pg.close(); continue
                pg.evaluate(GRATE, [n, skip, False]); im0 = shot(pg); pg.close()
                if pg.errs: print('errors', pg.errs[:2])
                mk = shmask([{'rings': [r['tile']], 'clip': [[-9999, -9999], [9999, 9999]]}], im.width, im.height)
                # how bright the grating's tile is against the plain floor tile there (the footprint on it): mean of the tile's pixels
                def mean(I):
                    s = [0, 0, 0]; px = I.load(); nn = 0
                    bb = mk.getbbox() or (0, 0, 0, 0)
                    for y in range(bb[1], bb[3]):
                        for x in range(bb[0], bb[2]):
                            if mk.getpixel((x, y)):
                                p_ = px[x, y]; s[0] += p_[0]; s[1] += p_[1]; s[2] += p_[2]; nn += 1
                    return sum(s) / max(1, nn) / 3
                print('grate %s %-7s floor %d seed %d c%d r%d (%s): mean level on the grating %.1f, on the plain floor there %.1f' % (tag, mode, n, r['sd'], r['c'], r['r'], r['kind'], mean(im), mean(im0)))
                row.append(crop(im, r['mid'][0], r['mid'][1] - 6, 70, 46, 2))
                lab = 'floor %d seed %d c%d r%d %s, under a beam through an %s' % (n, r['sd'], r['c'], r['r'], r['th'], r['kind'])
        if len(row) == 4:
            rows.append(row); labels.append(lab + ': Torchlight v82 | 38a, Classic v82 | 38a')
    sheet(rows, labels, os.path.join(HERE, 'r38a_grate.png'), 'round 38a: the fork\'s grating in a sky beam\'s footprint (laid there for the picture): its bars take the footprint (fpMarkGrate)')


# ---- blk: beam blockers. (a) a lift's (or sand lift's) mouth slab, down, in a beam's haze (ryBlkLit): it was no blocker at all; (b) a view
# with more than four blockers by the beams where one in a beam's haze came after the first four (the shader took the first four in order).
# Searched with the source's exports (beamBlockers, ryBlkLit); the same view drawn by v82 and 38a, Torchlight and Classic
BLKS = r"""([n,sd])=>{const H=__HK;window.__HKfreeze=true;const L=H.load(n,sd,true),C=L.cols,out={mouth:[],many:[]};const sb=H.skyBeam(),ops=H.ryOps().filter(o=>!(o.sh&&o.sh.own));
  if(!ops.length)return out;for(const o of ops)H.ryProfile(o.sh);const lit=i=>ops.some(o=>H.ryBlkLit(i,o,sb));
  for(const f of L.lifts){if(f.t!=='lift')continue;const ms=f.sand?(f.ms||[]).map(s=>[s,f.rB,1]):[[f.sT,f.rT,0],[f.sB,f.rB,2]];
    if(f.sand)f.y=f.yT;else{f.gB=0;f.gT=0;}
    for(const [s,rr,e] of ms){if(!s)continue;const gx=s<0?f.sc*32-3.5:(f.sc+1)*32+3.5,nb=H.beamBlockers(gx-30,gx+30,rr*64-10,rr*64+74);
      for(let i=0;i<nb;i++){const q=H.BLK.q,j=i*8;if(Math.abs((q[j]+q[j+2])/2-gx)>2)continue;if(lit(i))out.mouth.push([L.lifts.indexOf(f),e,s,Math.round(gx),rr]);}}}
  const xs=[];for(const o of L.dyn)if(o.f.t==='chomp'||o.f.t==='gate')xs.push([o.c*32+16,o.r]);
  for(const [x,r] of xs){const x0=x-200,x1=x+200,y0=(r+1)*64-102-10,y1=y0+212;const nb=H.beamBlockers(x0,x1,y0,y1);if(nb<=4)continue;let miss=0,nl=0;for(let i=0;i<nb;i++)if(lit(i)){nl++;if(i>=4)miss++;}
    if(miss)out.many.push([x,r,nb,nl,miss]);}
  return out;}"""
BLKSHOW = r"""([n,sd,x,r,lift,e])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS)H.S.hints[id]=1;const L=H.load(n,sd,true);H.banner=null;H.intro=0;
  for(const f of L.lifts){if(f.t!=='lift')continue;if(f.sand)f.y=f.yT;else{f.gB=0;f.gT=0;}}
  const P=H.P;P.inv=1e9;P.x=-999;H.clearRooms();H.cam.x=x-H.viewW/2;H.cam.y=(r+1)*64-64*1.6;H.cam.gy=H.cam.y;H.mode='play';H.GLP&&(H.GLP.pipe=false);
  H.render();H.render();H.render();const X=H.XF,cv=[...document.querySelectorAll('canvas')].find(q=>q.getBoundingClientRect().width>0),R=cv.getBoundingClientRect();
  return [R.left+(x*X.VZ-X.camD)/cv.width*R.width,R.top+(((r+1)*64-30)*X.VZ-X.camDY)/cv.height*R.height,H.themeName(n),H.GLC&&H.GLC.nb];}"""


def part_blk(b):
    pg = page(b, NEW, 'torch'); mouths, many = [], []
    for n in list(range(4, 49)):
        for sd in (1, 2):
            r = pg.evaluate(BLKS, [n, sd])
            mouths += [(n, sd) + tuple(m) for m in r['mouth']]; many += [(n, sd) + tuple(m) for m in r['many']]
    pg.close()
    print('blk: lift mouth slabs down in a beam\'s haze (floors 4-48, seeds 1-2): %d; views with a lit blocker past the first four: %d' % (len(mouths), len(many)))
    print('  mouths:', mouths[:8]); print('  many:', many[:8])
    # draw up to 10 of each in both builds and modes, measure how much 38a changes the view (mean level over the frame), keep the 3 + 2 that change most
    got = []
    for kind, lst in (('mouth', [(m[0], m[1], m[5], m[6]) for m in mouths[::max(1, len(mouths) // 10)][:10]]), ('many', [(m[0], m[1], m[2], m[3]) for m in many[::max(1, len(many) // 10)][:10]])):
        res = []
        for n, sd, x, r in lst:
            ims, th, nb = {}, '', {}
            for mode in ('torch', 'classic'):
                for tag, src in (('v82', BASE), ('38a', NEW)):
                    pg = page(b, src, mode); q = pg.evaluate(BLKSHOW, [n, sd, x, r, 0, 0]); ims[(mode, tag)] = (shot(pg), q); pg.close(); th = q[2]
                    if mode == 'torch': nb[tag] = q[3]
            dt = ImageChops.difference(ims[('torch', 'v82')][0], ims[('torch', '38a')][0]).convert('L'); dc = ImageChops.difference(ims[('classic', 'v82')][0], ims[('classic', '38a')][0]).convert('L')
            st = sum(i * v for i, v in enumerate(dt.histogram())) / (dt.width * dt.height); sc = sum(i * v for i, v in enumerate(dc.histogram())) / (dc.width * dc.height)
            print('  %s floor %d seed %d x %d row %d %s: blockers to the shader v82 %s 38a %s; mean change Torchlight %.3f Classic %.3f' % (kind, n, sd, x, r, th, nb.get('v82'), nb.get('38a'), st, sc), flush=True)
            res.append((st + sc, kind, n, sd, x, r, th, ims, dt, dc))
        res.sort(key=lambda z: -z[0]); got += res[:3 if kind == 'mouth' else 2]
    rows, labels = [], []
    for _, kind, n, sd, x, r, th, ims, dt, dc in got:
        row = []
        for mode, d in (('torch', dt), ('classic', dc)):
            q = ims[(mode, '38a')][1]; cx, cy = q[0], q[1] - 10
            row += [crop(ims[(mode, 'v82')][0], cx, cy, 130, 90, 1), crop(ims[(mode, '38a')][0], cx, cy, 130, 90, 1), crop(d.point(lambda v: min(255, v * 4)).convert('RGB'), cx, cy, 130, 90, 1)]
        rows.append(row); labels.append('%s: floor %d seed %d x %d row %d %s: Torchlight v82 | 38a | change x4, Classic v82 | 38a | change x4' % ('a lift mouth slab (down) in a beam' if kind == 'mouth' else 'more than four blockers by the beams', n, sd, x, r, th))
    if rows:
        sheet(rows, labels, os.path.join(HERE, 'r38a_blk.png'), 'round 38a: beam blockers: lift mouth slabs (down) shade the beam behind them; the shader tests up to eight, those in a beam\'s haze first')


# ---- cost: the frame's time, v82 against 38a, in views that carry the new work (the prince with a lamp by stakes, the sky clock, a portcullis:
# the carve; a view with many blockers by the beams: the shader's test). Each view drawn 40 times: script (render(), the JS and G2D's recording
# and replay calls) and the whole frame with gl.finish() (software WebGL here: the GPU's work on the CPU, a proxy for the GPU's own time)
COST_SET = r"""([kind,n,sd,i,x,r])=>{const H=__HK;if(kind!=='view'){SHS.show(n,sd,kind,i,true,false);}
  else{window.__HKfreeze=true;const L=H.load(n,sd,true);H.banner=null;H.intro=0;for(const f of L.lifts){if(f.t!=='lift')continue;if(f.sand)f.y=f.yT;else{f.gB=0;f.gT=0;}}
    const P=H.P;P.inv=1e9;P.x=x+30;P.y=(r+1)*64-4;P.state='stand';H.GLFX.shadow=true;H.clearRooms();H.cam.x=x-H.viewW/2;H.cam.y=(r+1)*64-64*1.6;H.cam.gy=H.cam.y;H.mode='play';H.GLP&&(H.GLP.pipe=false);}
  for(let k=0;k<8;k++)H.render();H.GLP.gl.finish();return [H.GLC&&H.GLC.nb||0,H.SHC?H.SHC.n:-1];}"""
COST_RUN = r"""([N,off])=>{const H=__HK,gl=H.GLP.gl;if(H.SHC)H.SHC.off=off;H.render();gl.finish();let s=0,w=0;
  for(let k=0;k<N;k++){const t0=performance.now();H.render();const t1=performance.now();gl.finish();const t2=performance.now();s+=t1-t0;w+=t2-t0;}
  if(H.SHC)H.SHC.off=false;return [s/N,w/N];}"""
COST_CASES = [('stakes', 20, 1, 0, 0, 0), ('clock', 20, 1, 0, 0, 0), ('slab', 20, 1, 0, 0, 0), ('stakes', 28, 1, 5, 0, 0)]


def part_cost(b):
    extra = [x for x in a if x.startswith('view=')]  # view=n,sd,x,r: a view by the beams with many blockers (blk's search)
    cases = COST_CASES + [('view',) + tuple(int(v) for v in e[5:].split(',')[:2]) + (0,) + tuple(int(v) for v in e[5:].split(',')[2:4]) for e in extra]
    med = lambda v: sorted(v)[len(v) // 2]
    for case in cases:
        pg82, pg38 = page(b, BASE, 'torch'), page(b, NEW, 'torch')
        i82, i38 = pg82.evaluate(COST_SET, list(case)), pg38.evaluate(COST_SET, list(case))
        R = {'v82': [], '38a': [], '38a carve off': []}
        for rnd in range(8):  # (batches of 10 frames, the builds taking turns, so a change in the machine's load falls on both)
            order = [('v82', pg82, False), ('38a', pg38, False), ('38a carve off', pg38, True)]
            for tag, pg, off in (order if rnd % 2 == 0 else order[::-1]):
                R[tag].append(pg.evaluate(COST_RUN, [10, off]))
        pg82.close(); pg38.close()
        s = {k: med([v[0] for v in R[k]]) for k in R}; w = {k: med([v[1] for v in R[k]]) for k in R}
        print('cost %-6s %s: frame ms (render + gl.finish, median of 8 batches) v82 %.2f, 38a %.2f (%+.1f%%), 38a carve off %.2f; script ms v82 %.2f 38a %.2f; blockers to the shader %d | %d; outlines carved %s' % (
            case[0], case[1:], w['v82'], w['38a'], 100 * (w['38a'] / w['v82'] - 1), w['38a carve off'], s['v82'], s['38a'], i82[0], i38[0], i38[1]), flush=True)


if __name__ == '__main__':
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--enable-gpu', '--ignore-gpu-blocklist'])
        for part in PARTS:
            globals()['part_' + part](b)
        b.close()
