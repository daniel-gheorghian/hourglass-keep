# contourscan.py [file.html] [lo hi] [seeds] [torch|classic] [kinds=a,b] [per=K] [nofigures] [dump=DIR]: the contour rule (round 46, owner: "as a rule,
# if you add contours or accents always use a darker shade of the pixels that are closer to the edge or lighter if light hits it - with some
# tinting of course"; "apply it everywhere"; dev/docs/rendering.md "Contours"). An edge is never a fixed near-black ink: it is the fill beside
# it, darker and moved toward the theme's shadow tint (selOut k < 1), or lighter toward the light's tint where light hits it (k > 1).
# For each floor lo..hi (default 1-48) and seed (default 1), views are chosen to cover every instance of each kind (layerscan.py's list: a
# feature's type in L.dyn, 'lamp', 'door', 'clock', 'block', 'flask', 'lift', 'jamb', 'heap', 'drift'; the figures 'guard', 'snake',
# 'prince', judged as the props since round 46d (reported only in 46c; `nofigures` leaves them out); each view is drawn whole and with one kind left out
# (LAYER_DBG.hide; lamps' drawn glows out of both, the clock frozen, him out of view; a drift's sand stream and the wind's dust, air, held out
# as heapscan.py does). The kind's pixels are those that differ (sum of
# channels > 30), less an even darkening (its shadow on the floor or wall: every channel down by the same ratio, as heapscan.py). Its edge
# pixels are those within one world px of its outline (a chessboard distance on the canvas), its fill the mean of its pixels 2 to 3.5 world
# px in from it within 4 world px of the edge pixel. An edge pixel fails when it is darker than DARK (60, its brightest channel) and more
# than NEAR (40 levels on any channel) from selOut(fill, k) for every k from 0.45 to 1.15 (selOut as the game's: toward the theme's lo by
# 0.28 (1 - k) / 0.45 and scaled by k; above 1 toward warm white by 1.5 (k - 1)). Edge pixels with no fill near them (a rope, a thin rod)
# are not judged. A kind is bad in a view when over SHARE (2%) of its judged edge pixels fail and at least MINPX (80 canvas px, about 5
# world px square at the phone's 4 px a world px) do: a slot's or a hole's own dark where it meets the thing's edge (a saw's slot under its
# blade, 77 px on floor 9) is not an outline and stays under it; v87's inks fail by hundreds (plates 200-640 px a view). Classic by default (software, cheap; Torchlight with `torch`). Prints a line per kind (views, bad, failing share,
# worst), 'contourscan: ok' or 'contourscan: FAIL'; per=K takes up to K instances of each kind a floor (default 3, spread along it); dump=DIR writes each kind's worst view with the failing pixels in magenta.
# Run from dev/tools.
import base64, os, sys, time
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
SRC = os.path.abspath(next((x for x in a if x.endswith('.html') and '=' not in x), os.path.join(HERE, '..', 'hourglass-keep.html')))
NUM = [int(x) for x in a if x.isdigit()]
LO, HI = (NUM[0], NUM[1]) if len(NUM) >= 2 else (1, 48)
SEEDS = [int(s) for s in next((x for x in a if ',' in x and '=' not in x), str(NUM[2]) if len(NUM) > 2 else '1').split(',') if s]
MODE = 'torch' if 'torch' in a else 'classic'
KINDS = next((x[6:].split(',') for x in a if x.startswith('kinds=')), None)
FIGS = 'nofigures' not in a
DUMP = next((x[5:] for x in a if x.startswith('dump=')), None)
PER = int(next((x[4:] for x in a if x.startswith('per=')), '3'))  # (up to K instances of each kind a floor, spread along it)
DARK, NEAR, SHARE, MINPX = 60, 40, 0.02, 80
FIGURES = {'guard', 'snake', 'prince'}  # (round 46d: judged with the same thresholds as the props)
SKIP = {'low', 'hurtdrop', 'trigger', 'jgrab', 'shaftfoot', 'sanctum', 'well', 'chain'}  # (no outline of their own: a low ceiling is the room picture's; a kick shaft's grips are holes in the wall; sand; a well's slabs are 'loose')

LIST = r'''([n,sd,kinds,figs])=>{const H=__HK;window.__HKfreeze=true;const L=H.load(n,sd,false),C=L.cols,TW=32,TH=64,out=[];
  const S=r=>(r+1)*TH-4,add=(k,c,r,x,y)=>{if(!kinds||kinds.includes(k))out.push([k,c,r,x===undefined?c*TW+16:x,y===undefined?S(r):y]);};
  for(const o of L.dyn)add(o.f.t,o.c,o.r);
  for(const t of L.torches)if(!t.broken)add('lamp',t.c,t.r);
  add('door',L.start.door===undefined?1:L.start.door,L.start.r);add('door',L.door.c,L.door.r);
  for(const q of L.cps)add('clock',q.c,q.r,q.x);
  for(const b of L.ext.blocks)add('block',b.c,b.r);
  for(const it of L.items)if(!it.hidden)add('flask',it.c,it.r,it.x);
  for(const lf of L.lifts)add('lift',lf.ca,lf.rB,(lf.ca+lf.cb+1)*TW/2,(lf.rT*TH+S(lf.rB))/2);
  for(const h of L.hills||[])add(h.d?'drift':'heap',h.c,h.r,(h.c+h.n/2)*TW);
  for(const k of L.courts||[]){add('jamb',k.c0,k.r,k.c0*TW);add('jamb',k.c1,k.r,(k.c1+1)*TW);}
  if(figs){for(const s of H.SN||[])add('snake',Math.floor(s.x/TW),Math.floor(s.y/TH),s.x,s.y);for(const g of H.G||[])add('guard',Math.floor(g.x/TW),Math.floor(g.y/TH),g.x,g.y);
    // (round 46d) him on the start's row where no wall stands in his cell or beside it, so no face cuts him (a cut is not his outline)
    const sr=L.start.r,clr=x=>{const c=Math.floor(x/TW);for(let d=-1;d<=1;d++){const q=c+d;if(q<0||q>=L.cols||L.base[sr*L.cols+q]===2)return false;}return true;}; // (2: WALL)
    const px=[40,-40,72,-72,104,-104,8].map(d=>L.start.x+d).find(clr);const ppx=px===undefined?L.start.x+40:px;add('prince',Math.floor(ppx/TW),sr,ppx,S(sr));}
  H.render();const vh=document.getElementById('game').height/H.XF.VZ;return {out,vw:H.viewW,vh,lo:L.theme.lo,th:H.themeName(n)};}'''

VIEW = r'''([n,sd,cx,cy,kinds,px,lo,DARK,NEAR,dump])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS)H.S.hints[id]=1;
  const L=H.L&&H.L.n===n&&H.L.seed===H.levelSeed(n)?H.L:H.load(n,sd,false);H.banner=null;
  const P=H.P;P.inv=1e9;if(px){P.x=px[0];P.y=px[1];P.fallY=P.y;P.vx=P.vy=0;P.state='stand';P.face=1;}else{P.x=-999;P.y=-999;}
  if(H.HILL_DBG)H.HILL_DBG.stream=false;if(L.winds)L.winds.length=0;H.cam.x=cx-H.viewW/2;H.cam.y=cy-H.vh/2;H.cam.gy=H.cam.y;H.mode='play';H.GLP&&(H.GLP.pipe=false);H.setGT(10);
  const torch=H.S.set.lightMode==='torch'&&H.shaderOn&&H.shaderOn(),src=torch?document.getElementById('glc'):document.getElementById('game');
  const tmp=window.__CSC||(window.__CSC=document.createElement('canvas'));
  const grab=()=>{H.render();H.render();if(tmp.width!==src.width||tmp.height!==src.height){tmp.width=src.width;tmp.height=src.height;}
    const g=tmp.getContext('2d',{willReadFrequently:true});g.clearRect(0,0,tmp.width,tmp.height);g.drawImage(src,0,0);return g.getImageData(0,0,tmp.width,tmp.height).data;};
  H.LAYER_DBG.hide=null;H.LAYER_DBG.glow=false;const A=grab().slice();
  const X=H.XF,sx=src.width/(document.getElementById('game').width),W=src.width,Hh=src.height,N=W*Hh,wp=X.VZ*sx;
  const E=Math.max(1,Math.round(wp)),I0=2*wp,I1=3.5*wp,R=Math.round(4*wp);
  const lc=[parseInt(lo.slice(1,3),16),parseInt(lo.slice(3,5),16),parseInt(lo.slice(5,7),16)],KS=[];for(let k=0.45;k<1.151;k+=0.05)KS.push(k);
  const M=window.__CSM&&window.__CSM.length===N?window.__CSM:(window.__CSM=new Uint8Array(N)),D=window.__CSD&&window.__CSD.length===N?window.__CSD:(window.__CSD=new Uint16Array(N)),SA=window.__CSA&&window.__CSA.length===(W+1)*(Hh+1)*4?window.__CSA:(window.__CSA=new Float64Array((W+1)*(Hh+1)*4)),res={};
  for(const k of kinds){H.LAYER_DBG.hide=new Set([k]);const B=grab();
    let any=0,mx0=1e9,my0=1e9,mx1=-1,my1=-1;for(let i=0,j=0;i<N;i++,j+=4){const a0=A[j],a1=A[j+1],a2=A[j+2],b0=B[j],b1=B[j+1],b2=B[j+2];
      if(Math.abs(a0-b0)+Math.abs(a1-b1)+Math.abs(a2-b2)<=30){M[i]=0;continue;}
      if(a0<=b0+2&&a1<=b1+2&&a2<=b2+2){const r0=(a0+1)/(b0+1),r1=(a1+1)/(b1+1),r2=(a2+1)/(b2+1),mx=Math.max(r0,r1,r2),mn=Math.min(r0,r1,r2);if(mx-mn<0.08&&(r0+r1+r2)/3<0.97){M[i]=0;continue;}}
      M[i]=1;any=1;const x=i%W,y=(i-x)/W;if(x<mx0)mx0=x;if(x>mx1)mx1=x;if(y<my0)my0=y;if(y>my1)my1=y;}
    if(!any){res[k]={e:0,f:0};continue;}
    // (only the box round its pixels, R and a pixel more: everything outside it is outside the kind)
    const X0=Math.max(0,mx0-R-2),Y0=Math.max(0,my0-R-2),X1=Math.min(W-1,mx1+R+2),Y1=Math.min(Hh-1,my1+R+2);
    // chessboard distance to the outside
    for(let y=Y0;y<=Y1;y++)for(let x=X0;x<=X1;x++){const i=y*W+x;if(!M[i]){D[i]=0;continue;}let d=60000;
      if(x>X0)d=Math.min(d,D[i-1]+1);else d=1;if(y>Y0){d=Math.min(d,D[i-W]+1);if(x>X0)d=Math.min(d,D[i-W-1]+1);if(x<X1)d=Math.min(d,D[i-W+1]+1);}else d=1;D[i]=d;}
    for(let y=Y1;y>=Y0;y--)for(let x=X1;x>=X0;x--){const i=y*W+x;if(!M[i])continue;let d=D[i];
      if(x<X1)d=Math.min(d,D[i+1]+1);else d=1;if(y<Y1){d=Math.min(d,D[i+W]+1);if(x<X1)d=Math.min(d,D[i+W+1]+1);if(x>X0)d=Math.min(d,D[i+W-1]+1);}else d=1;D[i]=d;}
    // summed areas of the fill ring (r, g, b, count), in the box
    const BW=X1-X0+1,BH=Y1-Y0+1,W1=BW+1;SA.fill(0,0,(BW+1)*(BH+1)*4);
    for(let y=0;y<BH;y++){let s0=0,s1=0,s2=0,s3=0;for(let x=0;x<BW;x++){const i=(y+Y0)*W+x+X0,j=i*4;if(M[i]&&D[i]>=I0&&D[i]<=I1){s0+=A[j];s1+=A[j+1];s2+=A[j+2];s3++;}
      const o=((y+1)*W1+x+1)*4,u=(y*W1+x+1)*4;SA[o]=SA[u]+s0;SA[o+1]=SA[u+1]+s1;SA[o+2]=SA[u+2]+s2;SA[o+3]=SA[u+3]+s3;}}
    let ne=0,nf=0,fx0=1e9,fy0=1e9,fx1=-1,fy1=-1;const fl=dump?new Uint8Array(N):null;const f=[0,0,0],t=[0,0,0];
    for(let y=Y0;y<=Y1;y++)for(let x=X0;x<=X1;x++){const i=y*W+x;if(!M[i]||D[i]>E)continue;
      const xa=Math.max(0,x-X0-R),xb=Math.min(BW,x-X0+R+1),ya=Math.max(0,y-Y0-R),yb=Math.min(BH,y-Y0+R+1),q=(a,b)=>(b*W1+a)*4;
      const c3=SA[q(xb,yb)+3]-SA[q(xa,yb)+3]-SA[q(xb,ya)+3]+SA[q(xa,ya)+3];if(c3<3)continue;ne++;
      const j=i*4,p0=A[j],p1=A[j+1],p2=A[j+2];if(Math.max(p0,p1,p2)>=DARK)continue;
      for(let c=0;c<3;c++)f[c]=(SA[q(xb,yb)+c]-SA[q(xa,yb)+c]-SA[q(xb,ya)+c]+SA[q(xa,ya)+c])/c3;let best=1e9;
      for(const kk of KS){if(kk<1){const u=Math.min(1,0.28*(1-kk)/0.45);for(let c=0;c<3;c++)t[c]=(f[c]+(lc[c]-f[c])*u)*kk;}else{const u=Math.min(0.5,(kk-1)*1.5);t[0]=Math.min(255,f[0]+(255-f[0])*u);t[1]=Math.min(255,f[1]+(240-f[1])*u);t[2]=Math.min(255,f[2]+(214-f[2])*u);}
        const dd=Math.max(Math.abs(t[0]-p0),Math.abs(t[1]-p1),Math.abs(t[2]-p2));if(dd<best)best=dd;}
      if(best>NEAR){nf++;if(fl)fl[i]=1;if(x<fx0)fx0=x;if(x>fx1)fx1=x;if(y<fy0)fy0=y;if(y>fy1)fy1=y;}}
    const o={e:ne,f:nf,box:nf?[fx0,fy0,fx1,fy1]:null};
    if(dump&&nf){const cw=Math.min(W,fx1-fx0+120),ch=Math.min(Hh,fy1-fy0+120),bx=Math.max(0,Math.min(W-cw,(fx0+fx1-cw)>>1)),by=Math.max(0,Math.min(Hh-ch,(fy0+fy1-ch)>>1));
      const cv=document.createElement('canvas');cv.width=cw*2;cv.height=ch;const g=cv.getContext('2d'),id=g.createImageData(cw,ch),id2=g.createImageData(cw,ch);
      for(let y=0;y<ch;y++)for(let x=0;x<cw;x++){const s=((by+y)*W+bx+x),j=s*4,t=(y*cw+x)*4;for(let c=0;c<4;c++){id.data[t+c]=A[j+c];id2.data[t+c]=A[j+c];}id.data[t+3]=id2.data[t+3]=255;if(fl[s]){id2.data[t]=255;id2.data[t+1]=0;id2.data[t+2]=255;}}
      g.putImageData(id,0,0);g.putImageData(id2,cw,0);o.png=cv.toDataURL('image/png');}
    res[k]=o;}
  H.LAYER_DBG.hide=null;H.LAYER_DBG.glow=true;return res;}'''


def views(inst, vw, vh):  # (layerscan.py's: centre a view on the first uncovered instance; it covers those within the middle of it)
    hw, hh = vw / 2 - 64, vh / 2 - 72
    left, out = list(inst), []
    while left:
        k, c, r, x, y = left[0]
        cov = [q for q in left if abs(q[3] - x) <= hw and abs(q[4] - y) <= hh]
        out.append((x, y - 20, cov)); left = [q for q in left if q not in cov]
    return out


if __name__ == '__main__':
    t0 = time.time()
    stats, errs, worst = {}, [], {}
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-angle=metal', '--force_high_performance_gpu', '--enable-gpu', '--ignore-gpu-blocklist'] if os.environ.get('HK_GPU') == '1' else [])
        pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=2)
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto('file://' + SRC); pg.wait_for_timeout(700)
        pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.body.classList.remove('panelOpen')")
        pg.evaluate("m=>{__HK.S.set.lightMode=m;__HK.GLFX.sheen=false;if(!('vh' in __HK))Object.defineProperty(__HK,'vh',{get(){return document.getElementById('game').height/__HK.XF.VZ;}});}", MODE)
        for n in range(LO, HI + 1):
            for sd in SEEDS:
                li = pg.evaluate(LIST, [n, sd, KINDS, FIGS])
                inst = [tuple(q) for q in li['out'] if q[0] not in SKIP and (FIGS or q[0] not in FIGURES)]
                by = {}
                for q in inst: by.setdefault(q[0], []).append(q)
                inst = [v[int(i * len(v) / PER)] if len(v) > PER else v[i] for v in by.values() for i in range(min(PER, len(v)))]
                for cx, cy, cov in views(inst, li['vw'], li['vh']):
                    ks = sorted(set(q[0] for q in cov))
                    pr = next(([q[3], q[4]] for q in cov if q[0] == 'prince'), None)
                    r = pg.evaluate(VIEW, [n, sd, cx, cy, ks, pr, li['lo'], DARK, NEAR, bool(DUMP)])
                    for k, o in r.items():
                        s = stats.setdefault(k, {'views': 0, 'bad': 0, 'e': 0, 'f': 0, 'worst': 0.0, 'where': []})
                        s['views'] += 1; s['e'] += o['e']; s['f'] += o['f']
                        sh = o['f'] / o['e'] if o['e'] else 0
                        if sh > SHARE and o['f'] >= MINPX:
                            s['bad'] += 1
                            if len(s['where']) < 4: s['where'].append('%d/%d x%d %.1f%% (%d px)' % (n, sd, cx, 100 * sh, o['f']))
                        if sh > s['worst']:
                            s['worst'] = sh
                            if DUMP and o.get('png'): worst[k] = (o['png'], n, sd, li['th'])
                print('floor %d seed %d (%s) done, %.0f s' % (n, sd, li['th'], time.time() - t0), flush=True)
        b.close()
    if DUMP:
        os.makedirs(DUMP, exist_ok=True)
        for k, (png, n, sd, th) in worst.items():
            open(os.path.join(DUMP, 'cs_%s_%s_%d.png' % (MODE, k, n)), 'wb').write(base64.b64decode(png.split(',')[1]))
    nbad = 0
    for k, s in sorted(stats.items()):
        nbad += s['bad']
        print('%-7s %-9s views %4d  bad %3d  edge px %8d  failing %5.2f%%  worst %5.1f%%  %s' % (MODE, k, s['views'], s['bad'], s['e'], 100 * s['f'] / max(1, s['e']), 100 * s['worst'], '; '.join(s['where'])))
    if errs: print('errors', errs[:3])
    print('contourscan: %s (%d bad kind-views, floors %d-%d, seeds %s, %s, %.0f s)' % ('ok' if nbad == 0 and not errs and stats else 'FAIL', nbad, LO, HI, ','.join(map(str, SEEDS)), MODE, time.time() - t0))
    sys.exit(0 if nbad == 0 and not errs and stats else 1)
