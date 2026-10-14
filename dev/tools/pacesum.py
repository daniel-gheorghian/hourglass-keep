import json,sys
from playwright.sync_api import sync_playwright
JS=r'''([ns,seeds])=>{const H=__HK,MOVE=new Set(['flat','up','down','drop2']);let out={};
 for(const n of ns){let haz=0,cols=0,g=0,cp=0,fl=0;for(let s=0;s<seeds;s++){const L=H.load(n,1000+n*97+s*7919,true);cols+=L.cols;g+=L.guards.length;cp+=L.cps.length;fl+=L.items.length;for(const q of L.segs)if(!MOVE.has(q.k))haz++;}
  out[n]=[+(haz/seeds).toFixed(1),Math.round(cols/seeds),+(g/seeds).toFixed(1),+(cp/seeds).toFixed(1),+(fl/seeds).toFixed(1)];}return out;}'''
ns=list(range(1,31)); seeds=int(sys.argv[2])
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(300)
    print(json.dumps(pg.evaluate(JS,[ns,seeds])))
    b.close()
