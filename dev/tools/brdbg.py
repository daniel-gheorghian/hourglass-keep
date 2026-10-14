from playwright.sync_api import sync_playwright
import os,sys
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e))); pg.on('console',lambda m:print('LOG',m.text))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(400)
    print(pg.evaluate('''()=>{const H=__HK;const L=H.load(3,5555+0*11,true);const bs=H.breaches().filter(Boolean);const h=bs[5]||bs[0];
      const pc=h.pieces[0];const cx=(pc[0][0]+pc[1][0])/2,cy=(pc[0][1]+pc[2][1])/2;const rx=Math.floor(cx/320),ry=Math.floor(cy/192);
      const c=document.createElement('canvas');c.width=320;c.height=192;const g=c.getContext('2d');H.drawRoomStatic(g,rx,ry,0);
      const d=g.getImageData(Math.round(cx-rx*320),Math.round(cy-ry*192),1,1).data;
      return {c0:h.c0,c1:h.c1,r:h.r,npieces:h.pieces.length,pc,cx,cy,rx,ry,px:[...d],inB:H.inBreach(cx,cy),bgOn:true};}'''))
    print(errs)
    b.close()
