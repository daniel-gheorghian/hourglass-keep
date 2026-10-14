from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':844,'height':390}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(300)
    pg.evaluate("window.__HKfreeze=true")
    r=pg.evaluate('''()=>{const H=__HK,o=[];for(let n=1;n<=27;n++){const L=H.load(n,9000+n,true);let nb=0;for(const b of H.breaches())if(b)nb++;
       for(let k=0;k<L.cols;k+=25){H.P.x=k*32+16;H.cam.snap=true;H.tick(1);while(H.roomWork());H.render();}o.push(nb);}return o;}''')
    print(r, errs[:3]); b.close()
