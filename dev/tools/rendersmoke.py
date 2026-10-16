from playwright.sync_api import sync_playwright
import sys, time
from slowguard import SlowGuard
# rendersmoke.py lo hi [torch|both]: every floor renders without errors. With 'torch' the Lighting mode is Torchlight and the
# WebGL canvas must be live (the shader on) and not blank (checked by reading its pixels back right after a render). With 'both'
# the floor is played once: Classic every 20th frame, Torchlight once per room entered (and every 600 frames), every torch
# render checked as above; that is what suite.py runs. Without either: Classic only.
lo,hi=int(sys.argv[1]),int(sys.argv[2]); mode=sys.argv[3] if len(sys.argv)>3 else 'classic'; assert mode in ('classic','torch','both'),mode
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':844,'height':390}); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(300); pg.add_script_tag(path='bot.js')
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    pg.evaluate("m=>{__HK.S.set.lightMode=m}",'torch' if mode=='torch' else 'classic')  # Torchlight is the default: the plain run checks Classic
    res=[];tot=0;t0=time.time();guard=SlowGuard('rendersmoke',ms=4,wall=240)  # (healthy: about 1.1 ms/frame with the renders and the WebGL readbacks)
    for n in range(lo,hi+1):
        r=guard.run(pg,'''([n,mode])=>{let k=0,ms=0,cnt=0,mcnt=0,blank=0,off=0,chk=0,torch=mode!=='classic',both=mode==='both';
          const H=__HK,look=()=>{const g=H.GLP;if(!H.shaderOn()||!g.gl){off++;return;}const gl=g.gl,w=g.cv.width,h=g.cv.height,px=new Uint8Array(w*h*4);gl.readPixels(0,0,w,h,gl.RGBA,gl.UNSIGNED_BYTE,px);
            let s=0,s2=0,m=0;for(let i=0;i<px.length;i+=64){const v=px[i]+px[i+1]+px[i+2];s+=v;s2+=v*v;m++;}const mean=s/m,vr=s2/m-mean*mean;chk++;if(mean<3||vr<4)blank++;};
          // in 'both': Classic every 20th frame; Torchlight (software WebGL here, ~145 ms of CPU a frame) once each time the
          // view enters a new room and at least every 600 frames, each one read back. The shader is the same code every
          // frame, so that covers every scene it draws at a small fraction of the cost. Two renders: Torchlight sends a frame
          // to WebGL at the start of the next render (v52), so the second one draws the first's picture before it is read.
          let room='',lastT=-1e9;
          const r=runBot(n,31337+n,{fight:true,stop:H=>{++k;
            if(both){const c=H.cam,rm=Math.floor((c.x+H.viewW/2)/320)+','+Math.floor((c.y+96)/192);
              if(rm!==room||k-lastT>=600){room=rm;lastT=k;H.S.set.lightMode='torch';H.render();H.render();look();H.S.set.lightMode='classic';}}
            if(k%20===0){cnt++;
              const t=performance.now();H.render();const dt=performance.now()-t;ms+=dt;mcnt++;
              if(torch&&!both&&cnt%4===1){H.render();look();}}
            return false;}});
          return {ok:r.ok&&(!torch||(blank===0&&off===0&&chk>0)),why:r.why||(torch&&(blank||off)?'blank '+blank+' off '+off:undefined),ms:ms/Math.max(1,mcnt),frames:r.frames};}''',[n,mode],'floor %d'%n)
        res.append((n,r['ok'],r.get('why'),round(r['ms'],2)))
    print(res); print('errors',errs[:5]); b.close()
sys.exit(guard.finish(True))
