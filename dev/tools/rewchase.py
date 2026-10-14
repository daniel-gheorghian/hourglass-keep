from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':390,'height':844},device_scale_factor=2)
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(500); pg.add_script_tag(path='bot.js')
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true)")
    # die in the storm by standing still, then rewind
    r=pg.evaluate('''()=>{const H=__HK;runBot(12,900,{stop:H=>{const c=H.L.ext.chase;return c&&c.on&&c.t>2.5;}});
      for(let i=0;i<600&&H.mode==='play';i++)H.tick(1);const cause=H.P.cause,wxDead=H.L.ext.chase.wx;
      for(let i=0;i<60;i++)H.tick(1);H.setKey('kb','g',true);H.tick(1);H.setKey('kb','g',false);for(let i=0;i<200&&H.mode==='rewind';i++)H.tick(1);
      const c=H.L.ext.chase;return {cause,mode:H.mode,gapBefore:null,gapAfter:Math.round(H.P.x-c.wx),wxDead:Math.round(wxDead),wxNow:Math.round(c.wx),hp:H.P.hp,sands:H.S.sands};}''')
    print('storm rewind',json.dumps(r))
    # rewind across a block push: the block must return to where it was
    r=pg.evaluate('''()=>{const H=__HK;runBot(7,707,{stop:H=>H.P.state==='push'});const b0=H.L.ext.blocks[0].c;
      for(let i=0;i<200;i++)H.tick(1);const b1=H.L.ext.blocks[0].c;H.P.hp=1;const P=H.P;P.y+=900;P.state='air';P.vy=300;for(let i=0;i<60&&H.mode!=='dead';i++)H.tick(1);
      for(let i=0;i<60;i++)H.tick(1);H.setKey('kb','g',true);H.tick(1);H.setKey('kb','g',false);for(let i=0;i<200&&H.mode==='rewind';i++)H.tick(1);
      const bl=H.L.ext.blocks[0];return {blockAtPush:b0,blockAfter:b1,blockRewound:bl.c,baseOk:H.L.base[bl.r*H.L.cols+bl.c]===2,mode:H.mode};}''')
    print('block rewind',json.dumps(r))
    # portrait HUD with a running gate timer and 6 lives
    pg.evaluate('''()=>{const H=__HK;H.S.maxHp=7;runBot(9,9000,{stop:H=>{const d=(H.L.detours||[]).find(q=>q.double);if(!d)return false;const g2=H.L.dyn.find(o=>o.c===d.g2c&&o.r===d.r);return g2&&g2.f.tm>0&&g2.f.tm<g2.f.dur*0.7&&H.P.state==='run';}});H.layout();H.render();}''')
    pg.screenshot(path='p_hud.png'); print(errs); b.close()
