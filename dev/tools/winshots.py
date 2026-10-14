from playwright.sync_api import sync_playwright
from PIL import Image
import sys,os
f=sys.argv[1] if len(sys.argv)>1 else '/Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'; out=sys.argv[2] if len(sys.argv)>2 else 'win_themes.png'
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2); pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+os.path.abspath(f)); pg.wait_for_timeout(500)
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    ims=[]
    for i,n in enumerate([3,7,11,15,19]):
        r=pg.evaluate('''(n)=>{const H=__HK;for(let s=0;s<30;s++){const L=H.load(n,4000+s*17,true);
            // a window with an open arch within 7 columns on the same rows
            for(const w of L.windows){let near=false;for(let c=w.c-7;c<=w.c+7;c++)for(let r=w.r-1;r<=w.r+1;r++)if(H.isOpenArch(c,r))near=true;if(!near)continue;
              let fr=w.r+1;while(fr<L.rows&&L.base[fr*L.cols+w.c]!==1)fr++;if(fr>=L.rows)continue;
              const P=H.P;P.x=w.c*32+16;P.y=(fr+1)*64-4;P.fallY=P.y;P.state='stand';P.face=1;H.cam.snap=true;H.tick(2);P.x=w.c*32+16;H.cam.snap=true;H.tick(20);H.render();return [s,w.c,w.r];}}return null;}''',n)
        pg.screenshot(path=f'wt{i}.png'); ims.append(Image.open(f'wt{i}.png')); print(n,r)
    w,h=ims[0].size; sh=Image.new('RGB',(2*w+10,3*h+20),(0,0,0))
    for i,im in enumerate(ims): sh.paste(im,((i%2)*(w+10),(i//2)*(h+10)))
    sh.resize((sh.width//2,sh.height//2)).save(out); print(errs[:3]); b.close()
