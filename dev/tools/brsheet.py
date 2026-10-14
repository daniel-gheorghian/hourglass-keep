from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont
import os,sys,io
f=sys.argv[1]; out=sys.argv[2]; spec=sys.argv[3]
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',26)
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2); pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+os.path.abspath(f)); pg.wait_for_timeout(500)
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    ims=[]
    for it in spec.split(','):
        n,idx,dx=map(int,it.split(':'))
        r=pg.evaluate('''([n,idx,dx])=>{const H=__HK;const all=[];for(let s=0;s<16&&all.length<=idx;s++){H.load(n,5555+s*11,true);for(const h of H.breaches().filter(b=>b&&b.open))all.push([s,h.c0,h.r]);}
          const [s,c0,r]=all[idx%all.length];const L=H.load(n,5555+s*11,true);const h=H.breaches().find(q=>q&&q.c0===c0&&q.r===r);
          const P=H.P;P.x=(h.c1+1)*32+dx;P.y=(h.r+1)*64-4;P.fallY=P.y;P.state='stand';P.face=-1;H.cam.snap=true;H.tick(2);H.cam.snap=true;H.tick(30);H.render();return L.theme.name;}''',[n,idx,dx])
        im=Image.open(io.BytesIO(pg.locator('#game').screenshot())).convert('RGB');ImageDraw.Draw(im).text((24,70),f'floor {n} · {r}',fill=(255,235,160),font=font);ims.append(im)
    w,h=ims[0].size;cols=2;rows=(len(ims)+1)//2;sh=Image.new('RGB',(cols*w+12,rows*h+12*(rows-1)),(0,0,0))
    for i,im in enumerate(ims):sh.paste(im,((i%cols)*(w+12),(i//cols)*(h+12)))
    sh=sh.resize((sh.width//2,sh.height//2),Image.LANCZOS);sh.save(out);print(errs[:3]);b.close()
