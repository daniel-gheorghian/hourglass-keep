from playwright.sync_api import sync_playwright
import sys
n,s=int(sys.argv[1]),int(sys.argv[2])
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(300); pg.add_script_tag(path='bot.js')
    print(pg.evaluate(r'''([n,s])=>{const H=__HK;const L0=H.genLevel(n,s,true);const ch=L0.ext.chase;
      const cell=(cc,rr)=>{const k=rr*L0.cols+cc;const f=L0.feat[k];if(f&&f.t==='spikes')return f.fixed?'v':'^';if(f&&f.t==='loose')return '~';return ['.','=','#'][L0.base[k]];};
      const m=[];for(let rr=ch.rTop;rr<=Math.min(L0.rows-1,ch.rBot+1);rr++){let row=String(rr).padStart(2)+' ';for(let cc=ch.c0-2;cc<=ch.c1+1;cc++)row+=cell(cc,rr);m.push(row);}
      let hdr='   ';for(let cc=ch.c0-2;cc<=ch.c1+1;cc++)hdr+=(cc%10===0?'|':(cc%5===0?'+':' '));
      const hist=[];let last='';const res=runBot(n,s,{stop:H=>{const c=H.L.ext.chase;if(c&&c.on){const st=H.P.state[0]+H.P.state.slice(1,4)+'@'+Math.floor(H.P.x/32)+','+Math.floor((H.P.y-1)/64);if(st!==last){hist.push(st);last=st;}}return false;}});
      return 'c0='+ch.c0+' c1='+ch.c1+'\n'+hdr+'\n'+m.join('\n')+'\n'+JSON.stringify({ok:res.ok,why:res.why})+'\n'+hist.slice(-40).join(' ');}''',[n,s]))
    b.close()
