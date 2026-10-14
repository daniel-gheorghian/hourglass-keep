from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont
import base64,io,json
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2); pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(400)
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    res=pg.evaluate('''()=>{const H=__HK;const L=H.load(4,544,true);const o=L.dyn.find(q=>q.f.t==='chomp');const P=H.P;
      let sc=o.c-3;while(sc<o.c-1&&H.L.base[o.r*H.L.cols+sc]!==1)sc++;P.x=sc*32+16;P.y=(o.r+1)*64-4;P.fallY=P.y;P.state='stand';P.face=1;H.cam.snap=true;H.tick(2);
      // wait for the jaws to be safe for the next second
      let g=0;while(g++<600){let ok=true;for(let t=0;t<1.0;t+=0.05)if(H.danger(o.f,H.gameTime+t))ok=false;if(ok)break;H.tick(1);}
      H.setKey('kb','r',true);const fr=[];let jumped=false,k=0;
      for(let i=0;i<120;i++){H.tick(1);if(!jumped&&P.state==='run'&&o.c*32-P.x<58){H.setKey('kb','j',true);H.tick(1);H.setKey('kb','j',false);jumped=true;}
        if(jumped&&(k++%2===0)&&fr.length<12){H.render();const X=H.XF,sx=Math.round(P.x*X.VZ-X.camD),sy=Math.round((P.y-40)*X.VZ-X.camDY),c=document.getElementById('game'),cv=document.createElement('canvas');cv.width=360;cv.height=400;
          cv.getContext('2d').drawImage(c,sx-180,sy-200,360,400,0,0,360,400);fr.push({u:cv.toDataURL(),s:P.state,low:!!P.lowJump});}
        if(P.state==='dead')break;}
      H.setKey('kb','r',false);return {fr,state:P.state,low:P.lowJump};}''')
    b.close()
print(res['state'],res['low'],len(res['fr']),errs[:2])
ims=[Image.open(io.BytesIO(base64.b64decode(x['u'].split(',')[1]))).convert('RGB') for x in res['fr']]
w,h=ims[0].size;tw,th=w//2,h//2;sheet=Image.new('RGB',(6*tw+20,2*th+4))
for i,im in enumerate(ims):sheet.paste(im.resize((tw,th)),((i%6)*(tw+4),(i//6)*(th+4)))
sheet.save('mo_chompjump.png')
