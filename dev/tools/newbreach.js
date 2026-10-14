function makeBreach(c0,c1,r,rnd,bd){const {bh,bw}=bd,xa=c0*TW+3,xb=(c1+1)*TW-3,W=xb-xa,yTop=(r-1)*TH,yFl=SURF(r)-HY;
  // The masonry above a hole stays up by arching: what falls is the stepped, roughly 45-degree triangle over the gap,
  // so the top of the hole is a corbelled point (steeper or flatter, off centre), its sides go down ragged, and its
  // foot is either a broken sill partway up or the floor itself, where the wall has gone to its base.
  const toFloor=rnd()<0.4,yb=toFloor?yFl+3:yFl-(12+rnd()*Math.min(34,(yFl-yTop)*0.3));
  const xm=xa+W*(0.3+0.4*rnd()),kl=0.6+0.65*rnd(),kr=0.6+0.65*rnd(),apex=yTop+5+rnd()*Math.max(4,(yb-yTop)*0.28);
  const ph=rnd()*6.28,ph2=rnd()*6.28,rise=(toFloor?4:10)+rnd()*12,lean=(rnd()-0.5)*0.25;
  const yTopAt=x=>apex+Math.abs(x-xm)*(x<xm?kl:kr)+3*Math.sin(x*0.21+ph),
        yBotAt=x=>{const u=Math.abs(x-(xa+xb)/2)/(W/2);return yb-rise*Math.pow(Math.min(1,u),2.2)+(toFloor?0:3*Math.sin(x*0.17+ph2));},
        sideL=y=>xa+W*0.05*(1+Math.sin(y*0.09+ph))+(y-yb)*lean,sideR=y=>xb-W*0.05*(1+Math.sin(y*0.11+ph2))+(y-yb)*lean;
  // how far a point lies inside the hole (negative outside)
  const depth=(x,y)=>Math.min(y-yTopAt(x),yBotAt(x)-y,x-sideL(y),sideR(y)-x);
  const R0=Math.floor((yTop-bh)/bh),R1=Math.floor((yFl-1)/bh),gone=new Map(),key=(k,R)=>R*100000+k,pieces=[],loose=[],cracks=[],halo=[];
  const kRange=R=>[Math.floor((xa-bw)/bw)-2,Math.ceil((xb+bw)/bw)+1];
  const score=(k,R)=>{const a=bd.joint(k,R),b=bd.joint(k+1,R),h=hash2(k*13+3,R*29+7);return depth((a+b)/2,(R+0.5)*bh)+((h%1000)/1000-0.5)*bh*0.9;};
  for(let R=R0;R<=R1;R++){const [kA,kB]=kRange(R);for(let k=kA;k<=kB;k++){const a=bd.joint(k,R),b=bd.joint(k+1,R);if(b<xa||a>xb)continue;if(R*bh<yTop)continue;if(score(k,R)>0)gone.set(key(k,R),[a,b,R]);}}
  if(gone.size<3)return null;
  const isGone=(R,x0,x1)=>{for(const q of gone.values())if(q[2]===R&&q[0]<x1-2&&q[1]>x0+2)return true;return false;};
  // whole bricks out; the bricks around the edge broken through toward the hole, or left standing but spalled
  for(const [a,b,R] of gone.values())pieces.push([[a,R*bh],[b,R*bh],[b,(R+1)*bh],[a,(R+1)*bh]]);
  for(let R=R0;R<=R1;R++){const [kA,kB]=kRange(R);for(let k=kA;k<=kB;k++){if(gone.has(key(k,R)))continue;const a=bd.joint(k,R),b=bd.joint(k+1,R),y0=R*bh,s=score(k,R);if(s<-bh*1.6||y0<yTop)continue;
      const lG=gone.has(key(k-1,R)),rG=gone.has(key(k+1,R)),uG=isGone(R-1,a,b),dG=isGone(R+1,a,b),hq=mulberry32(hash2(k*41+1,R*17+9)),j=()=>hq();
      if(s<-bh*0.5||!(lG||rG||uG||dG)){if(s>-bh*1.4)halo.push([a,b,R,hq()]);continue;}
      if(uG&&j()<0.8){const f=[0.2+0.5*j(),0.15+0.55*j(),0.15+0.55*j(),0.2+0.5*j()];pieces.push([[a,y0],[b,y0],[b,y0+f[0]*bh],[a+(b-a)*0.68,y0+f[1]*bh],[a+(b-a)*0.36,y0+f[2]*bh],[a,y0+f[3]*bh]]);}
      else if(dG&&j()<0.4){const y1=y0+bh,f=[0.15+0.4*j(),0.1+0.45*j(),0.15+0.4*j()];pieces.push([[a,y1],[a,y1-f[0]*bh],[a+(b-a)*0.5,y1-f[1]*bh],[b,y1-f[2]*bh],[b,y1]]);}
      else if(lG){const w=(b-a)*(0.2+0.45*j());pieces.push([[a,y0],[a+w*(0.6+0.5*j()),y0],[a+w*(0.7+0.4*j()),y0+bh*0.5],[a+w*(0.5+0.5*j()),y0+bh],[a,y0+bh]]);}
      else if(rG){const w=(b-a)*(0.2+0.45*j());pieces.push([[b-w*(0.6+0.5*j()),y0],[b,y0],[b,y0+bh],[b-w*(0.5+0.5*j()),y0+bh],[b-w*(0.7+0.4*j()),y0+bh*0.5]]);}
      else halo.push([a,b,R,hq()]);}}
  let bx0=1e9,bx1=-1e9,by0=1e9,by1=-1e9;for(const pc of pieces)for(const [x,y] of pc){bx0=Math.min(bx0,x);bx1=Math.max(bx1,x);by0=Math.min(by0,y);by1=Math.max(by1,y);}
  // a few loose bricks resting on the broken sill
  if(!toFloor)for(const [a,b,R] of gone.values()){if(loose.length>=2)break;if(!isGone(R+1,a,b)&&(R+1)*bh<yFl&&rnd()<0.3)loose.push([(a+b)/2+(rnd()-0.5)*6,(R+1)*bh,(rnd()-0.5)*0.7,bw*(0.4+0.3*rnd()),bh*0.7]);}
  // stepped cracks along the joints: up from the point of the hole toward the ceiling, and down from the corners of a
  // broken sill, the way cracks run out from the corners of an opening
  const step=(x,R,dir,side,n)=>{const pts=[[x,dir<0?R*bh:(R+1)*bh]];for(let i=0;i<n;i++){const yy=dir<0?R*bh:(R+1)*bh;R+=dir;const ny=dir<0?R*bh:(R+1)*bh;
      if(ny<yTop+1||ny>yFl-2)break;pts.push([x,ny]);let best=null;for(let k=Math.floor(x/bw)-2;k<=Math.floor(x/bw)+2;k++){const jx=bd.joint(k,R);if((jx-x)*side>1&&(!best||Math.abs(jx-x)<Math.abs(best-x)))best=jx;}if(best===null)break;x=best;pts.push([x,ny]);}
    return pts.length>2?pts:null;};
  {let top=null;for(const [a,b,R] of gone.values())if(!top||R<top[2])top=[a,b,R];
    if(top&&rnd()<0.75){const c=step((top[0]+top[1])/2,top[2]-1,-1,rnd()<0.5?-1:1,1+Math.floor(rnd()*3));if(c)cracks.push(c);}}
  if(!toFloor)for(const side of [-1,1]){let lowest=null;for(const [a,b,R] of gone.values()){const x=side<0?a:b;if(!lowest||R>lowest[1]||(R===lowest[1]&&(x-lowest[0])*side>0))lowest=[x,R];}
    if(lowest&&rnd()<0.6){const c=step(lowest[0],lowest[1]+1,1,side,1+Math.floor(rnd()*3));if(c)cracks.push(c);}}
  return {c0,c1,r,x0:bx0,x1:bx1,y0:by0,y1:by1,pieces,loose,cracks,halo,bh,xm,toFloor,seed:hash2(c0*31+7,r*17+5)};}
