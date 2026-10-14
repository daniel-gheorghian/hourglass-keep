from playwright.sync_api import sync_playwright
import json,sys
n,seed=int(sys.argv[1]),int(sys.argv[2])
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(300)
    print(pg.evaluate('''([n,seed])=>{const H=__HK,L=H.genLevel(n,seed,true);const ch=L.ext.chase;return {chase:ch&&{c0:ch.c0,c1:ch.c1,rTop:ch.rTop,rBot:ch.rBot},runs:L.runsInfo,path:L.path.slice(110,135).map(a=>a.a+'@'+(a.from??a.c)+(a.dir<0?'<':'')+' ')};}''',[n,seed]))
    b.close()
