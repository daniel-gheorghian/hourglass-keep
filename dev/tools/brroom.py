# renders the static room canvases around N breaches (stage 0 only = back plane, and all stages), magnified, over a flat backdrop colour
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont
import base64,io,os,sys
f=sys.argv[1]; out=sys.argv[2]; spec=sys.argv[3]  # spec: floor:idx,floor:idx,...
stage=sys.argv[4] if len(sys.argv)>4 else 'all'
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',16)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+os.path.abspath(f)); pg.wait_for_timeout(400)
    pg.evaluate("window.__HKfreeze=true")
    ims=[]
    for it in spec.split(','):
        n,idx=map(int,it.split(':'))
        u=pg.evaluate('''([n,idx,stage])=>{const H=__HK;const all=[];for(let s=0;s<16&&all.length<=idx;s++){H.load(n,5555+s*11,true);for(const h of H.breaches().filter(Boolean))all.push([s,h.c0,h.r]);}
          const [s,c0,r]=all[idx%all.length];const L=H.load(n,5555+s*11,true);const h=H.breaches().filter(Boolean).find(q=>q.c0===c0&&q.r===r);
          const Z=3,cx=(h.fx0+h.fx1)/2,W=Math.max(220,h.fx1-h.fx0+120),x0=cx-W/2,y0=(h.r-1)*64-24,Hh=64*2+48;
          const c=document.createElement('canvas');c.width=W*Z;c.height=Hh*Z;const g=c.getContext('2d');
          const rx0=Math.floor(x0/320),rx1=Math.floor((x0+W)/320),ry0=Math.floor(y0/192),ry1=Math.floor((y0+Hh)/192);
          g.fillStyle='#4a6a8a';g.fillRect(0,0,c.width,c.height);
          for(let ry=ry0;ry<=ry1;ry++)for(let rx=rx0;rx<=rx1;rx++){const rc=document.createElement('canvas');rc.width=320*Z;rc.height=192*Z;const rg=rc.getContext('2d');rg.setTransform(Z,0,0,Z,0,0);
            if(stage==='all')H.drawRoomStatic(rg,rx,ry);else for(const st of stage.split('+'))H.drawRoomStatic(rg,rx,ry,+st);
            g.drawImage(rc,(rx*320-x0)*Z,(ry*192-y0)*Z);}
          return [c.toDataURL(),L.theme.style,h.c1-h.c0+1,Math.round(h.y1-h.y0),h.open];}''',[n,idx,stage])
        im=Image.open(io.BytesIO(base64.b64decode(u[0].split(',')[1]))).convert('RGB');ImageDraw.Draw(im).text((8,6),f'f{n}#{idx} {u[1]} w{u[2]} h{u[3]} {"open" if u[4] else "facing"}',fill=(255,240,120),font=font);ims.append(im)
    cols=2 if len(ims)>1 else 1;rows=(len(ims)+cols-1)//cols;w=max(i.width for i in ims);h=max(i.height for i in ims)
    sh=Image.new('RGB',(cols*w+8*(cols-1),rows*h+8*(rows-1)),(0,0,0))
    for i,im in enumerate(ims):sh.paste(im,((i%cols)*(w+8),(i//cols)*(h+8)))
    sh.save(out);print(sh.size,errs[:3]);b.close()
