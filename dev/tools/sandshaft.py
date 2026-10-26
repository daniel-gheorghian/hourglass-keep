# sandshaft.py [file.html] [lo hi] [seeds] [v]: every sand lift stands in a shaft (round 26e, owner: "sand lifts must always work within
# a shaft otherwise they don't make sense"). A sand lift's slab rests on a column of sand in its shaft's cells (column sc, from under the top
# landing's floor, SURF(rT), down to the foot's floor, SURF(rB)); the sand runs out through the outlet in the foot of the back wall. On the
# tiles, for every storey the sand stands in (rows rT+1..rB), the cells either side of the shaft must be wall (stone that holds the sand in),
# and the shaft's foot must be a hole into its bottomless shaft (round 41). At the foot storey (row rB) an open side (the exit he leaves by, and the far side where a corridor
# runs on) must be shut by a mouth slab standing on floor (f.ms: shut while sand stands in the foot storey, up once the slab is down).
# Anything else is counted by storey and kind:
#   open  an open cell beside the shaft with floor in it or under it (a corridor, a hall's headroom over a floor);
#   hole  an open cell with open space under it (a pit, a drop);
#   exit  the foot storey's exit side with no mouth slab;
#   foot  the shaft's foot is not a hole into the bottomless shaft (round 41: it was floor before);
#   deep  (round 41) a cell of the bottomless shaft under the foot (rows rB+1..rD, SAND_DEEP 3 storeys) not open, a cell beside it not wall,
#         or no rock under it. It also prints how many sand lifts were built as the banner slide instead, and why (bn.fb).
# Floors lo..hi (default 1..48), `seeds` seeds each (default 3), seeds 40000+n*131+s*7919 as liftscan. Prints the counts, a few examples
# (all with v), then `sandshaft: ok` (0 sand lifts not enclosed) or `sandshaft: FAIL n`. Run from dev/tools.
import json, os, sys
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
SRC = next((x for x in a if x.endswith('.html')), os.path.join(HERE, '..', 'hourglass-keep.html'))
nums = [int(x) for x in a if x.isdigit()]
LO, HI = (nums[0], nums[1]) if len(nums) >= 2 else (1, 48)
SEEDS = nums[2] if len(nums) >= 3 else 3
SCAN = r'''([lo,hi,seeds])=>{const H=__HK,out=[];
  for(let n=lo;n<=hi;n++)for(let s=0;s<seeds;s++){const seed=40000+n*131+s*7919,L=H.genLevel(n,seed,true),C=L.cols;
    const B=(c,r)=>c<0||c>=C||r<0?2:r>=L.rows?0:L.base[r*C+c];
    L.lifts.forEach((f,i)=>{if(!f.sand)return;const bad=[];const ex=f.sB;let mo=0;
      for(let r=f.rT+1;r<=f.rB;r++)for(const sd of [-1,1]){const c=f.sc+sd,b=B(c,r);if(b===2)continue;
        const flo=b===1||B(c,r+1)===2; // (an open cell with a floor to stand a slab on)
        if(r===f.rB&&f.ms&&f.ms.includes(sd)&&flo){mo++;continue;}
        bad.push([r===f.rB&&sd===ex?'exit':flo||B(c,r+1)===1?'open':'hole',r-f.rT,sd]);}
      // (round 41) the foot is a hole into the bottomless shaft: open from the foot down SAND_DEEP storeys (rD), walled on both sides, rock under it
      if(B(f.sc,f.rB)!==0||!f.rD||f.rD-f.rB<3)bad.push(['foot',f.k,0]);
      else{for(let r=f.rB+1;r<=f.rD;r++){if(B(f.sc,r)!==0)bad.push(['deep',r-f.rT,0]);for(const sd of [-1,1])if(B(f.sc+sd,r)!==2)bad.push(['deep',r-f.rT,sd]);}if(B(f.sc,f.rD+1)!==2)bad.push(['deep',f.rD+1-f.rT,0]);}
      out.push({n,seed,i,sc:f.sc,rT:f.rT,k:f.k,ex,bad,mo,th:H.themeName(n)});});
    const seen=new Set();for(const q of L.feat)if(q&&q.t==='banner'&&q.bn&&q.bn.fb&&!seen.has(q.bn)){seen.add(q.bn);out.push({fb:q.bn.fb});}}
  return out;}'''
if __name__ == '__main__':
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={'width': 852, 'height': 393})
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto('file://' + os.path.abspath(SRC)); pg.wait_for_timeout(300)
        res = pg.evaluate(SCAN, [LO, HI, SEEDS]); b.close()
    fbs = [x['fb'] for x in res if 'fb' in x]; res = [x for x in res if 'fb' not in x]
    tot = len(res); badl = [x for x in res if x['bad']]
    kinds = {}
    for x in badl:
        for k, st, sd in x['bad']:
            key = '%s storey %d %s' % (k, st, 'exit side' if sd == x['ex'] else 'far side')
            kinds[key] = kinds.get(key, 0) + 1
    whys = {}
    for x in badl:
        w = '+'.join(sorted(set(k for k, _, _ in x['bad']))); whys[w] = whys.get(w, 0) + 1
    print('sand lifts %d on floors %d-%d x%d seeds (k3 %d, k4 %d); foot mouth slabs %d (two: %d); not enclosed %d; by kind %s' % (tot, LO, HI, SEEDS,
          sum(x['k'] == 3 for x in res), sum(x['k'] == 4 for x in res), sum(x['mo'] for x in res), sum(x['mo'] == 2 for x in res), len(badl), json.dumps(whys)))
    print('built as the banner slide instead (round 41: bn.fb): no rock for the bottomless shaft %d, the way on not to be taken off the slab %d, not walled or a jump under the kept walls %d' % (
          fbs.count(1), fbs.count(2), fbs.count(3)))
    for k in sorted(kinds):
        print('  %-28s %d' % (k, kinds[k]))
    for x in badl[:len(badl) if 'v' in a else 8]:
        print('  n=%d seed=%d lift %d col %d rows %d-%d k%d: %s' % (x['n'], x['seed'], x['i'], x['sc'], x['rT'], x['rT'] + x['k'], x['k'], x['bad']))
    if errs:
        print('page errors', errs[:3])
    print('sandshaft: ok' if not badl and not errs else 'sandshaft: FAIL %d' % len(badl))
