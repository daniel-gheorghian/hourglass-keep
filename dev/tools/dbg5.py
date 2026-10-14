from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(300)
    src=open('bot.js').read().replace("if (ph === 0) trace.push(ins.a + '@' + (ins.from ?? ins.c));","if (ph === 0) trace.push(ins.a + '@' + (ins.from ?? ins.c)); if((ins.a==='sjump'&&ins.from===221)||(ins.a==='crawl'&&ins.from===217&&ph>=4))window.__dbg.push(frames+' '+ins.a+' ph'+ph+':'+p.state+':'+p.x.toFixed(1)+' hp'+p.hp+' inv'+p.inv.toFixed(2)+' '+JSON.stringify(held));")
    pg.add_script_tag(content='window.__dbg=[];'+src)
    r=pg.evaluate('()=>{const r=runBot(10,700983,{});return {r,d:window.__dbg};}')
    print(json.dumps(r['r'])[:200]); print('\n'.join(r['d'][:60]))
    b.close()
