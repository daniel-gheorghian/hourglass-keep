from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(); errs=[]
    ctx=b.new_context(viewport={'width':390,'height':844},device_scale_factor=2,has_touch=True,is_mobile=True)
    pg=ctx.new_page(); pg.on('pageerror',lambda e:errs.append(str(e)))
    # an existing mid-floor save from the live version (gen 2)
    ctx.add_init_script('''if(!sessionStorage.getItem('seeded')){sessionStorage.setItem('seeded','1');localStorage.setItem('hourglass-keep-v1',JSON.stringify({v:1,gen:2,lifeTaken:[3],level:9,maxHp:5,deaths:4,time:1234,floorTime:80,floorDeaths:1,seed:777,cp:1,started:true,hints:{move:1},set:{sound:true,saver:false,lefty:false},resume:{n:9,x:1000,y:316,face:1,hp:3,dead:[],takenAt:[],fallen:[],rubble:[],cps:[1,1],door:0}}));}''')
    pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(400)
    out={'continue':pg.inner_text('#bContinue')}
    pg.tap('#bContinue'); pg.wait_for_timeout(300)
    out['after']=pg.evaluate('({level:__HK.S.level,maxHp:__HK.S.maxHp,lives:__HK.P.hp,x:__HK.P.x,startX:__HK.L.start.x,gen:__HK.S.gen,deaths:__HK.S.deaths})')
    pg.wait_for_timeout(2800); pg.screenshot(path='t4_port.png')
    out['errs']=errs; print(json.dumps(out)); b.close()
