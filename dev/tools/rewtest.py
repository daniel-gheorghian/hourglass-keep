from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2)
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(500); pg.add_script_tag(path='bot.js')
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    # play a floor for a while with guards, then kill the prince and rewind
    out=pg.evaluate('''()=>{const H=__HK;const r=runBot(9,4242,{fight:true,stop:H=>H.gameTime>40&&H.P.state==='run'});
      const before={x:H.P.x,t:H.gameTime,snaps:H.REW.length,sands:H.S.sands};
      // a fatal blow
      H.P.hp=1;const g=H.G.find(q=>q.alive);H.tick(1);
      // emulate death by a blade
      const P=H.P;P.hp=0;H.mode='play';
      return before;}''')
    print('before',out)
    # die for real through the game's own path: drop the prince into a pit far below
    res=pg.evaluate('''()=>{const H=__HK;const P=H.P;P.hp=1;P.y+=900;P.state='air';P.vy=300;for(let i=0;i<30&&H.mode!=='dead';i++)H.tick(1);
      const dead=H.mode;for(let i=0;i<50;i++)H.tick(1);H.setKey('kb','g',true);H.tick(1);H.setKey('kb','g',false);const m1=H.mode;
      for(let i=0;i<10;i++)H.tick(1);H.render();return {dead,afterPress:m1,midMode:H.mode};}''')
    pg.screenshot(path='r1_rewinding.png'); print(res)
    res2=pg.evaluate('''()=>{const H=__HK;for(let i=0;i<120&&H.mode==='rewind';i++)H.tick(1);H.render();return {mode:H.mode,x:Math.round(H.P.x),state:H.P.state,hp:H.P.hp,t:H.gameTime.toFixed(1),sands:H.S.sands,snaps:H.REW.length};}''')
    pg.screenshot(path='r2_after.png'); print(res2)
    print(errs); b.close()
