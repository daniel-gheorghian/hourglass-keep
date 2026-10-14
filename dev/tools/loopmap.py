# a whole floor's map with its loop drawn over it: the long way (the key's arc) and the shortcut (the ladder)
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont
import base64,sys,os,io
f,out,n,seed=sys.argv[1],sys.argv[2],int(sys.argv[3]),int(sys.argv[4]);tw=int(sys.argv[5]) if len(sys.argv)>5 else 3
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+os.path.abspath(f)); pg.wait_for_timeout(300)
    u=pg.evaluate('''([n,seed,tw])=>{const H=__HK,L=H.genLevel(n,seed,true),th=tw*2,cv=document.createElement('canvas');cv.width=L.cols*tw;cv.height=L.rows*th;const g=cv.getContext('2d');
      g.fillStyle='#2a2630';g.fillRect(0,0,cv.width,cv.height);
      for(let r=0;r<L.rows;r++)for(let c=0;c<L.cols;c++){const b=L.base[r*L.cols+c];if(b===2)continue;g.fillStyle=b===1?'#8f877a':'#5d574e';g.fillRect(c*tw,r*th,tw,th);
        const below=r+1<L.rows?L.base[(r+1)*L.cols+c]:2;if(b===1||below===2){g.fillStyle='#c9bfa8';g.fillRect(c*tw,r*th+th-2,tw,2);}}
      g.fillStyle='#00ff00';g.fillRect(L.start.x/32*tw-tw,L.start.r*th,tw*2,th);g.fillStyle='#ffffff';g.fillRect(L.door.c*tw-tw,L.door.r*th,tw*3,th);
      const X=c=>(c+0.5)*tw,Y=r=>(r+0.7)*th,line=(pts,col,w,dash)=>{g.strokeStyle=col;g.lineWidth=w;g.setLineDash(dash||[]);g.beginPath();pts.forEach(([c,r],i)=>i?g.lineTo(X(c),Y(r)):g.moveTo(X(c),Y(r)));g.stroke();g.setLineDash([]);};
      const res=[];
      for(const q of L.loops){const up=L.runsInfo[q.t],lo=L.runsInfo[q.t+1];
        line([[q.H,q.rUp],[up.c1,up.row],[lo.c0,lo.row],[q.gate.c,q.gate.r]],'#ffb347',tw*1.4);
        line([[q.H,q.rUp],[q.H,q.rLow],[q.gate.c,q.gate.r]],'#7fd4ff',tw*1.4,[tw*2,tw*1.5]);
        g.fillStyle='#a77ee6';g.fillRect(X(q.plate.c)-tw*1.5,Y(q.plate.r)-th,tw*3,th*1.4);g.fillRect(X(q.gate.c)-tw,Y(q.gate.r)-th*2,tw*2,th*2.4);
        res.push({x0:Math.min(q.H,up.c1,lo.c0,q.gate.c)*tw,x1:Math.max(q.H,up.c1,lo.c0,q.gate.c)*tw,y0:(q.rUp-3)*th,y1:(q.rLow+3)*th,plate:[X(q.plate.c),Y(q.plate.r)],gate:[X(q.gate.c),Y(q.gate.r)],hole:[X(q.H),Y(q.rUp)]});}
      return [cv.toDataURL(),res,L.cols,L.rows];}''',[n,seed,tw])
    b.close()
im=Image.open(io.BytesIO(base64.b64decode(u[0].split(',')[1]))).convert('RGB');print(u[2:],len(u[1]),errs[:2])
im.save(out)
# a close crop of the first loop, labelled
if u[1]:
    q=u[1][0];x0=max(0,int(q['x0'])-90);x1=min(im.width,int(q['x1'])+90);y0=max(0,int(q['y0'])-10);y1=min(im.height,int(q['y1'])+10)
    k=4;cr=im.crop((x0,y0,x1,y1)).resize(((x1-x0)*k,(y1-y0)*k),Image.NEAREST);d=ImageDraw.Draw(cr)
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',18)
    def lab(pt,t,dx=0,dy=-26,col=(255,235,150)):
        x=(pt[0]-x0)*k+dx;y=(pt[1]-y0)*k+dy;tw=d.textlength(t,font=font);d.rectangle([x-tw/2-5,y-12,x+tw/2+5,y+12],fill=(20,16,26));d.text((x-tw/2,y-11),t,fill=col,font=font)
    lab(q['plate'],'violet plate');lab(q['hole'],'hole',0,-30);lab(q['gate'],'violet gate',0,34)
    d.rectangle([8,8,560,64],fill=(20,16,26));d.text((16,12),'orange: the long way (plate on it)',fill=(255,179,71),font=font);d.text((16,38),'blue: the shortcut (ledges, both ways)',fill=(127,212,255),font=font)
    cr.save(out.replace('.png','_crop.png'));print('crop',cr.size)
