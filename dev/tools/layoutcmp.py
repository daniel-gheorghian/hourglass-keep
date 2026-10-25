# layoutcmp.py [baseline.html] [lo hi] [seeds] [file=other.html]: layouts identical (round 38a; rounds since 16a checked this by hand). For floors
# lo..hi (default 1-48) and seeds (default 1,2,3), genLevel(n, seed, true) in the baseline (default dev/tools/hk_v82_release.html) and in the
# source (dev/hourglass-keep.html, or file=) must give the same tiles (L.base), features (L.feat: every plain field, nested objects one level
# down), bot path (L.path), start, exit (L.door), lights (L.torches), windows, checkpoints, items, guards, snakes and lifts. Prints
# 'layoutcmp: same' or the first differences (floor, seed, what, the first index that differs and both values). Run from dev/tools.
import os, sys
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
BASE = os.path.abspath(next((x for x in a if x.endswith('.html') and '=' not in x), os.path.join(HERE, 'hk_v82_release.html')))
SRC = os.path.abspath(next((x[5:] for x in a if x.startswith('file=')), os.path.join(HERE, '..', 'hourglass-keep.html')))
NUM = [int(x) for x in a if x.isdigit()]
LO, HI = (NUM + [1, 48])[:2] if len(NUM) >= 2 else (1, 48)
SEEDS = [int(s) for s in next((x for x in a if ',' in x and '=' not in x), str(NUM[2]) if len(NUM) > 2 else '1,2,3').split(',')]
# each part of the floor as a list of strings, one an element (plain values only; objects one level down; no functions; cycles cut)
DUMP = r'''([n,sd])=>{const H=__HK,L=H.genLevel(n,sd,true);
  const v=(x,d)=>{if(x===null||x===undefined)return String(x);const t=typeof x;if(t==='function')return 'fn';if(t!=='object')return t==='number'?String(Math.round(x*1000)/1000):String(x);
    if(d<=0)return Array.isArray(x)?'['+x.length+']':'{}';if(x instanceof Set)return 'Set('+[...x].sort().join(',')+')';
    if(Array.isArray(x)||ArrayBuffer.isView(x))return '['+Array.from(x,y=>v(y,d-1)).join(',')+']';
    return '{'+Object.keys(x).sort().map(k=>k+':'+v(x[k],d-1)).join(',')+'}';};
  const ls=(a,d)=>a?Array.from(a,x=>v(x,d)):['none'];
  return {base:[Array.from(L.base).join('')],feat:Array.from(L.feat,f=>f?v(f,2):''),path:ls(L.path,2),start:[v(L.start,2)],exit:[v(L.door,2)],lights:ls(L.torches,2),
    windows:ls(L.windows,2),cps:ls(L.cps,2),items:ls(L.items,2),guards:ls(L.guards,2),snakes:ls(L.snakeSpecs,2),lifts:ls(L.lifts,1),dyn:ls(L.dyn,1),rows:[L.rows+'x'+L.cols]};}'''


def page(b, src):
    pg = b.new_page(viewport={'width': 852, 'height': 393})
    pg.errs = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e)))
    pg.goto('file://' + src); pg.wait_for_timeout(600)
    return pg


if __name__ == '__main__':
    with sync_playwright() as p:
        b = p.chromium.launch()
        pa, pb = page(b, BASE), page(b, SRC)
        diffs, n_ok = [], 0
        for n in range(LO, HI + 1):
            for sd in SEEDS:
                A, Bv = pa.evaluate(DUMP, [n, sd]), pb.evaluate(DUMP, [n, sd])
                same = True
                for k in A:
                    x, y = A[k], Bv.get(k)
                    if x == y: continue
                    same = False
                    i = next((i for i in range(min(len(x), len(y))) if x[i] != y[i]), min(len(x), len(y)))
                    xa, ya = (x[i] if i < len(x) else '(end)'), (y[i] if i < len(y) else '(end)')
                    if k == 'base':
                        j = next((j for j in range(min(len(xa), len(ya))) if xa[j] != ya[j]), 0); xa, ya = 'cell %d: %s' % (j, xa[j:j + 12]), ya[j:j + 12]
                    diffs.append('floor %d seed %d %s: %d vs %d entries, first at %d: %s | %s' % (n, sd, k, len(x), len(y), i, xa[:160], ya[:160]))
                n_ok += same
        errs = pa.errs + pb.errs
        if diffs:
            print('\n'.join(diffs[:20]))
        print('layoutcmp: %s (%d of %d floors identical; floors %d-%d seeds %s; %s against %s)' % ('same' if not diffs and not errs else 'DIFFERENT', n_ok, (HI - LO + 1) * len(SEEDS), LO, HI, ','.join(map(str, SEEDS)), os.path.basename(SRC), os.path.basename(BASE)), 'errors', errs[:3])
        b.close()
