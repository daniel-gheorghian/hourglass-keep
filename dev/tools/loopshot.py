from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont
import io,os,sys,base64,json
# loopshot.py out.png file n seed [loopIndex] [Z]: the static rooms and moving parts around one loop, labelled
out,f,n,seed=sys.argv[1],sys.argv[2],int(sys.argv[3]),int(sys.argv[4]);li=int(sys.argv[5]) if len(sys.argv)>5 else 0;Z=float(sys.argv[6]) if len(sys.argv)>6 else 2
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+os.path.abspath(f)); pg.wait_for_timeout(400); pg.evaluate("window.__HKfreeze=true")
    u=pg.evaluate('''([n,seed,li,Z])=>{const H=__HK;const L=H.load(n,seed,true);const q=L.loops[li];if(!q)return null;
      const cs=[q.H,q.O,q.gate.c,q.plate.c],x0=(Math.min(...cs)-6)*32,x1=(Math.max(...cs)+7)*32,y0=(q.rUp-1)*64-8,y1=(q.rLow+1)*64+8,Wd=x1-x0,Hh=y1-y0;
      const cv=document.createElement('canvas');cv.width=Wd*Z;cv.height=Hh*Z;const g=cv.getContext('2d');g.fillStyle='#000';g.fillRect(0,0,cv.width,cv.height);
      for(let ry=Math.floor(y0/192);ry<=Math.floor(y1/192);ry++)for(let rx=Math.floor(x0/320);rx<=Math.floor(x1/320);rx++){const rc=document.createElement('canvas');rc.width=320*Z;rc.height=192*Z;const rg=rc.getContext('2d');rg.setTransform(Z,0,0,Z,0,0);H.drawRoomStatic(rg,rx,ry);g.drawImage(rc,(rx*320-x0)*Z,(ry*192-y0)*Z);}
      g.save();g.setTransform(Z,0,0,Z,-x0*Z,-y0*Z);H.drawDynamic(g,x0,x1,y0,y1);g.restore();
      const P=(c,r)=>[(c*32+16-x0)*Z,((r+1)*64-4-y0)*Z];
      return {u:cv.toDataURL(),hole:P(q.H,q.rUp),gate:P(q.gate.c,q.gate.r),plate:P(q.plate.c,q.plate.r),dir:q.dir,h:q.rLow-q.rUp,theme:L.theme.name,lad:P(q.H-q.dir*4,Math.round((q.rUp+q.rLow)/2))};}''',[n,seed,li,Z])
    b.close()
if not u: print('no loop',errs[:3]); sys.exit()
im=Image.open(io.BytesIO(base64.b64decode(u['u'].split(',')[1]))).convert('RGB');d=ImageDraw.Draw(im)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',int(9*Z))
def lab(xy,t,dy=-18):
    x,y=xy;y+=dy*Z/2;tw=d.textlength(t,font=font);d.rectangle([x-tw/2-4,y-int(6*Z),x+tw/2+4,y+int(6*Z)],fill=(0,0,0));d.text((x-tw/2,y-int(5*Z)),t,fill=(255,230,120),font=font)
lab(u['hole'],'shortcut hole',-30);lab(u['plate'],'violet plate',-30);lab(u['gate'],'violet gate',-48);lab(u['lad'],'ledges, both ways',0)
im.save(out);print(im.size,u['theme'],'h',u['h'],errs[:3])
