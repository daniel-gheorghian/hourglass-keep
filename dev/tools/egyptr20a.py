# egyptr20a.py [new.html] [old.html] [outdir]: round 20a's pictures and numbers for egypt_themes.html, before (old.html, default the v67 release,
# hk_v67_release.html here or in the main checkout's dev/tools) and after, in the game at the phone's resolution (crops of the 1704 px canvas):
#  r20a_low.png     sky beams over a low ceiling's block (a tunnel's roof), the prince crawling under it: Torchlight and Classic, before and after,
#                   three floors (two themes), and Torchlight at GLP.rs 0.5 (the owner's phone ran at 50%)
#  r20a_blade.png   a beam across a slicer's blades, two themes: Torchlight (rs 1 and 0.5) and Classic, before and after
#  r20a_shadow.png  a lamp casting his shadow toward a tunnel's mouth: the low ceiling's front face, before and after, Torchlight, rs 1 and 0.5
# The cases are found by scanning floors 3 to 30, seeds 1 to 4 (FIND). It also prints, per case and build (Torchlight, rs 1), how much light the
# beams add on the low ceilings' front faces in view (the frame with the shafts minus the frame without, mean of R+G+B over the faces' pixels)
# and how much the figure shadow takes off them (the frame without GLFX.shadow minus the frame with it): both should be about 0 after.
# Writes r20a.json (cases, numbers, errors). Run from dev/tools.
import io, json, os, sys
from playwright.sync_api import sync_playwright
from PIL import Image
import egyptr12 as R12
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
NEW = os.path.abspath(a[0] if len(a) > 0 else os.path.join(HERE, '..', 'hourglass-keep.html'))
_old = os.path.join(HERE, 'hk_v67_release.html')
if not os.path.exists(_old):
    _old = os.path.join(HERE, '..', '..', '..', '..', '..', 'dev', 'tools', 'hk_v67_release.html')  # (from a worktree: the main checkout's)
OLD = os.path.abspath(a[1] if len(a) > 1 else _old)
OUT = a[2] if len(a) > 2 else os.path.join(HERE, 'egypt_themes')
R12.OUT = OUT
TAG = {'old': 'before (v67)', 'new': 'after (20a)'}
FIND = r'''([lo,hi,seeds])=>{const H=__HK,out={low:[],jaw:[],gate:[],lamp:[]};
 for(let n=lo;n<=hi;n++)for(const sd of seeds){const L=__P.load(n,sd),C=L.cols,F=(c,r)=>c<0||c>=C||r<0||r>=L.rows?null:L.feat[r*C+c],isLow=(c,r)=>{const f=F(c,r);return !!(f&&f.t==='low');};
  const sb=H.skyBeam();
  for(const o of H.ryOps()){if(o.sh.own||o.x0<10*32||o.x1>(C-10)*32)continue;const cx=(o.x0+o.x1)/2,cy=(o.y0+o.y1)/2;let lw=null,jw=null,gt=null;
    for(let t=2;t<(o.fl+8-cy)/sb.dy;t+=2){const x=cx+sb.dx*t,y=cy+sb.dy*t,r=Math.floor(y/64),c=Math.floor((x+8)/32);if(r<0||r>=L.rows||L.base[r*C+c]===2)break;
      if(!lw&&isLow(c,r)&&!isLow(c-1,r)&&y-r*64<30)lw={c,r};const c2=Math.floor(x/32),f=F(c2,r);
      if(!jw&&f&&f.t==='chomp'&&Math.abs(x-(c2*32+16))<8&&y-r*64<36)jw={c:c2,r};if(!gt&&f&&f.t==='gate'&&Math.abs(x-(c2*32+16))<8&&y-r*64>20)gt={c:c2,r};}
    if(lw)out.low.push({n,sd,c:lw.c,r:lw.r,name:H.themeName(n)});if(jw)out.jaw.push({n,sd,c:jw.c,r:jw.r,name:H.themeName(n)});if(gt)out.gate.push({n,sd,c:gt.c,r:gt.r,name:H.themeName(n)});}
  for(const t of L.torches){if(t.broken)continue;for(let d=2;d<=4;d++)if(isLow(t.c+d,t.r)&&!isLow(t.c+d-1,t.r)){let ok=true;for(let k=1;k<d;k++)if(!H.solidBelow(t.c+k,t.r)||F(t.c+k,t.r))ok=false;
    if(ok)out.lamp.push({n,sd,c:t.c,r:t.r,d,name:H.themeName(n)});break;}}}
 return out;}'''
# the case drawn: floor, seed, the prince's cell (pc<0: out of view), 'duck' to crouch, the view's centre, GLP.rs, a gate or slicer held (c, r, state)
SHOW = r'''([q,rs,meas])=>{const H=__HK;document.body.classList.remove('panelOpen');__P.load(q.n,q.sd);if(q.pc>=0)__P.stand(q.pc,q.r,q.face||1);else H.P.x=-999;
  const L=H.L,P=H.P;if(q.duck){H.setKey('kb','d',true);H.tick(20);H.setKey('kb','d',false);}
  for(const o of L.dyn){if(o.f.t==='chomp'){o.f.per=1e9;o.f.off=q.k||0.5;}if(o.f.t==='gate'&&q.gate&&o.c===q.c&&o.r===q.r){o.f.open=0.35;o.f.tm=99;}}
  if(H.GLP)H.GLP.rs=rs;H.cam.x=q.x-H.viewW/2;H.cam.y=q.y-150;H.cam.gy=H.cam.y;H.cam.snap=false;window.__HKfreeze=true;H.mode='play';H.banner=null;
  const R=()=>{for(let i=0;i<4;i++)H.render();};R();if(!meas)return __P.scr(q.x,q.y);
  const shot=()=>{const cv=[...document.querySelectorAll('canvas')].find(c=>c.getBoundingClientRect().width>0&&c.getContext&&c.width>800),g=document.createElement('canvas');g.width=cv.width;g.height=cv.height;const x=g.getContext('2d');
    for(const c of document.querySelectorAll('canvas'))if(c.getBoundingClientRect().width>0&&c.width===cv.width)x.drawImage(c,0,0);return x.getImageData(0,0,g.width,g.height).data;};
  const X=H.XF,W=Math.round(H.viewW*X.VZ),faces=[];for(let r=0;r<L.rows;r++)for(let c=0;c<L.cols;c++){const f=L.feat[r*L.cols+c];if(!f||f.t!=='low'||L.base[r*L.cols+c]===2)continue;
    const x0=Math.round((c*32-8)*X.VZ-X.camD)+2,x1=Math.round((c*32+24)*X.VZ-X.camD)-2,y0=Math.round(r*64*X.VZ-X.camDY)+2,y1=Math.round((r*64+27)*X.VZ-X.camDY)-1;faces.push([x0,y0,x1,y1]);}
  const mean=(d,e,w)=>{let s=0,n=0;for(const [x0,y0,x1,y1] of faces)for(let y=Math.max(0,y0);y<y1;y++)for(let x=Math.max(0,x0);x<Math.min(w,x1);x++){const i=(y*w+x)*4;if(i<0||i>=d.length)continue;s+=(d[i]+d[i+1]+d[i+2])-(e[i]+e[i+1]+e[i+2]);n++;}return n?s/n:null;};
  const cvw=[...document.querySelectorAll('canvas')].find(c=>c.getBoundingClientRect().width>0&&c.width>800).width;
  const a=shot();H.GLFX.shadow=false;R();const c=shot();H.GLFX.shadow=true; // (the shadow: the frame without it minus the frame with it)
  const G=H.GLFX,sv=[G.mist,G.caustics,G.sheen,G.lookfx];G.mist=G.caustics=G.sheen=G.lookfx=false;R();const a2=shot();H.GLC.on=false;R();const b=shot(); // (the beams alone: the atmosphere pass's mist, caustics, sheen and looks off)
  H.GLC.on=true;[G.mist,G.caustics,G.sheen,G.lookfx]=sv;R();return {beam:mean(a2,b,cvw),shadow:mean(c,a,cvw)};}'''


def tile(pg, q, rs, cw, ch, lab):
    xy = pg.evaluate(SHOW, [q, rs, False])
    return R12.label(R12.crop(R12.shot(pg), xy, cw, ch), lab)


if __name__ == '__main__':
    J = {'errors': [], 'cases': {}, 'num': []}
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
        P = {(v, m): R12.page(b, src, m) for v, src in (('old', OLD), ('new', NEW)) for m in ('torch', 'classic')}
        F = P[('new', 'torch')].evaluate(FIND, [3, 30, [1, 2, 3, 4]])

        def pick(lst, k, key=lambda q: q['name']):
            out, seen = [], set()
            for q in lst:
                if key(q) not in seen:
                    seen.add(key(q)); out.append(q)
                if len(out) == k:
                    break
            return out
        low = pick(F['low'], 3, lambda q: (q['n'], q['name']))
        for q in low:
            q.update(pc=q['c'], duck=True, x=q['c'] * 32, y=q['r'] * 64 + 30)
        jaw = pick(F['jaw'], 2)
        for q in jaw:
            q.update(pc=-1, x=q['c'] * 32 + 16, y=q['r'] * 64 + 10)
        gate = pick(F['gate'], 1)
        for q in gate:
            q.update(pc=-1, gate=True, x=q['c'] * 32 + 16, y=q['r'] * 64 + 20)
        lamp = pick(F['lamp'], 3)
        for q in lamp:
            q.update(pc=q['c'] + q['d'] - 1, face=1, x=(q['c'] + q['d']) * 32, y=q['r'] * 64 + 30)
        J['cases'] = {'low': low, 'jaw': jaw, 'gate': gate, 'lamp': lamp}
        # ---- the low ceilings in beams
        rows = []
        for q in low:
            t = [tile(P[(v, m)], q, 1, 420, 300, '%s, floor %d, %s, %s' % (q['name'][:22], q['n'], m, TAG[v])) for m in ('torch', 'classic') for v in ('old', 'new')]
            rows.append(R12.grid(t, 4))
        q = low[0]
        rows.append(R12.grid([tile(P[(v, 'torch')], q, 0.5, 420, 300, 'GLP.rs 0.5, torch, %s' % TAG[v]) for v in ('old', 'new')], 2))
        R12.stack(rows).save(os.path.join(OUT, 'r20a_low.png'))
        # ---- the blades (and a slab)
        rows = []
        for q in jaw:  # (a portcullis slab is handled the same way; the scan's slabs in beams sit at the edge of the light, so they make a poor picture)
            t = [tile(P[(v, m)], q, rs, 300, 320, '%s, %s, %s%s' % (q['name'][:18], m, TAG[v], ', rs .5' if rs < 1 else '')) for m in ('torch', 'classic') for v in ('old', 'new') for rs in ((1, 0.5) if m == 'torch' else (1,))]
            rows.append(R12.grid(t, 6))
        R12.stack(rows).save(os.path.join(OUT, 'r20a_blade.png'))
        # ---- the shadow on a low ceiling's face
        t = []
        for q in lamp:
            for rs in (1, 0.5):
                for v in ('old', 'new'):
                    t.append(tile(P[(v, 'torch')], q, rs, 300, 300, '%s, floor %d, %s%s' % (q['name'][:18], q['n'], TAG[v], ', rs .5' if rs < 1 else '')))
        R12.grid(t, 4).save(os.path.join(OUT, 'r20a_shadow.png'))
        # ---- the numbers (Torchlight, rs 1)
        for kind, lst in (('low', low), ('lamp', lamp)):
            for q in lst:
                r = {v: P[(v, 'torch')].evaluate(SHOW, [q, 1, True]) for v in ('old', 'new')}
                J['num'].append({'kind': kind, 'n': q['n'], 'sd': q['sd'], 'name': q['name'], 'old': r['old'], 'new': r['new']})
                print(kind, q['n'], q['sd'], q['name'], 'old', r['old'], 'new', r['new'], flush=True)
        for pg in P.values():
            J['errors'] += pg.errs
        json.dump(J, open(os.path.join(OUT, 'r20a.json'), 'w'), indent=1)
        print('errors', J['errors'][:4])
        b.close()
