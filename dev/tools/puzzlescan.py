# Plate-opens-gate puzzles: which (plate shape, gate place) pairs the generator makes, whether the bot solves every kind with
# no damage, and proof that the slab is needed in the slab shapes. Run from dev/tools:  python3 puzzlescan.py
#   plates: P1 branch (gallery/cellar), P2 slab over the plate, P3 slab jams the closers, P4 timed corridor plate (gate in the
#   next turn), P5 one-storey alcove plate; "double" is two branch plates.  gates: G1 on the corridor, G2 top of a kick shaft,
#   G3 foot of a banner slide, G4 between two moves of a turn.
import sys,json,collections
from playwright.sync_api import sync_playwright
LO,HI,SEEDS=4,27,20
PAIRS=['P1G1','P5G1','P2G1','P3G1','double','P4G2','P4G3','P4G4','P5G2','P5G3','P5G4','P1G2','P1G3','P1G4']
MIN_SEEN=5; BOT_FLOORS=3
SEED=lambda n,s:30000+s*101+n*7
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':844,'height':390}); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(300)
    pg.add_script_tag(path='bot.js')
    found=pg.evaluate('''([lo,hi,S])=>{const out=[];for(let n=lo;n<=hi;n++)for(let s=0;s<S;s++){const sd=30000+s*101+n*7;const L=__HK.genLevel(n,sd,true);for(const q of (L.puzzles||[]))out.push([n,sd,q.puz]);}return out;}''',[LO,HI,SEEDS])
    cnt=collections.Counter(x[2] for x in found); floors=collections.defaultdict(list)
    for n,sd,k in found:
        if (n,sd) not in floors[k]: floors[k].append((n,sd))
    print('pair counts over floors %d-%d x %d seeds (%d floors):'%(LO,HI,SEEDS,(HI-LO+1)*SEEDS))
    ok=True
    for k in PAIRS:
        print('  %-7s %4d puzzles on %4d floors'%(k,cnt[k],len(floors[k]))); 
        if cnt[k]<MIN_SEEN: print('    ** fewer than %d'%MIN_SEEN); ok=False
    extra=[k for k in cnt if k not in PAIRS]
    if extra: print('  unlisted pairs:',extra)
    tot=len(found); print('  puzzles per floor: %.2f'%(tot/((HI-LO+1)*SEEDS)))
    # the bot on at least BOT_FLOORS floors per pair (spread over the floor numbers), no fighting, no damage
    bad=[]
    for k in PAIRS:
        fl=floors[k]; pick=[fl[int(i*(len(fl)-1)/max(1,BOT_FLOORS-1))] for i in range(BOT_FLOORS)] if len(fl)>=BOT_FLOORS else fl
        res=[]
        for n,sd in pick:
            r=pg.evaluate('([n,s])=>runBot(n,s,{fight:false})',[n,sd]); res.append((n,sd,r.get('ok'),r.get('hurt'),r.get('why')))
            if r.get('ok') is not True or r.get('hurt'): bad.append((k,n,sd,r.get('ok'),r.get('hurt'),r.get('why')))
        print('  bot',k,res)
    print('bot failures or damage:',bad if bad else 'none')
    # the slab is the only way: stand on the plate and run for the gate (P2), or take the plate and run over the closers (P3)
    def proof(kind):
        fl=floors[kind]
        if not fl: return ('no floor',)
        n,sd=fl[0]
        info=pg.evaluate('''([n,sd,kind])=>{const L=__HK.genLevel(n,sd,true);
          // the slab plate/closer, found by its slab link; its gate; the walking direction from the plate to the gate
          const sp=L.dyn.filter(o=>o.f.slabF&&(o.f.t==='plate'||o.f.t==='closer'));
          for(const o of sp){const g=o.f.g;const go=L.dyn.find(q=>q.f===g);if(!go||go.r!==o.r)continue;
            const pl=kind==='P2G1'?o:L.dyn.find(q=>q.f.t==='plate'&&q.f.g===g&&q.r===o.r);if(!pl)continue;
            return {pc:pl.c,gc:go.c,r:o.r,dir:Math.sign(go.c-pl.c)};}
          return null;}''',[n,sd,kind])
        if not info: return ('no plate',)
        # (the stretch between the plate and the gate is first levelled and cleared of its obstacles, so only the gate can stop him)
        r=pg.evaluate('''([n,sd,I])=>{const t0={t:null};let openMax=0;
          const r=runBot(n,sd,{at:{c:I.pc,r:I.r,face:I.dir},path:[{a:'walk',c:I.gc+I.dir,dir:I.dir}],stop:H=>{const L=H.L;
            if(t0.t===null){t0.t=H.gameTime;const lo=Math.min(I.pc,I.gc)+1,hi=Math.max(I.pc,I.gc)-1;
              for(let c=lo;c<=hi;c++){L.base[I.r*L.cols+c]=1;L.base[(I.r-1)*L.cols+c]=0;const f=L.feat[I.r*L.cols+c];if(f&&f.t!=='closer'){L.feat[I.r*L.cols+c]=null;L.dyn=L.dyn.filter(o=>o.f!==f);}}}
            const g=L.dyn.find(o=>o.c===I.gc&&o.r===I.r&&o.f.t==='gate');if(g)openMax=Math.max(openMax,g.f.open*( (H.P.x-(I.gc*32+16))*I.dir>-40?1:0));
            return H.gameTime-t0.t>9;}});
          const H=__HK;const gx=I.gc*32+16;return {res:r.ok,x:Math.round(H.P.x),gx,passed:(H.P.x-gx)*I.dir>0,gateOpenWhenNear:+openMax.toFixed(2)};}''',[n,sd,info])
        return (n,sd,info,r)
    for kind in ('P2G1','P3G1'):
        print('proof, standing on the plate and running for the gate without the slab (%s):'%kind,proof(kind))
    print('errors',errs[:5]); b.close()
    sys.exit(0 if ok and not bad else 1)
