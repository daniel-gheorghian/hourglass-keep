from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=3,is_mobile=True,has_touch=True)
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(500)
    pg.evaluate("""()=>{window.__tp=[];window.addEventListener('touchstart',e=>window.__tp.push([e.target.closest('[id]').id,e.defaultPrevented]));
      document.querySelectorAll('.screen').forEach(e=>e.hidden=true);__HK.load(3,4242,true);}""")
    pg.wait_for_timeout(300)
    cdp=ctx.new_cdp_session(pg)
    def rect(sel): return pg.evaluate("s=>{const r=document.querySelector(s).getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2,r.width]}",sel)
    px,py,pw=rect('#pad'); gx,gy,_=rect('#bGrab'); bx,by,_=rect('#bPause')
    x0=pg.evaluate('()=>__HK.P.x')
    # long-press right on the d-pad for 1.2s
    cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':px+pw*0.36,'y':py,'id':1}]})
    pg.wait_for_timeout(1200)
    held=pg.evaluate("()=>document.querySelector('#pad .ar.r').classList.contains('on')")
    cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
    x1=pg.evaluate('()=>__HK.P.x')
    # long-press Grab
    cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':gx,'y':gy,'id':2}]}); pg.wait_for_timeout(800)
    grabOn=pg.evaluate("()=>document.getElementById('bGrab').classList.contains('on')")
    cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
    # tap pause: must still click through
    cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':bx,'y':by,'id':3}]}); cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
    pg.wait_for_timeout(300)
    styles=pg.evaluate("()=>['#bGrab','#bJump','#pad','#game'].map(s=>{const c=getComputedStyle(document.querySelector(s));return s+':'+c.webkitUserSelect+'/'+c.webkitTouchCallout})")
    print(json.dumps({'touchstart (target, cancelled)':pg.evaluate('()=>window.__tp'),'pad arrow lit while held':held,'prince moved px':round(x1-x0),'grab lit while held':grabOn,'mode after tapping pause':pg.evaluate('()=>__HK.mode'),'styles':styles,'errors':errs},indent=1))
    b.close()
