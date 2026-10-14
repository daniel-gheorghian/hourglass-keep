import random, math
RUN='<>S'
def free_run(occ,c):  # a run room: empty, and no run directly above or below (that band is kept for side passages)
    x,y=c
    return c not in occ and occ.get((x,y-1),'.') not in RUN and occ.get((x,y+1),'.') not in RUN
def walk(n,R,total):
    occ={(0,0):'S'}; x=y=0; dirx=1; runs=[]; trans=[]; left=total-1; first=True; revs=0
    maxrev=1 if n<=2 else 99
    while left>0:
        lo,hi=(8,14) if n<=2 else (4,10) if n<=6 else (3,9)
        L=min(left,R.randint(lo,hi)); run=[]; cx=x
        for i in range(L):
            cx+=dirx
            if not free_run(occ,(cx,y)): break
            run.append((cx,y))
        if len(run)<min(2,left): return None
        for c in run: occ[c]='>' if dirx>0 else '<'
        x=run[-1][0]; runs.append((len(run)+(1 if first else 0),dirx)); first=False; left-=len(run)
        if left<=0: break
        opts=[]
        for down in (True,False):
            for k in (1,2):
                for rev in (True,False):
                    if n<=2 and (not down or k>1 or (rev and revs>=maxrev)): continue
                    col=x if rev else x+dirx
                    cells=([] if rev else [(col,y)])+[(col,y+s*(1 if down else -1)) for s in range(1,k+1)]
                    land=cells[-1]
                    if all(c not in occ for c in cells) and free_run(occ,land):
                        w=(0.6 if down else 0.4)*(0.65 if k==1 else 0.35)*(0.55 if rev else 0.45)
                        opts.append((w,down,k,rev,cells))
        if not opts: return None
        t=R.random()*sum(o[0] for o in opts)
        for o in opts:
            t-=o[0]
            if t<=0: break
        w,down,k,rev,cells=o
        for c in cells: occ[c]='v' if down else '^'
        occ[cells[-1]]=('>' if (dirx>0)!=rev else '<')  # the landing room starts the next run
        trans.append((k if down else -k,rev)); revs+=rev; x,y=cells[-1]; dirx=-dirx if rev else dirx; left-=len(cells)
    return occ,runs,trans
def plan(n,seed,K=60):
    roomsN=min(28+int((n-1)*2.2),72); PKW=1.52 if n<=5 else 1.46; total=math.ceil(roomsN*PKW)
    best=None;fails=0
    for k in range(K):
        R=random.Random(seed*1009+k); w=walk(n,R,total)
        if not w: fails+=1; continue
        occ,runs,trans=w; xs=[c[0] for c in occ]; ys=[c[1] for c in occ]; W=max(xs)-min(xs)+1; H=max(ys)-min(ys)+1
        aspect=(W*320)/(H*192); dn=sum(1 for t in trans if t[0]>0)/max(1,len(trans))
        score=-abs(math.log(aspect/3.0))*3-abs(dn-0.6)*4
        if best is None or score>best[0]: best=(score,W,H,occ,runs,trans,total)
    return best,fails
def show(n,seed):
    (score,W,H,occ,runs,trans,total),fails=plan(n,seed)
    xs=[c[0] for c in occ]; ys=[c[1] for c in occ]
    dn=sum(1 for t in trans if t[0]>0); up=len(trans)-dn; sb=sum(1 for t in trans if t[1]); two=sum(1 for t in trans if abs(t[0])==2)
    print(f'floor {n}: {total} rooms of route -> {W} x {H} rooms; {len(runs)} runs (longest {max(r[0] for r in runs)}); {len(trans)} turns: {dn} down / {up} up, {two} two-storey, {sb} switchbacks  [{fails}/60 walks failed]')
    for yy in range(min(ys),max(ys)+1):
        print('   '+''.join({'>':'→','<':'←','v':'↓','^':'↑','S':'S'}.get(occ.get((xx,yy)),'·') for xx in range(min(xs),max(xs)+1)))
    print()
import sys
for n,s in [(2,7),(9,3),(14,5),(26,11)]: show(n,s)
