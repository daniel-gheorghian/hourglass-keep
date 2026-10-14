from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2)
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.add_init_script("""(()=>{window.__q=[];window.requestAnimationFrame=cb=>{window.__q.push(cb);return 1;};})();""")
    pg.goto('file:///tmp/claude-0/-home-claude-hourglass-keep/f01bc65f-8e08-5e8f-8f80-4fcb704e8720/scratchpad/prof2.html'); pg.wait_for_timeout(500); pg.add_script_tag(path='bot.js')
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    # play a chase floor with the bot, but drive the real loop so prefetch and interpolation run
    r=pg.evaluate('''()=>{const H=__HK;let ts=1000,needed=0,frames=0,heavy=[];const g=document.getElementById('game').getContext('2d');
      const res=runBot(11,788,{fight:false,stop:H2=>{H.mode;const q=window.__q;window.__q=[];
        // emulate one display frame: the loop would normally step the sim; the bot already stepped it, so freeze acc by giving dt=0
        const b0=H.roomBuilds,p0=H.prefetched;const t0=performance.now();for(const cb of q)cb(ts);g.getImageData(0,0,1,1);const dt=performance.now()-t0;
        const built=H.roomBuilds-b0,pf=H.prefetched-p0;if(built-pf>0)needed+=built-pf;frames++;heavy.push(dt);return false;}});
      heavy.sort((a,b)=>a-b);const lg=window.__bk.log.filter(x=>!x.pf);return {first:lg.filter(x=>x.first).length,afterInvalidate:lg.filter(x=>x.inv).length,afterEvict:lg.filter(x=>!x.first&&!x.inv).length,pf:window.__bk.log.filter(x=>x.pf).length,ok:res.ok,frames,roomBuilds:H.roomBuilds,prefetched:H.prefetched,neededAtDrawTime:needed,p50:+heavy[Math.floor(frames*0.5)].toFixed(1),p99:+heavy[Math.floor(frames*0.99)].toFixed(1),max:+heavy[frames-1].toFixed(1)};}''')
    print(json.dumps(r),errs[:3]); b.close()
