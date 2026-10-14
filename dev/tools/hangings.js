// ---- hangings and lights, and what the keep's decay has done to them ----
// Prince of Persia hangs its palace tapestries from the top of a storey: the "tapestry" tiles (7 and 12, the doortops)
// draw from the ceiling down. So here a tapestry hangs from a rod just under the ceiling, as far down as the wall allows
// while staying above head height: short under a plain ceiling, long where the hall is open two storeys up.
// Where the wall behind is damaged a tapestry is torn, where it has partly fallen the tapestry is down (its rod hanging
// from one hook, the cloth in a heap on the floor) or gone with the wall; a lamp on damaged wall has come down and lies
// broken and cold on the floor, and a working one takes its place a little way along, on wall that still stands.
function settleLevel(LL){const sv=L;L=LL;try{settleLights();L.hangings=planHangings();}finally{L=sv;}}
function lightWear(t){const x=t.c*TW+16,y=SURF(t.r)-38;return inBreach(x,y,true)||inBreach(x,y-14,true)||inBreach(x,y+10,true)?3:wearLevel(x,y);}
function lampSpot(c,r){if(c<1||c>=L.cols-1||r<1||r>=L.rows)return false;if(L.base[r*L.cols+c]!==FLOOR||F(L,c,r))return false;
  if(L.door&&L.door.r===r&&Math.abs(L.door.c-c)<=2)return false;if(L.start&&L.start.r===r&&Math.abs((L.start.door===undefined?1:L.start.door)-c)<=1)return false;return true;}
function settleLights(){const add=[];
  for(const t of L.torches){if(lightWear(t)<2)continue;t.broken=true;
    for(const k of [1,-1,2,-2,3,-3,4,-4]){const q={c:t.c+k,r:t.r};
      if(!lampSpot(q.c,q.r)||lightWear(q)>=2)continue;
      if(L.torches.concat(add).some(o=>!o.broken&&o.r===q.r&&Math.abs(o.c-q.c)<4))continue;
      add.push(q);break;}}
  L.torches.push(...add);}
function planHangings(){const out=[];if(L.theme.style!=='palace')return out;
  const lit=new Set(L.torches.filter(t=>!t.broken).map(t=>t.r*L.cols+t.c)),win=new Set(L.windows.map(w=>w.r*L.cols+w.c));
  for(let r=2;r<L.rows;r++)for(let c=1;c<L.cols-1;c++){
    if(D0(c,r)===WALL||!solidBelowD(c,r))continue;
    const h=hash2(c*7+3,r*11+5);if(h%5!==0||lit.has(r*L.cols+c))continue;
    let cr=r-1;while(cr>0&&D0(c,cr)!==WALL&&r-cr<5)cr--; // the ceiling over this stretch of floor
    if(D0(c,cr)!==WALL||r-cr<2)continue;
    const top=(cr+1)*TH+5,bot=Math.min(SURF(r)-80,top+112);if(bot-top<30)continue;
    let clash=false;
    for(let rr=cr+1;rr<=r;rr++){if(win.has(rr*L.cols+c)||isArchTop(c,rr)||inOpening(c,rr))clash=true;const f=F(L,c,rr);if(f&&(f.t==='banner'||f.t==='gate'||f.t==='low'||f.t==='chomp'))clash=true;}
    if(clash||!lampSpot(c,r)&&!(L.base[r*L.cols+c]===FLOOR))continue;
    const x=c*TW+16,mid=(top+bot)/2;
    const state=inBreach(x,top+4,true)||inBreach(x,mid,true)||inBreach(x,bot-2,true)?4:wearLevel(x,mid); // 4: gone with the wall
    out.push({c,r,x,top,bot,state,seed:h});}
  return out;}
// a tapestry on the back wall: intact, faded, torn, or down (only its rod left, askew)
function drawHanging(g,hg,ox,oy,th){const x=hg.x+ox,top=hg.top+oy,bot=hg.bot+oy,rq=mulberry32(hg.seed),w=13,len=bot-top;
  if(hg.state===4)return;
  const rod=(a)=>{g.save();g.translate(x,top);g.rotate(a);g.fillStyle='#0b0812';g.fillRect(-9.5,-1.6,19,3);g.fillStyle=th.trim;g.fillRect(-9,-1.2,18,1.6);g.fillRect(-10,-2.2,2,3.4);g.fillRect(8,-2.2,2,3.4);g.restore();
    g.fillStyle='#0b0812';g.fillRect(x-7.5,top-4,1.2,3);g.fillRect(x+6.3,top-4,1.2,3);};
  if(hg.state===3){ // down: the rod hangs from one hook, a rag of cloth still caught on it
    const s=rq()<0.5?-1:1,a=s*(0.55+0.3*rq());g.save();g.translate(x-s*8,top);g.rotate(a);g.translate(s*8,0);
    g.fillStyle='#0b0812';g.fillRect(-9.5,-1.6,19,3);g.fillStyle=th.trim;g.fillRect(-9,-1.2,18,1.6);
    g.fillStyle=th.cloth;g.globalAlpha=0.9;g.beginPath();g.moveTo(-3,1.4);g.lineTo(3,1.4);g.lineTo(2,6+rq()*5);g.lineTo(0,4);g.lineTo(-1.5,8+rq()*6);g.closePath();g.fill();g.globalAlpha=1;g.restore();
    g.fillStyle='#0b0812';g.fillRect(x-s*8-0.6,top-4,1.2,3);return;}
  // the cloth: a long panel with a gold border and a star, a pointed foot with a fringe; torn ones lose their lower part
  const torn=hg.state===2,cut=torn?len*(0.5+0.3*rq()):len,yb=top+cut,pts=[[x-w/2,top+1],[x+w/2,top+1],[x+w/2,yb]];
  if(torn){const n=5;for(let i=1;i<n;i++)pts.push([x+w/2-w*i/n,yb-(rq()*0.55+0.1)*Math.min(9,cut*0.2)*(i%2?1:0.35)]);pts.push([x-w/2,yb-rq()*6]);}
  else pts.push([x,yb+6],[x-w/2,yb]);
  const cloth=new Path2D();pts.forEach(([px,py],i)=>i?cloth.lineTo(px,py):cloth.moveTo(px,py));cloth.closePath();
  g.save();g.translate(0.8,0.8);g.fillStyle='rgba(0,0,0,.45)';g.fill(cloth);g.restore();
  g.fillStyle=th.cloth;g.fill(cloth);
  g.save();g.clip(cloth);
  g.strokeStyle=th.cloth2;g.lineWidth=0.9;g.beginPath();g.moveTo(x-w/2+2,top+3);g.lineTo(x-w/2+2,top+len-2);g.moveTo(x+w/2-2,top+3);g.lineTo(x+w/2-2,top+len-2);g.moveTo(x-w/2+2,top+4);g.lineTo(x+w/2-2,top+4);g.stroke();
  for(let k=0;k<Math.max(1,Math.floor(len/40));k++){const sy=top+14+k*38;if(sy<yb-6)star8(g,x,sy,3.4,1.7,th.cloth2);}
  g.fillStyle='rgba(255,255,255,.07)';g.fillRect(x-w/2,top,2.4,len); // folds catching the light
  g.fillStyle='rgba(0,0,0,.18)';g.fillRect(x+1.6,top,1.2,len);g.fillRect(x+w/2-3,top,3,len);
  if(hg.state>=1){g.fillStyle='rgba(30,20,10,'+(0.12+0.08*hg.state)+')';g.fillRect(x-w/2,top,w,len+8);} // faded, dusty
  if(torn){ // a slash and a hole
    g.fillStyle='rgba(8,5,10,.85)';const sx=x-3+rq()*6,sy=top+cut*(0.25+0.3*rq());g.beginPath();g.moveTo(sx,sy);g.lineTo(sx+3.5,sy+7);g.lineTo(sx+2.6,sy+8);g.lineTo(sx-0.4,sy+1.2);g.closePath();g.fill();
    g.beginPath();g.ellipse(x-2+rq()*4,top+cut*(0.6+0.15*rq()),1.4,2,0,0,6.2832);g.fill();}
  g.restore();
  if(!torn){g.fillStyle=th.cloth2;for(let i=0;i<5;i++){const fx=x-w/2+1.5+i*(w-3)/4,fy=yb+6*(1-Math.abs(fx-x)/(w/2));g.fillRect(fx-0.4,fy-0.5,0.8,2.6);}}
  else{g.strokeStyle=th.cloth;g.lineWidth=1;g.beginPath();const tx=x-w/2+2+rq()*(w-4);g.moveTo(tx,yb-2);g.quadraticCurveTo(tx+1.5,yb+6,tx-0.5,yb+9+rq()*6);g.stroke();} // a loose strand
  rod(0);}
function drawHangings(g,rx,ry,th){if(!L.hangings||!L.hangings.length)return;const ox=-rx*ROOM_W,oy=-ry*ROOM_H;
  for(const hg of L.hangings){if(hg.x+16<rx*ROOM_W-8||hg.x-16>(rx+1)*ROOM_W+8||hg.bot+12<ry*ROOM_H||hg.top-8>(ry+1)*ROOM_H)continue;drawHanging(g,hg,ox,oy,th);}}
// what's left on the wall where a lamp came down: the empty bracket or chain, and the soot it left
function drawLampScar(g,t,ox,oy,th){const x=t.c*TW+16+ox,y=SURF(t.r)-38+oy,st=th.style,rq=mulberry32(hash2(t.c*5+1,t.r*9+2)),free=GFX().bg&&inOpening(t.c,t.r);
  const sg=g.createRadialGradient(x+2,y-14,1,x+2,y-12,16);sg.addColorStop(0,'rgba(0,0,0,.28)');sg.addColorStop(1,'rgba(0,0,0,0)');if(!free){g.fillStyle=sg;g.fillRect(x-16,y-30,36,34);}
  if(free){const key=(t.r-1)*TH+11+oy;g.strokeStyle='#0b0812';g.lineWidth=1.6;g.setLineDash([1.8,1.1]);g.beginPath();g.moveTo(x,key);g.lineTo(x+1,key+6+rq()*8);g.stroke();g.setLineDash([]);return;}
  if(st==='dungeon'){g.fillStyle='#16181e';g.fillRect(x-3,y+1,6,10);g.fillStyle='#3b404b';g.fillRect(x-3,y+1,6,1);g.strokeStyle='#14151a';g.lineWidth=1.5;g.beginPath();g.moveTo(x,y+7);g.lineTo(x+4.5,y+5.5);g.stroke();}
  else if(st==='palace'){g.fillStyle='#7c5c25';g.fillRect(x-4.4,y-2,3,11);g.fillStyle='#b48a3c';g.fillRect(x-4.4,y-2,3,1);g.strokeStyle='#8d6a2a';g.lineWidth=1.3;g.beginPath();g.moveTo(x-2.4,y+3);g.quadraticCurveTo(x-2.2,y-4,x+0.5,y-6.5);g.stroke();}
  else if(st==='tile'){const top=B(L,t.c,t.r-1)===EMPTY?(t.r-1)*TH+oy:t.r*TH+oy;g.strokeStyle='#2a2016';g.lineWidth=0.8;g.beginPath();g.moveTo(x,top);g.lineTo(x+0.6,top+8+rq()*10);g.stroke();}
  else if(st==='forge'){const by=y+2;g.strokeStyle='#120b08';g.lineWidth=1.6;g.beginPath();g.moveTo(x,by+12);g.lineTo(x,by+5);g.moveTo(x-4,by+10);g.lineTo(x-0.5,by+7);g.stroke();g.fillStyle='#120b08';g.fillRect(x-1.6,by+10,3.2,4);}}
// a fallen lamp lying broken and cold on the floor below where it hung
function drawFallenLamp(g,t,ox,oy,th){const st=th.style,rq=mulberry32(hash2(t.c*11+3,t.r*7+1)),ys=SURF(t.r)+oy,s=rq()<0.5?-1:1;
  const at=(dx,d)=>onFloor(t.c*TW+16+ox+dx,d,ys);
  if(st==='dungeon'){const p=at(s*3,0.78);g.save();g.translate(p.x,p.y-1);g.rotate(s*(1.35+0.15*rq()));
      g.strokeStyle='#0b0812';g.lineWidth=3;g.beginPath();g.moveTo(0,5);g.lineTo(0,-8);g.stroke();g.strokeStyle='#4a3020';g.lineWidth=1.8;g.stroke();
      g.fillStyle='#120c08';g.beginPath();g.ellipse(0,-9,2.4,2.9,0,0,6.2832);g.fill();g.restore();
    g.fillStyle='rgba(40,38,44,.7)';for(let i=0;i<5;i++){const q=at(s*(8+rq()*8),0.7+rq()*0.25);g.fillRect(q.x,q.y-1,1.2,1);}}
  else if(st==='palace'){const p=at(s*2,0.8);g.save();g.translate(p.x,p.y-4.5);g.rotate(s*1.45);
      g.fillStyle='#0b0812';g.beginPath();g.moveTo(-5,-3);g.quadraticCurveTo(-4,-9,0,-9.5);g.quadraticCurveTo(4,-9,5,-3);g.lineTo(4.2,5);g.lineTo(0,8);g.lineTo(-4.2,5);g.closePath();g.fill();
      g.fillStyle='#8a6a2a';g.beginPath();g.moveTo(-5,-3);g.quadraticCurveTo(-4,-9,0,-9.5);g.quadraticCurveTo(4,-9,3.5,-4);g.closePath();g.fill();
      g.fillStyle='#1a1410';g.fillRect(-3.3,-2.4,6.6,6.6);g.fillStyle='rgba(255,240,210,.25)';g.fillRect(-3.3,-2.4,2,6.6);g.restore();
    for(let i=0;i<6;i++){const q=at(s*(-6+rq()*16),0.6+rq()*0.35);g.fillStyle='rgba(240,225,190,'+(0.35+0.3*rq())+')';g.beginPath();g.moveTo(q.x,q.y);g.lineTo(q.x+1.6,q.y-0.6);g.lineTo(q.x+0.6,q.y+0.5);g.closePath();g.fill();}}
  else if(st==='tile'){const p=at(s*2,0.8);g.save();g.translate(p.x,p.y-5);g.rotate(s*0.5);
      g.fillStyle='#0b0812';g.beginPath();for(let i=0;i<8;i++){const a=i*Math.PI/4+Math.PI/8;g[i?'lineTo':'moveTo'](Math.cos(a)*6.4,Math.sin(a)*6.4);}g.closePath();g.fill();
      const panes=['rgba(50,100,170,.55)','rgba(140,100,50,.5)'];for(let i=0;i<8;i++){if(rq()<0.4)continue;const a0=i*Math.PI/4,a1=a0+Math.PI/4;g.fillStyle=panes[i%2];g.beginPath();g.moveTo(0,0);g.lineTo(Math.cos(a0)*5,Math.sin(a0)*5);g.lineTo(Math.cos(a1)*5,Math.sin(a1)*5);g.closePath();g.fill();}
      g.restore();
    for(let i=0;i<7;i++){const q=at(s*(-7+rq()*18),0.6+rq()*0.35);g.fillStyle=i%2?'rgba(70,140,230,.6)':'rgba(255,190,90,.55)';g.beginPath();g.moveTo(q.x,q.y);g.lineTo(q.x+1.8,q.y-0.7);g.lineTo(q.x+0.5,q.y+0.6);g.closePath();g.fill();}}
  else if(st==='forge'){const p=at(s*2,0.8);g.save();g.translate(p.x,p.y-3);g.rotate(s*1.2);g.strokeStyle='#120b08';g.lineWidth=1.3;g.beginPath();g.moveTo(-6.4,-3);g.lineTo(-3.6,4);g.lineTo(3.6,4);g.lineTo(6.4,-3);g.stroke();g.restore();
    for(let i=0;i<9;i++){const q=at(s*(3+rq()*12),0.62+rq()*0.33);g.fillStyle=i%3?'#1c1614':'#2c2624';g.beginPath();g.ellipse(q.x,q.y-0.6,1.3+rq(),0.9,0,0,6.2832);g.fill();}}
  else{const p=at(s*2,0.82);g.fillStyle='rgba(10,20,16,.45)';g.beginPath();g.ellipse(p.x+s*5,p.y,7,1.6,0,0,6.2832);g.fill();
    g.save();g.translate(p.x,p.y-2);g.rotate(s*1.3);g.fillStyle='#0b0812';g.beginPath();g.ellipse(0,0,4.6,2.4,0,0,6.2832);g.fill();g.fillStyle=th.wallB;g.beginPath();g.ellipse(0,-0.3,3.8,1.7,0,0,6.2832);g.fill();
      g.strokeStyle='#0b0812';g.lineWidth=0.6;g.beginPath();g.moveTo(-1,-1.5);g.lineTo(0.5,0.4);g.lineTo(-0.3,1.6);g.stroke();g.restore();}}
// a tapestry that came down: crumpled on the floor under where it hung
function drawFallenCloth(g,hg,ox,oy,th){const rq=mulberry32(hg.seed+3),ys=SURF(hg.r)+oy,p0=onFloor(hg.x+ox-8,0.82,ys),p1=onFloor(hg.x+ox+9,0.82,ys);
  g.fillStyle='rgba(0,0,0,.3)';g.beginPath();g.ellipse((p0.x+p1.x)/2,(p0.y+p1.y)/2+0.5,11,2.2,0,0,6.2832);g.fill();
  const pts=[];for(let i=0;i<=8;i++){const u=i/8,x=p0.x+(p1.x-p0.x)*u,y=p0.y+(p1.y-p0.y)*u;pts.push([x,y-(Math.sin(u*Math.PI)*(3.5+rq()*2)+rq()*1.2)]);}
  g.fillStyle=th.cloth;g.beginPath();g.moveTo(p0.x,p0.y);for(const [x,y] of pts)g.lineTo(x,y);g.lineTo(p1.x,p1.y);g.closePath();g.fill();
  g.fillStyle='rgba(0,0,0,.25)';g.beginPath();g.moveTo(p0.x,p0.y);for(let i=0;i<=8;i+=2)g.lineTo(pts[i][0],pts[i][1]+1.6);g.lineTo(p1.x,p1.y);g.closePath();g.fill();
  g.strokeStyle=th.cloth2;g.lineWidth=0.8;g.beginPath();g.moveTo(pts[1][0],pts[1][1]+0.5);g.quadraticCurveTo(pts[4][0],pts[4][1]+2.5,pts[7][0],pts[7][1]+0.8);g.stroke();
  if(hg.state===3)return;g.fillStyle='#0b0812';g.fillRect(pts[2][0]-3,pts[2][1]+1,7,1.2);g.fillStyle=th.trim;g.fillRect(pts[2][0]-3,pts[2][1]+0.6,7,0.8);} // its rod came down with it
function drawWallScars(g,rx,ry,th){const ox=-rx*ROOM_W,oy=-ry*ROOM_H;
  for(const t of L.torches){if(!t.broken||t.c<rx*RW-1||t.c>(rx+1)*RW||t.r<ry*RH-1||t.r>(ry+1)*RH+1)continue;if(lightWear(t)<4&&!inBreach(t.c*TW+16,SURF(t.r)-38,true))drawLampScar(g,t,ox,oy,th);}}
function drawFallen(g,rx,ry,th){const ox=-rx*ROOM_W,oy=-ry*ROOM_H;
  for(const t of L.torches){if(!t.broken||t.c<rx*RW-1||t.c>(rx+1)*RW||t.r<ry*RH-1||t.r>(ry+1)*RH+1)continue;drawFallenLamp(g,t,ox,oy,th);}
  for(const hg of L.hangings||[]){if(hg.state<3||hg.c<rx*RW-1||hg.c>(rx+1)*RW||hg.r<ry*RH-1||hg.r>(ry+1)*RH+1)continue;drawFallenCloth(g,hg,ox,oy,th);}}
