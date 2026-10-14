from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont
import sys,os
f=sys.argv[1] if len(sys.argv)>1 else '/home/claude/hourglass-keep.html'; out=sys.argv[2] if len(sys.argv)>2 else 'wear_themes.png'
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',22)
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2); pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+os.path.abspath(f)); pg.wait_for_timeout(500)
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    ims=[]
    for n in [3,7,11,15,19]:
        for want in (0,3):
            r=pg.evaluate('''([n,want])=>{const H=__HK;const L=H.load(n,4242,true);
              for(const a of L.path){if(a.a!=='walk')continue;const c=a.c;let r=0;for(let rr=0;rr<L.rows;rr++)if(L.base[rr*L.cols+c]===1&&(rr===0||L.base[(rr-1)*L.cols+c]!==1))r=rr;
                if(c<12)continue;let ok=true;for(let dc=-3;dc<=3;dc++)if(H.wearLevel((c+dc)*32+16,r*64+60)!==want)ok=false;if(!ok)continue;
                const P=H.P;P.x=c*32+16;P.y=(r+1)*64-4;P.fallY=P.y;P.state='stand';P.face=1;H.cam.snap=true;H.tick(2);P.x=c*32+16;H.cam.snap=true;H.tick(15);H.render();return [c,r];}return null;}''',[n,want])
            pg.screenshot(path='ws.png'); im=Image.open('ws.png').convert('RGB'); d=ImageDraw.Draw(im); d.text((20,340),f"floor {n} — {['pristine','worn','damaged','partly fallen'][want]} {r}",fill=(255,230,170),font=font); ims.append(im)
    w,h=ims[0].size; sh=Image.new('RGB',(2*w+10,5*h+40),(0,0,0))
    for i,im in enumerate(ims): sh.paste(im,((i%2)*(w+10),(i//2)*(h+10)))
    sh.resize((sh.width//2,sh.height//2)).save(out); print(errs[:3]); b.close()
