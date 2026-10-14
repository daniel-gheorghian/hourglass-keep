from playwright.sync_api import sync_playwright
import os,sys,base64
out,f=sys.argv[1],sys.argv[2]
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+os.path.abspath(f)); pg.wait_for_timeout(400); pg.evaluate("window.__HKfreeze=true")
    u=pg.evaluate('''()=>{const H=__HK;const L=H.load(8,700000+8*97,true);const o=L.dyn.find(o=>o.f.t==='spikes'&&o.f.fixed&&L.base[o.r*L.cols+o.c+1]===2&&L.base[(o.r-1)*L.cols+o.c]!==2);
      const Z=4,x0=o.c*32-40,y0=o.r*64-30,Wd=110,Hh=110;const cv=document.createElement('canvas');cv.width=Wd*Z;cv.height=Hh*Z;const g=cv.getContext('2d');
      for(let ry=Math.floor(y0/192);ry<=Math.floor((y0+Hh)/192);ry++)for(let rx=Math.floor(x0/320);rx<=Math.floor((x0+Wd)/320);rx++){const rc=document.createElement('canvas');rc.width=320*Z;rc.height=192*Z;const rg=rc.getContext('2d');rg.setTransform(Z,0,0,Z,0,0);H.drawRoomStatic(rg,rx,ry);g.drawImage(rc,(rx*320-x0)*Z,(ry*192-y0)*Z);}
      if(H.drawDynamic){g.save();g.setTransform(Z,0,0,Z,-x0*Z,-y0*Z);H.drawDynamic(g,x0,x0+Wd,y0,y0+Hh);g.restore();}
      return cv.toDataURL();}''')
    open(out,'wb').write(base64.b64decode(u.split(',')[1]));print(errs[:2]);b.close()
