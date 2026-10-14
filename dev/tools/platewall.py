from playwright.sync_api import sync_playwright
import json,sys
f=sys.argv[1] if len(sys.argv)>1 else '/Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); pg.goto('file://'+f); pg.wait_for_timeout(300)
    print(pg.evaluate(r'''()=>{const out={};let tot=0,lv=0;for(let n=1;n<=27;n++)for(let s=0;s<4;s++){const L=__HK.load(n,700000+n*97+s*13,true);lv++;
      for(const o of L.dyn){const t=o.f.t;if(!['plate','xplate','closer','loose','spikes'].includes(t))continue;const B=(c,r)=>L.base[r*L.cols+c];
        if(B(o.c+1,o.r)===2){out[t]=(out[t]||0)+1;if(!out.ex&&t==='plate'&&n===27)out.ex=[n,700000+n*97+s*13,o.c,o.r,!!o.f.where];tot++;}}}
      return JSON.stringify({levels:lv,tot,...out});}'''))
    b.close()
