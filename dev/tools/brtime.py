from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(400)
    print(pg.evaluate('''()=>{const H=__HK,o={};for(const n of [3,7,11,15,19,23,27]){let t=0,c=0;for(let s=0;s<4;s++){const L=H.load(n,1000+s,true);L.breaches=null;const t0=performance.now();c+=H.breaches().filter(Boolean).length;t+=performance.now()-t0;}o[n]=[+(t/4).toFixed(1),c/4];}return o;}'''))
    b.close()
