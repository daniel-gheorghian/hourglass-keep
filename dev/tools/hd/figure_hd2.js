// ===== HD figure: shaped, shaded body parts on the same skeleton; cloth that trails the motion =====
function shadeHex(h,k){const n=parseInt(h.slice(1),16),r=n>>16,g=(n>>8)&255,b=n&255,f=c=>Math.max(0,Math.min(255,Math.round(k<0?c*(1+k):c+(255-c)*k)));return '#'+((1<<24)|(f(r)<<16)|(f(g)<<8)|f(b)).toString(16).slice(1);}
// a tapered tube through points, with a width at each point; returns a Path2D
function tubePath(pts,ws){const n=pts.length,L=[],R=[];
  for(let i=0;i<n;i++){const a=pts[Math.max(0,i-1)],b=pts[Math.min(n-1,i+1)];let dx=b[0]-a[0],dy=b[1]-a[1];const d=Math.hypot(dx,dy)||1;dx/=d;dy/=d;const w=ws[i]/2;L.push([pts[i][0]-dy*w,pts[i][1]+dx*w]);R.push([pts[i][0]+dy*w,pts[i][1]-dx*w]);}
  const p=new Path2D();p.moveTo(L[0][0],L[0][1]);
  for(let i=1;i<n;i++){const m=[(L[i-1][0]+L[i][0])/2,(L[i-1][1]+L[i][1])/2];if(i===1)p.lineTo(m[0],m[1]);else p.quadraticCurveTo(L[i-1][0],L[i-1][1],m[0],m[1]);}
  p.lineTo(L[n-1][0],L[n-1][1]);
  {const c=pts[n-1],a0=Math.atan2(L[n-1][1]-c[1],L[n-1][0]-c[0]);p.arc(c[0],c[1],ws[n-1]/2,a0,a0+Math.PI,true);}
  for(let i=n-2;i>=0;i--){const m=[(R[i+1][0]+R[i][0])/2,(R[i+1][1]+R[i][1])/2];if(i===n-2)p.lineTo(m[0],m[1]);else p.quadraticCurveTo(R[i+1][0],R[i+1][1],m[0],m[1]);}
  p.lineTo(R[0][0],R[0][1]);
  {const c=pts[0],a0=Math.atan2(R[0][1]-c[1],R[0][0]-c[0]);p.arc(c[0],c[1],ws[0]/2,a0,a0+Math.PI,true);}
  p.closePath();return p;}
// fill a part two-tone: shadow over all of it, then the base colour shifted toward the light (up and forward)
function cel(ctx,path,base,shadow,o,lx=0.9,ly=-0.9){
  if(o.mono){ctx.fillStyle=o.mono;ctx.fill(path);ctx.strokeStyle=o.mono;ctx.lineWidth=1.4;ctx.stroke(path);return;}
  ctx.strokeStyle=o.out;ctx.lineWidth=1.25;ctx.stroke(path);
  ctx.fillStyle=shadow;ctx.fill(path);
  ctx.save();ctx.clip(path);ctx.translate(lx,ly);ctx.fillStyle=base;ctx.fill(path);ctx.restore();}
function tcel(ctx,pts,ws,base,shadow,o){const path=tubePath(pts,ws);
  if(o.mono){ctx.fillStyle=o.mono;ctx.fill(path);ctx.strokeStyle=o.mono;ctx.lineWidth=1.4;ctx.stroke(path);return;}
  ctx.strokeStyle=o.out;ctx.lineWidth=1.25;ctx.stroke(path);ctx.fillStyle=shadow;ctx.fill(path);
  ctx.fillStyle=base;ctx.fill(tubePath(pts.map(q=>[q[0]+0.42,q[1]-0.42]),ws.map(w=>Math.max(0.5,w-1.25))));}
// cloth that trails behind its anchor: each link leans further from gravity toward the wind, with a ripple
function trail(anchor,n,seg,wind,t,ripple,phase){const pts=[anchor.slice()];let x=anchor[0],y=anchor[1];
  const ga=Math.PI/2,wa=Math.atan2(wind[1],wind[0]),ws=Math.min(1,Math.hypot(wind[0],wind[1]));
  for(let i=1;i<=n;i++){const k=ws*(0.55+0.45*i/n),a=ga+(((wa-ga+Math.PI*3)%(Math.PI*2))-Math.PI)*k+Math.sin(t*(7+ripple*6)-i*0.9+phase)*(0.12+0.28*ripple)*(i/n);
    x+=Math.cos(a)*seg;y+=Math.sin(a)*seg;pts.push([x,y]);}
  return pts;}
function drawFigureHD(ctx,x,y,face,p,pal,o){
  const s=skel(p);
  ctx.save();
  ctx.translate(x,y-s.hipH+(o.yo||0));
  if(face<0)ctx.scale(-1,1);
  if(p.rot)ctx.rotate(p.rot);
  if(o.sq){ctx.translate(0,s.hipH);ctx.scale(1/o.sq,o.sq);ctx.translate(0,-s.hipH);} // squash (<1) / stretch (>1) about the feet
  if(o.alpha!==undefined)ctx.globalAlpha=o.alpha;
  ctx.lineCap='round';ctx.lineJoin='round';
  const O=Object.assign({},o,{out:o.mono||'#120c18'});
  const t=o.time||0,vx=(o.vx||0)*face,vy=o.vy||0;
  // wind in figure space: cloth streams away from the direction of travel and lifts when falling
  const wind=[-vx/110,-vy/260+0.25];
  const C=k=>pal[k]||'#888',D=(k,d)=>pal[k+'D']||shadeHex(C(k),d||-0.28);
  const lean=p.lean,tx=Math.sin(lean),ty=-Math.cos(lean),nx=-ty,ny=tx; // torso axis and its forward normal
  const at=(u)=>[s.sh[0]*u,s.sh[1]*u];
  // --- back layer: scarf tail, sash tails, back arm, back leg ---
  if(pal.hero){const nk=[s.sh[0]-nx*1.5+tx*1,s.sh[1]-ny*1.5+ty*1];const sc=trail(nk,5,3.2,wind,t,0.6+0.4*Math.min(1,Math.abs(vx)/90),0);
    tcel(ctx,sc,[3.0,2.8,2.5,2.1,1.6,1.0],C('sash'),D('sash'),O);}
  {const w0=at(0.16),wa=[w0[0]-nx*4,w0[1]-ny*4];const st=trail(wa,2,2.6,wind,t+0.3,0.5,1.7);tcel(ctx,st,[2.2,1.8,1.2],D('sash',-0.2),shadeHex(D('sash',-0.2),-0.25),O);}
  const arm=(sh,e,h,base,shade)=>{tcel(ctx,[sh,e,h],[3.5,2.9,2.2],base,shade,O);
    const hp=new Path2D();hp.ellipse(h[0],h[1],1.35,1.2,0,0,Math.PI*2);if(O.mono){ctx.fillStyle=O.mono;ctx.fill(hp);}else{ctx.strokeStyle=O.out;ctx.lineWidth=1.1;ctx.stroke(hp);ctx.fillStyle=base;ctx.fill(hp);}};
  const leg=(f,k,base,shade,cuff,boot)=>{
    const mid=[k[0]+(f[0]-k[0])*0.55-0.6,k[1]+(f[1]-k[1])*0.55],ank=[k[0]+(f[0]-k[0])*0.9,k[1]+(f[1]-k[1])*0.9];
    tcel(ctx,[[0,0],k,mid,ank],[8.2,6.8,6.2,3.6],base,shade,O);
    // cuff band and the slipper with its curled toe
    if(!O.mono){ctx.strokeStyle=cuff;ctx.lineWidth=1.3;const dx=f[0]-k[0],dy=f[1]-k[1],d=Math.hypot(dx,dy)||1;ctx.beginPath();ctx.moveTo(ank[0]-dy/d*1.9,ank[1]+dx/d*1.9);ctx.lineTo(ank[0]+dy/d*1.9,ank[1]-dx/d*1.9);ctx.stroke();}
    const sp=new Path2D();sp.moveTo(f[0]-2.2,f[1]+0.6);sp.quadraticCurveTo(f[0]-2.4,f[1]-2.2,f[0]+0.2,f[1]-2.0);sp.quadraticCurveTo(f[0]+3.4,f[1]-1.4,f[0]+5.6,f[1]-0.2);
    sp.quadraticCurveTo(f[0]+7.2,f[1]-0.6,f[0]+7.0,f[1]-2.2);sp.quadraticCurveTo(f[0]+7.8,f[1]+0.4,f[0]+5.2,f[1]+1.0);sp.lineTo(f[0]-1.4,f[1]+1.0);sp.closePath();
    cel(ctx,sp,boot,shadeHex(boot,-0.35),O);};
  arm(s.sh,s.eB,s.hB,D('skin',-0.18),shadeHex(D('skin',-0.18),-0.22));
  leg(s.fB,s.kB,D('pants',-0.12),shadeHex(D('pants',-0.12),-0.18),shadeHex(C('pants'),-0.45),shadeHex(C('boot'),-0.2));
  // sheathed sword at the hip when not drawn
  if(!o.sword&&o.hasSword&&!O.mono){ctx.save();const hp=at(0.12);ctx.translate(hp[0]-nx*1,hp[1]-ny*1);ctx.rotate(lean+1.95);
    const sc=new Path2D();sc.moveTo(0,-1.3);sc.quadraticCurveTo(7,-2.2,13,0.2);sc.lineTo(12.6,1.5);sc.quadraticCurveTo(7,0.2,0,1.3);sc.closePath();cel(ctx,sc,'#6b4a2a','#4a321c',O);
    ctx.fillStyle='#d8b04a';ctx.fillRect(-1.6,-1.8,1.6,3.6);ctx.restore();}
  // --- torso: vest over the chest, sash at the waist ---
  const tp=[[0,0],at(0.38),at(0.78),at(1)],tw=[9.2,8.2,11.2,9.6];
  tcel(ctx,tp,tw,C('tunic'),D('tunic'),O);
  if(!O.mono){ // open collar and trim along the vest's front edge
    const c0=at(0.98),c1=at(0.7);ctx.fillStyle=C('skin');ctx.beginPath();ctx.moveTo(c0[0]+nx*4.2,c0[1]+ny*4.2);ctx.lineTo(c1[0]+nx*5.3,c1[1]+ny*5.3);ctx.lineTo(c0[0]+nx*1.2,c0[1]+ny*1.2);ctx.closePath();ctx.fill();
    ctx.strokeStyle=pal.trim||'#d8b04a';ctx.lineWidth=0.9;ctx.beginPath();const e0=at(0.2),e1=at(0.72);ctx.moveTo(e0[0]+nx*4.4,e0[1]+ny*4.4);ctx.quadraticCurveTo(e1[0]+nx*5.8,e1[1]+ny*5.8,c1[0]+nx*5.2,c1[1]+ny*5.2);ctx.lineTo(c0[0]+nx*4.2,c0[1]+ny*4.2);ctx.stroke();}
  {const a=at(0.08),b=at(0.27);tcel(ctx,[a,b],[10,9.2],C('sash'),D('sash'),O);
    if(!O.mono){ctx.strokeStyle=shadeHex(C('sash'),-0.35);ctx.lineWidth=0.7;ctx.beginPath();const m=at(0.17);ctx.moveTo(m[0]-nx*4.3,m[1]-ny*4.3);ctx.lineTo(m[0]+nx*4.3,m[1]+ny*4.3);ctx.stroke();}}
  // --- head ---
  const hd=s.hd,ha=lean+p.head,hx=Math.sin(ha),hy=-Math.cos(ha),hnx=-hy,hny=hx;
  {const n0=at(0.95),n1=[hd[0]-hx*3.6,hd[1]-hy*3.6];tcel(ctx,[n0,n1],[3.4,3.0],C('skin'),D('skin'),O);}
  if(pal.hero){const nk=[s.sh[0]+tx*1.4,s.sh[1]+ty*1.4];cel(ctx,tubePath([[nk[0]-nx*2.6,nk[1]-ny*2.6],[nk[0]+nx*2.6,nk[1]+ny*2.6]],[3.2,3.2]),C('sash'),D('sash'),O);}
  {const hp=new Path2D();const r=LEN.hd;
    // skull, with the jaw and nose pushed forward
    hp.moveTo(hd[0]-hnx*r*0.95+hx*r*0.2,hd[1]-hny*r*0.95+hy*r*0.2);
    hp.bezierCurveTo(hd[0]-hnx*r*1.05+hx*r*1.35,hd[1]-hny*r*1.05+hy*r*1.35,hd[0]+hnx*r*0.9+hx*r*1.35,hd[1]+hny*r*0.9+hy*r*1.35,hd[0]+hnx*r*0.95+hx*r*0.25,hd[1]+hny*r*0.95+hy*r*0.25);
    hp.lineTo(hd[0]+hnx*r*1.22-hx*r*0.12,hd[1]+hny*r*1.22-hy*r*0.12);            // nose tip
    hp.lineTo(hd[0]+hnx*r*0.95-hx*r*0.38,hd[1]+hny*r*0.95-hy*r*0.38);
    hp.quadraticCurveTo(hd[0]+hnx*r*0.85-hx*r*1.1,hd[1]+hny*r*0.85-hy*r*1.1,hd[0]+hnx*r*0.1-hx*r*1.15,hd[1]+hny*r*0.1-hy*r*1.15); // chin
    hp.quadraticCurveTo(hd[0]-hnx*r*0.7-hx*r*0.95,hd[1]-hny*r*0.7-hy*r*0.95,hd[0]-hnx*r*0.95+hx*r*0.2,hd[1]-hny*r*0.95+hy*r*0.2);hp.closePath();
    cel(ctx,hp,C('skin'),D('skin'),O,0.8,-0.6);}
  if(pal.helm){const hm=new Path2D(),r=LEN.hd+1;hm.moveTo(hd[0]-hnx*r,hd[1]-hny*r);hm.bezierCurveTo(hd[0]-hnx*r+hx*r*1.5,hd[1]-hny*r+hy*r*1.5,hd[0]+hnx*r+hx*r*1.5,hd[1]+hny*r+hy*r*1.5,hd[0]+hnx*r*1.05,hd[1]+hny*r*1.05);
      hm.lineTo(hd[0]+hnx*r*1.25+hx*0.2,hd[1]+hny*r*1.25+hy*0.2);hm.lineTo(hd[0]-hnx*r*1.15+hx*0.2,hd[1]-hny*r*1.15+hy*0.2);hm.closePath();
      cel(ctx,hm,pal.helm,shadeHex(pal.helm,-0.35),O,0.8,-1);
      if(!O.mono){ctx.strokeStyle=shadeHex(pal.helm,0.35);ctx.lineWidth=0.7;ctx.beginPath();ctx.moveTo(hd[0]-hnx*r*0.4+hx*r*1.05,hd[1]-hny*r*0.4+hy*r*1.05);ctx.quadraticCurveTo(hd[0]+hx*r*1.12,hd[1]+hy*r*1.12,hd[0]+hnx*r*0.5+hx*r*0.95,hd[1]+hny*r*0.5+hy*r*0.95);ctx.stroke();}
      const sp=[hd[0]+hx*(r+0.5),hd[1]+hy*(r+0.5)];ctx.fillStyle=O.mono||shadeHex(pal.helm,-0.2);ctx.beginPath();ctx.moveTo(sp[0]-hnx*0.9,sp[1]-hny*0.9);ctx.lineTo(sp[0]+hx*3.4,sp[1]+hy*3.4);ctx.lineTo(sp[0]+hnx*0.9,sp[1]+hny*0.9);ctx.fill();
      if(pal.plume){const pl=trail([sp[0]+hx*3,sp[1]+hy*3],4,2.6,[-1+wind[0],-0.8],t,0.5,2.2);tcel(ctx,pl,[2.6,2.8,2.4,1.8,1],pal.plume,shadeHex(pal.plume,-0.35),O);}}
  else if(!pal.bones){ // hair: a swept mass over the crown, and a short tail that trails
    const r=LEN.hd,hp=new Path2D();
    hp.moveTo(hd[0]+hnx*r*0.85+hx*r*0.55,hd[1]+hny*r*0.85+hy*r*0.55);
    hp.bezierCurveTo(hd[0]+hnx*r*0.6+hx*r*1.45,hd[1]+hny*r*0.6+hy*r*1.45,hd[0]-hnx*r*1.3+hx*r*1.3,hd[1]-hny*r*1.3+hy*r*1.3,hd[0]-hnx*r*1.15-hx*r*0.2,hd[1]-hny*r*1.15-hy*r*0.2);
    hp.quadraticCurveTo(hd[0]-hnx*r*0.9-hx*r*0.9,hd[1]-hny*r*0.9-hy*r*0.9,hd[0]-hnx*r*0.25-hx*r*0.2,hd[1]-hny*r*0.25-hy*r*0.2);
    hp.quadraticCurveTo(hd[0]+hnx*r*0.1+hx*r*0.5,hd[1]+hny*r*0.1+hy*r*0.5,hd[0]+hnx*r*0.85+hx*r*0.55,hd[1]+hny*r*0.85+hy*r*0.55);hp.closePath();
    const tl=trail([hd[0]-hnx*r*1.0+hx*r*0.1,hd[1]-hny*r*1.0+hy*r*0.1],3,2.4,wind,t+0.6,0.7,3.1);
    tcel(ctx,tl,[3,2.5,1.8,0.9],C('hair'),shadeHex(C('hair'),-0.4),O);
    cel(ctx,hp,C('hair'),shadeHex(C('hair'),-0.45),O,0.6,-0.9);
    if(!O.mono){ctx.strokeStyle=shadeHex(C('hair'),0.25);ctx.lineWidth=0.6;ctx.beginPath();ctx.moveTo(hd[0]-hnx*r*0.4+hx*r*1.0,hd[1]-hny*r*0.4+hy*r*1.0);ctx.quadraticCurveTo(hd[0]+hx*r*1.12,hd[1]+hy*r*1.12,hd[0]+hnx*r*0.45+hx*r*0.85,hd[1]+hny*r*0.45+hy*r*0.85);ctx.stroke();}}
  if(!pal.bones&&!O.mono){ // eye and brow
    const r=LEN.hd,ex=hd[0]+hnx*r*0.48+hx*r*0.12,ey=hd[1]+hny*r*0.48+hy*r*0.12;ctx.fillStyle='#120c18';ctx.beginPath();ctx.ellipse(ex,ey,0.62,0.85,ha,0,Math.PI*2);ctx.fill();
    ctx.strokeStyle=shadeHex(C(pal.helm?'skin':'hair'),-0.3);ctx.lineWidth=0.7;ctx.beginPath();ctx.moveTo(ex-hnx*0.9+hx*1.4,ey-hny*0.9+hy*1.4);ctx.lineTo(ex+hnx*1.1+hx*1.2,ey+hny*1.1+hy*1.2);ctx.stroke();}
  // --- front layer: leg, sword, arm ---
  leg(s.fF,s.kF,C('pants'),D('pants'),shadeHex(C('pants'),-0.42),C('boot'));
  if(o.sword&&o.smear&&!O.mono){const h=s.hF;for(const [f,al] of [[1,0.16],[0.5,0.3]]){const a=p.sw+o.smear*f,dx=Math.cos(a),dy=-Math.sin(a);ctx.globalAlpha=al*(o.alpha===undefined?1:o.alpha);
    ctx.fillStyle='#e8eef8';ctx.beginPath();ctx.moveTo(h[0],h[1]);ctx.lineTo(h[0]+Math.cos(p.sw)*18,h[1]-Math.sin(p.sw)*18);ctx.lineTo(h[0]+dx*18,h[1]+dy*18);ctx.closePath();ctx.fill();}ctx.globalAlpha=o.alpha===undefined?1:o.alpha;}
  if(o.sword){const h=s.hF,a=p.sw,dx=Math.cos(a),dy=-Math.sin(a),nx2=-dy,ny2=dx,L2=18;
    const bl=new Path2D();bl.moveTo(h[0]+nx2*0.9,h[1]+ny2*0.9);bl.quadraticCurveTo(h[0]+dx*L2*0.6+nx2*1.6,h[1]+dy*L2*0.6+ny2*1.6,h[0]+dx*L2+nx2*2.6,h[1]+dy*L2+ny2*2.6);
    bl.quadraticCurveTo(h[0]+dx*L2*0.7-nx2*0.6,h[1]+dy*L2*0.7-ny2*0.6,h[0]-nx2*0.9,h[1]-ny2*0.9);bl.closePath();
    if(O.mono){ctx.fillStyle=O.mono;ctx.fill(bl);}else{ctx.strokeStyle=O.out;ctx.lineWidth=1.1;ctx.stroke(bl);ctx.fillStyle='#c9cfda';ctx.fill(bl);
      ctx.strokeStyle='#f6f8fc';ctx.lineWidth=0.6;ctx.beginPath();ctx.moveTo(h[0]+dx*3+nx2*1.1,h[1]+dy*3+ny2*1.1);ctx.quadraticCurveTo(h[0]+dx*L2*0.6+nx2*1.9,h[1]+dy*L2*0.6+ny2*1.9,h[0]+dx*(L2-1)+nx2*2.4,h[1]+dy*(L2-1)+ny2*2.4);ctx.stroke();
      ctx.strokeStyle='#d8b04a';ctx.lineWidth=1.8;ctx.beginPath();ctx.moveTo(h[0]+nx2*3,h[1]+ny2*3);ctx.lineTo(h[0]-nx2*3,h[1]-ny2*3);ctx.stroke();
      ctx.strokeStyle='#4a321c';ctx.lineWidth=1.6;ctx.beginPath();ctx.moveTo(h[0],h[1]);ctx.lineTo(h[0]-dx*3,h[1]-dy*3);ctx.stroke();}}
  arm(s.sh,s.eF,s.hF,C('skin'),D('skin'));
  ctx.restore();
  if(o.flash>0&&!o.white&&!o.mono)drawFigureHD(ctx,x,y,face,p,pal,Object.assign({},o,{white:true,mono:'#ffffff',flash:0,alpha:Math.min(0.75,o.flash*3)*(o.alpha===undefined?1:o.alpha)}));
}

// A keyed run cycle (contact, down, passing, up, then the same with legs and arms swapped), smoothed with
// Catmull-Rom so it flows; the body dips on the down beat and floats on the up beat.
const RUNK=[
  mk({lean:0.26,head:-0.05,hF:0.85,kF:0.32,hB:-0.55,kB:1.25,aF:-0.75,eF:1.45,aB:0.95,eB:1.55,air:0,hy:24}),   // contact
  mk({lean:0.3,head:-0.08,hF:0.42,kF:0.85,hB:-0.15,kB:1.95,aF:-0.45,eF:1.5,aB:0.6,eB:1.6,air:0,hy:24}),        // down
  mk({lean:0.28,head:-0.05,hF:-0.12,kF:0.4,hB:0.55,kB:2.15,aF:0.05,eF:1.5,aB:0.1,eB:1.5,air:0,hy:24}),         // passing
  mk({lean:0.24,head:-0.03,hF:-0.62,kF:0.22,hB:1.0,kB:1.25,aF:0.6,eF:1.5,aB:-0.55,eB:1.45,air:0.45,hy:25.2}),   // up
];
const swapLR=q=>mk({lean:q.lean,head:q.head,hF:q.hB,kF:q.kB,hB:q.hF,kB:q.kF,aF:q.aB,eF:q.eB,aB:q.aF,eB:q.eF,air:q.air,hy:q.hy,sw:q.sw});
const RUN8=[...RUNK,...RUNK.map(swapLR)];
function runPoseHD(ph,amp=1){const n=RUN8.length,f=((ph%1)+1)%1*n,i=Math.floor(f),u=f-i,P0=RUN8[(i+n-1)%n],P1=RUN8[i],P2=RUN8[(i+1)%n],P3=RUN8[(i+2)%n],out=mk({});
  for(const k of PK){const a=P0[k],b=P1[k],c=P2[k],d=P3[k];out[k]=0.5*((2*b)+(-a+c)*u+(2*a-5*b+4*c-d)*u*u+(-a+3*b-3*c+d)*u*u*u);}
  if(amp<1){const st=PS.stand;for(const k of PK)out[k]=st[k]+(out[k]-st[k])*amp;}
  return out;}

function figDraw(ctx,x,y,face,p,pal,o){if(pal.bones||!GFX().hd)return drawFigure(ctx,x,y,face,p,pal,o);return drawFigureHD(ctx,x,y,face,p,pal,o);}
