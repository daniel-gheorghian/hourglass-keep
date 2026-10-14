from playwright.sync_api import sync_playwright
import base64,os,subprocess,shutil
d='vidframes';shutil.rmtree(d,ignore_errors=True);os.makedirs(d)
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=1); pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(400); pg.add_script_tag(path='bot.js')
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    k=0
    pg.evaluate('''()=>{window.__rec=[];let on=false,c=0;runBot(11,788,{fight:false,stop:H=>{const ch=H.L.ext.chase;if(!on&&ch&&ch.on&&ch.t>0.8)on=true;if(on){c++;if(c%2===0){H.render();window.__rec.push(document.getElementById('game').toDataURL('image/jpeg',0.85));}if(window.__rec.length>=150)return true;}return false;}});}''')
    for dd in pg.evaluate("window.__rec"):
        open(f'{d}/f{k:04d}.jpg','wb').write(base64.b64decode(dd.split(',')[1])); k+=1
    pg.evaluate('''()=>{const H=__HK;let L;for(let s=0;s<80;s++){L=H.load(10,700+s,false);if(H.SN.length)break;}const sn=H.SN[0];H.G.length=0;
      sn.x=Math.min(sn.hi-10,Math.max(sn.lo+60,sn.x));H.P.x=sn.x-70;H.P.y=sn.y;H.P.state='stand';H.P.face=1;H.P.inv=1e9;H.cam.snap=true;H.tick(2);sn.dir=-1;window.__rec=[];
      for(let i=0;i<300;i++){H.P.inv=1e9;if(i===40)H.P.x=sn.x-36;H.tick(1);if(i%2===0){H.render();window.__rec.push(document.getElementById('game').toDataURL('image/jpeg',0.85));}}}''')
    for dd in pg.evaluate("window.__rec"):
        open(f'{d}/f{k:04d}.jpg','wb').write(base64.b64decode(dd.split(',')[1])); k+=1
    print(k,errs); b.close()
subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','30','-i',f'{d}/f%04d.jpg','-vf','scale=844:-2,format=yuv420p','-c:v','libx264','-crf','22','-movflags','+faststart','storm_snake.mp4'],check=True)
from PIL import Image
ims=[Image.open('vidframes/f%04d.jpg'%i) for i in (60,170,220,270)]
w,h=ims[0].size;sh=Image.new('RGB',(2*w,2*h));[sh.paste(im,((i%2)*w,(i//2)*h)) for i,im in enumerate(ims)];sh.save('vidcheck.png')
print(os.path.getsize('storm_snake.mp4'))
