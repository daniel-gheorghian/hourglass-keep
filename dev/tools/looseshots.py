from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont
import base64,io,os,sys
files=[('v33','v32_hooks.html' if len(sys.argv)<2 else sys.argv[1]),('now','/home/claude/hourglass-keep.html')]
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',18)
rows=[]
with sync_playwright() as p:
    b=p.chromium.launch()
    for label,f in files:
        ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2); pg=ctx.new_page(); pg.goto('file://'+os.path.abspath(f)); pg.wait_for_timeout(500)
        pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
        ims=[]
        for n in [3,11,19]:
            u=pg.evaluate('''(n)=>{const H=__HK;for(let s=0;s<30;s++){const L=H.load(n,6100+s*7,true);
                for(const o of L.dyn){if(o.f.t!=='loose'||o.f.plank)continue;if(H.wearLevel&&H.wearLevel(o.c*32+16,o.r*64+60)<2)continue;
                  const P=H.P;P.x=(o.c-3)*32+16;P.y=(o.r+1)*64-4;P.fallY=P.y;P.state='stand';P.face=1;if(L.base[o.r*L.cols+o.c-3]!==1)continue;H.cam.snap=true;H.tick(2);P.x=(o.c-3)*32+16;H.cam.snap=true;H.tick(6);H.render();
                  const X=H.XF,cx=(o.c*32+16)*X.VZ-X.camD,cy=(o.r*64+60)*X.VZ-X.camDY,c=document.getElementById('game'),cv=document.createElement('canvas');cv.width=560;cv.height=200;
                  cv.getContext('2d').drawImage(c,cx-300,cy-110,560,200,0,0,560,200);return cv.toDataURL();}}return null;}''',n)
            if u: ims.append(Image.open(io.BytesIO(base64.b64decode(u.split(',')[1]))).convert('RGB'))
        rows.append((label,ims)); ctx.close()
    b.close()
w,h=rows[1][1][0].size; sheet=Image.new('RGB',(3*w+16,2*(h+30)),(14,12,18)); d=ImageDraw.Draw(sheet)
for ri,(label,ims) in enumerate(rows):
    d.text((6,ri*(h+30)+4),label+' — the crumbling tile is the one in the middle',fill=(240,220,170),font=font)
    for i,im in enumerate(ims): sheet.paste(im,(i*(w+8),ri*(h+30)+28))
sheet.save('loose_cmp.png');print(sheet.size)
