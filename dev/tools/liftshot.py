# liftshot.py out.png n seed want frac [Z] [alone]: the chamber around the first lift of kind `want` (lift2d, lift3u, chn2d ...). A
# counterweight lift: the platform frac of the way down its shaft (0 top, 1 bottom), the prince standing on it (not with `alone`).
# A chain-loop lift: frac is the clock time to draw it at (seconds), the prince riding slab 0. Run from dev/tools.
from playwright.sync_api import sync_playwright
import sys,base64
out,n,seed,want,frac=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),sys.argv[4],float(sys.argv[5]);Z=float(sys.argv[6]) if len(sys.argv)>6 else 2;alone=len(sys.argv)>7
f='/Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'
JS='''([n,seed,want,frac,Z,alone])=>{const H=__HK;const L=H.load(n,seed,true);
  const sg=L.segs.find(q=>q.k==='turn-'+want);if(!sg)return null;
  const lf=L.lifts.find(q=>q.ca>=Math.min(sg.c0,sg.c1)-1&&q.cb<=Math.max(sg.c0,sg.c1)+1&&q.rT>=Math.min(sg.r0,sg.r1)&&q.rB<=Math.max(sg.r0,sg.r1));const P=H.P;
  if(lf.t==='lift'){lf.y=lf.yT+(lf.yB-lf.yT)*frac;P.x=lf.sc*32+16;P.y=lf.y;P.state='stand';P.face=1;
    // the mouth cell's floor follows the platform, as updateLift does
    L.base[lf.rT*L.cols+lf.sc]=frac===0?1:0;lf.gT=frac===0?1:0;lf.gB=frac===1?1:0;if(alone){P.x=-999;}}
  else{H.tick(Math.round(frac*60));const q=H.chainPos(lf,0,H.gameTime);P.x=q.x;P.y=q.y;P.state='lift';P.lift=lf;P.slab=0;P.bx=q.x;P.by=q.y;P.bt=0;}
  const c0=lf.ca-5,c1=lf.cb+6,r0=lf.rT-1,r1=lf.rB+1;
  const x0=c0*32,x1=c1*32,y0=r0*64-8,y1=r1*64+8,Wd=x1-x0,Hh=y1-y0;
  const cv=document.createElement('canvas');cv.width=Wd*Z;cv.height=Hh*Z;const g2=cv.getContext('2d');g2.fillStyle='#000';g2.fillRect(0,0,cv.width,cv.height);
  for(let ry=Math.floor(y0/192);ry<=Math.floor(y1/192);ry++)for(let rx=Math.floor(x0/320);rx<=Math.floor(x1/320);rx++){const rc=document.createElement('canvas');rc.width=320*Z;rc.height=192*Z;const rg=rc.getContext('2d');rg.setTransform(Z,0,0,Z,0,0);H.drawRoomStatic(rg,rx,ry);g2.drawImage(rc,(rx*320-x0)*Z,(ry*192-y0)*Z);}
  g2.save();g2.setTransform(Z,0,0,Z,-x0*Z,-y0*Z);H.drawDynamic(g2,x0,x1,y0,y1);g2.restore();
  return {u:cv.toDataURL(),k:lf.k};}'''
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+f); pg.wait_for_timeout(400); pg.evaluate("window.__HKfreeze=true")
    u=pg.evaluate(JS,[n,seed,want,frac,Z,alone]); b.close()
if not u: print('no',want,errs[:3]); sys.exit(1)
open(out,'wb').write(base64.b64decode(u['u'].split(',')[1]));print(out,u['k'],errs[:2])
