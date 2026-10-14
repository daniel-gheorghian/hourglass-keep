from playwright.sync_api import sync_playwright
from PIL import Image
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2)
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(500)
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    ims=[]
    for i,n in enumerate([7,13]):
        pg.evaluate('''(n)=>{const H=__HK;const L=H.load(n,8000,false);const t=L.torches.find(t=>t.c>10&&[...Array(10)].every((_,k)=>{const c=t.c-6+k;return L.base[t.r*L.cols+c]!==2&&(L.base[t.r*L.cols+c]===1||L.base[(t.r+1)*L.cols+c]===2);}))||L.torches[3];
          H.G.length=0;const specs=[{tier:0},{tier:1},{tier:2},{cap:true,tier:2}];
          H.P.x=t.c*32-110;H.P.y=(t.r+1)*64-4;H.P.state='stand';H.P.face=1;H.cam.snap=true;H.tick(2);
          specs.forEach((sp,k)=>{const g={x:t.c*32-60+k*36,y:(t.r+1)*64-4,r:t.r,face:-1,alive:true,gone:false,state:'garde',t:0,tier:sp.tier,cap:!!sp.cap,pose:H.mk?H.mk({}):Object.assign({},H.PS.garde),flash:0,lo:0,hi:1e9};g.pose=Object.assign({},H.PS.garde);H.G.push(g);});
          H.P.x=t.c*32-110;H.cam.snap=true;H.tick(1);for(const g of H.G){g.state='garde';g.pose=Object.assign({},H.PS.garde);g.x=g.x;}H.render();}''',n)
        pg.screenshot(path=f'rk{i}.png'); ims.append(Image.open(f'rk{i}.png'))
    w,h=ims[0].size; sh=Image.new('RGB',(w,2*h+10));sh.paste(ims[0],(0,0));sh.paste(ims[1],(0,h+10));sh.resize((w//2,(2*h+10)//2)).save('ranks.png'); print(errs); b.close()
