# in-game frames around tapestries (by state) and broken lamps (by theme), cropped around the subject
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont
import io,os,sys,base64
f=sys.argv[1]; out=sys.argv[2]; spec=sys.argv[3]  # items: hang:<state> or lamp:<floor>
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',22)
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2); pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+os.path.abspath(f)); pg.wait_for_timeout(500)
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    ims=[]
    for it in spec.split(','):
        kind,arg=it.split(':');arg=int(arg)
        r=pg.evaluate('''([kind,arg])=>{const H=__HK;const floors=kind==='hang'?[7,8,26,25]:[arg];
          for(const n of floors)for(let s=0;s<30;s++){const L=H.load(n,700+s*17,false);let tx,tr;
            if(kind==='hang'){const hg=(L.hangings||[]).find(h=>h.state===arg&&h.bot-h.top>60)||(L.hangings||[]).find(h=>h.state===arg);if(!hg)continue;tx=hg.x;tr=hg.r;}
            else{const t=L.torches.find(t=>t.broken&&!L.torches.some(o=>!o.broken&&o.r===t.r&&Math.abs(o.c-t.c)<2));if(!t)continue;tx=t.c*32+16;tr=t.r;}
            const P=H.P;P.x=tx+60;P.y=(tr+1)*64-4;P.fallY=P.y;P.state='stand';P.face=-1;H.cam.snap=true;H.tick(2);P.x=tx+60;H.cam.snap=true;H.tick(20);H.render();
            const X=H.XF,cx=tx*X.VZ-X.camD,cy=((tr+1)*64-70)*X.VZ-X.camDY,c=document.getElementById('game'),o=document.createElement('canvas');o.width=560;o.height=420;
            o.getContext('2d').drawImage(c,cx-280,cy-240,560,420,0,0,560,420);return [o.toDataURL(),n,L.theme.name];}return null;}''',[kind,arg])
        if not r: print('none',it); continue
        im=Image.open(io.BytesIO(base64.b64decode(r[0].split(',')[1]))).convert('RGB')
        lab={'hang':['intact','faded','torn','down','gone'][arg] if kind=='hang' else '', 'lamp':'broken lamp'}[kind]
        ImageDraw.Draw(im).text((8,6),f'{lab} · {r[2]}',fill=(255,235,160),font=font);ims.append(im)
    w,h=ims[0].size;cols=3;rows=(len(ims)+cols-1)//cols;sh=Image.new('RGB',(cols*w+8*(cols-1),rows*h+8*(rows-1)),(0,0,0))
    for i,im in enumerate(ims):sh.paste(im,((i%cols)*(w+8),(i//cols)*(h+8)))
    sh.save(out);print(sh.size,errs[:3]);b.close()
