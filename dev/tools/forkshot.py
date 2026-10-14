# forkshot.py out.png n seed [index] [Z]: the fork `index` (default 0) of floor n: the stretch of the upper run round the hole, the
# chamber under it and the lower run's foot, drawn from the room caches. Run from dev/tools.
from playwright.sync_api import sync_playwright
import sys,base64
out,n,seed=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]);idx=int(sys.argv[4]) if len(sys.argv)>4 else 0;Z=float(sys.argv[5]) if len(sys.argv)>5 else 1.5
f='/Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'
JS='''([n,seed,idx,Z])=>{const H=__HK;const L=H.load(n,seed,true);const q=L.forks[idx];if(!q)return null;
  const a=Math.min(q.H,q.Xl),b=Math.max(q.H,q.Xl);const c0=a-4,c1=b+5,r0=q.rUp-1,r1=q.rLow+1;
  const x0=c0*32,x1=c1*32,y0=r0*64-8,y1=r1*64+8,Wd=x1-x0,Hh=y1-y0;
  const cv=document.createElement('canvas');cv.width=Wd*Z;cv.height=Hh*Z;const g2=cv.getContext('2d');g2.fillStyle='#000';g2.fillRect(0,0,cv.width,cv.height);
  for(let ry=Math.floor(y0/192);ry<=Math.floor(y1/192);ry++)for(let rx=Math.floor(x0/320);rx<=Math.floor(x1/320);rx++){const rc=document.createElement('canvas');rc.width=320*Z;rc.height=192*Z;const rg=rc.getContext('2d');rg.setTransform(Z,0,0,Z,0,0);H.drawRoomStatic(rg,rx,ry);g2.drawImage(rc,(rx*320-x0)*Z,(ry*192-y0)*Z);}
  g2.save();g2.setTransform(Z,0,0,Z,-x0*Z,-y0*Z);H.drawDynamic(g2,x0,x1,y0,y1);g2.restore();
  return {u:cv.toDataURL(),v:q.v,g:q.grate};}'''
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+f); pg.wait_for_timeout(400); pg.evaluate("window.__HKfreeze=true")
    u=pg.evaluate(JS,[n,seed,idx,Z]); b.close()
if not u: print('no fork',errs[:3]); sys.exit(1)
open(out,'wb').write(base64.b64decode(u['u'].split(',')[1]));print(out,'kind',u['v'],'grate',u['g'],errs[:2])
