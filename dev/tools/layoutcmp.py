# layoutcmp.py [baseline.html] [lo hi] [seeds] [file=other.html] [notimers]: layouts identical (round 38a; round 38b's layoutcmp_play.py
# merged in, round 38c). For floors lo..hi (default 1-48) and seeds (default 1,2,3; one number n means 1..n), genLevel(n, seed, true) in
# the baseline (default: the newest hk_vNN_release.html in dev/tools) and in the source (dev/hourglass-keep.html, or file=) must give the
# same tiles (L.base), features (L.feat, every field at any depth; a shared object is named by its first place), bot path (L.path), start,
# exit (L.door), lights (L.torches), windows, checkpoints, items, guards, snakes, lifts, the dynamic list (L.dyn), forks and hurtdrops.
# 'notimers' leaves the gates' timer durations (dur, est) out, for a round that only resizes timers. 'liftrest' (round 50e: a counterweight
# lift rests at the end the route leaves by) leaves out where a counterweight lift's platform rests (its y, gT, gB, cv, sm) and its top cell
# in L.base (FLOOR only while the platform rests there). Prints 'layoutcmp: same' or the
# first differences (floor, seed, part, the first entry that differs and both values). A round that changes the generator on purpose
# differs, so this is run by hand for look-only rounds, not in suite.py. Run from dev/tools.
import os, re, sys
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
def newest():
    rel = [(int(m[1]), f) for f in os.listdir(HERE) for m in [re.match(r'hk_v(\d+)_release\.html$', f)] if m]
    return os.path.join(HERE, max(rel)[1]) if rel else None
BASE = next((x for x in a if x.endswith('.html') and '=' not in x), None) or newest()
if not BASE: sys.exit('layoutcmp: no baseline (no hk_vNN_release.html in dev/tools; pass one)')
BASE = os.path.abspath(BASE)
SRC = os.path.abspath(next((x[5:] for x in a if x.startswith('file=')), os.path.join(HERE, '..', 'hourglass-keep.html')))
NOTIMERS = 'notimers' in a
LIFTREST = 'liftrest' in a
NUM = [int(x) for x in a if x.isdigit()]
LO, HI = (NUM[0], NUM[1]) if len(NUM) >= 2 else (1, 48)
SL = next((x for x in a if ',' in x and '=' not in x), None)
SEEDS = [int(s) for s in SL.split(',')] if SL else list(range(1, NUM[2] + 1)) if len(NUM) > 2 else [1, 2, 3]
# each part as a list of strings, one an element; one walk a part, so an object met again (a plate's gate, a lift's feature) is
# '#k', its first place in that part; numbers to 1/1000; functions 'fn'
DUMP = r'''([n,sd,notimers,lr])=>{delete window.__FEAT;delete window.__PZ;const L=__HK.genLevel(n,sd,true);
  const part=a=>{if(!a)return ['none'];const seen=new Map();let k=0;
    const v=x=>{if(x===null||x===undefined)return String(x);const t=typeof x;if(t==='function')return 'fn';
      if(t!=='object')return t==='number'?String(Math.round(x*1000)/1000):JSON.stringify(x);
      if(seen.has(x))return '#'+seen.get(x);seen.set(x,k++);
      if(x instanceof Set)return 'Set('+[...x].map(v).sort().join(',')+')';
      if(x instanceof Map)return 'Map('+[...x].map(([p,q])=>v(p)+'>'+v(q)).join(',')+')';
      if(Array.isArray(x)||ArrayBuffer.isView(x))return '['+Array.from(x,v).join(',')+']';
      return '{'+Object.keys(x).sort().filter(q=>!(notimers&&x.t==='gate'&&(q==='dur'||q==='est'))&&!(lr&&x.t==='lift'&&!x.sand&&['y','gT','gB','cv','sm'].includes(q))).map(q=>q+':'+v(x[q])).join(',')+'}';};
    return Array.from(a,v);};
  const bs=Array.from(L.base);if(lr)for(const f of L.lifts)if(f.t==='lift'&&!f.sand)bs[f.rT*L.cols+f.sc]='L';
  return {base:[bs.join('')],rows:[L.rows+'x'+L.cols],feat:part(L.feat),path:part(L.path),start:part([L.start]),exit:part([L.door]),
    lights:part(L.torches),windows:part(L.windows),cps:part(L.cps),items:part(L.items),guards:part(L.guards),snakes:part(L.snakeSpecs),
    lifts:part(L.lifts),dyn:part(L.dyn),forks:part(L.forks),hurtdrops:part(L.hurtdrops)};}'''


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
                A, Bv = pa.evaluate(DUMP, [n, sd, NOTIMERS, LIFTREST]), pb.evaluate(DUMP, [n, sd, NOTIMERS, LIFTREST])
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
        ok = not diffs and not errs
        print('layoutcmp: %s (%d of %d floors identical; floors %d-%d seeds %s%s; %s against %s)' % ('same' if ok else 'DIFFERENT', n_ok, (HI - LO + 1) * len(SEEDS), LO, HI, ','.join(map(str, SEEDS)), ', gate timers left out' if NOTIMERS else '', os.path.basename(SRC), os.path.basename(BASE)), 'errors', errs[:3])
        b.close()
        sys.exit(0 if ok else 1)
