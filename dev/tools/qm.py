from playwright.sync_api import sync_playwright
import json,sys
fs=sys.argv[1:]
with sync_playwright() as p:
    b=p.chromium.launch()
    res={}
    for f in fs:
        pg=b.new_page(); pg.goto('file://'+f); pg.wait_for_timeout(300)
        res[f]=pg.evaluate('''()=>{const H=__HK,MOV=new Set(['flat','up','down','drop2']);const o={};
          for(let n=6;n<=27;n++){let rt=0,tr=0,rv=0,lp=0;for(let s=0;s<20;s++){const L=H.genLevel(n,30000+s*101+n*7,true);
            tr+=L.segs.filter(q=>!q.k.startsWith('turn-')&&!q.k.startsWith('loop-')&&!MOV.has(q.k)).length;
            let route=0;for(const ri of L.runsInfo)route+=Math.abs(ri.c1-ri.c0);route+=Math.abs(L.door.c-L.runsInfo[L.runsInfo.length-1].c1);rt+=route;rv+=L.plan.turns.filter(t=>t.rev).length;lp+=(L.loops||[]).length;}
            o[n]=[+(rt/20).toFixed(1),+(tr/20).toFixed(1),+(rv/20).toFixed(2),+(lp/20).toFixed(2)];}return o;}''')
        pg.close()
    b.close()
for n in range(6,28):
    print(n,' | '.join(str(res[f][str(n)]) for f in fs))
