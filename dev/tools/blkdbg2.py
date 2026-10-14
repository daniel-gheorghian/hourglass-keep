from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(300); pg.add_script_tag(path='bot.js')
    for n,s in [(7,701),(7,700),(7,702)]:
        print(n,s,pg.evaluate('''([n,s])=>{const H=__HK;const hist=[];let last='',on=false;const r=runBot(n,s,{stop:H=>{const bl=H.L.ext.blocks[0];if(!bl)return false;if(Math.abs(H.P.x-bl.c*32)<120&&Math.floor((H.P.y-1)/64)>=bl.r-1)on=true;
          if(on){const st=H.P.state+'@'+Math.floor(H.P.x/32)+'/'+Math.round(H.P.x%32)+' b'+bl.c+(bl.mv?'m':'')+' f'+H.P.face;if(st!==last){hist.push(st);last=st;if(hist.length>40)hist.shift();}}return false;}});
          return JSON.stringify({ok:r.ok,why:r.why,ins:r.ins})+'\\n  '+hist.join(' ');}''',[n,s]))
    b.close()
