# prototype of a room-scale route planner: runs along room bands, joined by 1-2 band drops/climbs,
# switchbacks allowed, grows in any direction, best of K candidates by critics
import random, sys, math
def plan(n, seed, K=12):
    d=min(1,(n-1)/24); roomsN=min(28+int((n-1)*2.2),72); PKW=1.52 if n<=5 else 1.46
    total=math.ceil(roomsN*PKW)          # horizontal path length in rooms, as today
    best=None
    for k in range(K):
        R=random.Random(seed*101+k)
        occ={}; path=[]; x=y=0; dirx=1; runs=[]; trans=[]; left=total
        occ[(0,0)]='S'; first=True
        ok=True
        while left>0:
            L=min(left, R.randint(*( (6,12) if n<=2 else (4,10) if n<=6 else (3,9))))
            # lay the run
            cells=[]
            for i in range(1 if first else 0, L+ (0 if first else 0)):
                pass
            cx=x; run=[]
            for i in range(L):
                cx+=dirx if not (first and i==0) else 0
                if first and i==0: run.append((cx,y)); continue
                if (cx,y) in occ: ok=False; break
                run.append((cx,y)); occ[(cx,y)]='>' if dirx>0 else '<'
            if not ok: break
            first=False; x=run[-1][0]; runs.append((run[0],run[-1],dirx)); left-=L
            if left<=0: break
            # a turn: down 60%, up 40%; one or two bands; then switch back (55%) or carry on
            for attempt in range(12):
                dy=(1 if R.random()<0.6 else -1)*(1 if R.random()<0.65 else 2)
                if n<=2: dy=abs(dy)//abs(dy)*1
                rev=R.random()<(0.55 if n>2 else 0.5)
                col=x if rev else x+dirx           # a switchback turns in the last room; carrying on moves one room ahead
                cells=[(col,y+s*(1 if dy>0 else -1)) for s in range(1,abs(dy)+1)]
                if not rev: cells=[(col,y)]+cells
                if all(c not in occ for c in cells):
                    for c in cells: occ[c]='v' if dy>0 else '^'
                    trans.append((dy,rev)); x,y=cells[-1]; dirx=-dirx if rev else dirx
                    # the room where the next run starts is the landing cell itself
                    occ[(x,y)]='v' if dy>0 else '^'; left-=1
                    break
            else: ok=False; break
        if not ok: continue
        xs=[c[0] for c in occ]; ys=[c[1] for c in occ]; W=max(xs)-min(xs)+1; H=max(ys)-min(ys)+1
        # free neighbours above/below run cells: room for side passages (gate plates, gold flask)
        side=sum(1 for (cx,cy),v in occ.items() if v in '<>' and ((cx,cy-1) not in occ or (cx,cy+1) not in occ))
        aspect=(W*320)/(H*192)
        score=-abs(math.log(aspect/3.2))*3 - max(0,max(r[1][0]-r[0][0] for r in runs)/1-10)*0.5 + min(side,40)*0.05
        cand=(score,W,H,occ,runs,trans,side)
        if best is None or score>best[0]: best=cand
    return best,total
def show(n,seed):
    b,total=plan(n,seed)
    score,W,H,occ,runs,trans,side=b
    xs=[c[0] for c in occ]; ys=[c[1] for c in occ]
    print(f'floor {n}: path {total} rooms -> map {W}x{H} rooms ({W*10}x{H*3} tiles), runs {len(runs)}, turns {len(trans)} (down {sum(1 for t in trans if t[0]>0)}, up {sum(1 for t in trans if t[0]<0)}, switchbacks {sum(1 for t in trans if t[1])}), free side slots {side}')
    for yy in range(min(ys),max(ys)+1):
        print('   '+''.join({'>':'→','<':'←','v':'↓','^':'↑','S':'S'}.get(occ.get((xx,yy)),'·') for xx in range(min(xs),max(xs)+1)))
for n,s in [(2,7),(9,3),(14,5),(26,11)]:
    show(n,s)
