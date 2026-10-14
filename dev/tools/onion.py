from playwright.sync_api import sync_playwright
import sys,os,base64
# onion.py out.png file n seed "start" "stop" every [scale] [title]
out,f,n,seed,start,stop,every=sys.argv[1],sys.argv[2],int(sys.argv[3]),int(sys.argv[4]),sys.argv[5],sys.argv[6],int(sys.argv[7])
sc=float(sys.argv[8]) if len(sys.argv)>8 else 3; title=sys.argv[9] if len(sys.argv)>9 else ''
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1200,'height':900}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+os.path.abspath(f)); pg.wait_for_timeout(300); pg.add_script_tag(path='bot.js')
    d=pg.evaluate('''([n,seed,start,stop,every,sc,title])=>{const H=__HK;const fr=[];let on=false,k=0;const ts=new Function('H','P','return ('+start+')'),tp=new Function('H','P','return ('+stop+')');
      runBot(n,seed,{fight:false,stop:H=>{const P=H.P;if(!on&&ts(H,P))on=true;if(!on)return false;if(k++%every===0)fr.push({x:P.x+(P.rdx||0),y:P.y+(P.rdy||0)+(P.yo||0),face:P.face,pose:Object.assign({},P.pose),st:P.state,pl:!!P.plant,sl:P.state==='slide',t:H.gameTime});return tp(H,P)||fr.length>80;}});
      const L=H.L;let x0=1e9,x1=-1e9,y0=1e9,y1=-1e9;for(const q of fr){x0=Math.min(x0,q.x);x1=Math.max(x1,q.x);y0=Math.min(y0,q.y-70);y1=Math.max(y1,q.y+6);}
      x0-=40;x1+=40;y0-=10;y1+=10;const W=Math.ceil((x1-x0)*sc),Hh=Math.ceil((y1-y0)*sc)+24;const c=document.createElement('canvas');c.width=W;c.height=Hh;const g=c.getContext('2d');
      g.fillStyle='#231d28';g.fillRect(0,0,W,Hh);g.save();g.translate(0,24);g.scale(sc,sc);g.translate(-x0,-y0);
      for(let r=Math.floor(y0/64);r<=Math.floor(y1/64);r++)for(let cc=Math.floor(x0/32);cc<=Math.floor(x1/32);cc++){const v=L.base[r*L.cols+cc];
        if(v===2){g.fillStyle='#7a6250';g.fillRect(cc*32,r*64,32,64);g.strokeStyle='#5a4638';g.lineWidth=0.5;g.strokeRect(cc*32+0.25,r*64+0.25,31.5,63.5);}
        else if(v===1){g.fillStyle='#9a8068';g.fillRect(cc*32,(r+1)*64-4,32,4);}
        const ft=L.feat[r*L.cols+cc];if(ft&&ft.t==='banner'){g.fillStyle='rgba(150,40,50,.5)';g.fillRect(cc*32+10,r*64,12,64);}}
      fr.forEach((q,i)=>{g.globalAlpha=i===fr.length-1?1:0.38+0.4*(i/fr.length);H.drawFigureHD(g,q.x,q.y,q.face,q.pose,H.PAL_HERO,{hasSword:true,time:0,sword:q.sl,swLen:9});
        g.globalAlpha=1;g.fillStyle=q.pl?'#ffdc60':'#9fd0ff';g.beginPath();g.arc(q.x,q.y-25,0.9,0,7);g.fill();});
      g.restore();g.fillStyle='#fff';g.font='14px sans-serif';g.fillText(title+'  ('+fr.length+' frames, every '+every+' ticks = '+(every/60).toFixed(3)+'s; yellow dot = planted)',6,17);
      return c.toDataURL();}''',[n,seed,start,stop,every,sc,title])
    open(out,'wb').write(base64.b64decode(d.split(',')[1])); print(errs[:2]); b.close()
