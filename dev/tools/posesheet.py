from playwright.sync_api import sync_playwright
import sys,os
# posesheet.py out.png "js returning [[label,pose,face,opts]...]"  (H available)
out,js=sys.argv[1],sys.argv[2]
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1200,'height':400}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(300)
    pg.evaluate('''(js)=>{const H=__HK;const items=new Function('H','return ('+js+')')(H);document.body.innerHTML='';const c=document.createElement('canvas');const W=150,Hh=170;c.width=W*items.length;c.height=Hh;document.body.appendChild(c);
      const g=c.getContext('2d');g.fillStyle='#2a2430';g.fillRect(0,0,c.width,c.height);
      items.forEach(([lab,pose,face,o,wall],i)=>{g.save();g.translate(i*W+W/2,Hh-20);g.scale(2.4,2.4);
        if(wall!==undefined){g.fillStyle='#6a5444';g.fillRect(wall,-70,face*30,80);}
        g.strokeStyle='#555';g.lineWidth=0.3;g.beginPath();g.moveTo(-30,0);g.lineTo(30,0);g.stroke();
        H.drawFigureHD(g,0,0,face,pose,H.PAL_HERO,Object.assign({hasSword:true,time:0},o||{}));g.restore();
        g.fillStyle='#fff';g.font='12px sans-serif';g.fillText(lab,i*W+4,14);});
      window.__png=c.toDataURL();}''',js)
    import base64; d=pg.evaluate('window.__png'); open(out,'wb').write(base64.b64decode(d.split(',')[1])); print(errs[:2])
    b.close()
