import random, math
def walk(n,R,total):
    occ={(0,0):'S'}; x=y=0; dirx=1; runs=[]; trans=[]; left=total-1; first=True
    while left>0:
        lo,hi=(6,12) if n<=2 else (4,10) if n<=6 else (3,9)
        for tryL in range(6):
            L=min(left,R.randint(lo,hi)); run=[]; cx=x; ok=True
            for i in range(L):
                cx+=dirx
                if (cx,y) in occ: ok=False; break
                run.append((cx,y))
            if ok: break
        if not ok: return None
        for c in run: occ[c]='>' if dirx>0 else '<'
        x=run[-1][0]; runs.append((len(run)+(1 if first else 0),dirx)); first=False; left-=L
        if left<=0: break
        for attempt in range(16):
            down=R.random()<0.6; k=1 if (n<=2 or R.random()<0.65) else 2; dy=k if down else -k
            rev=R.random()<(0.5 if n<=2 else 0.55)
            col=x if rev else x+dirx
            cells=([] if rev else [(col,y)])+[(col,y+s*(1 if down else -1)) for s in range(1,k+1)]
            if rev: cells=cells  # turning in the room the run ended in: only the rooms below/above are new
            if all(c not in occ for c in cells) and (n>2 or down):
                for c in cells: occ[c]='v' if down else '^'
                trans.append((dy,rev)); x,y=cells[-1]; dirx=-dirx if rev else dirx; left-=len(cells)
                break
        else: return None
    return occ,runs,trans
def plan(n,seed,K=40):
    roomsN=min(28+int((n-1)*2.2),72); PKW=1.52 if n<=5 else 1.46; total=math.ceil(roomsN*PKW)
    best=None
    for k in range(K):
        R=random.Random(seed*1009+k); w=walk(n,R,total)
        if not w: continue
        occ,runs,trans=w; xs=[c[0] for c in occ]; ys=[c[1] for c in occ]; W=max(xs)-min(xs)+1; H=max(ys)-min(ys)+1
        side=sum(1 for (cx,cy),v in occ.items() if v in '<>' and ((cx,cy-1) not in occ or (cx,cy+1) not in occ))
        aspect=(W*320)/(H*192)
        score=-abs(math.log(aspect/3.0))*3+min(side,60)*0.03-abs(sum(1 for t in trans if t[0]>0)/max(1,len(trans))-0.6)*4
        if best is None or score>best[0]: best=(score,W,H,occ,runs,trans,side,total)
    return best
def show(n,seed):
    score,W,H,occ,runs,trans,side,total=plan(n,seed)
    xs=[c[0] for c in occ]; ys=[c[1] for c in occ]
    dn=sum(1 for t in trans if t[0]>0); up=len(trans)-dn; sb=sum(1 for t in trans if t[1]); two=sum(1 for t in trans if abs(t[0])==2)
    print(f'floor {n}: {total} rooms of route -> map {W} x {H} rooms; runs {len(runs)} (longest {max(r[0] for r in runs)}); turns {len(trans)}: {dn} down / {up} up, {two} of them two storeys, {sb} switchbacks')
    for yy in range(min(ys),max(ys)+1):
        print('   '+''.join({'>':'→','<':'←','v':'↓','^':'↑','S':'S'}.get(occ.get((xx,yy)),'·') for xx in range(min(xs),max(xs)+1)))
    print()
for n,s in [(2,7),(9,3),(14,5),(26,11)]: show(n,s)
