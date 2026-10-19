# liftscan.py [file.html] [lo hi] [seeds] [classic|torch|both]: no part of a lift, nor the prince riding it, is painted over
# the front face of a wall or a low ceiling (stone that stands nearer than the shaft), nor over a mouth grating where the grating
# stands in front. For many lifts (floors lo..hi, `seeds` seeds each, both kinds) at the top, halfway and at the bottom (the
# counterweight lift) or at three clock times (the paternoster), with him riding: the game's own render() is drawn twice, once
# as it is and once with the lifts and him left out (LIFT_DBG.off), and the two
# pictures must agree inside every wall front and low ceiling round the shaft (the 9 px floor lip on top of a wall is left out:
# a platform docked there shows its own). Torchlight is checked on its scene picture (what the shader lights) and on the metal
# mask (what it shines): on the WebGL path (v62) the scene target and the metal's place in the masks' atlas, read back. Prints one line per failing case, then ALL OK or FAILURES n. Run from dev/tools.
import os, sys
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
SRC = next((x for x in a if x.endswith('.html')), os.path.join(HERE, '..', 'hourglass-keep.html'))
nums = [int(x) for x in a if x.isdigit()]
LO, HI = (nums[0], nums[1]) if len(nums) >= 2 else (3, 60)
SEEDS = nums[2] if len(nums) >= 3 else 3
MODES = ['classic', 'torch'] if 'both' in a or not ('classic' in a or 'torch' in a) else (['classic'] if 'classic' in a else ['torch'])
CASES = r'''([lo,hi,seeds])=>{const H=__HK,out=[];
  for(let n=lo;n<=hi;n++)for(let s=0;s<seeds;s++){const seed=40000+n*131+s*7919,L=H.genLevel(n,seed,true);
    const seen={};L.lifts.forEach((f,i)=>{const k=f.t+(f.sand?'S':'')+(f.y===f.yT?'T':'B')+(f.sT||0);if(seen[k])return;seen[k]=1;out.push([n,seed,i,f.t]);});}
  return out;}'''
RUN = r'''([n,seed,i,pos,mode])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS)H.S.hints[id]=1;H.S.set.lightMode=mode;
  const L=H.load(n,seed,true);H.banner=null;const f=L.lifts[i],P=H.P;P.inv=1e9;
  const place=()=>{if(f.t==='lift'){const fr=[0,0.5,1][pos];f.y=f.yT+(f.yB-f.yT)*fr;f.tgt=null;L.base[f.rT*L.cols+f.sc]=fr===0?1:0;f.gT=fr===0?1:0;f.gB=fr===1?1:0;
      P.x=f.sc*32+16;P.y=f.y;P.fallY=P.y;P.face=pos===1?1:-f.sT;P.vx=P.vy=0;if(pos===1){P.state='lift';P.lift=f;}else{P.state='stand';P.lift=null;}}
    else{const q=H.chainPos(f,0,H.gameTime);P.x=q.x;P.y=q.y;P.fallY=P.y;P.state='lift';P.lift=f;P.slab=0;P.bx=q.x;P.by=q.y;P.bt=-9;P.face=pos===1?-f.dx:f.dx;}};
  if(f.t==='chain')H.tick(60*2*pos+1);place();H.cam.snap=true;
  for(let k=0;k<24;k++){H.tick(1);if(f.t==='lift')place();} // (his look offsets ease in)
  if(H.GLP)H.GLP.pipe=false;
  const tor=mode==='torch'&&H.shaderOn();
  if(tor&&H.GLP.gls){window.__HKnoauto=true;H.GLP.rs=1;}
  // (v62) the WebGL path: the scene target's resolved texture, and the metal mask from its place in the masks' atlas (GLA.G)
  const rdTex=(f,w,h)=>{const gl=H.GLP.gl,px=new Uint8Array(w*h*4);gl.bindFramebuffer(gl.FRAMEBUFFER,f);gl.readPixels(0,0,w,h,gl.RGBA,gl.UNSIGNED_BYTE,px);gl.bindFramebuffer(gl.FRAMEBUFFER,null);return px;};
  const grab=()=>{if(H.MS)H.MS.pv=false;H.render();H.render();const X=H.XF;
    if(tor&&H.GLP.gls){const G=H.GLS,t=G.scene,w=t.w,h=t.h,raw=rdTex(t.rf,w,h),img=new Uint8Array(w*h*4);for(let y=0;y<h;y++)img.set(raw.subarray((h-1-y)*w*4,(h-y)*w*4),y*w*4);
      const A=H.GLA.G,AT=G.atlT,mw=G.metal.w0||0,mh=G.metal.h0||0;let mk=null;
      if(mw&&mh&&A&&AT&&AT.rf){mk=new Uint8Array(mw*mh*4);for(let o=3;o<mk.length;o+=4)mk[o]=255;
        if(A.mo){const at=rdTex(AT.rf,AT.w,AT.h);for(let py=A.by;py<Math.min(mh,A.by+A.bh);py++){const ar=AT.h-1-(A.Y0+py-A.by);if(ar<0||ar>=AT.h)continue;
          for(let px=A.bx;px<Math.min(mw,A.bx+A.bw);px++){const s=(ar*AT.w+px-A.bx)*4,d=(py*mw+px)*4;mk[d]=at[s];mk[d+1]=at[s+1];mk[d+2]=at[s+2];}}}}
      return {img,w,h,VZ:X.VZ,camD:X.camD,camDY:X.camDY,mk,mw,mh,mox:0,moy:0};}
    const src=tor?H.GLP.sceneC:[...document.querySelectorAll('canvas')].find(c=>c.getBoundingClientRect().width>0&&c!==H.GLP.cv);
    const g=src.getContext('2d'),img=g.getImageData(0,0,src.width,src.height).data;let mk=null,mw=0,mh=0;
    const MS=H.MS;if(tor&&MS&&MS.c){mw=MS.c.width;mh=MS.c.height;mk=MS.g.getImageData(0,0,mw,mh).data;}
    return {img,w:src.width,h:src.height,VZ:X.VZ,camD:X.camD,camDY:X.camDY,mk,mw,mh,mox:0,moy:0};};
  const A=grab();
  H.LIFT_DBG.off=true;H.LIFT_DBG.rider=!window.__keepRider;let B;try{B=grab();}finally{H.LIFT_DBG.off=false;H.LIFT_DBG.rider=false;}
  // a grating on the shaft's right edge stands in front of everything in the shaft: where it is drawn (a frame with only those
  // gratings, against one with nothing of the lift) the full frame must show it
  let G=null;if(f.t==='lift'&&(f.sT>0||f.sB>0)){H.LIFT_DBG.gatesR=true;H.LIFT_DBG.rider=true;try{G=grab();}finally{H.LIFT_DBG.gatesR=false;H.LIFT_DBG.rider=false;}}
  let badG=0,gwhere=null;if(G){for(let o=0;o<A.img.length;o+=4){const dg=Math.abs(G.img[o]-B.img[o])+Math.abs(G.img[o+1]-B.img[o+1])+Math.abs(G.img[o+2]-B.img[o+2]);if(dg<90||Math.max(G.img[o]-B.img[o],G.img[o+1]-B.img[o+1],G.img[o+2]-B.img[o+2])<30)continue; // (the grating's own metal, brighter than what is behind it: not its slot's translucent shade)
    if(Math.abs(A.img[o]-G.img[o])+Math.abs(A.img[o+1]-G.img[o+1])+Math.abs(A.img[o+2]-G.img[o+2])>60){badG++;if(!gwhere){const px=(o/4)%A.w,py=Math.floor(o/4/A.w);gwhere=['grating',Math.round((px+A.camD)/A.VZ),Math.round((py+A.camDY)/A.VZ),'shaft x',f.sc*32,'P',Math.round(H.P.x),Math.round(H.P.y)];}}}}
  // the stone that stands nearer than the shaft: wall fronts (less the floor lip on their top) and low ceilings
  const rects=[];for(let r=f.rT-2;r<=f.rB+2;r++)for(let c=f.ca-3;c<=f.cb+3;c++){if(c<0||c>=L.cols||r<0||r>=L.rows)continue;const b=L.base[r*L.cols+c];
    if(b===2){const lip=r>0&&L.base[(r-1)*L.cols+c]!==2?9:0;rects.push([c*32-8,r*64+lip,32,64-lip]);}
    else{const q=L.feat[r*L.cols+c];if(q&&q.t==='low')rects.push([c*32-8,r*64,32,64-34]);}}
  let bad=0,badM=0,where=null;const sc=A.w/(A.VZ?1:1);
  for(const [x,y,w,h] of rects){const k=A.w/Math.max(1,document.querySelector('canvas').width); // (scene canvas and main canvas share the size)
    const x0=Math.max(0,Math.ceil(x*A.VZ-A.camD)+1),x1=Math.min(A.w,Math.floor((x+w)*A.VZ-A.camD)-1),y0=Math.max(0,Math.ceil(y*A.VZ-A.camDY)+1),y1=Math.min(A.h,Math.floor((y+h)*A.VZ-A.camDY)-1);
    for(let py=y0;py<y1;py++)for(let px=x0;px<x1;px++){const o=(py*A.w+px)*4,d=Math.abs(A.img[o]-B.img[o])+Math.abs(A.img[o+1]-B.img[o+1])+Math.abs(A.img[o+2]-B.img[o+2]);
      if(d>24){bad++;if(!where)where=[Math.round((px+A.camD)/A.VZ),Math.round((py+A.camDY)/A.VZ)];}}
    if(A.mk){const hx=Math.floor(A.camD/2),hy=Math.floor(A.camDY/2),mx0=Math.max(0,Math.ceil(x*A.VZ/2-hx)+1),mx1=Math.min(A.mw,Math.floor((x+w)*A.VZ/2-hx)-1),my0=Math.max(0,Math.ceil(y*A.VZ/2-hy)+1),my1=Math.min(A.mh,Math.floor((y+h)*A.VZ/2-hy)-1);
      for(let py=my0;py<my1;py++)for(let px=mx0;px<mx1;px++){const o=(py*A.mw+px)*4;if(Math.abs(A.mk[o]-B.mk[o])+Math.abs(A.mk[o+1]-B.mk[o+1])+Math.abs(A.mk[o+2]-B.mk[o+2])>24){badM++;if(!where)where=['mask',Math.round((px*2+A.camD)/A.VZ),Math.round((py*2+A.camDY)/A.VZ),[...A.mk.slice(o,o+3)],[...B.mk.slice(o,o+3)],A.mw,A.mh];}}}}
  return {bad,badM,badG,where:where||gwhere,rects:rects.length,t:f.t,st:P.state,rdx:+(P.rdx||0).toFixed(1)};}'''
fails = 0; n_cases = 0; tot = {}
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 844, 'height': 390})
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://' + os.path.abspath(SRC)); pg.wait_for_timeout(300)
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true)")
    if 'keeprider' in a: pg.evaluate("()=>{window.__keepRider=true}")  # (debug: leave him in both frames)
    cases = pg.evaluate(CASES, [LO, HI, SEEDS])
    for mode in MODES:
        for n, seed, i, t in cases:
            for pos in range(3):
                r = pg.evaluate(RUN, [n, seed, i, pos, mode]); n_cases += 1
                k = (mode, t); tot.setdefault(k, [0, 0]); tot[k][0] += 1
                if r['bad'] > 6 or r['badM'] > 3 or r['badG'] > 6:
                    fails += 1; tot[k][1] += 1
                    print('BAD %-7s n=%d seed=%d lift %d (%s) pos %d: %d px over stone (mask %d), %d over a grating in front, first at %s, he is %s rdx %s' % (mode, n, seed, i, t, pos, r['bad'], r['badM'], r['badG'], r['where'], r['st'], r['rdx']), flush=True)
    b.close()
print('cases', n_cases, ' '.join('%s/%s %d bad of %d' % (k[0], k[1], v[1], v[0]) for k, v in sorted(tot.items())), 'errors', errs[:3])
print('ALL OK' if fails == 0 and not errs else 'FAILURES %d' % (fails + (1 if errs else 0)))
sys.exit(1 if fails or errs else 0)
