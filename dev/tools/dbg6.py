from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(300)
    r=pg.evaluate('''()=>{const L=__HK.genLevel(14,701358,true);const r=9;const cells=[];for(let c=268;c<=282;c++){const b=[];for(let rr=r-2;rr<=r+1;rr++){const f=L.feat[rr*L.cols+c];b.push(L.base[rr*L.cols+c]+(f?f.t[0]:''));}cells.push(c+':'+b.join(','));}
      const i=L.path.findIndex(a=>a.a==='walk'&&a.c===276);return {cells,path:L.path.slice(i-1,i+3),snakes:L.snakeSpecs.filter(s=>s.r===9)};}''')
    print(json.dumps(r,indent=0)); b.close()
