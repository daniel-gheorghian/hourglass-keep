from playwright.sync_api import sync_playwright
import base64,os,subprocess,shutil
d='ambframes';shutil.rmtree(d,ignore_errors=True);os.makedirs(d)
scenes=[(2,8003,None),(7,8000,(249,6)),(10,8000,(120,5)),(14,8001,None),(18,8000,(51,3))]
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=1); pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(500)
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    k=0
    for n,sd,tp in scenes:
        frames=pg.evaluate('''([n,sd,tp])=>{const H=__HK;const L=H.load(n,sd,false);H.G.length=0;let x,r;if(tp){x=tp[0]*32-30;r=tp[1];}else{const t=L.torches.find(t=>t.c>8);x=t.c*32-30;r=t.r;}
          H.P.x=x;H.P.y=(r+1)*64-4;H.P.fallY=H.P.y;H.P.state='stand';H.P.face=1;H.P.inv=1e9;H.cam.snap=true;H.tick(2);H.mode='play';
          for(let i=0;i<60*8;i++){H.P.x=x;H.P.state='stand';H.P.inv=1e9;H.tick(1);}const out=[];
          for(let i=0;i<150;i++){H.P.x=x;H.P.state='stand';H.P.inv=1e9;H.tick(2);H.render();out.push(document.getElementById('game').toDataURL('image/jpeg',0.85));}return out;}''',[n,sd,tp])
        for dd in frames:
            open(f'{d}/f{k:04d}.jpg','wb').write(base64.b64decode(dd.split(',')[1])); k+=1
    print(k,errs); b.close()
subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','30','-i',f'{d}/f%04d.jpg','-vf','scale=844:-2,format=yuv420p','-c:v','libx264','-crf','21','-movflags','+faststart','ambient.mp4'],check=True)
print(os.path.getsize('ambient.mp4'))
