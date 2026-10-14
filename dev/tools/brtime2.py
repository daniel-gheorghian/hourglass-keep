from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(400)
    print(pg.evaluate('''()=>{const H=__HK,o={};for(const n of [19]){let t=0,t2=0;for(let s=0;s<4;s++){const L=H.load(n,1000+s,true);let t0=performance.now();for(let r=0;r<L.rows;r++)for(let c=0;c<L.cols;c++)H.wearLevel(c*32+16,r*64+20);t+=performance.now()-t0;}o[n]=[t/4];}return o;}'''))
    b.close()
