# in-game frames of segments built in leftward runs (and turn kits), the prince placed just before each
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont
import io,os,sys,json
f=sys.argv[1]; out=sys.argv[2]; kinds=sys.argv[3].split(','); dirWant=int(sys.argv[4]) if len(sys.argv)>4 else -1
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',26)
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2); pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+os.path.abspath(f)); pg.wait_for_timeout(500)
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    ims=[]
    for k in kinds:
        r=pg.evaluate('''([k,dw])=>{const H=__HK;for(const n of [26,22,18,14,11,8,6,4,3]){for(let s=0;s<6;s++){const L=H.load(n,8100+s*7+n*3,false);
            const q=L.segs.find(q=>q.k===k&&(dw===0||q.dir===dw));if(!q)continue;
            H.S&&0;const P=H.P,d=q.dir||1;P.x=q.c0*32+16-d*20;P.y=(q.r0+1)*64-4;P.fallY=P.y;P.state='stand';P.face=d;H.cam.snap=true;H.tick(2);P.x=q.c0*32+16-d*20;P.face=d;H.cam.snap=true;H.tick(40);H.render();
            return {n,s,c0:q.c0,c1:q.c1,r:q.r0,d,theme:L.theme.name};}}return null;}''',[k,dirWant])
        if not r: print('none',k); continue
        im=Image.open(io.BytesIO(pg.locator('#game').screenshot())).convert('RGB')
        ImageDraw.Draw(im).text((24,64),f"{k} {'←' if r['d']<0 else '→'}  floor {r['n']}",fill=(255,235,160),font=font);ims.append(im)
    w,h=ims[0].size;cols=2;rows=(len(ims)+1)//2;sh=Image.new('RGB',(cols*w+12,rows*h+12*(rows-1)),(0,0,0))
    for i,im in enumerate(ims):sh.paste(im,((i%cols)*(w+12),(i//cols)*(h+12)))
    sh=sh.resize((sh.width//2,sh.height//2),Image.LANCZOS);sh.save(out);print(errs[:3]);b.close()
