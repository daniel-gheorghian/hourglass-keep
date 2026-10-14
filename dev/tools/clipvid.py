from playwright.sync_api import sync_playwright
import io,base64,os,subprocess,shutil
d='vidframes';shutil.rmtree(d,ignore_errors=True);os.makedirs(d)
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=1); pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(400); pg.add_script_tag(path='bot.js')
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    k=0
    for n,seed,start,count in [(11,788,"(()=>{const c=H.L.ext.chase;return c&&c.on&&c.t>0.8;})()",150),(9,4109,"H.SN.some(s=>s.alive&&Math.abs(s.x-H.P.x)<90&&s.r===Math.floor((H.P.y-1)/64))",150)]:
        pg.evaluate('''([n,seed,start,count])=>{const f=new Function('H','return '+start);window.__rec=[];let on=false,k=0;
          runBot(n,seed,{fight:true,stop:H=>{if(!on&&f(H))on=true;if(on){k++;if(k%2===0){H.render();window.__rec.push(document.getElementById('game').toDataURL('image/jpeg',0.85));}if(window.__rec.length>=count)return true;}return false;}});}''',[n,seed,start,count])
        for dd in pg.evaluate("window.__rec"):
            open(f'{d}/f{k:04d}.jpg','wb').write(base64.b64decode(dd.split(',')[1])); k+=1
    print(k,errs); b.close()
subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','30','-i',f'{d}/f%04d.jpg','-vf','scale=844:-2,format=yuv420p','-c:v','libx264','-crf','22','-movflags','+faststart','storm_snake.mp4'],check=True)
print(os.path.getsize('storm_snake.mp4'))
