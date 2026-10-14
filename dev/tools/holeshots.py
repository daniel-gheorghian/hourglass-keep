from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont
import base64,io,os,sys
f=sys.argv[1] if len(sys.argv)>1 else '/Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'; out=sys.argv[2] if len(sys.argv)>2 else 'holes.png'
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',18)
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2); pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+os.path.abspath(f)); pg.wait_for_timeout(500)
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    cnt=pg.evaluate('''()=>{const H=__HK,o={};for(const n of [3,7,11,15,19]){let t=0,cols=0;for(let s=0;s<4;s++){const L=H.load(n,5555+s*11,true);t+=H.wallHoles().length;cols+=L.cols;}o[n]=[t/4,Math.round(cols/4)];}return o;}''')
    print('holes per floor [count, cols]',cnt)
    ims=[]
    for n in [3,7,11,15,19]:
        u=pg.evaluate('''(n)=>{const H=__HK;for(let s=0;s<12;s++){const L=H.load(n,5555+s*11,true);const hs=H.wallHoles();if(!hs.length)continue;const h=hs[Math.floor(hs.length/2)];
            const P=H.P;P.x=h.c*32+16+40;P.y=(h.r+1)*64-4;P.fallY=P.y;P.state='stand';P.face=-1;H.cam.snap=true;H.tick(2);P.x=h.c*32+56;H.cam.snap=true;H.tick(10);H.render();
            const X=H.XF,cx=(h.c*32+16)*X.VZ-X.camD,cy=(h.r*64+10)*X.VZ-X.camDY,c=document.getElementById('game'),o=document.createElement('canvas');o.width=640;o.height=380;
            o.getContext('2d').drawImage(c,cx-320,cy-210,640,380,0,0,640,380);return o.toDataURL();}return null;}''',n)
        if u:
            im=Image.open(io.BytesIO(base64.b64decode(u.split(',')[1]))).convert('RGB');ImageDraw.Draw(im).text((8,6),f'floor {n}',fill=(255,230,170),font=font);ims.append(im)
    w,h=ims[0].size;sh=Image.new('RGB',(3*w+16,2*h+8),(0,0,0))
    for i,im in enumerate(ims):sh.paste(im,((i%3)*(w+8),(i//3)*(h+8)))
    sh=sh.resize((sh.width*2//3,sh.height*2//3));sh.save(out);print(errs[:3]);b.close()
