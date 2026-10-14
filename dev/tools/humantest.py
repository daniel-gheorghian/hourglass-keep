from playwright.sync_api import sync_playwright
import json
# reach the foot of the shaft with the bot, then play it by hand under different timings
JS=r'''([mode])=>{const H=__HK;let at=null;
  runBot(5,700511,{fight:false,stop:H=>{const P=H.P;if(P.state==='jumpPrep'&&P.x>5400){at=true;return true;}return false;}});
  const P=()=>H.P,tap=()=>{H.setKey('kb','j',true);H.tick(1);H.setKey('kb','j',false);};
  const log=[];let kicks=0,f=0,lastTouch=false;const y0=P().y;
  while(f<600){const p=P();const wt=H.wallTouch();
    if(mode==='onTouch'&&p.state==='air'&&wt&&!lastTouch){tap();kicks++;f++;}
    else if(mode==='early'&&p.state==='air'&&!wt&&p.vx!==0&&p.jumpKind==='kick'&&Math.abs((p.vx>0?5434:5415.4)-p.x)<5&&!p._e){p._e=1;tap();kicks++;f++;}
    else if(mode==='once'&&p.state==='air'&&wt&&kicks<1){tap();kicks++;f++;}
    else if(mode==='late'&&p.state==='air'&&((p.plant&&H.gameTime-p.plant.t0>0.3)||(kicks===0&&wt))){tap();kicks++;f++;}
    else {H.tick(1);f++;}
    if(P().jumpKind!=='kick'&&P()._e)P()._e=0; if(P().plant===null&&P()._e&&P().vx===0)P()._e=0;
    lastTouch=wt;const q=P();if(['hang','stand','land','landHurt','dead'].includes(q.state)&&f>20){log.push(q.state+' after '+f+' ticks, kicks '+kicks+', rise '+(y0-q.y).toFixed(0)+', hp '+q.hp);break;}}
  return log.join(' | ')||('timeout '+P().state+' y'+P().y);}'''
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':844,'height':390}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    for mode in ['late','early']:
        pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(300); pg.add_script_tag(path='bot.js')
        print(mode, pg.evaluate(JS,[mode]))
    print(errs[:3]); b.close()
