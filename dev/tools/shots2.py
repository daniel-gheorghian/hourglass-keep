from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); errs=[]
    for name,(w,h) in {'land':(844,390),'se':(667,375),'port':(390,844),'tab':(1024,768)}.items():
        ctx=b.new_context(viewport={'width':w,'height':h},device_scale_factor=2,has_touch=True,is_mobile=True)
        pg=ctx.new_page(); pg.on('pageerror',lambda e:errs.append(name+':'+str(e)))
        pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(500)
        pg.screenshot(path=f'v4_{name}_title.png')
        pg.tap('#bNew'); pg.wait_for_timeout(300)
        pg.evaluate("__HK.setKey('kb','r',true)"); pg.wait_for_timeout(900); pg.evaluate("__HK.setKey('kb','r',false)"); pg.wait_for_timeout(2300)
        pg.screenshot(path=f'v4_{name}_play.png')
        if name=='land':
            # fight scene on a palace floor
            pg.evaluate('''()=>{const H=__HK;H.startLevel(6,-1);const g=H.G[0];for(const o of H.G)if(o!==g){o.alive=false;o.gone=true;}
              const P=H.P;P.x=g.x-70;P.y=g.y;P.face=1;P.state='stand';H.cam.snap=true;H.tick(50);
              H.setKey('kb','g',true);H.tick(1);H.setKey('kb','g',false);H.tick(9);H.render();}''')
            pg.wait_for_timeout(50); pg.screenshot(path='v4_land_fight.png')
            pg.tap('#bPause'); pg.wait_for_timeout(200); pg.screenshot(path='v4_land_pause.png')
            print('paused via button:', pg.evaluate('__HK.mode'))
        ctx.close()
    print(errs); b.close()
