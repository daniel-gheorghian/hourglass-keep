from playwright.sync_api import sync_playwright
import json,sys
f=sys.argv[1] if len(sys.argv)>1 else '/home/claude/hourglass-keep.html'
lo,hi,ns=(int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4])) if len(sys.argv)>4 else (1,27,4)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e))); pg.goto('file://'+f); pg.wait_for_timeout(300)
    print(pg.evaluate(r'''([lo,hi,ns])=>{const rows=[];let tot=0,withL=0,nl=0,atts={};const t0=performance.now();
      for(let n=lo;n<=hi;n++)for(let s=0;s<ns;s++){const seed=700000+n*97+s*13;const L=__HK.load(n,seed,true);tot++;atts[L.att]=(atts[L.att]||0)+1;
        const k=(L.loops||[]).length;if(k){withL++;nl+=k;}
        if(n>=6&&s<2)rows.push(n+':'+k+(L.loops||[]).map(q=>' [H'+q.H+' r'+q.rUp+'->'+q.rLow+' gate'+q.gate.c+' plate'+q.plate.c+']').join(''));}
      return JSON.stringify({tot,withL,nl,atts,ms:Math.round((performance.now()-t0)/tot)})+'\n'+rows.join('\n');}''',[lo,hi,ns]))
    print(errs[:3]); b.close()
