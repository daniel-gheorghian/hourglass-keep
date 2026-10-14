from playwright.sync_api import sync_playwright
import statistics as S,collections,sys
f=sys.argv[1]
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); pg.goto('file://'+f); pg.wait_for_timeout(300)
    r=pg.evaluate('''()=>{const H=__HK,o={};for(const n of [1,5,9,14,20,26]){const t=[],tb=[];for(let s=0;s<20;s++){const t0=performance.now();const L=H.load(n,12000+s*7,false);t.push(performance.now()-t0);const t1=performance.now();H.breaches();tb.push(performance.now()-t1);}o[n]=[t,tb];}return o;}''')
    for n,(t,tb) in r.items(): print(f.split('/')[-1][:12],'floor',n,'gen+load ms mean',round(S.mean(t),1),'max',round(max(t),1),'| breaches mean',round(S.mean(tb),1),'max',round(max(tb),1))
    b.close()
