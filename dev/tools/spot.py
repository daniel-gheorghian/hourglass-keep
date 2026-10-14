from playwright.sync_api import sync_playwright
import sys,base64,os
# spot.py out.png file n seed c r [face] : stand the prince at (c,r) and render the screen
out,f,n,seed,c,r=sys.argv[1],sys.argv[2],int(sys.argv[3]),int(sys.argv[4]),int(sys.argv[5]),int(sys.argv[6]);face=int(sys.argv[7]) if len(sys.argv)>7 else 1
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':844,'height':390},device_scale_factor=2); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+os.path.abspath(f)); pg.wait_for_timeout(400)
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    pg.evaluate('''([n,seed,c,r,face])=>{const H=__HK;H.load(n,seed,true);const P=H.P;P.x=c*32+16;P.y=(r+1)*64-4;P.face=face;H.cam.snap=true;H.tick(30);H.render();}''',[n,seed,c,r,face])
    pg.screenshot(path=out); print(errs[:2]); b.close()
