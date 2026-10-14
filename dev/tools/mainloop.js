  // ---- the route, run by run: each planned run filled as the strip used to be, then the turn to the next one ----
  const roomLo=x=>(x+1)*RW, roomHi=x=>(x+1)*RW+RW-1;
  // A turn is built from a kit of moves whose drops or climbs add up to it. A switchback heads straight back under the
  // turn, so its kits leave no ledge just above the floor it returns along.
  const KITS={d3:[['drop2','down'],['down','drop2'],['banner3'],['down','down','down']],
    d6:[['drop2','drop2','drop2'],['banner4','drop2'],['drop2','banner4'],['banner3','drop2','down']],
    d6r:[['drop2','drop2','drop2'],['banner4','drop2'],['drop2','banner4']],
    u3:[['up','up','up'],['shaft3'],['wallrun','up'],['shaft2','up']],
    u6:[['shaft3','shaft3'],['up','up','up','up','up','up'],['shaft3','up','up','up'],['wallrun','up','wallrun','up']]};
  const PRIM={drop2:()=>drop2(),down:()=>down(),up:()=>up(),banner3:()=>n>=4&&bannerSeg(3),banner4:()=>n>=4&&bannerSeg(4),
    shaft2:()=>n>=5&&shaftSeg(2),shaft3:()=>n>=5&&shaftSeg(3),wallrun:()=>n>=3&&wallRunSeg()};
  const LAND={drop2:-1,down:-1,up:0,banner3:-2,banner4:-2,shaft2:-1,shaft3:-1,wallrun:-1}; // where he stands after it, from c
  function buildTurn(t,nextRow){
    const key=(t.down?'d':'u')+(3*t.k),kits=(t.rev&&KITS[key+'r']?KITS[key+'r']:KITS[key]).slice();
    for(let i=kits.length-1;i>0;i--){const j=Math.floor(rng()*(i+1)),q=kits[i];kits[i]=kits[j];kits[j]=q;}
    const keep=[rMin,rMax];rMin=-1e9;rMax=1e9;let res=null;
    for(const kit of kits){
      const sv={base:L.base.slice(),feat:L.feat.slice(),kw:new Set(keepWall),path:bot.length,nf:newFeats.length,tc:touched.length,c,r,run};
      let ok=true,lastM=null;
      for(const m of kit){run=3;const t0=c,r0=r;if(!PRIM[m]()){ok=false;break;}lastM=m;L.segs.push({k:'turn-'+m,c0:t0,c1:c,r0,r1:r});}
      if(ok&&r===nextRow){res={land:c+LAND[lastM],kit};break;}
      L.base.set(sv.base);for(let i=0;i<sv.feat.length;i++)L.feat[i]=sv.feat[i];keepWall.clear();for(const k of sv.kw)keepWall.add(k);
      bot.length=sv.path;newFeats.length=sv.nf;touched.length=sv.tc;c=sv.c;r=sv.r;run=sv.run;
      while(L.segs.length&&L.segs[L.segs.length-1].k.startsWith('turn-')&&L.segs[L.segs.length-1].c0>=sv.c-0)L.segs.pop();
    }
    rMin=keep[0];rMax=keep[1];return res;
  }
  // what a run leaves to the generator's lists is in its own column space: put it back on the map
  const PXx=x=>(MX+1)*TW-x;
  function finishRun(m){
    const ordOf=x=>progBase+(x/TW-cEntry);
    for(let i=m.guards;i<L.guards.length;i++)L.guards[i].ord=ordOf(L.guards[i].x);
    for(let i=m.snakes;i<L.snakeSpecs.length;i++)L.snakeSpecs[i].ord=ordOf(L.snakeSpecs[i].x);
    for(let i=m.items;i<L.items.length;i++)L.items[i].ord=progBase+(L.items[i].c-cEntry);
    for(let i=m.det;i<(L.detours||[]).length;i++){const dd=L.detours[i];dd.c0=Math.min(PC(dd.c),PC(dd.c+dd.len));dd.c1=Math.max(PC(dd.c),PC(dd.c+dd.len));}
    if(L.secret&&!L.secret.fixed){L.secret.c=PC(L.secret.c);L.secret.fixed=true;}
    for(let i=m.segs;i<L.segs.length;i++){const q=L.segs[i];q.c0=PC(q.c0);q.c1=PC(q.c1);q.dir=MX<0?1:-1;}
    if(MX<0)return;
    for(let i=m.items;i<L.items.length;i++){const it=L.items[i];it.c=PC(it.c);it.x=PXx(it.x);}
    for(let i=m.guards;i<L.guards.length;i++){const g=L.guards[i],lo=g.lo;g.x=PXx(g.x);g.lo=PXx(g.hi);g.hi=PXx(lo);g.face=1;g.pit=-(g.pit||1);}
    for(let i=m.snakes;i<L.snakeSpecs.length;i++){const s=L.snakeSpecs[i],lo=s.lo;s.x=PXx(s.x);s.lo=PXx(s.hi);s.hi=PXx(lo);s.dir=1;}
    for(let i=m.torches;i<L.torches.length;i++)L.torches[i].c=PC(L.torches[i].c);
    for(let i=m.cps;i<L.cps.length;i++){const q=L.cps[i];q.c=PC(q.c);q.x=PXx(q.x);}
    for(let i=m.blocks;i<L.ext.blocks.length;i++){const b=L.ext.blocks[i],lo=b.lo;b.c=PC(b.c);b.lo=PC(b.hi);b.hi=PC(lo);}
    const seen=new Set();
    for(let i=m.path;i<bot.length;i++){const a=bot[i];if(seen.has(a))continue;seen.add(a);
      if(a.c!==undefined)a.c=PC(a.c);if(a.from!==undefined)a.from=PC(a.from);if(a.to!==undefined)a.to=PC(a.to);a.dir=-(a.dir||1);}
    for(const f of new Set(newFeats)){
      if(f.t==='darter'){f.x=PXx(f.x);f.x0=PXx(f.x0);f.dir=1;}
      else if(f.t==='saw'){const x0=f.x0;f.x0=PXx(f.x1);f.x1=PXx(x0);}
      else if(f.t==='bar')f.x=PXx(f.x);
      if(f.amb){const a=f.amb,lo=a.lo;a.x=PXx(a.x);a.lo=PXx(a.hi);a.hi=PXx(lo);a.end=PXx(a.end);a.dir=-1;}}
  }
  // keep a run's (or a turn's) surroundings clear of whatever comes later, so no later passage opens into it
  function keepClear(list){for(const idx of list){const p=idx%cols,rr=(idx-p)/cols;
    for(let dy=-2;dy<=1;dy++)for(let dx=-1;dx<=1;dx++){const q=(rr+dy)*cols+p+dx;if(rr+dy>=0&&rr+dy<rows&&p+dx>=0&&p+dx<cols&&L.base[q]===WALL)resv[q]=1;}}}
  const runs=plan.runs;let entryP=-1,prevKit=null;L.runsInfo=[];
  for(let k=0;k<runs.length;k++){
    const rn=runs[k],dir=rn.dir,R0=bandRow(rn.band),first=k===0,last=k===runs.length-1,endRoom=rn.rooms[rn.rooms.length-1];
    if(first)entryP=dir>0?roomLo(rn.rooms[0])+1:roomHi(rn.rooms[0])-1;
    MX=dir>0?-1:cols-1;c=PC(entryP);cEntry=c;r=R0;rMin=R0-1;rMax=R0;run=3;
    const vFar=PC(dir>0?roomHi(endRoom)-1:roomLo(endRoom)+1);vLo=first?c-1:c-3;vHi=vFar;
    touched=[];newFeats=[];
    const m={items:L.items.length,guards:L.guards.length,snakes:L.snakeSpecs.length,torches:L.torches.length,cps:L.cps.length,blocks:L.ext.blocks.length,path:bot.length,segs:L.segs.length,det:(L.detours||[]).length};
    if(first){ // the entrance: a door in the wall behind, a few tiles of floor
      set(c-1,r,FLOOR);set(c,r,FLOOR);set(c+1,r,FLOOR);
      L.start={x:entryP*TW+16,r,face:dir,door:PC(c-1)};c+=1;cEntry=c-2;
      {const kk=n<=2?ri(4,5):ri(1,3);flat(kk);}
    }
    let target=R0,iter=0;vHi=last?vFar-14:vFar-3; // room to settle before the turn; the last run ends on open floor before the door
    while(c<vHi&&iter++<5000){
      if(chaseWanted&&!L.ext.chase&&k===plan.chaseRun&&MX<0&&vHi-c>=60&&prog()>=6){
        if(raw(c,r)===FLOOR&&!fe(c,r)&&!L.cps.some(q=>prog()-q.ord<12)){L.cps.push({c,r,x:c*TW+16,on:false,ord:prog()});nextCp=prog()+CP_GAP;}
        {const c0=c,r0=r;if(chaseSeg()){L.segs.push({k:'chase',c0,c1:c,r0,r1:r});breathe();continue;}}}
      if(!secretDone&&prog()>=secretAt&&prog()<routeT*0.8&&c-cEntry>=8){const c0=c,r0=r;if(secretPassage()){secretDone=true;L.segs.push({k:'secret',c0,c1:c,r0,r1:r});breathe();continue;}}
      if(!xDone&&prog()>routeT*0.82&&W(c+1,r)&&W(c+2,r)){
        set(c+1,r,FLOOR);set(c+2,r,FLOOR);feat(c+1,r,{t:'xplate',press:-9});
        bot.push({a:'walk',c:c+2});c+=2;run+=2;xDone=true;continue;
      }
      if(L.guards.length-extraG<guardsWanted&&prog()-lastGuard>=guardGap&&c+12<vHi){const c0=c,r0=r,sk=style==='crypt'&&ch(0.5);if(sk?skeleton():guard()){L.segs.push({k:sk?'skel':'guard',c0,c1:c,r0,r1:r});flat(1);breathe();continue;}}
      if(prog()>=nextCp&&c<vHi-12&&raw(c,r)===FLOOR&&!fe(c,r)&&!L.items.some(it=>it.c===c&&it.r===r)){L.cps.push({c,r,x:c*TW+16,on:false,ord:prog()});nextCp=prog()+CP_GAP;}
      if(r===target||ch(0.08))target=ri(rMin,rMax);
      const opts=[];const add=(w,f,kd)=>{if(w>0)opts.push([w,f,kd]);};
      add(run<2?4:1.4,()=>flat(ri(1,3)),'flat');
      add(n<=2?2.2:1.5,()=>gap(1),'gap1');
      if(n>=2)add(1.3,()=>gap(2),'gap2');
      if(n>=4)add(0.9,()=>gap(3),'gap3');
      add(r>target?3:0.5,up,'up');
      add(r<target?3:0.5,down,'down');
      if(n>=2)add(1.1,()=>spikes(n>=6&&ch(0.4)?2:1),'spikes');
      if(n>=3)add(1.0,()=>loose(n>=5&&ch(0.45)?2:1),'loose');
      if(n>=4)add(0.9,chomp,'chomp');
      if(n>=3)add(0.75,gate,'gate');
      if(n>=4&&c-cEntry>=8)add(0.22,detourGate,'detour');
      if(n>=7&&c-cEntry>=8)add(0.08,doubleGate,'double');
      if(n>=6)add(0.3,swingSeg,'swing');
      if(n>=5)add(0.1,sawSeg,'saw');
      if(n>=6&&r===rMax)add(0.12,dartSeg,'darts');
      if(n>=7)add(0.065,blockSeg,'block');
      if(n>=3)add(0.45,tunnel,'tunnel');
      if(style==='dungeon'&&n>=2)add(0.9,stones,'stones');
      if(style==='palace')add(0.9,bridge,'bridge');
      if(style==='tile')add(0.85,pendulum,'pend');
      if(style==='forge')add(0.9,vents,'vents');
      let tot=0;for(const o of opts)tot+=o[0];
      let x=rng()*tot,chosen=opts[0][1],kind=opts[0][2];
      for(const o of opts){x-=o[0];if(x<=0){chosen=o[1];kind=o[2];break;}}
      const before=c,rBefore=r;
      if(chosen()){L.segs.push({k:kind,c0:before,c1:c,r0:rBefore,r1:r});if(!MOVES.has(kind))breathe();}
      else{if(!flat(1))break;}
      if(c!==before&&raw(c,r)===FLOOR&&!fe(c,r)){
        if(ch(0.07))L.items.push({c,r,x:c*TW+16,type:(n>=8&&ch(0.2))?'poison':'heal',taken:false});
        else if(prog()-lastTorch>=6&&ch(0.55)){L.torches.push({c,r});lastTorch=prog();}
      }
      if(alcoves.length&&prog()>routeT*alcoves[0].at&&ch(0.3)){if(alcove(alcoves[0].type))alcoves.shift();}
    }
    vHi=vFar;
    if(r<R0)down(); // back onto the band's floor
    const runEnd=c,runCells=touched;
    if(last){
      while(c<vFar-1&&W(c+1,r)){set(c+1,r,FLOOR);c++;}
      bot.push({a:'walk',c:c-1});
      L.door={c:PC(c-1),r,x:PC(c-1)*TW+16,open:xDone?0:1,opening:!xDone};
      bot.push({a:'door'});
      L.torches.push({c:c-3,r});
    }
    L.runsInfo.push({dir,band:rn.band,row:R0,c0:entryP,c1:PC(runEnd)});
    let next=null;
    if(!last){
      const t=plan.turns[k],nextRow=bandRow(runs[k+1].band),tcol=endRoom+dir;
      vHi=PC(dir>0?roomHi(tcol)-1:roomLo(tcol)+1);vLo=c-2;touched=[];
      next=buildTurn(t,nextRow);
      if(!next)return null;
      next.cells=touched;
      entryP=t.rev?PC(next.land):PC(c);
    }
    finishRun(m);
    progBase+=runEnd-cEntry;
    MX=-1;keepClear(runCells);if(prevKit)keepClear(prevKit.cells);
    prevKit=next;
  }
  MX=-1;vLo=-1e9;vHi=1e9;rMin=0;rMax=1e9;touched=null;
  if(!secretDone){ // no room for a hidden passage: fall back to a gold flask in an alcove near the end
    for(let k=0;k<L.items.length;k++){const it=L.items[k];if(it.alc){it.type='life';secretDone=true;break;}}}
  // thin out flasks: the gold flask always stays; every other flask keeps FLASK_GAP tiles of route from any kept one (alcoves before floor flasks)
  {const FLASK_GAP=Math.round(35*PKW),kept=[],rank=it=>it.type==='life'?0:it.type==='big'?1:it.alc?2:3;
    for(const it of L.items.slice().sort((a,b)=>rank(a)-rank(b)||a.ord-b.ord))if(kept.every(k=>Math.abs(k.ord-it.ord)>=FLASK_GAP))kept.push(it);
    L.items=L.items.filter(it=>kept.includes(it));}
  // open a hall over everything the prince moves through: one row of headroom above every floor, gap and shaft top.
  // Gates and blades keep their lintel; the entrance and exit keep a wall to sit in.
  {const hol=[];
    for(let rr=1;rr<rows;rr++)for(let cc=1;cc<cols-1;cc++){
      if(raw(cc,rr)===WALL||raw(cc,rr-1)!==WALL)continue;
      const f=fe(cc,rr);if(f&&(f.t==='gate'||f.t==='chomp'||f.t==='low'))continue;
      if(rr===L.door.r&&Math.abs(cc-L.door.c)<=2)continue;
      if(rr===L.start.r&&(cc===L.start.door||cc===L.start.door+L.start.face))continue;
      if(keepWall.has((rr-1)*cols+cc))continue;
      hol.push(cc,rr-1);}
    for(let i=0;i<hol.length;i+=2){set(hol[i],hol[i+1],EMPTY);if(ch(0.16))L.windows.push({c:hol[i],r:hol[i+1]});}}
