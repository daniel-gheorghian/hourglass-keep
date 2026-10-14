from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(300)
    r=pg.evaluate('''()=>{const H=__HK,o=[];for(let s=0;s<12;s++){const L=H.genLevel(14,5000+s*31,true);let route=0;const rr=[];
      L.runsInfo.forEach((ri,i)=>{const len=Math.abs(ri.c1-ri.c0);route+=len;rr.push(len+'/'+L.plan.runs[i].cap);});
      o.push({s,route,routeT:L.routeT,budget:Math.ceil(L.routeT*1.09),rr:rr.join(' ')});}return o;}''')
    for x in r: print(x)
    b.close()
