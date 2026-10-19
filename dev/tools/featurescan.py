# featurescan.py [file [seeds [lo hi]]]: the floors' featured choices (unit F, "oatmeal spice").
# Per floor band: how often each featured family is drawn, how much of its category it really holds on the floor (mean, min over
# floors with enough material), the rare flags' frequency, the trap count, and a sameness number: the mean pairwise distance
# between floors' mix vectors (move mix + puzzle mix + obstacle mix; higher = floors differ more). "dom" is the share of the most
# common family of the category on a floor, which also works on a source that has no featured families (the commit before F).
# To compare: python3 featurescan.py /path/to/older.html   and   python3 featurescan.py
from playwright.sync_api import sync_playwright
import json,sys,itertools,statistics as S
f=sys.argv[1] if len(sys.argv)>1 and sys.argv[1] else '/Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'
ns=int(sys.argv[2]) if len(sys.argv)>2 else 20
lo,hi=(int(sys.argv[3]),int(sys.argv[4])) if len(sys.argv)>4 else (3,27)
JS=r'''([lo,hi,ns])=>{
  const MF={plain:['down','drop2','up'],collapse:['collapse'],jumps:['jumpdown','jumpup'],banners:['banner3','banner4','sand3','sand4','shaft2','shaft3'],lifts:['lift2d','lift3d','lift2u','lift3u','chn2d','chn3d','chn2u','chn3u']};
  const PF=n=>n.startsWith('P2')||n.startsWith('P3')?'slab':n.startsWith('P1')?'side':n.startsWith('P5')?'alcove':n.startsWith('P4')?'timed':n==='double'?'double':'other';
  const OBS=['spikes','loose','chomp','saw','tunnel'];
  const MOV=new Set(['flat','up','down','drop2']);const isTrap=q=>!MOV.has(q.k)&&!/^(turn-|loop-|fork-)/.test(q.k)&&q.k!=='guard'&&q.k!=='skel';
  const out=[];
  for(let n=lo;n<=hi;n++)for(let s=0;s<ns;s++){const seed=800000+n*131+s*17,L=__HK.genLevel(n,seed,true);
    const mv={},pz={},ob={},rm=L.runMv||{};
    for(const q of L.segs){if(q.k.startsWith('turn-')){const m=q.k.slice(5);if(m==='gslot'||m==='hgap')continue;mv[m]=(mv[m]||0)+1;}
      const k=q.k.replace(/^fork-/,'');if(OBS.includes(k))ob[k]=(ob[k]||0)+1;}
    for(const p of L.puzzles){const k=PF(p.puz);pz[k]=(pz[k]||0)+1;}
    const route=(()=>{let r=0;for(const ri of L.runsInfo)r+=Math.abs(ri.c1-ri.c0);const lr=L.runsInfo[L.runsInfo.length-1];return r+Math.abs(L.door.c-lr.c1);})();
    out.push({n,s,feat:L.feature||null,mv,rm,pz,ob,traps:L.segs.filter(isTrap).length,guards:L.guards.length,snakes:L.snakeSpecs.length,route,forks:L.forks.length});}
  return {out,MF};}'''
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e))); pg.goto('file://'+f); pg.wait_for_timeout(300)
    R=pg.evaluate(JS,[lo,hi,ns]); b.close()
if errs: print('page errors',errs[:3])
MF=R['MF']; fl=R['out']
fam_of={m:k for k,v in MF.items() for m in v}
def mvfam(mv):
    t={}
    for m,c in mv.items(): t[fam_of.get(m,'other')]=t.get(fam_of.get(m,'other'),0)+c
    return t
DOWNM={'down','drop2','banner3','banner4','sand3','sand4','collapse','jumpdown','lift2d','lift3d','chn2d','chn3d'}
OBSF=['spikes','loose','chomp','saw','tunnel']
def vec(x):
    keys=['plain','collapse','jumps','banners','lifts','other']
    a=mvfam(x['mv']); ta=sum(a.values()) or 1
    pz=x['pz']; tp=sum(pz.values()) or 1
    ob=x['ob']; to=sum(ob.values()) or 1
    return [a.get(k,0)/ta for k in keys]+[pz.get(k,0)/tp for k in ['slab','side','alcove','timed','double','other']]+[ob.get(k,0)/to for k in OBSF]
def band(n): return '3-5' if n<=5 else '6-11' if n<=11 else '12-19' if n<=19 else '20-27'
bands={}
for x in fl: bands.setdefault(band(x['n']),[]).append(x)
def dom(d): t=sum(d.values()); return max(d.values())/t if t else None
def sameness(xs):
    v=[vec(x) for x in xs]; tot=0;k=0
    for i in range(len(v)):
        for j in range(i+1,len(v)):
            tot+=sum(abs(a-b) for a,b in zip(v[i],v[j]))/3;k+=1
    return tot/max(1,k)
print('file',f.split('/')[-1],' floors',len(fl))
print('band   floors  traps  guards snakes  route  forks | dom(move) dom(puz) dom(obs) | featured share: move mean/min  puzzle mean/min  obstacle mean/min | flags | sameness')
for bn in ['3-5','6-11','12-19','20-27']:
    xs=bands.get(bn,[]); 
    if not xs: continue
    dm=[dom(mvfam(x['mv'])) for x in xs]; dm=[d for d in dm if d is not None]
    dp=[dom(x['pz']) for x in xs]; dp=[d for d in dp if d is not None]
    do=[dom(x['ob']) for x in xs]; do=[d for d in do if d is not None]
    sh={'move':[],'puzzle':[],'obstacle':[]}
    for x in xs:
        ft=x['feat']
        if not ft: continue
        if ft['move']:
            # (turn moves plus the steps of the runs; dom and sameness use the turns' moves only, which the older source has too)
            # the category is the moves going the way(s) the family has members for (a collapse has no upward twin)
            dirs={d for m in MF[ft['move']] for d in (['d'] if m in DOWNM else ['u'])}
            allmv=dict(x['mv'])
            for m,c in x['rm'].items(): allmv[m]=allmv.get(m,0)+c
            cat={m:c for m,c in allmv.items() if ('d' if m in DOWNM else 'u') in dirs}
            t=sum(cat.values()); fm=sum(c for m,c in cat.items() if m in MF[ft['move']])
            if t>=3: sh['move'].append(fm/t)
        if ft['puzzle']:
            t=sum(x['pz'].values())
            if t>=2: sh['puzzle'].append(x['pz'].get(ft['puzzle'],0)/t)
        if ft['obstacle']:
            t=sum(x['ob'].values())
            if t>=4: sh['obstacle'].append(x['ob'].get(ft['obstacle'],0)/t)
    def ms(v): return '%.2f/%.2f(n=%d)'%(S.mean(v),min(v),len(v)) if v else '-'
    nf=sum(1 for x in xs if x['feat'] and x['feat']['flag'])
    print('%-6s %5d %6.1f %6.1f %6.1f %6.1f %5.2f | %.2f %.2f %.2f | %s %s %s | %.3f | %.3f'%(bn,len(xs),S.mean(x['traps'] for x in xs),S.mean(x['guards'] for x in xs),S.mean(x['snakes'] for x in xs),S.mean(x['route'] for x in xs),S.mean(x['forks'] for x in xs),
        S.mean(dm),S.mean(dp) if dp else 0,S.mean(do) if do else 0,ms(sh['move']),ms(sh['puzzle']),ms(sh['obstacle']),nf/len(xs),sameness(xs)))
# featured-family frequency and flags
if fl[0]['feat']:
    for k in ['move','puzzle','obstacle','flag']:
        c={}
        for x in fl:
            v=x['feat'][k]; c[v]=c.get(v,0)+1
        print(k,dict(sorted(c.items(),key=lambda a:str(a[0]))))
    # per flag: measured share on the floors that carry it
    for flg in ['tower','rotten','barracks','longway','maze']:
        xs=[x for x in fl if x['feat']['flag']==flg]
        if xs: print('flag',flg,len(xs),'traps %.1f guards %.1f forks %.2f'%(S.mean(x['traps'] for x in xs),S.mean(x['guards'] for x in xs),S.mean(x['forks'] for x in xs)),
            'puzzles %.1f'%S.mean(sum(x['pz'].values()) for x in xs),'lift-share %.2f'%S.mean((mvfam(x['mv']).get('lifts',0))/max(1,sum(mvfam(x['mv']).values())) for x in xs),
            'collapse-share %.2f'%S.mean((mvfam(x['mv']).get('collapse',0))/max(1,sum(mvfam(x['mv']).values())) for x in xs))
json.dump(fl,open('featurescan_out.json','w'))
