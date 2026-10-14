from playwright.sync_api import sync_playwright
import sys,collections
for f in sys.argv[1:]:
  with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); pg.goto('file://'+f); pg.wait_for_timeout(300)
    r=pg.evaluate('''()=>{const H=__HK,o={};for(const n of [4,5,6,7,8,11,15]){const a=[];for(let s=0;s<20;s++){const L=H.genLevel(n,9000+s*37,true);a.push((L.detours||[]).length+(L.secret?1:0));}o[n]=a;}return o;}''')
    print(f.split('/')[-1][:16],{k:(sum(v)/len(v),dict(collections.Counter(v))) for k,v in r.items()}); b.close()
