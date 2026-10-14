# grid: themes (rows) x wear stage (cols): back wall patches rendered from the room canvases at 3x
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont
import base64,io,os,sys
f=sys.argv[1]; out=sys.argv[2]
floors=[int(x) for x in (sys.argv[3] if len(sys.argv)>3 else '3,7,11,15,19').split(',')]
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',15)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+os.path.abspath(f)); pg.wait_for_timeout(400); pg.evaluate("window.__HKfreeze=true")
    rows=[]
    for n in floors:
        row=[]
        for W in range(4):
            u=pg.evaluate('''([n,W])=>{const H=__HK;for(let s=0;s<10;s++){const L=H.load(n,7777+s*13,true);
              const ok=(c,r)=>c>2&&c<L.cols-3&&r>0&&L.base[r*L.cols+c]===1&&L.base[(r-1)*L.cols+c]===0&&H.wearLevel(c*32+16,r*64+20)===W&&H.wearLevel(c*32+16,(r-1)*64+40)===W;
              const cand=[];for(let r=1;r<L.rows;r++)for(let c=3;c<L.cols-4;c++)if(ok(c,r)&&ok(c+1,r)&&ok(c+2,r)&&!H.isOpenArch(c,r-1)&&!H.isOpenArch(c+1,r-1)&&!H.isOpenArch(c+2,r-1))cand.push([c,r]);
              if(W===3){const bs=H.breaches().filter(b=>b&&b.open);if(bs.length){const b=bs[Math.floor(bs.length/2)];cand.unshift([Math.round((b.fx0+b.fx1)/64)-1,b.r]);}}
              if(!cand.length)continue;const [c,r]=cand[Math.floor(cand.length/2)];
              const Z=3,x0=c*32-24,y0=(r-1)*64-8,Wd=3*32+48,Hh=128+20;const cv=document.createElement('canvas');cv.width=Wd*Z;cv.height=Hh*Z;const g=cv.getContext('2d');g.fillStyle='#4a6a8a';g.fillRect(0,0,cv.width,cv.height);
              for(let ry=Math.floor(y0/192);ry<=Math.floor((y0+Hh)/192);ry++)for(let rx=Math.floor(x0/320);rx<=Math.floor((x0+Wd)/320);rx++){const rc=document.createElement('canvas');rc.width=320*Z;rc.height=192*Z;const rg=rc.getContext('2d');rg.setTransform(Z,0,0,Z,0,0);H.drawRoomStatic(rg,rx,ry);g.drawImage(rc,(rx*320-x0)*Z,(ry*192-y0)*Z);}
              return [cv.toDataURL(),L.theme.style];}return null;}''',[n,W])
            if u:
                im=Image.open(io.BytesIO(base64.b64decode(u[0].split(',')[1]))).convert('RGB');ImageDraw.Draw(im).text((6,4),f'{u[1]} · {["pristine","worn","damaged","partly fallen"][W]}',fill=(255,240,120),font=font);row.append(im)
            else: row.append(None)
        rows.append(row)
    w,h=[(i.width,i.height) for r in rows for i in r if i][0]
    sh=Image.new('RGB',(4*w+24,len(rows)*h+8*(len(rows)-1)),(0,0,0))
    for ri,r in enumerate(rows):
        for ci,im in enumerate(r):
            if im: sh.paste(im,(ci*(w+8),ri*(h+8)))
    sh.save(out);print(sh.size,errs[:3]);b.close()
