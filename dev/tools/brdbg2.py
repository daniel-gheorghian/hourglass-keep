from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(400)
    print(pg.evaluate('''()=>{const H=__HK;const L=H.load(3,5555,true);const bs=H.breaches().filter(Boolean);const h=bs[5];
      const out=[];for(const st of [0]){const c=document.createElement('canvas');c.width=320;c.height=192;const g=c.getContext('2d');
       H.drawRoomStatic(g,7,0,0);const d=g.getImageData(0,0,320,192).data;let tr=0;for(let i=3;i<d.length;i+=4)if(d[i]<20)tr++;out.push(tr);}
      // breaches touching room 7,0
      const touching=H.breaches().filter(b=>b&&b.x1>7*320&&b.x0<8*320&&b.y0<192).map(b=>[b.c0,b.c1,b.r,Math.round(b.y0),Math.round(b.y1)]);
      return {out,touching};}'''))
    print(errs)
    b.close()
