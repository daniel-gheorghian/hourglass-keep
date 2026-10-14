from playwright.sync_api import sync_playwright
import os
with sync_playwright() as p:
    b=p.chromium.launch()
    for f in ('v30_hooks.html','/Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'):
        pg=b.new_page(); pg.goto('file://'+os.path.abspath(f)); pg.wait_for_timeout(300)
        print(f.split('/')[-1],pg.evaluate('''()=>{const H=__HK,o={};for(const n of [5,15,25,30]){const t=performance.now();for(let i=0;i<5;i++)H.genLevel(n,1234+i,false);o[n]=+((performance.now()-t)/5).toFixed(1);}return o;}'''))
        pg.close()
    b.close()
