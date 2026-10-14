from playwright.sync_api import sync_playwright
from PIL import Image
import sys
out=sys.argv[1] if len(sys.argv)>1 else 'lamps.png'
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=3); pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(500)
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    ims=[]
    for n in [2,6,10,14,18]:
        clip=pg.evaluate('''(n)=>{const H=__HK;let t=null;for(let s=0;s<200&&!t;s++){const L=H.load(n,9100+s,true);t=L.torches.find(q=>{const r=q.r-1;return r>=0&&L.base[r*L.cols+q.c]===0&&L.base[q.r*L.cols+q.c]===1&&!(L.base[r*L.cols+q.c-1]===2&&L.base[r*L.cols+q.c+1]===2)&&q.c>4;})&&null;
            if(!t){t=H.L.torches.find(q=>q.c>4&&window.__inOp&&window.__inOp(q.c,q.r));}}
          return t?{c:t.c,r:t.r}:null;}''',n)
        # fallback: search via the game's own test
        r=pg.evaluate('''(n)=>{const H=__HK;for(let s=0;s<300;s++){const L=H.load(n,9100+s,true);for(const q of L.torches){if(q.c<5)continue;H.P.x=q.c*32-40;H.P.y=(q.r+1)*64-4;H.P.state='stand';H.P.face=1;H.cam.snap=true;H.tick(2);
              if(H.lampFree&&H.lampFree(q)){H.P.x=q.c*32-40;H.cam.snap=true;H.tick(20);H.render();const cam=H.cam,rc=document.getElementById('game').getBoundingClientRect(),sc=rc.height/192;
                let x=rc.left+(q.c*32-cam.x-40)*sc,y=rc.top+((q.r-1)*64-cam.y)*sc;const w=112*sc,h=132*sc;x=Math.max(0,Math.min(innerWidth-w,x));y=Math.max(0,Math.min(innerHeight-h,y));return {s,clip:{x,y,width:w,height:h}};}}}return null;}''',n)
        if not r: print('none',n); continue
        pg.screenshot(path=f'lp{n}.png',clip=r['clip']); ims.append(Image.open(f'lp{n}.png'))
    w,h=ims[0].size; sh=Image.new('RGB',(len(ims)*(w+6),h)); [sh.paste(im,(i*(w+6),0)) for i,im in enumerate(ims)]
    sh.resize((sh.width*2//5,sh.height*2//5)).save(out); print(errs); b.close()
