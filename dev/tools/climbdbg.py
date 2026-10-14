from playwright.sync_api import sync_playwright
import sys
n,s,cc0,f=int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3]),sys.argv[4]=='fight'
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(300); pg.add_script_tag(path='bot.js')
    print(pg.evaluate(r'''([n,s,cc0,f])=>{const H=__HK;const L0=H.genLevel(n,s,!f);const i=L0.path.findIndex(a=>a.a==='climb'&&a.from===cc0);
      const ctx=L0.path.slice(Math.max(0,i-5),i+3).map(a=>JSON.stringify(a)).join(' ');
      let r=-1;for(let rr=0;rr<L0.rows;rr++)if(L0.base[rr*L0.cols+cc0]===1)r=rr;
      const cell=(cc,rr)=>{const k=rr*L0.cols+cc;const f=L0.feat[k];if(L0.blockAt.get(k))return 'B';if(f)return f.t==='plate'?'p':f.t==='gate'?'g':f.t[0];return ['.','=','#'][L0.base[k]];};
      const m=[];for(let rr=Math.max(0,r-3);rr<=Math.min(L0.rows-1,r+2);rr++){let row=String(rr).padStart(2)+' ';for(let cc=cc0-8;cc<=cc0+8;cc++)row+=cell(cc,rr);m.push(row);}
      const hist=[];let last='';const res=runBot(n,s,{fight:f,stop:H=>{if(Math.abs(H.P.x-cc0*32)<300){const st=H.P.state.slice(0,5)+'@'+Math.floor(H.P.x/32)+','+Math.floor((H.P.y-1)/64);if(st!==last){hist.push(st);last=st;if(hist.length>40)hist.shift();}}return false;}});
      return ctx+'\ncols '+(cc0-8)+'..'+(cc0+8)+'\n'+m.join('\n')+'\n'+JSON.stringify({ok:res.ok,why:res.why})+'\n'+hist.join(' ');}''',[n,s,cc0,f]))
    b.close()
