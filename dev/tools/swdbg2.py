from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(300); pg.add_script_tag(path='bot.js')
    for n,s in [(6,503),(6,500),(6,501)]:
        r=pg.evaluate('''([n,s])=>{const H=__HK;const hist=[];let last='';const r=runBot(n,s,{stop:H=>{const st=H.P.state+'@'+Math.floor(H.P.x/32)+','+Math.floor((H.P.y-1)/64);if(st!==last){hist.push(st);last=st;if(hist.length>40)hist.shift();}return false;}});
          r.hist=hist.join(' ');if(r.ins)r.insJ=JSON.stringify(r.ins);return r;}''',[n,s])
        print(n,s,r.get('ok'),r.get('why'),r.get('insJ'),'col',r.get('col'),'row',r.get('row')); print('   ',r.get('hist','')[-900:])
    b.close()
