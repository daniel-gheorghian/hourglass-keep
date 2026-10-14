from playwright.sync_api import sync_playwright
from PIL import Image
import sys,os,base64,io
f=sys.argv[1] if len(sys.argv)>1 else '/home/claude/hourglass-keep.html'; out=sys.argv[2] if len(sys.argv)>2 else 'win_crops.png'
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2); pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+os.path.abspath(f)); pg.wait_for_timeout(500)
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    ims=[]
    for i,n in enumerate([3,7,11,15,19]):
        u=pg.evaluate('''(n)=>{const H=__HK;for(let s=0;s<30;s++){const L=H.load(n,4000+s*17,true);
            for(const w of L.windows){let ac=null;for(let c=w.c-6;c<=w.c+6&&ac===null;c++)for(let r=w.r-1;r<=w.r+1;r++)if(H.isOpenArch(c,r)){ac=c;break;}if(ac===null)continue;
              let fr=w.r+1;while(fr<L.rows&&L.base[fr*L.cols+w.c]!==1)fr++;if(fr>=L.rows)continue;
              const P=H.P;P.x=(w.c+ac)/2*32+16;P.y=(fr+1)*64-4;P.fallY=P.y;P.state='stand';P.face=1;H.cam.snap=true;H.tick(2);H.cam.snap=true;H.tick(20);H.render();
              const X=H.XF,cx=((w.c+ac)/2*32+16)*X.VZ-X.camD,cy=(w.r*64+40)*X.VZ-X.camDY,c=document.getElementById('game'),o=document.createElement('canvas');o.width=900;o.height=360;
              o.getContext('2d').drawImage(c,cx-450,cy-160,900,360,0,0,900,360);return o.toDataURL();}}return null;}''',n)
        if u: ims.append(Image.open(io.BytesIO(base64.b64decode(u.split(',')[1]))).convert('RGB'))
    w,h=ims[0].size; sh=Image.new('RGB',(w,len(ims)*(h+8)),(0,0,0))
    for i,im in enumerate(ims): sh.paste(im,(0,i*(h+8)))
    sh.resize((sh.width*2//3,sh.height*2//3)).save(out); print(len(ims),errs[:3]); b.close()
