from playwright.sync_api import sync_playwright
import base64
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(400)
    u=pg.evaluate('''()=>{const H=__HK;const L=H.load(15,5555+2*11,true);const bs=H.breaches().filter(Boolean);const h=bs[Math.floor(bs.length/2)];
      const rx=Math.floor((h.x0+h.x1)/2/320),ry=Math.floor(h.y1/192);
      const c=document.createElement('canvas');c.width=960;c.height=576;const g=c.getContext('2d');g.setTransform(3,0,0,3,0,0);g.fillStyle='#fff';g.fillRect(0,0,320,192);
      H.drawBreaches(g,rx,ry,L.theme,true);const o=document.createElement('canvas');o.width=960;o.height=576;const og=o.getContext('2d');og.fillStyle='#f0f';og.fillRect(0,0,960,576);og.drawImage(c,0,0);return o.toDataURL();}''')
    open('brdbg7.png','wb').write(base64.b64decode(u.split(',')[1]))
    print(errs)
    b.close()
