# Route length, trap count/spacing, the bare corridor beside gate side passages, and how many turn storeys are plain steps.
# Compares the last release (hk_v39_release.html) with the working source. Run from dev/tools.
from playwright.sync_api import sync_playwright
import json,statistics as S,sys,os
HERE=os.path.dirname(os.path.abspath(__file__))
BT=sys.argv[1] if len(sys.argv)>1 else 'v39' # the release to compare with (v39 is the standing reference of the trap density rule G1)
BASE=(BT,os.path.join(HERE,'hk_%s_release.html'%BT))
CUR=('cur',os.path.join(HERE,'..','hourglass-keep.html'))
JS='''()=>{const H=__HK,out={};const MOV=new Set(['flat','up','down','drop2']),VERT=new Set(['wallrun','shaft','banner']);
  const STEP=new Set(['turn-up','turn-down','turn-drop2']);
  // a trap is any seg that is not a plain move, a turn piece, a loop piece or a fork piece (unknown kinds count as traps).
  // Guards and skeletons are fighters on their own budget (guardBudget), no longer traps; isTrapOld keeps the old count for comparison.
  const isTrapOld=q=>!MOV.has(q.k)&&!/^(turn-|loop-|fork-)/.test(q.k), isTrap=q=>isTrapOld(q)&&q.k!=='guard'&&q.k!=='skel';
  const SIDE=new Set(['detour','double','secret','puzzle']); // the side passage's own seg spans its corridor: not an obstacle in it
  for(let n=1;n<=27;n++){const acc=[];for(let s=0;s<20;s++){const L=H.genLevel(n,30000+s*101+n*7,true);
    const tr=L.segs.filter(isTrap);
    const turnsV=L.segs.filter(q=>/turn-(banner|sand|shaft|wallrun)/.test(q.k)).length;
    let gaps=[];for(let i=1;i<tr.length;i++){const a=tr[i-1],b2=tr[i],d=b2.dir||1;if((a.dir||1)!==d||Math.abs(a.r1-b2.r0)>1)continue;const g=(b2.c0-a.c1)*d;if(g>=0&&g<60)gaps.push(g);}
    let route;if(L.runsInfo){route=0;for(const ri of L.runsInfo)route+=Math.abs(ri.c1-ri.c0);const lr=L.runsInfo[L.runsInfo.length-1];route+=Math.abs(L.door.c-lr.c1);}else route=L.door.c-L.start.x/32;
    // bare: for each gate side passage, the longest stretch of its corridor (columns under/over the branch) with no obstacle
    const bare=[],bareS=[];
    for(const dd of L.detours||[]){const lo=dd.c0,hi=dd.c1,cov=new Set();
      for(const q of L.segs){if(!isTrap(q)||SIDE.has(q.k))continue;if(q.r0!==dd.r&&q.r1!==dd.r)continue;
        const a=Math.min(q.c0,q.c1),b=Math.max(q.c0,q.c1);if(b<lo||a>hi)continue;for(let x=Math.max(a,lo);x<=Math.min(b,hi);x++)cov.add(x);}
      let best=0,cur=0;for(let x=lo;x<=hi;x++){if(cov.has(x))cur=0;else{cur++;if(cur>best)best=cur;}}
      (dd.secret?bareS:bare).push(best);}
    // storeys climbed or dropped in turns, and the share done by plain steps
    let st=0,all=0;for(const q of L.segs){if(!q.k.startsWith('turn-'))continue;const h=Math.abs(q.r1-q.r0);all+=h;if(STEP.has(q.k))st+=h;}
    acc.push({route,traps:tr.length,trapsOld:L.segs.filter(isTrapOld).length,snakes:L.snakeSpecs.length,vert:tr.filter(q=>VERT.has(q.k)).length+turnsV,gapMin:gaps.length?Math.min(...gaps):99,gapMean:gaps.reduce((a,b)=>a+b,0)/Math.max(1,gaps.length),
      guards:L.guards.length,cps:L.cps.length,det:(L.detours||[]).length,loops:(L.forks||L.loops||[]).length,bare,bareS,stepSt:st,allSt:all});}
    out[n]=acc;}return out;}'''
out={}
for tag,f in (BASE,CUR):
  with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+f); pg.wait_for_timeout(300)
    out[tag]=pg.evaluate(JS); b.close()
    if errs: print('page errors',tag,errs[:3])
json.dump(out,open('fm40.json','w'))
def m(a,k): return S.mean(x[k] for x in a)
def mn(a,k): return min(x[k] for x in a)
def bare(a,k='bare'):
    v=[w for x in a for w in x[k]]; return (round(S.mean(v),1),max(v)) if v else (0,0)
def share(a):
    s=sum(x['stepSt'] for x in a);t=sum(x['allSt'] for x in a); return round(s/t,2) if t else 0
A,B=BASE[0],CUR[0]
hdr=['n','route'+A,'route'+B,'tOld'+A,'tOld'+B,'guards'+A,'guards'+B,'snakes'+A,'snakes'+B,'rmin'+A,'rmin'+B,'traps'+A,'traps'+B,'gmin'+A,'gmin'+B,'bareMean'+A,'bareMean'+B,'bareMax'+A,'bareMax'+B,'step'+A,'step'+B]
print(' '.join(hdr)); flags=[]
for n in range(1,28):
    a=out[A][str(n)];b=out[B][str(n)];ba,bb=bare(a),bare(b)
    row=[n,round(m(a,'route'),1),round(m(b,'route'),1),round(m(a,'trapsOld'),1),round(m(b,'trapsOld'),1),round(m(a,'guards'),1),round(m(b,'guards'),1),round(m(a,'snakes'),1),round(m(b,'snakes'),1),round(mn(a,'route'),1),round(mn(b,'route'),1),round(m(a,'traps'),1),round(m(b,'traps'),1),mn(a,'gapMin'),mn(b,'gapMin'),ba[0],bb[0],ba[1],bb[1],share(a),share(b)]
    print(' '.join(str(x) for x in row))
    if m(b,'route')<m(a,'route')-1e-9: flags.append((n,'route mean %.1f<%.1f'%(m(b,'route'),m(a,'route'))))
    if mn(b,'route')<mn(a,'route')-1e-9: flags.append((n,'route min %.1f<%.1f'%(mn(b,'route'),mn(a,'route'))))
    if mn(b,'gapMin')<2: flags.append((n,'min trap gap %d<2'%mn(b,'gapMin')))
print('FLAGS:',flags if flags else 'none')
