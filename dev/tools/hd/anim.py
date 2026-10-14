from playwright.sync_api import sync_playwright
import base64,io,os
from PIL import Image
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':900,'height':500}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+os.getcwd()+'/proto.html'); pg.wait_for_timeout(500)
    pg.evaluate("window.__HKfreeze=true;__HK.load(7,8000,true);")
    frames=[]
    N=24
    for i in range(N):
        d=pg.evaluate('''([i,N])=>{const H=__HK,SC=4,W=6*46*SC,Hh=90*SC;const c=document.createElement('canvas');c.width=W;c.height=Hh;const g=c.getContext('2d');
          const bg=g.createLinearGradient(0,0,0,Hh);bg.addColorStop(0,'#2a2338');bg.addColorStop(1,'#16121f');g.fillStyle=bg;g.fillRect(0,0,W,Hh);
          g.font=(6*SC)+'px sans-serif';g.textAlign='center';g.fillStyle='#bfb6d6';
          const ph=i/N,t=i/N*0.88;
          const cells=[['run',0],['run',1],['sword',0],['sword',1],['guard',0],['guard',1]];
          cells.forEach(([what,nw],k)=>{const ox=(k+0.5)*46*SC,oy=80*SC;g.setTransform(1,0,0,1,0,0);g.fillStyle='rgba(255,255,255,.08)';g.fillRect(k*46*SC+8,oy,46*SC-16,SC*1.2);
            g.fillStyle='#bfb6d6';g.fillText(what+(nw?' new':' now'),ox,10*SC);g.setTransform(SC,0,0,SC,ox,oy);
            const fn=nw?H.drawFigureHD:H.drawFigure;
            if(what==='run'){fn(g,0,0,1,nw?H.runPoseHD(ph*2):H.runPose(ph*2),H.PAL_HERO,{hasSword:true,flutter:1,time:t,vx:100,vy:0});}
            else{const u=(ph*2)%1,pose=u<0.35?H.PS.garde:u<0.5?H.PS.windup:u<0.7?H.PS.lunge:H.PS.garde;const pal=what==='guard'?H.guardPal({tier:2,cap:false}):H.PAL_HERO;
              fn(g,0,0,what==='guard'?-1:1,pose,pal,{sword:true,hasSword:true,flutter:0.3,time:t,vx:0,vy:0});}});
          return c.toDataURL();}''',[i,N])
        frames.append(Image.open(io.BytesIO(base64.b64decode(d.split(',')[1]))).convert('RGB'))
    frames=[f.resize((f.width*3//4,f.height*3//4)) for f in frames]
    frames[0].save('motion.gif',save_all=True,append_images=frames[1:],duration=45,loop=0,optimize=True)
    print(errs,frames[0].size); b.close()
