from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2,has_touch=True,is_mobile=True)
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(500)
    pg.tap('#bNew'); pg.wait_for_timeout(200)
    for n in (1,5,9,13,17):
        info=pg.evaluate('''(n)=>{const H=__HK;H.startLevel(n,-1);const L=H.L;for(const g of H.G){g.alive=false;g.gone=true;}
          // a torch with plain floor to its left, mid-floor
          const ts=L.torches.filter(t=>t.c>12&&t.c<L.cols-10);const t=ts[Math.floor(ts.length/2)];
          let c=t.c-3;while(c>2&&!(L.base[t.r*L.cols+c]===1&&!L.feat[t.r*L.cols+c]))c--;
          const P=H.P;P.x=c*32+16;P.y=(t.r+1)*64-4;P.state='stand';P.face=1;P.fallY=P.y;H.cam.snap=true;H.tick(40);H.render();
          return {theme:L.theme.name,rows:L.rows,torch:[t.c,t.r]};}''',n)
        pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true)")
        pg.screenshot(path=f't2_{n}.png'); print(n,info)
    print(errs); b.close()
