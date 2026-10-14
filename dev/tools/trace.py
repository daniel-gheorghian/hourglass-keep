from playwright.sync_api import sync_playwright
import sys,json,os
# trace.py file n seed "start-pred" "stop-pred" fields(js expr returning array)
f,n,seed,start,stop=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),sys.argv[4],sys.argv[5]
expr=sys.argv[6] if len(sys.argv)>6 else "[P.state,+P.x.toFixed(1),+P.y.toFixed(1),+P.vx.toFixed(0),+P.vy.toFixed(0),P.face,H.wallTouch?H.wallTouch():'-']"
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':844,'height':390}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+os.path.abspath(f)); pg.wait_for_timeout(300); pg.add_script_tag(path='bot.js')
    res=pg.evaluate('''([n,seed,start,stop,expr])=>{const rows=[];let on=false;const ts=new Function('H','P','return ('+start+')'),tp=new Function('H','P','return ('+stop+')'),ex=new Function('H','P','return ('+expr+')');
      const r=runBot(n,seed,{fight:false,stop:H=>{if(!on&&ts(H,H.P))on=true;if(!on)return false;rows.push(ex(H,H.P));return tp(H,H.P)||rows.length>400;}});return {ok:r.ok,why:r.why,rows};}''',[n,seed,start,stop,expr])
    b.close()
print(res['ok'],res['why'],errs[:2])
for i,r in enumerate(res['rows']): print(i,json.dumps(r))
