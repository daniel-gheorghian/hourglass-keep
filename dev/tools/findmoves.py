from playwright.sync_api import sync_playwright
import json,sys
f=sys.argv[1] if len(sys.argv)>1 else '/home/claude/hourglass-keep.html'
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); pg.goto('file://'+f); pg.wait_for_timeout(300)
    print(pg.evaluate(r'''()=>{const o={walljump:[],slide:[]};for(let n=1;n<=27;n++)for(let s=0;s<6;s++){const seed=700000+n*97+s*13;const L=__HK.load(n,seed,true);
      for(const a of L.path){if(a.a==='walljump')o.walljump.push([n,seed,a.k,a.dir||1]);if(a.a==='slide')o.slide.push([n,seed,a.dir||1]);}}
      return JSON.stringify({wj:o.walljump.length,sl:o.slide.length,wjx:o.walljump.slice(0,12),slx:o.slide.slice(0,12)});}'''))
    b.close()
