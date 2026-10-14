from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont
import base64,io,sys,os
f=sys.argv[1] if len(sys.argv)>1 else '/home/claude/hourglass-keep.html'; out=sys.argv[2] if len(sys.argv)>2 else 'arch_wear.png'
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',18)
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2); pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+os.path.abspath(f)); pg.wait_for_timeout(500)
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    ims=[]
    for n in [3,7,11,15,19]:
      for want in (0,3):
        u=pg.evaluate('''([n,want])=>{const H=__HK;for(let s=0;s<40;s++){const L=H.load(n,9100+s*13,true);
          for(let c=10;c<L.cols-10;c++)for(let r=0;r<L.rows-1;r++){if(!H.isArchTop(c,r)||H.isOpenArch(c,r))continue;let ok=0;for(let k=0;k<4;k++)if(H.isArchTop(c+k,r)&&H.wearLevel((c+k)*32+16,r*64+30)===want)ok++;if(ok<4)continue;
            const P=H.P;P.x=(c+2)*32;P.y=(r+2)*64-4;P.fallY=P.y;P.state='stand';P.face=1;H.cam.snap=true;H.tick(2);P.x=(c+2)*32;H.cam.snap=true;H.tick(8);H.render();
            const X=H.XF,x0=(c*32-36)*X.VZ-X.camD,y0=(r*64-6)*X.VZ-X.camDY,c2=document.getElementById('game'),o=document.createElement('canvas');o.width=Math.round(200*X.VZ);o.height=Math.round(134*X.VZ);
            o.getContext('2d').drawImage(c2,x0,y0,o.width,o.height,0,0,o.width,o.height);return o.toDataURL();}}return null;}''',[n,want])
        if u:
          im=Image.open(io.BytesIO(base64.b64decode(u.split(',')[1]))).convert('RGB'); d=ImageDraw.Draw(im); d.text((6,4),f"floor {n} {['pristine','worn','damaged','partly fallen'][want]}",fill=(255,230,170),font=font); ims.append(im)
        else: print('none',n,want)
    w=max(i.width for i in ims);h=max(i.height for i in ims); sh=Image.new('RGB',(2*w+8,5*(h+8)),(0,0,0))
    for i,im in enumerate(ims): sh.paste(im,((i%2)*(w+8),(i//2)*(h+8)))
    sh=sh.resize((sh.width*3//5,sh.height*3//5)); sh.save(out); print(sh.size,errs[:3]); b.close()
