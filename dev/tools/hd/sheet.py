from playwright.sync_api import sync_playwright
import base64,io,os,sys
from PIL import Image
out=sys.argv[1] if len(sys.argv)>1 else 'sheet.png'
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':900,'height':500}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+os.getcwd()+'/proto.html'); pg.wait_for_timeout(500)
    d=pg.evaluate('''()=>{window.__HKfreeze=true;const H=__HK;H.load(7,8000,true);
      const PS=H.PS,poses=[['stand',PS.stand,0,0,0],['run 1',H.runPose(0.0),100,0,1],['run 2',H.runPose(0.25),100,0,1],['run 3',H.runPose(0.5),100,0,1],['run 4',H.runPose(0.75),100,0,1],
        ['jump',PS.jumpR,120,-120,0],['fall',PS.fall,20,300,0],['hang',PS.hang,0,0,0],['crouch',PS.crouch,0,0,0],['en garde',PS.garde,0,0,0],['lunge',PS.lunge,0,0,0],['parry',PS.parry,0,0,0],['hurt',PS.hurt,-40,0,0],['drink',PS.drink,0,0,0]];
      const SC=5,cw=46,chh=78,W=poses.length*cw*SC,Hh=(chh*2+16)*SC;const c=document.createElement('canvas');c.width=W;c.height=Hh;const g=c.getContext('2d');
      const bg=g.createLinearGradient(0,0,0,Hh);bg.addColorStop(0,'#2a2338');bg.addColorStop(1,'#16121f');g.fillStyle=bg;g.fillRect(0,0,W,Hh);
      g.font=(7*SC)+'px sans-serif';g.textAlign='center';
      poses.forEach(([name,pose0,vx,vy,isRun],i)=>{for(const row of [0,1]){
        let pose=pose0;if(row===1&&isRun)pose=H.runPoseHD([0,0.25,0.5,0.75][i-1]);
        const ox=(i+0.5)*cw*SC,oy=(row*(chh+8)+chh-6)*SC;g.setTransform(1,0,0,1,0,0);g.fillStyle='rgba(255,255,255,.08)';g.fillRect(i*cw*SC+SC*2,oy,cw*SC-SC*4,SC*1.2);
        g.setTransform(SC,0,0,SC,ox,oy);const air=['jump','fall','hang'].includes(name);const yy=air?-8:0;
        const o={sword:['en garde','lunge','parry'].includes(name),hasSword:true,flutter:isRun||name==='jump'?1:0.2,time:1.3+i*0.37,vx,vy};
        (row?H.drawFigureHD:H.drawFigure)(g,0,yy,1,pose,H.PAL_HERO,o);
        g.setTransform(1,0,0,1,0,0);g.fillStyle='#bfb6d6';g.fillText(name+(row?' (new)':''),ox,(row*(chh+8)+10)*SC);}});
      return c.toDataURL();}''')
    Image.open(io.BytesIO(base64.b64decode(d.split(',')[1]))).save(out)
    print(errs); b.close()
