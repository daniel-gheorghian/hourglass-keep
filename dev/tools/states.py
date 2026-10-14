from playwright.sync_api import sync_playwright
from PIL import Image
want=['swing','wallrun','slide','push','pull','crouch','climb','air','land','drink','strike','hurt']
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2)
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(400); pg.add_script_tag(path='bot.js')
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    got={}
    for n in range(6,26):
        left=[w for w in want if w not in got]
        if not left: break
        r=pg.evaluate('''([n,left])=>{let st=null,k=0;const res=runBot(n,6600+n,{fight:true,stop:H=>{const s=H.P.state;if(left.includes(s)&&H.P.t>(s==='crouch'?0.5:s==='air'?0.15:0.12)&&(s!=='crouch'||H.P.crawling)){st=s;return true;}return false;}});
          if(!st)return null;const H=__HK;H.render();const cam=H.cam,rc=document.getElementById('game').getBoundingClientRect(),sc=rc.height/192;
          let x=rc.left+(H.P.x-cam.x-55)*sc,y=rc.top+(H.P.y-cam.y-90)*sc;const w=110*sc,h=110*sc;x=Math.max(0,Math.min(innerWidth-w,x));y=Math.max(0,Math.min(innerHeight-h,y));return {st,clip:{x,y,width:w,height:h}};}''',[n,left])
        if r:
            pg.screenshot(path=f'st_{r["st"]}.png',clip=r['clip']); got[r['st']]=f'st_{r["st"]}.png'; print(n,r['st'])
    ims=[Image.open(got[w]) for w in want if w in got]; w,h=ims[0].size; cols=6; rows=(len(ims)+cols-1)//cols
    sh=Image.new('RGB',(cols*(w+6),rows*(h+6)),(0,0,0))
    for i,im in enumerate(ims): sh.paste(im,((i%cols)*(w+6),(i//cols)*(h+6)))
    sh.resize((sh.width//2,sh.height//2)).save('states.png'); print('missing',[w for w in want if w not in got],errs); b.close()
