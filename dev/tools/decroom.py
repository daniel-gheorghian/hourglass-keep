# the static room canvases around tapestries (by state) and broken lamps (by theme), magnified
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont
import io,os,sys,base64
f=sys.argv[1]; out=sys.argv[2]; spec=sys.argv[3]
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',16)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+os.path.abspath(f)); pg.wait_for_timeout(400); pg.evaluate("window.__HKfreeze=true")
    ims=[]
    for it in spec.split(','):
        kind,arg=it.split(':');arg=int(arg)
        u=pg.evaluate('''([kind,arg])=>{const H=__HK;const floors=kind==='hang'?[7,8,26,25,27]:[arg];
          for(const n of floors)for(let s=0;s<40;s++){const L=H.load(n,700+s*17,true);let tx,ty;
            if(kind==='hang'){const hg=(L.hangings||[]).find(h=>h.state===arg&&h.bot-h.top>70)||(L.hangings||[]).find(h=>h.state===arg);if(!hg)continue;tx=hg.x;ty=SURFY(hg.r);}
            else{const t=L.torches.find(t=>t.broken);if(!t)continue;tx=t.c*32+16;ty=SURFY(t.r);}
            const Z=3,Wd=170,Hh=240,x0=tx-Wd/2,y0=ty-Hh+24;const cv=document.createElement('canvas');cv.width=Wd*Z;cv.height=Hh*Z;const g=cv.getContext('2d');g.fillStyle='#4a6a8a';g.fillRect(0,0,cv.width,cv.height);
            for(let ry=Math.floor(y0/192);ry<=Math.floor((y0+Hh)/192);ry++)for(let rx=Math.floor(x0/320);rx<=Math.floor((x0+Wd)/320);rx++){const rc=document.createElement('canvas');rc.width=320*Z;rc.height=192*Z;const rg=rc.getContext('2d');rg.setTransform(Z,0,0,Z,0,0);H.drawRoomStatic(rg,rx,ry);g.drawImage(rc,(rx*320-x0)*Z,(ry*192-y0)*Z);}
            return [cv.toDataURL(),L.theme.name];}return null;
          function SURFY(r){return (r+1)*64-4;}}''',[kind,arg])
        if not u: print('none',it); continue
        im=Image.open(io.BytesIO(base64.b64decode(u[0].split(',')[1]))).convert('RGB')
        lab=['intact','faded','torn','down','gone'][arg] if kind=='hang' else 'broken lamp'
        ImageDraw.Draw(im).text((6,4),f'{lab} · {u[1]}',fill=(255,240,120),font=font);ims.append(im)
    w,h=ims[0].size;cols=3;rows=(len(ims)+cols-1)//cols;sh=Image.new('RGB',(cols*w+8*(cols-1),rows*h+8*(rows-1)),(0,0,0))
    for i,im in enumerate(ims):sh.paste(im,((i%cols)*(w+8),(i//cols)*(h+8)))
    sh.save(out);print(sh.size,errs[:3]);b.close()
