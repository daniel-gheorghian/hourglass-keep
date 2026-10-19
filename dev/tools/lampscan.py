# lampscan.py [file.html] [lo hi] [seeds]: round 19's lamp placement check. Every lamp still burning (L.torches, after settleLights)
# must stand clear of a wall's front face or a step (a WALL beside it on its row), a ledge (no floor beside it), a gate, a lift's or a
# sand lift's shaft, a banner, kick shaft, swing bar or pendulum beside it, and a door or water clock (the checkpoint) near it.
# Prints the counts by kind and the lamps per floor (so a move is seen to keep them), and 'ok' when there are none. Run from dev/tools.
import json, os, sys
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
SRC = os.path.abspath(a[0] if a and a[0].endswith('.html') else os.path.join(HERE, '..', 'hourglass-keep.html'))
nums = [x for x in a if not x.endswith('.html')]
LO, HI = (int(nums[0]), int(nums[1])) if len(nums) >= 2 else (1, 48)
SEEDS = [int(s) for s in nums[2].split(',')] if len(nums) >= 3 else [1, 2, 3]
SCAN = r'''([lo,hi,seeds])=>{const H=__HK,out={n:0,bad:{},per:[],ex:[]};
  const FT=new Set(['gate','lift','sandcol','chain','banner','shaftfoot','bar','pend','lplate']);
  for(let n=lo;n<=hi;n++)for(const sd of seeds){window.__HKfreeze=true;const L=H.load(n,sd,true),C=L.cols,B=(c,r)=>c<0||c>=C||r<0?2:r>=L.rows?0:L.base[r*C+c],F=(c,r)=>c<0||c>=C||r<0||r>=L.rows?null:L.feat[r*C+c];
    const sb=(c,r)=>{const b=B(c,r);return b===1||(b===0&&B(c,r+1)===2);};let k=0;
    for(const t of L.torches){if(t.broken)continue;k++;out.n++;const why=[];
      for(const d of [-1,1]){const c=t.c+d;
        if(B(c,t.r)===2)why.push('wall');else if(!sb(c,t.r))why.push('ledge');
        const f=F(c,t.r);if(f&&FT.has(f.t))why.push('feat:'+f.t);}
      const f0=F(t.c,t.r);if(f0)why.push('on:'+f0.t);
      for(const lf of L.lifts)if(t.c>=lf.ca-1&&t.c<=lf.cb+1&&t.r>=lf.rT&&t.r<=lf.rB)why.push('liftshaft');
      if(L.door&&L.door.r===t.r&&Math.abs(L.door.c-t.c)<=2)why.push('door');
      const sdc=L.start.door===undefined?1:L.start.door;if(L.start.r===t.r&&Math.abs(sdc-t.c)<=1)why.push('door');
      for(const cp of L.cps)if(cp.r===t.r&&Math.abs(Math.floor(cp.x/32)-t.c)<=1)why.push('clock');
      const u=[...new Set(why)];for(const w of u)out.bad[w]=(out.bad[w]||0)+1;
      if(u.length){out.bad.lamps=(out.bad.lamps||0)+1;if(out.ex.length<12)out.ex.push([n,sd,t.c,t.r,u.join('+')]);}}
    out.per.push(k);}
  return out;}'''
if __name__ == '__main__':
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={'width': 852, 'height': 393})
        pg.goto('file://' + SRC); pg.wait_for_timeout(600)
        r = pg.evaluate(SCAN, [LO, HI, SEEDS])
        print('floors %d-%d seeds %s: %d lamps, %.2f a floor' % (LO, HI, SEEDS, r['n'], r['n'] / max(1, len(r['per']))))
        print('violations', json.dumps(r['bad'], sort_keys=True))
        for e in r['ex']:
            print('  e.g. floor %d seed %d lamp c%d r%d: %s' % tuple(e))
        print('ok' if not r['bad'] else 'FAIL')
        b.close()
