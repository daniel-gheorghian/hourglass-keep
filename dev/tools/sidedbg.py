from playwright.sync_api import sync_playwright
import sys
for f in sys.argv[1:]:
  with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); pg.goto('file://'+f); pg.wait_for_timeout(300)
    r=pg.evaluate('''()=>{const H=__HK,o={};for(const n of [6,11,17,18,24,25,27]){let sec=0,det=0,dbl=0;for(let s=0;s<20;s++){const L=H.genLevel(n,30000+s*101+n*7,true);sec+=L.secret?1:0;for(const d of L.detours||[]){if(d.double)dbl++;else if(!d.secret)det++;}}o[n]={sec:sec/20,det:det/20,dbl:dbl/20};}return o;}''')
    print(f.split('/')[-1][:12],r); b.close()
