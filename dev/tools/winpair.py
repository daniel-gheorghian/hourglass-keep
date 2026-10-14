from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont
import base64,io,sys,os
files=[('before (v32)','v32_hooks.html'),('after','/Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html')]
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',20)
rows=[]
with sync_playwright() as p:
    b=p.chromium.launch()
    for label,f in files:
        ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2); pg=ctx.new_page(); pg.goto('file://'+os.path.abspath(f)); pg.wait_for_timeout(500)
        pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
        ims=[]
        for n in [3,7,11,19]:
            u=pg.evaluate('''(n)=>{const H=__HK;for(let s=0;s<40;s++){const L=H.load(n,8100+s*13,true);
              for(const w of L.windows){let ac=null;for(let c=w.c+3;c<=w.c+8&&ac===null;c++)if(H.isOpenArch(c,w.r))ac=c;if(ac===null)continue;
                let fr=w.r+1;if(L.base[fr*L.cols+w.c]!==1)continue;
                const P=H.P;P.x=(w.c+2)*32+16;P.y=(fr+1)*64-4;P.fallY=P.y;P.state='stand';P.face=1;H.cam.snap=true;H.tick(2);P.x=(w.c+2)*32+16;H.cam.snap=true;H.tick(10);H.render();
                const X=H.XF,x0=(w.c*32-10)*X.VZ-X.camD,y0=(w.r*64)*X.VZ-X.camDY,x1=((ac+1)*32+10)*X.VZ-X.camD,y1=((w.r+2)*64)*X.VZ-X.camDY,c=document.getElementById('game'),o=document.createElement('canvas');
                o.width=Math.round(x1-x0);o.height=Math.round(y1-y0);o.getContext('2d').drawImage(c,x0,y0,o.width,o.height,0,0,o.width,o.height);return o.toDataURL();}}return null;}''',n)
            if u: ims.append(Image.open(io.BytesIO(base64.b64decode(u.split(',')[1]))).convert('RGB'))
        rows.append((label,ims)); ctx.close()
    b.close()
H=max(im.height for _,ims in rows for im in ims); Wd=sum(im.width for im in rows[0][1])+8*len(rows[0][1])
sheet=Image.new('RGB',(Wd,2*(H+34)),(14,12,18)); d=ImageDraw.Draw(sheet)
for ri,(label,ims) in enumerate(rows):
    y=ri*(H+34); d.text((8,y+6),label,fill=(240,220,170),font=font); x=0
    for im in ims: sheet.paste(im,(x,y+32)); x+=im.width+8
sheet=sheet.resize((sheet.width*2//3,sheet.height*2//3)); sheet.save('win_pair.png'); print(sheet.size)
