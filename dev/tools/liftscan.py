# liftscan.py [file.html] [lo hi] [seeds] [classic|torch|both]: no part of a lift, nor the prince riding it, is painted over
# the front face of a wall or a low ceiling (stone that stands nearer than the shaft), nor over a mouth grating where the grating
# stands in front. For many lifts (floors lo..hi, `seeds` seeds each, both kinds) at the top, halfway and at the bottom (the
# counterweight lift) or at three clock times (the paternoster), with him riding: the game's own render() is drawn twice, once
# as it is and once with the lifts and him left out (LIFT_DBG.off), and the two
# pictures must agree inside every wall front and low ceiling round the shaft (the 9 px floor lip on top of a wall is left out:
# a platform docked there shows its own). Torchlight is checked on its scene picture (what the shader lights) and on the metal
# mask (what it shines): on the WebGL path (v62) the scene target and the metal's place in the masks' atlas, read back. Prints one line per failing case, then ALL OK or FAILURES n. Run from dev/tools.
# Round 26a (owner: "windows or walls or wall trims are drawn over the lift mechanisms", "at the top the lift slab is drawn in front of the
# wall", "when at the bottom the slab digs into the tile floor", "part of the door slab doesn't respect the shadow") adds, per case:
#  near: in the column right of the shaft, the walls' whole front faces (their strip under a floor's lip too) and each floor tile's top and
#        lip must show nothing of the lift (a frame with the lift but not him, against one without the lift; a right mouth slab, which stands
#        on that landing, is in both): a slab or platform's right side face lay over the landing beside it;
#  foot: a paternoster's foot floor's lip (its shaft columns) must show nothing of the slabs: a slab on its bottom run covered it;
#  wedge: a left mouth slab that is shut, where it rises past the ceiling's edge beside the shaft, is no brighter there than the ceiling's
#        shade just under that edge (it was lit, a bright wedge over the dark band);
#  relief (Torchlight, with a lamp near): the final picture of the lift's slabs, platform and counterweight is the same with Torchlight's
#        relief off: the back wall's art was embossed on them;
# and the paternoster gets two more clock times: a slab on its bottom run, and one at the top of the column beside the right landing.
# Round 37a (owner after v81: "The lift shafts, at the very bottom the floor tile should be missing because the moving tile of the lift will
# replace it"), per counterweight and sand lift case:
#  pit:  the room's picture draws no floor tile (slab()) in the foot cell of a lift with a pit (liftPit: all but the counterweight lifts whose
#        foot is open on its far side, which keep theirs), and does draw one where there is none (and at a paternoster's foot);
#  flush: with the platform or slab at rest at the foot, its lip covers the floor lips' rows (the floor line + 0.5 to + 4.5 px: every row over
#        60% of the cell's width), its top the rows just above them (- 2 to - 0.5 px, 60%), and nothing of it is under them (+ 6.25 to + 7.5
#        px, where the pit's floor edge and the lips' shade are: no row over 30%), against the frame with no lift: its top and lip within 1 px
#        of the floor tiles' beside it. 'flushlog' prints the three numbers for every such case. (round 38c) The platform is drawn unworn for
#        it (f.wl 0): a worn lip's chips are as dark as the pit's floor and read as uncovered (floors 17, 24, 37, 40, 43, 57: 0.51-0.6 worn, 1 unworn).
# Before the cases it counts the arches (recesses, openings) and breaches set in a lift shaft's back wall (cells, any number is a failure).
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
# arches and breaches in a lift shaft's back wall, counted on the tiles
ART = r'''([lo,hi,seeds])=>{const H=__HK;let arch=0,br=0,cells=0;const where=[];
  for(let n=lo;n<=hi;n++)for(let s=0;s<seeds;s++){const seed=40000+n*131+s*7919,L=H.load(n,seed,true);
    for(const f of L.lifts){for(let r=f.rT-1;r<=f.rB;r++)for(let c=f.ca;c<=f.cb;c++){cells++;if(r>=f.rT&&H.isArchTop(c,r)){arch++;if(where.length<5)where.push(['arch',n,seed,c,r]);}}
      for(const b of H.breaches())if(b&&b.x1>f.ca*32-8+4&&b.x0<(f.cb+1)*32-8-4&&b.y1>f.rT*64+4&&b.y0<SURF(f.rB)-4){br++;if(where.length<5)where.push(['breach',n,seed,f.ca,f.rB]);}}}
  return {arch,br,cells,where};function SURF(r){return (r+1)*64-4;}}'''
RUN = r'''([n,seed,i,pos,mode])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS)H.S.hints[id]=1;H.S.set.lightMode=mode;
  const SL=H.LIFT_DBG.tiles=new Set(); // (round 37a: the floor tiles the room pictures draw)
  let L;try{L=H.load(n,seed,true);}catch(e){H.LIFT_DBG.tiles=null;throw e;}H.banner=null;const f=L.lifts[i],P=H.P;P.inv=1e9;
  const place=()=>{if(f.t==='lift'){const fr=[0,0.5,1][pos];f.y=f.yT+(f.yB-f.yT)*fr;f.tgt=null;L.base[f.rT*L.cols+f.sc]=fr===0?1:0;f.gT=fr===0?1:0;f.gB=fr===1?1:0;
      P.x=f.sc*32+16;P.y=f.y;P.fallY=P.y;P.face=pos===1?1:-f.sT;P.vx=P.vy=0;if(pos===1){P.state='lift';P.lift=f;}else{P.state='stand';P.lift=null;}}
    else{const q=H.chainPos(f,0,H.gameTime);P.x=q.x;P.y=q.y;P.fallY=P.y;P.state='lift';P.lift=f;P.slab=0;P.bx=q.x;P.by=q.y;P.bt=-9;P.face=pos===1?-f.dx:f.dx;}};
  if(f.t==='chain'){if(pos<3)H.tick(60*2*pos+1);else{H.tick(1);for(let k=0;k<1200;k++){let hit=false;for(let j=0;j<f.n;j++){const q=H.chainPos(f,j,H.gameTime);
        if(pos===3?Math.abs(q.y-f.yB)<0.5&&(Math.abs(q.x-(f.ca*32+16))<1.5||Math.abs(q.x-(f.cb*32+16))<1.5):Math.abs(q.y-f.yT)<0.5&&Math.abs(q.x-(f.cb*32+16))<1.5)hit=true;}
      if(hit)break;H.tick(1);}}}
  place();H.cam.snap=true;
  for(let k=0;k<(f.t==='chain'&&pos>=3?1:24);k++){H.tick(1);if(f.t==='lift')place();} // (his look offsets ease in; at the chain's set places, one tick)
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
  let A;try{A=grab();}finally{H.LIFT_DBG.tiles=null;}const slN=SL.size;
  H.LIFT_DBG.off=true;H.LIFT_DBG.rider=!window.__keepRider;let B;try{B=grab();}finally{H.LIFT_DBG.off=false;H.LIFT_DBG.rider=false;}
  // a grating on the shaft's right edge stands in front of everything in the shaft: where it is drawn (a frame with only those
  // gratings, against one with nothing of the lift) the full frame must show it
  let G=null;if(f.t==='lift'&&(f.sT>0||f.sB>0)){H.LIFT_DBG.gatesR=true;H.LIFT_DBG.rider=true;try{G=grab();}finally{H.LIFT_DBG.gatesR=false;H.LIFT_DBG.rider=false;}}
  let badG=0,gwhere=null;if(G){for(let o=0;o<A.img.length;o+=4){const dg=Math.abs(G.img[o]-B.img[o])+Math.abs(G.img[o+1]-B.img[o+1])+Math.abs(G.img[o+2]-B.img[o+2]);if(dg<90||Math.max(G.img[o]-B.img[o],G.img[o+1]-B.img[o+1],G.img[o+2]-B.img[o+2])<30)continue; // (the grating's own metal, brighter than what is behind it: not its slot's translucent shade)
    if(Math.abs(A.img[o]-G.img[o])+Math.abs(A.img[o+1]-G.img[o+1])+Math.abs(A.img[o+2]-G.img[o+2])>60){badG++;if(!gwhere){const px=(o/4)%A.w,py=Math.floor(o/4/A.w);gwhere=['grating',Math.round((px+A.camD)/A.VZ),Math.round((py+A.camDY)/A.VZ),'shaft x',f.sc*32,'P',Math.round(H.P.x),Math.round(H.P.y)];}}}}
  // (round 26a) the lift without him: C; and the final picture of C with and without the relief (Torchlight, WebGL path)
  H.LIFT_DBG.rider=true;let C;try{C=grab();}finally{H.LIFT_DBG.rider=false;}
  const B0=G||B,inS=(px,py)=>px>=0&&py>=0&&px<A.w&&py<A.h,dif=(X,Y,o)=>Math.abs(X.img[o]-Y.img[o])+Math.abs(X.img[o+1]-Y.img[o+1])+Math.abs(X.img[o+2]-Y.img[o+2]);
  const pxOf=(x,y)=>[Math.round(x*A.VZ-A.camD),Math.round(y*A.VZ-A.camDY)];
  // near: the column right of the shaft
  let near=0,nwhere=null;{const cc=(f.t==='chain'?f.cb:f.sc)+1,xr=cc*32-8,pts=[];
    for(let r=f.rT-1;r<=f.rB+1;r++){if(r<0||r>=L.rows||cc>=L.cols)continue;const b=L.base[r*L.cols+cc];
      if(b===2){for(let y=r*64+1;y<r*64+63;y+=0.5)for(let x=xr+1;x<xr+31;x+=0.5)pts.push(x,y);}
      else if(H.solidBelow(cc,r)){const sy=(r+1)*64-4;for(let y=sy-3.5;y<sy+12;y+=0.5)for(let x=xr+1;x<xr+40;x+=0.5){const dl=y>sy+4?xr+1:xr+1+(sy+4-y)*2; // (left of the depth diagonal is the shaft)
          if(x<dl||x>xr+31+Math.min(16,Math.max(0,(sy+4-y)*2))-1||y>sy+12.5)continue;pts.push(x,y);}}}
    for(let k=0;k<pts.length;k+=2){const [px,py]=pxOf(pts[k],pts[k+1]);if(!inS(px,py))continue;const o=(py*A.w+px)*4;if(dif(C,B0,o)>36){near++;if(!nwhere)nwhere=['near',Math.round(pts[k]),Math.round(pts[k+1])];}}}
  // foot: a paternoster's foot floor's lip in its shaft columns
  let foot=0;if(f.t==='chain'){for(let y=f.yB+5;y<f.yB+12.5;y+=0.5)for(let x=f.ca*32-8+1;x<(f.cb+1)*32-8-1;x+=0.5){const [px,py]=pxOf(x,y);if(!inS(px,py))continue;const o=(py*A.w+px)*4;if(dif(C,B,o)>36){foot++;if(!nwhere)nwhere=['foot',Math.round(x),Math.round(y)];}}}
  // wedge: a shut left mouth slab where it rises past the ceiling's front edge beside the shaft
  let wedge=0,wv=null;if(f.t==='lift'&&!f.sand)for(let e=0;e<2;e++){const s=e?f.sB:f.sT,op=e?f.gB:f.gT,rr=e?f.rB:f.rT;if(s>=0||op>=1)continue;
    const X=f.sc*32-3.5-16,Y=rr*64,gc=Math.floor(X/32),co=L.base[(rr-1)*L.cols+gc]===1?5:0,pl={L0:X+8,R0:X+24,top:Y+co,ce:x=>Y+co-8*(x-X-8)/16},c=Math.floor((X+1)/32),xe=(c+1)*32-8; // (the gate's plane, as plane() makes it)
    if(!(rr>0&&L.base[(rr-1)*L.cols+c]===2&&L.base[(rr-1)*L.cols+c+1]!==2))continue;
    let sw=0,nw=0,sb=0,nb=0;for(let x=xe+1.5;x<pl.R0+3.5-1;x+=0.5){for(let y=pl.ce(x)-3+1.5;y<pl.top-1;y+=0.5){const [px,py]=pxOf(x,y);if(!inS(px,py))continue;const o=(py*A.w+px)*4;sw+=C.img[o]+C.img[o+1]+C.img[o+2];nw++;}
      for(let y=pl.top+0.6;y<pl.top+2.5;y+=0.5){const [px,py]=pxOf(x,y);if(!inS(px,py))continue;const o=(py*A.w+px)*4;sb+=C.img[o]+C.img[o+1]+C.img[o+2];nb++;}}
    if(nw>4&&nb>4){const mw=sw/nw/3,mb=sb/nb/3;wv=[Math.round(mw),Math.round(mb)];if(mw>mb+4)wedge++;}}
  // relief: the final picture over the lift's stone with the relief on and off
  let relief=0;if(tor&&H.GLP.gls&&H.GLFX.relief){const fin=()=>{H.LIFT_DBG.rider=true;try{if(H.MS)H.MS.pv=false;H.render();H.render();const gl=H.GLP.gl,w=gl.drawingBufferWidth,h=gl.drawingBufferHeight;return {px:rdTex(null,w,h),w,h};}finally{H.LIFT_DBG.rider=false;}};
    const R1=fin(),relOn=H.GLREL.on;H.GLFX.relief=false;let R0;try{R0=fin();}finally{H.GLFX.relief=true;}
    if(relOn){const k=R1.w/A.w,boxes=[];if(f.t==='chain'){for(let j=0;j<f.n;j++){const q=H.chainPos(f,j,H.gameTime);boxes.push([q.x-16-8+2,q.y+4+1,q.x-16-8+30,q.y+4+4]);}}else if(!f.sand)boxes.push([f.sc*32-8+2,f.y+4+1,f.sc*32-8+30,f.y+4+4]);
      for(const [x0,y0,x1,y1] of boxes)for(let y=y0;y<=y1;y+=0.5)for(let x=x0;x<=x1;x+=0.5){const [px,py]=pxOf(x,y);if(!inS(px,py))continue;const qx=Math.round(px*k),qy=R1.h-1-Math.round(py*k);if(qx<0||qy<0||qx>=R1.w||qy>=R1.h)continue;
        const o=(qy*R1.w+qx)*4;if(Math.abs(R1.px[o]-R0.px[o])+Math.abs(R1.px[o+1]-R0.px[o+1])+Math.abs(R1.px[o+2]-R0.px[o+2])>30){relief++;if(!nwhere)nwhere=['relief',Math.round(x),Math.round(y)];}}}}
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
  // (round 37a) pit: no floor tile in the room's picture at the foot of a lift with a pit, one where it has none; flush: the platform at rest
  // at the foot covers the floors' lip rows and its top the rows above, against the frame with no lift
  let pit=0,pwhere=null,flush=null;{const C0=L.cols,exp=f.t==='lift'&&(!!f.sand||L.base0[f.rB*C0+f.sc-f.sB]===2),cols=f.t==='chain'?[f.ca,f.cb]:[f.sc];
    for(const c of cols){const has=SL.has(f.rB*C0+c);if(slN===0||has===exp){pit++;pwhere=['pit',c,f.rB,'tile drawn',has,'pit expected',exp,'tiles drawn',slN];}}
    if(exp&&pos===2&&Math.abs(f.y-f.yB)<0.01){const ft=(f.rB+1)*64,fx=f.sc*32-8;
      // (round 38c) measured on the platform drawn unworn: a worn lip's chips are as dark as the pit's floor (floor 40 seed 45240: 0.51 worn, 1 unworn); wear is look only
      let Cf=C;{const w0=f.wl,n0=f.wn;f.wl=0;f.wn=L.n;H.LIFT_DBG.rider=true;try{Cf=grab();}finally{H.LIFT_DBG.rider=false;f.wl=w0;f.wn=n0;}}
      const cov=(y,xa,xb)=>{let k=0,m=0;for(let x=xa;x<=xb;x+=0.5){const [px,py]=pxOf(x,y);if(!inS(px,py))continue;m++;if(dif(Cf,B,(py*A.w+px)*4)>36)k++;}return m?k/m:1;};
      let lip=1,top=1,und=0;for(let y=ft+0.5;y<=ft+4.5;y+=0.5)lip=Math.min(lip,cov(y,fx+2,fx+30));for(let y=ft-2;y<=ft-0.5;y+=0.5)top=Math.min(top,cov(y,fx+7,fx+30));
      for(let y=ft+6.25;y<=ft+7.5;y+=0.25)und=Math.max(und,cov(y,fx+2,fx+30));flush=[+lip.toFixed(2),+top.toFixed(2),+und.toFixed(2)];
      if(lip<0.6||top<0.6||und>0.3){pit++;if(!pwhere)pwhere=['flush',f.sc,f.rB,flush];}}}
  return {pit,flush,bad,badM,badG,near,foot,wedge,wv,relief,where:where||gwhere||nwhere||pwhere,rects:rects.length,t:f.t,st:P.state,rdx:+(P.rdx||0).toFixed(1)};}'''
fails = 0; n_cases = 0; tot = {}
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 844, 'height': 390})
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://' + os.path.abspath(SRC)); pg.wait_for_timeout(300)
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true)")
    if 'keeprider' in a: pg.evaluate("()=>{window.__keepRider=true}")  # (debug: leave him in both frames)
    art = pg.evaluate(ART, [LO, HI, SEEDS])
    print('lift shafts: %d cells, %d arches and %d breaches in their back walls %s' % (art['cells'], art['arch'], art['br'], art['where']), flush=True)
    if art['arch'] or art['br']: fails += 1
    cases = pg.evaluate(CASES, [LO, HI, SEEDS])
    for mode in MODES:
        for n, seed, i, t in cases:
            for pos in range(5 if t == 'chain' else 3):
                r = pg.evaluate(RUN, [n, seed, i, pos, mode]); n_cases += 1
                k = (mode, t); tot.setdefault(k, [0, 0]); tot[k][0] += 1
                for q in ('near', 'foot', 'wedge', 'relief'): tot.setdefault(q, 0); tot[q] += 1 if r[q] > (0 if q == 'wedge' else 6) else 0
                tot.setdefault('pit', 0); tot['pit'] += 1 if r['pit'] else 0
                if r['flush']: tot.setdefault('flushed', 0); tot['flushed'] += 1
                if 'flushlog' in a and r['flush']: print('flush', mode, n, seed, i, r['flush'], flush=True)
                if r['pit'] or r['bad'] > 6 or r['badM'] > 3 or r['badG'] > 6 or r['near'] > 6 or r['foot'] > 6 or r['wedge'] or r['relief'] > 6:
                    fails += 1; tot[k][1] += 1
                    print('BAD %-7s n=%d seed=%d lift %d (%s) pos %d: %d px over stone (mask %d), %d over a grating in front, near %d, foot %d, wedge %d %s, relief %d, pit %d %s, first at %s, he is %s rdx %s' % (mode, n, seed, i, t, pos, r['bad'], r['badM'], r['badG'], r['near'], r['foot'], r['wedge'], r['wv'], r['relief'], r['pit'], r['flush'], r['where'], r['st'], r['rdx']), flush=True)
    b.close()
print('cases', n_cases, ' '.join('%s/%s %d bad of %d' % (k[0], k[1], v[1], v[0]) for k, v in sorted((k, v) for k, v in tot.items() if isinstance(k, tuple))), 'cases failing near %d foot %d wedge %d relief %d pit %d (platforms at rest at a pit checked flush: %d)' % tuple(tot.get(q, 0) for q in ('near', 'foot', 'wedge', 'relief', 'pit', 'flushed')), 'errors', errs[:3])
print('ALL OK' if fails == 0 and not errs else 'FAILURES %d' % (fails + (1 if errs else 0)))
sys.exit(1 if fails or errs else 0)
