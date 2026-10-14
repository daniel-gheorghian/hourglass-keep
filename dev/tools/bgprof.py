from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2); pg=ctx.new_page()
    pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(500)
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    r=pg.evaluate('''()=>{const H=__HK,g=document.getElementById('game').getContext('2d');H.load(10,8000,false);H.P.x=120*32-30;H.P.y=6*64-4;H.P.state='stand';H.cam.snap=true;H.tick(30);
      const t=(cfg)=>{H.S.set.gfx=Object.assign({light:1,atmo:1,grade:1,hero:1,fx:1,hd:1,bg:1},cfg);for(let i=0;i<40;i++)H.roomWork&&H.roomWork();for(let i=0;i<5;i++){H.render();g.getImageData(0,0,1,1);}
        const t0=performance.now();for(let i=0;i<30;i++){H.render();g.getImageData(0,0,1,1);}return +((performance.now()-t0)/30).toFixed(2);};
      const out={};out.all=t({});out.noBg=t({bg:0});out.noLight=t({light:0});out.bgNoLight=t({light:0,grade:0});out.noBgNoLight=t({light:0,grade:0,bg:0});return out;}''')
    print(json.dumps(r)); b.close()
