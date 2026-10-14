// ================= the route =================
// A floor is planned first at the scale of rooms (as Spelunky lays its path through a grid of rooms before filling
// them, and as Prince of Persia's levels are maps of rooms linked on all four sides), then filled tile by tile.
// The route is a chain of runs, each along one storey band and heading left or right, joined by turns: a drop or a
// climb of one or two storeys that carries on the same way, or a two-storey drop that switches back underneath.
// A run never lies directly on top of another: the band between is left for the side passages.
// Many candidate plans are walked and the best one kept, scored on its proportions (neither a tower nor a strip),
// on going down about three times in five, and on room for side passages.
const ROUTE_SLACK=1.07; // the runs are planned a little long: each one's last few tiles go to plain floor before its turn
function routeWalk(n,R,budget){
  const lo=n<=2?8:n<=6?4:3,hi=n<=2?14:n<=6?10:9,occ=new Map(),K=(x,y)=>(x+2048)*4096+(y+2048);
  const isRun=(x,y)=>occ.get(K(x,y))===1,freeRun=(x,y)=>!occ.has(K(x,y))&&!isRun(x,y-1)&&!isRun(x,y+1);
  let x=0,y=0,dir=n<=2||R()<0.6?1:-1,left=budget,revs=0,first=true,prevRev=false;occ.set(K(0,0),1);
  const runs=[],turns=[];
  for(let guard=0;guard<80;guard++){
    const want=lo+Math.floor(R()*(hi-lo+1)),rooms=[[x,y]];
    let cap=first?RW-4:prevRev?5:RW-6; // the first room holds the entrance, or the foot of the turn that led here
    while(rooms.length<want&&cap<left+8){const nx=x+dir;if(!freeRun(nx,y))break;occ.set(K(nx,y),1);x=nx;rooms.push([x,y]);cap+=RW;}
    const last=cap>=left+8;
    if(!last&&rooms.length<2)return null;
    runs.push({rooms,y,dir,cap:last?left:cap});left-=cap;first=false;
    if(last)break;
    // the turn takes the room column just past the run's end
    const opts=[],cx=x+dir;
    const tryAdd=(w,down,k,rev)=>{if(w<=0)return;const cells=[];for(let i=0;i<k;i++)cells.push([cx,y+(down?i:-i)]);const ly=y+(down?k:-k);
      if(cells.some(([a,b])=>occ.has(K(a,b)))||!freeRun(cx,ly))return;
      if(rev&&!freeRun(cx-dir,ly))return; // a switchback heads straight back underneath
      opts.push([w,down,k,rev,cells,ly]);};
    if(n<=2){tryAdd(revs?0:0.6,true,2,true);tryAdd(1,true,1,false);}
    else{tryAdd(0.30,true,1,false);tryAdd(0.10,true,2,false);tryAdd(0.25,true,2,true);tryAdd(0.25,false,1,false);tryAdd(0.10,false,2,false);}
    if(!opts.length)return null;
    let t=R()*opts.reduce((a,o)=>a+o[0],0),o=opts[0];for(const q of opts){t-=q[0];if(t<=0){o=q;break;}}
    const [,down,k,rev,cells,ly]=o;
    for(const [a,b] of cells)occ.set(K(a,b),2);
    occ.set(K(cx,ly),1);turns.push({down,k,rev});revs+=rev?1:0;prevRev=rev;x=cx;y=ly;if(rev)dir=-dir;
  }
  if(left>0)return null;
  return {runs,turns,occ,revs};
}
function routePlan(n,seed,budget,needChase,att){
  const R=mulberry32(hash2((seed|0)+att*7919,7717));let best=null;
  for(let k=0;k<60;k++){
    const w=routeWalk(n,R,budget);if(!w)continue;
    if(n<=2&&w.revs!==1)continue;
    let x0=1e9,x1=-1e9,y0=1e9,y1=-1e9;for(const r of w.runs)for(const [a,b] of r.rooms){x0=Math.min(x0,a);x1=Math.max(x1,a);y0=Math.min(y0,b);y1=Math.max(y1,b);}
    for(const [key] of w.occ){const a=Math.floor(key/4096)-2048,b=key%4096-2048;x0=Math.min(x0,a);x1=Math.max(x1,a);y0=Math.min(y0,b);y1=Math.max(y1,b);}
    const W=x1-x0+1,H=y1-y0+1,aspect=W*ROOM_W/(H*ROOM_H),dn=w.turns.length?w.turns.filter(t=>t.down).length/w.turns.length:0.6;
    // a run heading right, long enough for the sandstorm, somewhere in the middle of the floor
    let chaseRun=-1;if(needChase){let p=0;for(let i=0;i<w.runs.length;i++){const r=w.runs[i];if(r.dir>0&&r.cap>=70&&p>=budget*0.12&&p<=budget*0.7&&i<w.runs.length-1){chaseRun=i;break;}p+=r.cap;}}
    if(needChase&&chaseRun<0)continue;
    let side=0;for(const r of w.runs)for(const [a,b] of r.rooms)if(!w.occ.has((a+2048)*4096+(b-1+2048))||!w.occ.has((a+2048)*4096+(b+1+2048)))side++;
    const score=-Math.abs(Math.log(aspect/3))*3-(n>2?Math.abs(dn-0.6)*4:0)+Math.min(side,40)*0.03;
    if(!best||score>best.score)best={score,w,x0,y0,W,H,chaseRun};
  }
  if(!best)return null;
  const {w,x0,y0}=best;
  return {W:best.W,H:best.H,chaseRun:best.chaseRun,turns:w.turns,
    runs:w.runs.map(r=>({dir:r.dir,band:r.y-y0,cap:r.cap,rooms:r.rooms.map(([a])=>a-x0)}))};
}
