from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(300); pg.add_script_tag(path='bot.js')
    print(pg.evaluate(r'''()=>{const H=__HK;const L0=H.genLevel(7,703,true);const i=L0.path.findIndex(a=>a.a==='walk'&&a.c===248);
      const ctx=L0.path.slice(Math.max(0,i-4),i+3).map(a=>JSON.stringify(a)).join(' ');
      let r=-1;for(let rr=0;rr<L0.rows;rr++)if(L0.base[rr*L0.cols+248]===1)r=rr;
      const cell=(cc,rr)=>{const k=rr*L0.cols+cc;const f=L0.feat[k];if(L0.blockAt.get(k))return 'B';if(f)return f.t[0];return ['.','=','#'][L0.base[k]];};
      const m=[];for(let rr=Math.max(0,r-3);rr<=Math.min(L0.rows-1,r+2);rr++){let row='';for(let cc=236;cc<=252;cc++)row+=cell(cc,rr);m.push(row);}
      const hist=[];let last='';const res=runBot(7,703,{stop:H=>{if(Math.abs(H.P.x-248*32)<400){const st=H.P.state+'@'+Math.floor(H.P.x/32)+','+Math.floor((H.P.y-1)/64);if(st!==last){hist.push(st);last=st;if(hist.length>30)hist.shift();}}return false;}});
      return ctx+'\n'+m.join('\n')+'\n'+JSON.stringify({ok:res.ok,why:res.why})+'\n'+hist.join(' ');}'''))
    b.close()
