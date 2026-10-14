from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(500); pg.add_script_tag(path='bot.js')
    pg.evaluate("window.__HKfreeze=true")
    r=pg.evaluate('''()=>{const H=__HK;runBot(7,707,{stop:H=>H.P.state==='push'});['l','r','u','d','j','g'].forEach(k=>H.setKey('kb',k,false));const b0=H.L.ext.blocks[0].c;
      for(let i=0;i<60;i++)H.tick(1);const b1=H.L.ext.blocks[0].c;for(let i=0;i<360;i++)H.tick(1);
      const P=H.P;P.hp=1;P.y+=900;P.state='air';P.vy=300;for(let i=0;i<60&&H.mode!=='dead';i++)H.tick(1);
      for(let i=0;i<60;i++)H.tick(1);H.setKey('kb','g',true);H.tick(1);H.setKey('kb','g',false);for(let i=0;i<200&&H.mode==='rewind';i++)H.tick(1);
      const bl=H.L.ext.blocks[0];return {blockStart:b0,afterPush:b1,afterRewind:bl.c,solid:H.L.base[bl.r*H.L.cols+bl.c]===2,oldCellFree:H.L.base[bl.r*H.L.cols+b1]!==2||bl.c===b1,mode:H.mode,px:Math.round(P.x/32)};}''')
    print(json.dumps(r)); print(errs); b.close()
