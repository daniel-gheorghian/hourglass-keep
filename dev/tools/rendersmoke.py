from playwright.sync_api import sync_playwright
import sys, time
# rendersmoke.py lo hi [torch]: every floor renders without errors; with 'torch' the Lighting mode is Torchlight and the
# WebGL canvas must be live (the shader on) and not blank (checked by reading its pixels back right after a render)
lo,hi=int(sys.argv[1]),int(sys.argv[2]); torch=len(sys.argv)>3 and sys.argv[3]=='torch'
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':844,'height':390}); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(300); pg.add_script_tag(path='bot.js')
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    pg.evaluate("m=>{__HK.S.set.lightMode=m}",'torch' if torch else 'classic')  # Torchlight is the default: the plain run checks Classic
    res=[];tot=0;t0=time.time()
    for n in range(lo,hi+1):
        r=pg.evaluate('''([n,torch])=>{let k=0,ms=0,cnt=0,blank=0,off=0,chk=0;
          const H=__HK,look=()=>{const g=H.GLP;if(!H.shaderOn()||!g.gl){off++;return;}const gl=g.gl,w=g.cv.width,h=g.cv.height,px=new Uint8Array(w*h*4);gl.readPixels(0,0,w,h,gl.RGBA,gl.UNSIGNED_BYTE,px);
            let s=0,s2=0,m=0;for(let i=0;i<px.length;i+=64){const v=px[i]+px[i+1]+px[i+2];s+=v;s2+=v*v;m++;}const mean=s/m,vr=s2/m-mean*mean;chk++;if(mean<3||vr<4)blank++;};
          const r=runBot(n,31337+n,{fight:true,stop:H=>{if(++k%20===0){const t=performance.now();H.render();ms+=performance.now()-t;cnt++;if(torch&&cnt%4===1)look();}return false;}});
          return {ok:r.ok&&(!torch||(blank===0&&off===0&&chk>0)),why:r.why||(torch&&(blank||off)?'blank '+blank+' off '+off:undefined),ms:ms/Math.max(1,cnt)};}''',[n,torch])
        res.append((n,r['ok'],r.get('why'),round(r['ms'],2)))
    print(res); print('errors',errs[:5]); b.close()
