# cpscan.py [file.html] [lo hi] [seeds] [torch|classic|both] [old] [out.png]: the water clock (the checkpoint) over the walls (round 37c, owner
# after v81: "The timer checkpoint over the front wall"). The clock stands at mid-depth; a wall's front face (a step's, a low ceiling's) stands
# HX nearer and HX to the left of its cell, so in the cell before a wall the clock's right half was drawn over that face. For every checkpoint
# on floors lo..hi (default 1-48: all twelve themes), seeds (default 1,2,3), in Torchlight and in Classic: those with a nearer face in a cell
# beside them on their row (WALL, or a low ceiling's block) are framed lit (its halo on), the clock drawn and then left out (CP_DBG.off, which
# keeps only Classic's wide room glow, a lamp's light, not the clock's own drawing), and the pixels of those faces (1 px in from their edges)
# must not change. Any other checkpoint cannot reach a face: what the clock draws reaches 32 px from its middle (the halo), the faces two cells
# off begin 40 px away. A clock is bad when more than 4 of its face pixels differ by more than 24 (sum of channels). 'old' draws v81's
# placement with no cut (CP_DBG.old: the count before). Prints the counts per mode and 'cpscan: ok'; a sheet of the worst cases (cpscan.png).
# Run from dev/tools.
import io, os, sys
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
SRC = os.path.abspath(next((x for x in a if x.endswith('.html')), os.path.join(HERE, '..', 'hourglass-keep.html')))
NUM = [int(x) for x in a if x.isdigit()]
LO, HI = (NUM + [1, 48])[:2] if len(NUM) >= 2 else (1, 48)
SEEDS = [int(s) for s in next((x for x in a if ',' in x), '1,2,3').split(',')]
OUT = next((x for x in a if x.endswith('.png')), os.path.join(HERE, 'cpscan.png'))
MODES = ['torch', 'classic'] if 'both' in a or not ('torch' in a or 'classic' in a) else (['torch'] if 'torch' in a else ['classic'])
OLD = 'old' in a
# every checkpoint of the floor, and whether a nearer face stands beside it on its row (the cell before it or after it)
LIST = r'''([n,sd])=>{const H=__HK;window.__HKfreeze=true;const L=H.load(n,sd,true),C=L.cols,out=[];
  const face=(c,r)=>{if(c<0||c>=C||r<0||r>=L.rows)return 0;if(L.base[r*C+c]===2)return 1;const f=L.feat[r*C+c];return f&&f.t==='low'?1:0;};
  for(let i=0;i<L.cps.length;i++){const q=L.cps[i];out.push([i,q.c,q.r,face(q.c-1,q.r)+2*face(q.c+1,q.r),q.x-q.c*32]);}return out;}'''
# frame checkpoint i lit, with the clock drawn (off false) or left out; returns the faces beside it in css px and its drawn x
SHOW = r'''([n,sd,i,off,old])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS)H.S.hints[id]=1;const L=H.load(n,sd,true),C=L.cols;H.banner=null;
  H.CP_DBG.old=old;H.CP_DBG.off=off;H.clearRooms();const P=H.P;P.inv=1e9;P.x=-999;const q=L.cps[i];for(const o of L.cps)o.on=false;q.on=true;q.onAt=-100;
  H.cam.x=q.x-H.viewW/2;H.cam.y=(q.r+1)*64-64*1.6;H.cam.gy=H.cam.y;H.mode='play';H.GLP&&(H.GLP.pipe=false);H.gameTime=10;
  H.render();H.render();H.render();H.CP_DBG.off=false;H.CP_DBG.old=false;const X=H.XF,cv=[...document.querySelectorAll('canvas')].find(c=>c.getBoundingClientRect().width>0),R=cv.getBoundingClientRect();
  const m=([x,y])=>[R.left+(x*X.VZ-X.camD)/cv.width*R.width,R.top+(y*X.VZ-X.camDY)/cv.height*R.height];
  const faces=[];for(let c=q.c-1;c<=q.c+1;c++){if(c<0||c>=C)continue;const b=L.base[q.r*C+c],f=L.feat[q.r*C+c],h=b===2?64:f&&f.t==='low'?30:0;if(!h)continue;
    const x0=c*32-8+1,x1=c*32+24-1,y0=q.r*64+1,y1=q.r*64+h-1;faces.push([[x0,y0],[x1,y0],[x1,y1],[x0,y1]].map(m));}
  return {faces,mid:m([H.cpX?H.cpX(q):q.x,(q.r+1)*64-30]),th:H.themeName(n),x:H.cpX?H.cpX(q)-q.c*32:q.x-q.c*32};}'''


def page(b, mode):
    pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=2)
    pg.errs = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e)))
    pg.goto('file://' + SRC)
    pg.wait_for_timeout(700)
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.body.classList.remove('panelOpen')")
    pg.evaluate("m=>{__HK.S.set.lightMode=m;}", mode)
    pg.evaluate("()=>{__HK.GLFX.sheen=false;}")  # (the wet floor's reflection mirrors the lit clock onto the floor by design; never on a wall's face, but off for a clean comparison)
    return pg


def pixels(polys, w, h):  # the device pixels inside the polygons (css px, device scale 2)
    out = []
    for p in polys:
        xs = [x * 2 for x, y in p]; ys = [y * 2 for x, y in p]
        x0, y0, x1, y1 = max(0, int(min(xs)) + 1), max(0, int(min(ys)) + 1), min(w, int(max(xs))), min(h, int(max(ys)))
        out += [(x, y) for y in range(y0, y1) for x in range(x0, x1)]
    return out


if __name__ == '__main__':
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
        errs, worst, where = [], [], []
        floors = [(n, sd) for n in range(LO, HI + 1) for sd in SEEDS]
        lists, ncp, odd = {}, 0, 0
        pg = page(b, MODES[0])
        for n, sd in floors:
            lists[(n, sd)] = pg.evaluate(LIST, [n, sd]); ncp += len(lists[(n, sd)]); odd += sum(1 for e in lists[(n, sd)] if e[4] != 16)
        pg.close()
        cand = [(n, sd, e) for (n, sd), l in lists.items() for e in l if e[3]]
        print('floors %d-%d seeds %s: %d checkpoints, %d beside a wall face or low ceiling (%d with one on the left, %d on the right), %d off the cell middle%s' % (
            LO, HI, ','.join(map(str, SEEDS)), ncp, len(cand), sum(1 for c in cand if c[2][3] & 1), sum(1 for c in cand if c[2][3] & 2), odd, ' [old: v81 placement, no cut]' if OLD else ''))
        bad = {}
        for mode in MODES:
            pg = page(b, mode); bad[mode] = 0
            for n, sd, (i, c, r, side, dx) in cand:
                r1 = pg.evaluate(SHOW, [n, sd, i, False, OLD]); im1 = Image.open(io.BytesIO(pg.screenshot())).convert('RGB')
                pg.evaluate(SHOW, [n, sd, i, True, OLD]); im0 = Image.open(io.BytesIO(pg.screenshot())).convert('RGB')
                A, B0 = im1.load(), im0.load(); nb = 0
                for q in pixels(r1['faces'], im1.width, im1.height):
                    u, v = A[q], B0[q]
                    if abs(u[0] - v[0]) + abs(u[1] - v[1]) + abs(u[2] - v[2]) > 24: nb += 1
                if nb > 4:
                    bad[mode] += 1; where.append('%s %d/%d cp%d c%d r%d %s (%d px)' % (mode, n, sd, i, c, r, 'LR'[side - 1] if side < 3 else 'both', nb))
                    if len(worst) < 16:
                        cx, cy = int(r1['mid'][0] * 2), int(r1['mid'][1] * 2)
                        cr = im1.crop((cx - 120, cy - 100, cx + 120, cy + 100))
                        ImageDraw.Draw(cr).text((4, 3), '%s %d/%d c%d,%d %s (%d px)' % (mode, n, sd, c, r, r1['th'][:14], nb), fill=(255, 240, 160)); worst.append(cr)
            errs += pg.errs; pg.close()
            print('%-7s checkpoints drawn over a wall face: %d of %d' % (mode, bad[mode], len(cand)))
        if where:
            print('bad:', '; '.join(where[:24]))
        nbad = sum(bad.values())
        print('cpscan: %s (%d bad of %d checkpoints beside a face, %d checkpoints, floors %d-%d)' % ('ok' if nbad == 0 and not errs else 'FAIL', nbad, len(cand) * len(MODES), ncp, LO, HI), 'errors', errs[:3])
        if worst:
            sh = Image.new('RGB', (4 * 242, ((len(worst) + 3) // 4) * 202), (20, 16, 24))
            for k, c in enumerate(worst):
                sh.paste(c, ((k % 4) * 242, (k // 4) * 202))
            sh.save(OUT); print('wrote', OUT)
        b.close()
