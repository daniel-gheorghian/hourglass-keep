from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2)
    pg=ctx.new_page(); pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(500); pg.add_script_tag(path='bot.js')
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    print(pg.evaluate('''()=>{const H=__HK;const L=H.load(6,502,true);const ins=L.path.find(a=>a.a==='walljump');const c=ins.from;const P=H.P;
       P.x=c*32+16;P.y=7*64-4;P.fallY=P.y;P.state='stand';P.face=1;H.cam.snap=true;
       // jump into the right wall and kick twice
       const set=(k,v)=>H.setKey('kb',k,v);set('j',true);H.tick(1);set('j',false);let kicks=0,log=[];
       for(let f=0;f<120;f++){if(P.state==='air'&&H.wallTouch()&&P.vy>-170&&kicks<2){set('j',true);H.tick(1);set('j',false);kicks++;log.push('kick@'+Math.round(P.y));}else H.tick(1);if(kicks===2&&P.vy>-80)break;}
       H.render();return {c,px:Math.round(P.x-c*32),py:Math.round(P.y),state:P.state,log};}'''))
    pg.screenshot(path='m_kick2.png'); b.close()
