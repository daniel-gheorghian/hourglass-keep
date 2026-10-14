from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2,has_touch=True,is_mobile=True)
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(500)
    pg.add_script_tag(path='bot.js')
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true)")
    for n in (1,17):
        r=pg.evaluate('''(n)=>{const H=__HK;let res=null;
          for(let s=0;s<6&&!res;s++){res=runBot(n,900+s*13,{stop:(H)=>{const P=H.P,L=H.L;if(P.state!=='stand'||H.mode!=='play')return false;const c=Math.floor(P.x/32),r=Math.floor((P.y-1)/64);
            return L.torches.some(t=>t.r===r&&t.c-c>=2&&t.c-c<=4&&t.c>8);}});if(res.ok!=='stopped')res=null;}
          H.tick(20);H.render();return {res,theme:H.L.theme.name};}''',n)
        pg.screenshot(path=f't3_{n}.png'); print(n,r)
    print(errs); b.close()
