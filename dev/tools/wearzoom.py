from playwright.sync_api import sync_playwright
from PIL import Image
import sys,os,base64,io
f=sys.argv[1] if len(sys.argv)>1 else '/Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'; out=sys.argv[2] if len(sys.argv)>2 else 'wear_zoom.png'
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2); pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+os.path.abspath(f)); pg.wait_for_timeout(500)
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    ims=[]
    for n,want in [(3,1),(3,3),(7,0),(7,2),(15,3),(19,2)]:
        u=pg.evaluate('''([n,want])=>{const H=__HK;for(let s=0;s<12;s++){const L=H.load(n,4242+s*7,true);
              for(const a of L.path){if(a.a!=='walk')continue;const c=a.c;let r=-1;for(let rr=0;rr<L.rows-1;rr++)if(L.base[rr*L.cols+c]===1&&L.base[(rr+1)*L.cols+c]===0)r=rr;
                if(c<12||r<0)continue;let ok=true;for(let dc=-1;dc<=1;dc++)if(H.wearLevel((c+dc)*32+16,r*64+60)!==want)ok=false;if(!ok)continue;
                const P=H.P;P.x=c*32+16;P.y=(r+1)*64-4;P.fallY=P.y;P.state='stand';P.face=1;H.cam.snap=true;H.tick(2);P.x=c*32+16;H.cam.snap=true;H.tick(15);H.render();
                const X=H.XF,cx=(c*32+16)*X.VZ-X.camD,cy=(r*64+60)*X.VZ-X.camDY,cv=document.getElementById('game'),o=document.createElement('canvas');o.width=760;o.height=380;
                o.getContext('2d').drawImage(cv,cx-380,cy-170,760,380,0,0,760,380);return o.toDataURL();}}return null;}''',[n,want])
        if u: ims.append(Image.open(io.BytesIO(base64.b64decode(u.split(',')[1]))).convert('RGB'))
        else: print('none',n,want)
    w,h=ims[0].size; sh=Image.new('RGB',(2*w+8,3*h+16),(0,0,0))
    for i,im in enumerate(ims): sh.paste(im,((i%2)*(w+8),(i//2)*(h+8)))
    sh.resize((sh.width*3//4,sh.height*3//4)).save(out); print(errs[:3]); b.close()
