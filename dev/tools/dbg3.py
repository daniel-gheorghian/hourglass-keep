from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(300)
    src=open('bot.js').read().replace("if (ph === 0) trace.push(ins.a + '@' + (ins.from ?? ins.c));","if (ph === 0) trace.push(ins.a + '@' + (ins.from ?? ins.c)); if(ins.a==='crawl'&&window.__dbg.length<4000){if(frames%30===0||ph>=2)window.__dbg.push(frames+' ph'+ph+':'+p.state+':'+p.x.toFixed(1)+' snakes:'+JSON.stringify(H.SN.map(s=>[s.x|0,s.state,s.alive,s.dir,s.lo|0,s.hi|0]))+' tunnel?'+JSON.stringify(H.L.feat[row()*H.L.cols+col()+1]));}")
    pg.add_script_tag(content='window.__dbg=[];'+src)
    r=pg.evaluate('()=>{const r=runBot(6,700582,{});return {r,d:window.__dbg};}')
    print(json.dumps(r['r'])[:300]); print('\n'.join(r['d'][-30:]))
    b.close()
