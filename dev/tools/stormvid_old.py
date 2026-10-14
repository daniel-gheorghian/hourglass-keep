from playwright.sync_api import sync_playwright
import base64,os,subprocess,shutil,sys,json
# play a chase floor with the test bot; film the last stretch of the chase and the storm breaking up
out=sys.argv[1] if len(sys.argv)>1 else 'storm_end.mp4'; n=int(sys.argv[2]) if len(sys.argv)>2 else 11; seed=int(sys.argv[3]) if len(sys.argv)>3 else 788
d='stvframes_old';shutil.rmtree(d,ignore_errors=True);os.makedirs(d)
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=1); pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///tmp/claude-0/-home-claude-hourglass-keep/f01bc65f-8e08-5e8f-8f80-4fcb704e8720/scratchpad/hk_v31_release.html'); pg.wait_for_timeout(500); pg.add_script_tag(path='bot.js')
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay');__HK.S.set.gfx.atmo=true")
    info=pg.evaluate('''([n,seed])=>{window.__fr=[];let k=0,after=0;const r=runBot(n,seed,{fight:false,stop:H=>{const c=H.L.ext.chase;if(!c||!c.on)return false;
        if(H.P.x<(c.c1-14)*32&&!c.done)return false;k++;
        if(c.done)after++;if(k%2===0){H.render();window.__fr.push(document.getElementById('game').toDataURL('image/jpeg',0.86));}
        return after>60*4.2;}});const c=__HK.L.ext.chase;return {r:JSON.stringify(r).slice(0,200),frames:window.__fr.length,c1:c&&c.c1,diss:c&&JSON.stringify(c.diss)};}''',[n,seed])
    print(info)
    frames=pg.evaluate('window.__fr')
    for i,dd in enumerate(frames): open(f'{d}/f{i:04d}.jpg','wb').write(base64.b64decode(dd.split(',')[1]))
    print(len(frames),errs[:3]); b.close()
subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','30','-i',f'{d}/f%04d.jpg','-vf','scale=844:-2,format=yuv420p','-c:v','libx264','-crf','21','-movflags','+faststart',out],check=True)
print(os.path.getsize(out))
