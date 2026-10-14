from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2)
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(500)
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    # find a chomper, park the prince next to it, render open and closed jaws
    r=pg.evaluate('''()=>{const H=__HK;for(let s=0;s<40;s++){const L=H.load(9,300+s,true);const o=L.dyn.find(q=>q.f.t==='chomp');if(!o)continue;
        H.P.x=o.c*32-40;H.P.y=(o.r+1)*64-4;H.P.fallY=H.P.y;H.P.state='stand';for(let i=0;i<5;i++)H.tick(1);
        // advance until the jaws are fully shut
        for(let i=0;i<400;i++){H.tick(1);const f=o.f,p=(((H.gameTime+f.off)%f.per)+f.per)%f.per/f.per;if(p>0.08&&p<0.14)break;}
        o.f.blood=1;H.cam.snap=true;H.render();return [s,o.c];}return null;}''')
    pg.screenshot(path='f1_jaws.png'); print('jaws',r)
    # stumble: drop the prince two floors onto open ground and capture mid-stumble with the flash
    r=pg.evaluate('''()=>{const H=__HK;const L=H.load(9,301,true);for(let k=0;k<L.cols;k++){const c=k,r=L.start.r;}
        const P=H.P;P.y-=128;P.fallY=P.y;P.state='air';P.vx=0;P.vy=0;P.hp=2;let t=0;
        while(P.state==='air'&&t<200){H.tick(1);t++;}const lh=P.state;for(let i=0;i<6;i++)H.tick(1);H.render();return [lh,P.stumble.toFixed(2),P.hp];}''')
    pg.screenshot(path='f2_fall.png'); print('fall',r)
    print(errs); b.close()
