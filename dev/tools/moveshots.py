from playwright.sync_api import sync_playwright
scenes=[('wallrun',6,501,"H=>H.P.state==='wallrun'&&H.P.vy>-120"),
        ('kick',6,502,"H=>H.P.state==='air'&&H.P.jumpKind==='kick'&&H.P.vy>-60"),
        ('slide',6,505,"H=>H.P.state==='slide'&&H.P.t>0.4"),
        ('swing',6,504,"H=>H.P.state==='swing'&&(H.gameTime-H.P.sw0)>0.02"),
        ('rewind',9,4242,None)]
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2)
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(500); pg.add_script_tag(path='bot.js')
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    for name,n,s,stop in scenes:
        if stop:
            r=pg.evaluate("([n,s])=>{const r=runBot(n,s,{stop:%s});__HK.render();return r.ok;}"%stop,[n,s])
        else:
            r=pg.evaluate('''()=>{const H=__HK;runBot(9,4242,{stop:H=>H.gameTime>30&&H.P.state==='run'});const P=H.P;P.hp=1;P.y+=900;P.state='air';P.vy=300;
              for(let i=0;i<40&&H.mode!=='dead';i++)H.tick(1);for(let i=0;i<50;i++)H.tick(1);H.setKey('kb','g',true);H.tick(1);H.setKey('kb','g',false);for(let i=0;i<12;i++)H.tick(1);H.render();return H.mode;}''')
        pg.screenshot(path=f'm_{name}.png'); print(name,r)
    print(errs); b.close()
