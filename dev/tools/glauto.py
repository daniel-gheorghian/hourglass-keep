# (v63, owner: "disable the automatic disabling of the torchlight. Leave only manual control") Slow frames never change the lighting mode:
# two slow 2 s windows in a row (a single one is a burst) only make Torchlight's scene copy smaller (scale 1 -> .75 -> .5, one 2 s window
# each), and it stays Torchlight however long the run is slow, also across a new floor (the scale found is kept for the session and starts
# at full size when Torchlight is switched on again). A save left in Classic by the old automatic switch (torchRetry) gets Torchlight back at
# the next floor; Classic chosen in Graphics stays. The Graphics button still switches both ways. Fast windows (no dropped frame) step the
# scale back up, three a step; a step up that goes slow within 10 s doubles the windows needed next time, and a new floor resets that.
# (round 16d) Since v65 a slow window is one over 38 ms (was 18.5): windows of 20, 25, 31.25 and 37 ms keep the full scale (mid*), the fake
# times are whole windows (16, 25, 31.25, 40 ms divide 2 s) so a window never mixes two phases, and a lost WebGL context (WEBGL_lose_context)
# still falls back to Classic through glKill (lost*).
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':844,'height':390}); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(300)
    r=pg.evaluate('''()=>{const H=__HK;H.S.set.lightMode='torch';H.render();const o={};
      const al=()=>{H.GLP.wsum=0;H.GLP.wn=0;};al();
      for(let i=0;i<250;i++)H.glTime(16);o.fastStill=H.S.set.lightMode;o.rsFast=H.GLP.rs;   // 4 s at 16 ms: stays on, full scale
      for(let i=0;i<300;i++)H.glTime(20);o.mid20=H.GLP.rs;                                  // (v65) 6 s at 20 ms (over v64's 18.5): full scale
      for(let i=0;i<240;i++)H.glTime(25);o.mid25=H.GLP.rs;                                  // 6 s at 25 ms: full scale
      for(let i=0;i<192;i++)H.glTime(31.25);o.mid31=H.GLP.rs;                               // 6 s at 31.25 ms: full scale
      for(let i=0;i<300;i++)H.glTime(37);o.mid37=H.GLP.rs;o.midTorch=H.S.set.lightMode;al(); // 11 s at 37 ms, just under 38: full scale, Torchlight
      for(let i=0;i<50;i++)H.glTime(40);o.rsOne=H.GLP.rs;                                   // one slow window: a burst, nothing changes
      for(let i=0;i<50;i++)H.glTime(40);o.rsSlow=H.GLP.rs;o.stillTorch=H.S.set.lightMode;  // two in a row: a smaller scene, still Torchlight
      for(let i=0;i<1200;i++)H.glTime(40);o.slow=H.S.set.lightMode;o.rsLow=H.GLP.rs;       // 48 s at 40 ms: down to .5, and still Torchlight
      o.retry=H.S.set.torchRetry===undefined;H.startLevel(2,-1);o.rsNew=H.GLP.rs;o.newFloor=H.S.set.lightMode;
      // (v63) back up: three fast windows a step (0.5 -> .75 -> 1); an up then slow within 10 s doubles the windows the next try needs
      H.GLP.quiet=0;H.GLP.skip=false;H.GLP.wsum=0;H.GLP.wn=0;H.GLP.fastN=0;const win=(ms,k)=>{for(let i=0;i<k*Math.round(2000/ms);i++)H.glTime(ms);};
      win(16,2);o.upEarly=H.GLP.rs;win(16,1);o.up1=H.GLP.rs;win(16,3);o.up2=H.GLP.rs;
      win(40,2);o.downAgain=H.GLP.rs;o.need=H.GLP.upNeed;win(16,3);o.heldBack=H.GLP.rs;win(16,3);o.up3=H.GLP.rs;
      H.startLevel(2,-1);o.needReset=H.GLP.upNeed;
      H.S.set.lightMode='classic';H.S.set.torchRetry=1;H.startLevel(3,-1);o.oldAuto=H.S.set.lightMode;                       // the old switch's leftover: Torchlight back
      const g=document.getElementById('gShader');g.click();o.manualOff=H.S.set.lightMode;H.startLevel(4,-1);o.manualStays=H.S.set.lightMode; // the menu: off, and it stays off
      H.render();o.shaderOn=H.shaderOn();o.glHidden=H.GLP.cv.style.display;g.click();o.manualOn=H.S.set.lightMode;H.render();o.rsOn=H.GLP.rs;return o;}''')
    # a lost context: glKill hides the WebGL canvas and puts the save in Classic (the screen would otherwise be black)
    r.update(pg.evaluate('''async()=>{const H=__HK;H.render();const x=H.GLP.gl&&H.GLP.gl.getExtension('WEBGL_lose_context');if(!x)return {lostExt:false};
      x.loseContext();for(let i=0;i<40&&!H.GLP.dead;i++)await new Promise(f=>setTimeout(f,50));H.render();
      return {lostExt:true,lostDead:!!H.GLP.dead,lostMode:H.S.set.lightMode,lostShader:H.shaderOn(),lostHidden:H.GLP.cv.style.display};}'''))
    want={'fastStill':'torch','rsFast':1,'mid20':1,'mid25':1,'mid31':1,'mid37':1,'midTorch':'torch','rsOne':1,'rsSlow':0.75,'stillTorch':'torch','slow':'torch','rsLow':0.5,'retry':True,'rsNew':0.5,'newFloor':'torch','upEarly':0.5,'up1':0.75,'up2':1,'downAgain':0.75,'need':6,'heldBack':0.75,'up3':1,'needReset':3,
          'oldAuto':'torch','manualOff':'classic','manualStays':'classic','shaderOn':False,'glHidden':'none','manualOn':'torch','rsOn':1,
          'lostExt':True,'lostDead':True,'lostMode':'classic','lostShader':False,'lostHidden':'none'}
    bad={k:(r.get(k),v) for k,v in want.items() if r.get(k)!=v}
    print(r,errs,'FAILURES',0 if not bad and not errs else 1,bad if bad else ''); b.close()
