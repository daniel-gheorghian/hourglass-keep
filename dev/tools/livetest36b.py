from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2)
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(800)
    # start on floor 9 directly through the save, as a returning player would
    pg.evaluate("(()=>{const s=JSON.parse(localStorage.getItem('hourglass-keep-v1')||'null');})()")
    pg.click('#bNew'); pg.wait_for_timeout(1500)
    pg.evaluate("(()=>{__HK.startLevel(9,-1);})()"); pg.wait_for_timeout(1200)
    info=pg.evaluate("(()=>{const L=__HK.L,P=__HK.P;const cp=L.cps[3];P.x=cp.x;P.y=(cp.r+1)*64-4;P.fallY=P.y;P.state='stand';P.vx=0;P.vy=0;return {n:L.n,cp:{c:cp.c,r:cp.r,ord:cp.ord},guardOrds:L.guards.map(g=>Math.round(g.ord))};})()")
    print(info); pg.wait_for_timeout(1500)
    print('cp on',pg.evaluate("({idx:__HK.L.cpIndex,saved:JSON.parse(localStorage.getItem('hourglass-keep-v1')).cp})"))
    pg.wait_for_timeout(3500)
    pg.reload(); pg.wait_for_timeout(1000); pg.click('#bContinue'); pg.wait_for_timeout(2000)
    print('resumed',pg.evaluate("(()=>{const L=__HK.L,P=__HK.P;return {n:L.n,x:P.x,r:Math.floor(P.y/64),cpIdx:L.cpIndex,gone:__HK.G.map((g,i)=>[Math.round(L.guards[i].ord),g.gone?1:0])};})()"))
    pg.screenshot(path='lt_resume.png')
    print('errors',errs[:5]); b.close()
