# a real start from the title screen, a checkpoint save, a reload that resumes mid-floor, and an old (gen 8) save
from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2)
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(800)
    pg.screenshot(path='lt_title.png')
    pg.click('#bNew'); pg.wait_for_timeout(2500)
    s=pg.evaluate("({mode:__HK.mode,x:__HK.P.x,r:Math.floor(__HK.P.y/64),face:__HK.P.face,start:__HK.L.start,door:__HK.L.door&&{c:__HK.L.door.c,r:__HK.L.door.r},cols:__HK.L.cols,rows:__HK.L.rows})")
    print('started',s)
    pg.screenshot(path='lt_start.png')
    # hold the run key the way he faces for a few seconds
    k='r' if s['face']>0 else 'l'
    pg.evaluate(f"__HK.setKey('kb','{k}',true)"); pg.wait_for_timeout(3000); pg.evaluate(f"__HK.setKey('kb','{k}',false)")
    pg.wait_for_timeout(500)
    print('after run',pg.evaluate("({x:__HK.P.x,st:__HK.P.state,hp:__HK.P.hp})"))
    pg.screenshot(path='lt_run.png')
    # jump to a checkpoint on the route and save
    print(pg.evaluate("(()=>{const L=__HK.L;const cp=L.cps[2];const P=__HK.P;P.x=cp.x;P.y=(cp.r+1)*64-4;P.fallY=P.y;P.state='stand';__HK.tick(30);return {cp:{c:cp.c,r:cp.r,ord:cp.ord},on:cp.on,idx:L.cpIndex};})()"))
    pg.wait_for_timeout(3500)
    pg.reload(); pg.wait_for_timeout(1000)
    print('title after reload', pg.evaluate("document.getElementById('bContinue')&&!document.getElementById('bContinue').hidden"))
    pg.click('#bContinue'); pg.wait_for_timeout(2000)
    print('resumed',pg.evaluate("({mode:__HK.mode,x:__HK.P.x,r:Math.floor(__HK.P.y/64),cpIdx:__HK.L.cpIndex,alive:__HK.G.filter(g=>g.alive).length,guards:__HK.G.length})"))
    pg.screenshot(path='lt_resume.png')
    # an old save from gen 8 with a mid-floor checkpoint
    pg.evaluate("(()=>{const s=JSON.parse(localStorage.getItem('hourglass-keep-v1'));s.gen=8;s.cp=3;s.level=7;s.floorTime=55;localStorage.setItem('hourglass-keep-v1',JSON.stringify(s));})()")
    pg.reload(); pg.wait_for_timeout(1000); pg.click('#bContinue'); pg.wait_for_timeout(2000)
    print('old save',pg.evaluate("({n:__HK.L.n,x:__HK.P.x,startx:__HK.L.start.x,cpIdx:__HK.L.cpIndex})"))
    print('errors',errs[:5]); b.close()
