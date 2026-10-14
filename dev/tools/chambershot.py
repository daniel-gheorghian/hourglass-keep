# chambershot.py out.png n seed want [Z]: the rooms around the first turn chamber that holds the move `want` (e.g. collapse, jumpup,
# hgap), the moving parts drawn in, each piece of the chamber labelled. Run from dev/tools.
from playwright.sync_api import sync_playwright
import os,sys
out,n,seed,want=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),sys.argv[4];Z=float(sys.argv[5]) if len(sys.argv)>5 else 2
f='/Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'
JS='''([n,seed,want,Z])=>{const H=__HK;const L=H.load(n,seed,true);
  let groups=[],g=null;for(const q of L.segs){if(q.k.startsWith('turn-')){if(!g){g={segs:[]};groups.push(g);}g.segs.push(q);}else if(q.corr&&g)g.segs.push(q);else g=null;}
  const G=groups.find(x=>x.segs.some(q=>q.k==='turn-'+want));if(!G)return null;
  let c0=1e9,c1=-1e9,r0=1e9,r1=-1e9;for(const q of G.segs){c0=Math.min(c0,q.c0,q.c1);c1=Math.max(c1,q.c0,q.c1);r0=Math.min(r0,q.r0,q.r1);r1=Math.max(r1,q.r0,q.r1);}
  const x0=(c0-4)*32,x1=(c1+6)*32,y0=(r0-2)*64-8,y1=(r1+2)*64+8,Wd=x1-x0,Hh=y1-y0;
  const cv=document.createElement('canvas');cv.width=Wd*Z;cv.height=Hh*Z;const g2=cv.getContext('2d');g2.fillStyle='#000';g2.fillRect(0,0,cv.width,cv.height);
  for(let ry=Math.floor(y0/192);ry<=Math.floor(y1/192);ry++)for(let rx=Math.floor(x0/320);rx<=Math.floor(x1/320);rx++){const rc=document.createElement('canvas');rc.width=320*Z;rc.height=192*Z;const rg=rc.getContext('2d');rg.setTransform(Z,0,0,Z,0,0);H.drawRoomStatic(rg,rx,ry);g2.drawImage(rc,(rx*320-x0)*Z,(ry*192-y0)*Z);}
  g2.save();g2.setTransform(Z,0,0,Z,-x0*Z,-y0*Z);H.drawDynamic(g2,x0,x1,y0,y1);g2.restore();
  const labs=G.segs.map(q=>({k:q.k.replace('turn-',''),x:((q.c0+q.c1)/2*32+16-x0)*Z,y:(Math.min(q.r0,q.r1)*64+4-y0)*Z,corr:!!q.corr}));
  g2.font='bold '+Math.round(8*Z)+'px sans-serif';labs.forEach((l,i)=>{const w=g2.measureText(l.k).width,x=l.x,y=l.y-(10+(i%2)*10)*Z;g2.fillStyle='#000';g2.fillRect(x-w/2-3,y-5*Z,w+6,10*Z);g2.fillStyle=l.corr?'#96e6ff':'#ffe678';g2.fillText(l.k,x-w/2,y+3*Z);});
  return {u:cv.toDataURL(),steps:G.segs.filter(q=>!q.corr).map(q=>q.k).join(' ')};}'''
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+f); pg.wait_for_timeout(400); pg.evaluate("window.__HKfreeze=true")
    u=pg.evaluate(JS,[n,seed,want,Z]); b.close()
if not u: print('no chamber with',want,errs[:3]); sys.exit(1)
import base64
open(out,'wb').write(base64.b64decode(u['u'].split(',')[1]));print(out,u['steps'],errs[:2])
