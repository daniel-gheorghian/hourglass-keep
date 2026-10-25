# layerscan.py [file.html] [lo hi] [seeds] [torch|classic|both] [kinds=a,b] [phases=K] [out.png]: nothing in the corridor is drawn over
# the front plane (round 39, the layering rule: dev/docs/layers.md). The room picture holds the back wall AND the front plane (wall
# blocks' front faces, low ceilings' faces, floor slabs' lips, all drawn HX left of their cell); every live thing is drawn after it, so
# a live thing stays behind a nearer face only where its drawing is cut. For each floor lo..hi (default 1-48) and seed (default 1),
# in Classic and Torchlight: views are chosen to cover every instance of each kind (a feature's type in L.dyn, and 'lamp', 'door',
# 'clock', 'block', 'flask', 'cue', 'jet', 'well', 'snake', 'guard', plus once per view the air passes 'ambient', 'atmo', 'emissive');
# each view is drawn whole and then with one kind left out (LAYER_DBG.hide, which leaves its light, shadow carve and relief rubbing as
# they are), at K clock phases where a kind moves (default 4: saws, pendulums, bars, jaws, vents, lifts' parts), and the pixels of the
# front plane (1 canvas px in from each face's edge; not the kind's own tile where it is drawn live, nor a lift's shaft) must not
# change. A kind is bad in a view when more than 4 of those pixels differ by more than 24 (sum of channels). The prince is moved out
# of the view; things that only exist in play (darts, debris, dust, trails, the prince's states) are not covered here.
# Prints a line per kind (views, bad, worst), 'layerscan: ok' or 'layerscan: FAIL', and a sheet of the worst cases (layerscan.png).
# Run from dev/tools.
import io, os, sys, time
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
SRC = os.path.abspath(next((x for x in a if x.endswith('.html')), os.path.join(HERE, '..', 'hourglass-keep.html')))
NUM = [int(x) for x in a if x.isdigit()]
LO, HI = (NUM + [1, 48])[:2] if len(NUM) >= 2 else (1, 48)
SEEDS = [int(s) for s in next((x for x in a if ',' in x and '=' not in x), '1').split(',')]
OUT = next((x for x in a if x.endswith('.png')), os.path.join(HERE, 'layerscan.png'))
MODES = ['torch', 'classic'] if 'both' in a or not ('torch' in a or 'classic' in a) else (['torch'] if 'torch' in a else ['classic'])
KINDS = next((x[6:].split(',') for x in a if x.startswith('kinds=')), None)
NPH = int(next((x[7:] for x in a if x.startswith('phases=')), '4'))
MOVING = ['saw', 'pend', 'bar', 'chomp', 'vent', 'lift', 'banner', 'emissive', 'ambient', 'atmo', 'lamp', 'jet', 'cue']

# every instance of every kind on the floor (world px: x, the floor line y), then views that cover them
LIST = r'''([n,sd,kinds])=>{const H=__HK;window.__HKfreeze=true;const L=H.load(n,sd,true),C=L.cols,TW=32,TH=64,out=[];
  const S=r=>(r+1)*TH-4,add=(k,c,r,x,y)=>{if(!kinds||kinds.includes(k))out.push([k,c,r,x===undefined?c*TW+16:x,y===undefined?S(r):y]);};
  for(const o of L.dyn)if(o.f.t!=='low')add(o.f.t,o.c,o.r);
  for(const t of L.torches)if(!t.broken)add('lamp',t.c,t.r);
  add('door',L.start.door===undefined?1:L.start.door,L.start.r);add('door',L.door.c,L.door.r);
  for(const q of L.cps)add('clock',q.c,q.r,q.x);
  for(const b of L.ext.blocks)add('block',b.c,b.r);
  for(const it of L.items){add('flask',it.c,it.r,it.x);if(it.hidden)add('cue',it.c,it.r,it.x);}
  for(const o of L.dyn)if(o.f.t==='shaftfoot')add('jet',o.c,o.r);
  for(const o of L.dyn)if(o.f.t==='loose'&&!o.f.plank&&o.f.wg&&o.f.wg.os&&o.f.wg.os[0]===o)add('well',o.c,o.r);
  for(const lf of L.lifts)add('lift',lf.ca,lf.rB,(lf.ca+lf.cb+1)*TW/2,(lf.rT*TH+S(lf.rB))/2);
  for(const s of H.SN||[])add('snake',Math.floor(s.x/TW),Math.floor(s.y/TH),s.x,s.y);
  for(const g of H.G||[])add('guard',Math.floor(g.x/TW),Math.floor(g.y/TH),g.x,g.y);
  H.render();const vh=document.getElementById('game').height/H.XF.VZ;return {out,vw:H.viewW,vh,rows:L.rows,cols:C};}'''

# draw the view whole and with each kind left out; compare the front plane's pixels in the page (no screenshots)
VIEW = r'''([n,sd,cx,cy,kinds,phases,own,vh])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS)H.S.hints[id]=1;
  const L=H.L&&H.L.n===n&&H.L.seed===H.levelSeed(n)?H.L:H.load(n,sd,true);H.banner=null;const C=L.cols,TW=32,TH=64,HX=8,HY=4,FHH=5,LOWH=30;
  const P=H.P;P.inv=1e9;P.x=-999;P.y=-999;H.cam.x=cx-H.viewW/2;H.cam.y=cy-vh/2;H.cam.gy=H.cam.y;H.mode='play';H.GLP&&(H.GLP.pipe=false);
  const torch=H.S.set.lightMode==='torch'&&H.shaderOn&&H.shaderOn(),src=torch?document.getElementById('glc'):document.getElementById('game');
  const tmp=window.__LYC||(window.__LYC=document.createElement('canvas'));
  const grab=()=>{H.render();H.render();if(tmp.width!==src.width||tmp.height!==src.height){tmp.width=src.width;tmp.height=src.height;}
    const g=tmp.getContext('2d',{willReadFrequently:true});g.clearRect(0,0,tmp.width,tmp.height);g.drawImage(src,0,0);return g.getImageData(0,0,tmp.width,tmp.height).data;};
  H.LAYER_DBG.hide=null;H.render();
  const X=H.XF,sx=src.width/(document.getElementById('game').width),W=tmp.width||src.width;
  const m=(x,y)=>[(x*X.VZ-X.camD)*sx,(y*X.VZ-X.camDY)*sx];
  // the front plane's faces in view, by cell; lift shafts left out (liftscan.py's)
  const shaft=new Set();for(const lf of L.lifts)for(let r=lf.rT;r<=lf.rB;r++)for(let c=lf.ca;c<=lf.cb;c++)shaft.add(r*C+c);
  const c0=Math.max(0,Math.floor((cx-H.viewW/2)/TW)-1),c1=Math.min(C-1,Math.floor((cx+H.viewW/2)/TW)+1),r0=Math.max(0,Math.floor((cy-vh/2)/TH)-1),r1=Math.min(L.rows-1,Math.floor((cy+vh/2)/TH)+1);
  const faces=[];for(let r=r0;r<=r1;r++)for(let c=c0;c<=c1;c++){const b=L.base[r*C+c],f=L.feat[r*C+c];if(shaft.has(r*C+c))continue;
    const X0=c*TW-HX,Y0=r*TH;
    if(b===2)faces.push([c,r,X0,Y0,X0+TW,Y0+TH,'wall']);else if(f&&f.t==='low')faces.push([c,r,X0,Y0,X0+TW,Y0+LOWH,'low']);
    if(b===1){const ys=(r+1)*TH-4;faces.push([c,r,X0,ys+HY,X0+TW,ys+HY+FHH,'lip']);}}
  const res={};const rec=(k,ph,A,B)=>{let nb=0,bx0=1e9,by0=1e9,bx1=-1e9,by1=-1e9,wc=null,wn=0;const per={};
    for(const fc of faces){const [c,r,x0,y0,x1,y1,kd]=fc;if(own[k]&&own[k].includes(r*C+c))continue;
      const p0=m(x0,y0),p1=m(x1,y1),ix0=Math.max(0,Math.ceil(p0[0])+1),iy0=Math.max(0,Math.ceil(p0[1])+1),ix1=Math.min(W,Math.floor(p1[0])-1),iy1=Math.min(tmp.height,Math.floor(p1[1])-1);let n=0;
      for(let y=iy0;y<iy1;y++){let i=(y*W+ix0)*4;for(let x=ix0;x<ix1;x++,i+=4){if(Math.abs(A[i]-B[i])+Math.abs(A[i+1]-B[i+1])+Math.abs(A[i+2]-B[i+2])>24){n++;if(x<bx0)bx0=x;if(x>bx1)bx1=x;if(y<by0)by0=y;if(y>by1)by1=y;}}}
      if(n){nb+=n;if(n>wn){wn=n;wc=[c,r,kd];}}}
    const o=res[k]||(res[k]={n:0,box:null,face:null,ph:0});if(nb>o.n){o.n=nb;o.box=[bx0/sx,by0/sx,bx1/sx,by1/sx];o.face=wc;o.ph=ph;}};
  for(const ph of phases){H.setGT(ph);H.LAYER_DBG.hide=null;const A=grab().slice();
    for(const k of kinds){if(k.mv===false&&ph!==phases[0])continue;H.LAYER_DBG.hide=new Set([k.k]);const B=grab();rec(k.k,ph,A,B);}
    H.LAYER_DBG.hide=null;const A2=grab();rec('_noise',ph,A,A2);}
  H.LAYER_DBG.hide=null;return {res,th:H.themeName(n)};}'''

# the cells whose tile a kind draws live itself (its own top and lip are its own drawing)
OWN = {'loose', 'plate', 'xplate', 'lplate', 'closer', 'grate', 'vent'}


def page(b, mode):
    pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=2)
    pg.errs = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e)))
    pg.goto('file://' + SRC)
    pg.wait_for_timeout(700)
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.body.classList.remove('panelOpen')")
    pg.evaluate("m=>{__HK.S.set.lightMode=m;}", mode)
    pg.evaluate("()=>{__HK.GLFX.sheen=false;}")  # (the wet floor's reflection mirrors lit things onto the floor by design, never on a face)
    return pg


def views(inst, vw, vh):  # greedy: centre a view on the first uncovered instance; it covers those within the middle of it
    hw, hh = vw / 2 - 64, vh / 2 - 72
    left, out = list(inst), []
    while left:
        k, c, r, x, y = left[0]
        cov = [q for q in left if abs(q[3] - x) <= hw and abs(q[4] - y) <= hh]
        out.append((x, y - 20, cov)); left = [q for q in left if q not in cov]
    return out


if __name__ == '__main__':
    t0 = time.time()
    with sync_playwright() as p:
        b = p.chromium.launch()
        stats, worst, errs = {}, [], []
        for mode in MODES:
            pg = page(b, mode)
            for n in range(LO, HI + 1):
                for sd in SEEDS:
                    li = pg.evaluate(LIST, [n, sd, KINDS])
                    inst = [tuple(q) for q in li['out']]
                    # one pass of views over every instance; each view tests every kind that has an instance in it, and the air once
                    for cx, cy, cov in views(inst, li['vw'], li['vh']):
                        ks = sorted(set(q[0] for q in cov))
                        if not KINDS or 'ambient' in KINDS: ks += ['ambient', 'atmo', 'emissive']
                        mv = any(k in MOVING for k in ks)
                        phases = [10 + 0.731 * i for i in range(NPH)] if mv else [10]
                        own = {}
                        for k in ks:
                            if k in OWN: own[k] = [q[2] * li['cols'] + q[1] for q in inst if q[0] == k]
                        r = pg.evaluate(VIEW, [n, sd, cx, cy, [{'k': k, 'mv': k in MOVING} for k in ks], phases, own, li['vh']])
                        for k, o in r['res'].items():
                            s = stats.setdefault((mode, k), {'views': 0, 'bad': 0, 'worst': 0, 'where': []})
                            s['views'] += 1
                            if o['n'] > 4:
                                s['bad'] += 1; s['worst'] = max(s['worst'], o['n'])
                                if len(s['where']) < 6: s['where'].append('%d/%d c%d r%d %s %dpx t%.2f' % (n, sd, o['face'][0], o['face'][1], o['face'][2], o['n'], o['ph']))
                                if k != '_noise' and len(worst) < 24 and sum(1 for w in worst if w[0] == (mode, k)) < 3:
                                    worst.append(((mode, k), n, sd, cx, cy, o, r['th'], li['vh']))
                errs += pg.errs
            pg.close()
        # pictures of the worst: the view drawn whole, the bad box marked
        sheet = []
        if worst:
            for mode in MODES:
                pg = page(b, mode)
                for (md, k), n, sd, cx, cy, o, th, vh in worst:
                    if md != mode: continue
                    pg.evaluate(VIEW, [n, sd, cx, cy, [], [o['ph']], {}, vh])
                    im = Image.open(io.BytesIO(pg.screenshot())).convert('RGB')
                    bx = o['box']; ccx, ccy = int((bx[0] + bx[2])), int((bx[1] + bx[3]))
                    cr = im.crop((ccx - 110, ccy - 90, ccx + 110, ccy + 90)); d = ImageDraw.Draw(cr)
                    d.rectangle((bx[0] * 2 - ccx + 110 - 3, bx[1] * 2 - ccy + 90 - 3, bx[2] * 2 - ccx + 110 + 3, bx[3] * 2 - ccy + 90 + 3), outline=(255, 60, 60))
                    d.text((4, 3), '%s %s %d/%d %dpx' % (mode[0], k, n, sd, o['n']), fill=(255, 240, 160)); sheet.append(cr)
                pg.close()
        b.close()
    nbad = 0
    for (mode, k), s in sorted(stats.items()):
        if k != '_noise': nbad += s['bad']
        print('%-7s %-9s views %4d  bad %3d  worst %5d  %s' % (mode, k, s['views'], s['bad'], s['worst'], '; '.join(s['where'][:4])))
    if sheet:
        W = 4
        sh = Image.new('RGB', (W * 222, ((len(sheet) + W - 1) // W) * 182), (20, 16, 24))
        for i, c in enumerate(sheet): sh.paste(c, ((i % W) * 222, (i // W) * 182))
        sh.save(OUT); print('wrote', OUT)
    print('layerscan: %s (%d bad kind-views, floors %d-%d, seeds %s, %.0f s)' % ('ok' if nbad == 0 and not errs else 'FAIL', nbad, LO, HI, ','.join(map(str, SEEDS)), time.time() - t0), 'errors', errs[:3])
