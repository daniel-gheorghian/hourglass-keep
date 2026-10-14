from playwright.sync_api import sync_playwright
from PIL import Image
import sys
out=sys.argv[1]
jobs=[('saw',-40,''),('darter',-40,''),('vent',-40,''),('pend',-40,''),('banner',-40,''),('bar',-40,''),('sanctum',-60,''),('exitdoor',-50,'')]
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2)
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(500)
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    ims=[]
    for i,(kind,dx,mode) in enumerate(jobs):
        r=pg.evaluate('''([kind,dx,mode,i])=>{const H=__HK;let o=null,L;
          for(let s=0;s<200&&!o;s++){const n=6+((s*7+i*3)%20);L=H.load(n,900+s,false);H.G.length=0;
            if(kind==='exitdoor'){o={c:L.door.c,r:L.door.r,f:{}};L.door.open=1;}else if(kind==='block'){const bl=L.ext.blocks.find(b=>b.c>4);if(bl)o={c:bl.c,r:bl.r,f:{}};}
            else if(kind==='plank')o=L.dyn.find(q=>q.f.t==='loose'&&q.f.plank&&q.c>4);
            else o=L.dyn.find(q=>q.f.t===kind&&q.c>4&&(kind!=='loose'||!q.f.plank));}
          if(!o)return 'none';
          H.P.x=o.c*32+16+dx;H.P.y=(o.r+1)*64-4;H.P.fallY=H.P.y;H.P.state='stand';H.P.face=1;H.cam.snap=true;H.tick(1);H.P.x=o.c*32+16+dx;H.P.y=(o.r+1)*64-4;
          if(o.f.t==='gate'){o.f.open=0;o.f.tm=0;}
          if(mode==='dead'){o.f.off=0.1*o.f.per-H.gameTime;o.f.blood=1;}
          if(mode==='walkopen'){o.f.off=0.5*o.f.per-H.gameTime;}if(mode==='closedwait'){o.f.off=0.1*o.f.per-H.gameTime;}
          H.cam.snap=true;H.tick(1);H.P.x=o.c*32+16+dx;if(mode==='dead'||mode==='closedwait'){o.f.off=0.1*o.f.per-H.gameTime;}H.render();
          const cam=H.cam,rc=document.getElementById('game').getBoundingClientRect(),sc=rc.height/192;
          let x=rc.left+(o.c*32-cam.x-60)*sc,y=rc.top+(o.r*64-cam.y-40)*sc;const w=150*sc,h=120*sc;x=Math.max(0,Math.min(innerWidth-w,x));y=Math.max(0,Math.min(innerHeight-h,y));return {x,y,width:w,height:h};}''',[kind,dx,mode,i])
        if r=='none': print('none',kind); continue
        pg.screenshot(path=f'ft{i}.png',clip=r); ims.append(Image.open(f'ft{i}.png'))
    w,h=ims[0].size; cols=4; rows=(len(ims)+cols-1)//cols
    sheet=Image.new('RGB',(cols*(w+8),rows*(h+8)),(20,16,28))
    for i,im in enumerate(ims): sheet.paste(im,((i%cols)*(w+8),(i//cols)*(h+8)))
    sheet=sheet.resize((sheet.width//2,sheet.height//2)); sheet.save(out); print(errs)
    b.close()
