from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(400)
    print(pg.evaluate('''()=>{const H=__HK;const L=H.load(3,5555,true);const b=H.breaches().filter(Boolean)[5];
      const ox=-7*320,oy=0;const mk=(dx,dy)=>{const p=new Path2D();for(const pc of b.pieces){pc.forEach(([x,y],i)=>i?p.lineTo(x+ox+dx,y+oy+dy):p.moveTo(x+ox+dx,y+oy+dy));p.closePath();}return p;};
      const c=document.createElement('canvas');c.width=320;c.height=192;const g=c.getContext('2d');g.fillStyle='#fff';g.fillRect(0,0,320,192);const P=mk(0,0);
      const cnt=()=>{const d=g.getImageData(0,0,320,192).data;let tr=0;for(let i=3;i<d.length;i+=4)if(d[i]<20)tr++;return tr;};const r=[];
      g.save();g.globalCompositeOperation='destination-out';g.fillStyle='#000';g.fill(P);g.restore();r.push(cnt());
      g.save();g.clip(P);g.fillStyle='#333';g.fill(P);r.push(cnt());g.globalCompositeOperation='destination-out';g.fill(mk(5,-2.5));r.push(cnt());g.restore();r.push(cnt());
      return r;}'''))
    print(errs)
    b.close()
