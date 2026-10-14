from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(400)
    print(pg.evaluate('''()=>{const H=__HK;const L=H.load(3,5555,true);
      const c=document.createElement('canvas');c.width=320;c.height=192;const g=c.getContext('2d');g.fillStyle='#fff';g.fillRect(0,0,320,192);
      const cnt=()=>{const d=g.getImageData(0,0,320,192).data;let tr=0;for(let i=3;i<d.length;i+=4)if(d[i]<20)tr++;return tr;};
      const log=[];const orig={fill:g.fill.bind(g)};const proto=CanvasRenderingContext2D.prototype;
      const of=proto.fill;g.fill=function(...a){of.apply(this,a);log.push(['fill',this.globalCompositeOperation,String(this.fillStyle).slice(0,30),cnt()]);};
      H.drawBreaches(g,7,0,L.theme,true);return log.slice(0,12);}'''))
    print(errs)
    b.close()
