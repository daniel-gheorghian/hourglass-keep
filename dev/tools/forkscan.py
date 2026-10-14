# forkscan.py [file lo hi seeds]: how many floors carry a fork, and of which kind, by floor band; the damaging shortcuts' saving.
# (The fork kinds: 1 guard against traps, 2 damaging descent, 3 short dense way against a long easy one, 4 one-way hole, g = 4 with a grating.)
from playwright.sync_api import sync_playwright
import json,sys
f=sys.argv[1] if len(sys.argv)>1 else '/Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'
lo,hi,ns=(int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4])) if len(sys.argv)>4 else (6,27,10)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e))); pg.goto('file://'+f); pg.wait_for_timeout(300)
    print(pg.evaluate(r'''([lo,hi,ns])=>{const band=n=>n<=9?'6-9':n<=17?'10-17':'18-27',out={};let atts={},tot=0;
      for(let n=lo;n<=hi;n++)for(let s=0;s<ns;s++){const L=__HK.genLevel(n,700000+n*97+s*13,true);tot++;atts[L.att]=(atts[L.att]||0)+1;const b=band(n),o=out[b]=out[b]||{floors:0,forks:0,k:{}};o.floors++;
        for(const q of L.forks){o.forks++;const key=q.grate?'g':q.v;o.k[key]=(o.k[key]||0)+1;}}
      return JSON.stringify({tot,atts,out},null,1);}''',[lo,hi,ns]))
    print(errs[:3]); b.close()
