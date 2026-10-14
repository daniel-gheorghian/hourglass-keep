from playwright.sync_api import sync_playwright
import sys,os,base64,json
# chrono.py out.png sc  panel-json...   panel = {"f":file,"n":..,"seed":..,"start":js,"stop":js,"every":ticks,"K":px/s,"title":..,"tmax":s}
out,sc=sys.argv[1],float(sys.argv[2]);panels=[json.loads(a) for a in sys.argv[3:]]
imgs=[]
with sync_playwright() as p:
    b=p.chromium.launch(); errs=[]
    for pn in panels:
        pg=b.new_page(viewport={'width':1200,'height':900}); pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.goto('file://'+os.path.abspath(pn['f'])); pg.wait_for_timeout(300); pg.add_script_tag(path='bot.js')
        d=pg.evaluate('''([pn,sc])=>{const H=__HK;const tr=[];let on=false,k=0;const ts=new Function('H','P','return ('+pn.start+')'),tp=new Function('H','P','return ('+pn.stop+')');let t0=0;
          runBot(pn.n,pn.seed,{fight:false,stop:H=>{const P=H.P;if(!on&&ts(H,P)){on=true;t0=H.gameTime;}if(!on)return false;
            tr.push({t:H.gameTime-t0,y:P.y+(P.yo||0),face:P.face,pose:Object.assign({},P.pose),pl:!!P.plant,st:P.state,wt:H.wallTouch(),sl:P.state==='slide'&&pn.sword!==false});return tp(H,P)||H.gameTime-t0>(pn.tmax||4);}});
          const K=pn.K,yb=Math.max(...tr.map(q=>q.y))+8,yt=Math.min(...tr.map(q=>q.y))-66,W=Math.ceil((tr[tr.length-1].t*K+60)*sc),Hh=Math.ceil((yb-yt)*sc)+40;
          const c=document.createElement('canvas');c.width=W;c.height=Hh;const g=c.getContext('2d');g.fillStyle='#1e1a24';g.fillRect(0,0,W,Hh);
          g.save();g.translate(0,26);g.scale(sc,sc);g.translate(30,-yt);
          // storeys
          for(let r=Math.floor(yt/64);r<=Math.floor(yb/64)+1;r++){const y=(r+1)*64-4;g.strokeStyle='rgba(255,255,255,.10)';g.lineWidth=0.6;g.beginPath();g.moveTo(-30,y);g.lineTo(W,y);g.stroke();}
          // seconds
          for(let s=0;s<=tr[tr.length-1].t+0.01;s+=0.5){g.strokeStyle='rgba(255,255,255,.08)';g.beginPath();g.moveTo(s*K,yt);g.lineTo(s*K,yb);g.stroke();g.fillStyle='rgba(255,255,255,.45)';g.font='7px sans-serif';g.fillText(s.toFixed(1)+'s',s*K+1,yb-1);}
          let lastF=-1e9;tr.forEach((q,i)=>{if(i%pn.every)return;const x=q.t*K;H.drawFigureHD(g,x,q.y,q.face,q.pose,H.PAL_HERO,{hasSword:true,time:0,sword:q.sl,swLen:9});});
          for(let i=1;i<tr.length;i++){const a=tr[i-1],q=tr[i];g.strokeStyle=q.pl?'#ffd34d':(q.wt?'#ff8a5c':'#7fc4ff');g.lineWidth=1.4;g.beginPath();g.moveTo(a.t*K,a.y-25);g.lineTo(q.t*K,q.y-25);g.stroke();}
          g.restore();g.fillStyle='#fff';g.font='15px sans-serif';g.fillText(pn.title,8,18);return c.toDataURL();}''',[pn,sc])
        imgs.append(d); pg.close()
    b.close()
from PIL import Image
import io
ims=[Image.open(io.BytesIO(base64.b64decode(d.split(',')[1]))) for d in imgs]
W=max(i.width for i in ims);H=sum(i.height for i in ims)+6*(len(ims)-1)
sh=Image.new('RGB',(W,H),(10,8,12));y=0
for i in ims: sh.paste(i,(0,y)); y+=i.height+6
sh.save(out);print(sh.size,errs[:2])
