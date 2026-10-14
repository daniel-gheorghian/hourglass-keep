import json, shutil, sys, time
from playwright.sync_api import sync_playwright
SP=sys.argv[1]
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},has_touch=True,is_mobile=True)
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    out={}
    pg.goto('http://127.0.0.1:8766/'); pg.wait_for_timeout(1200); pg.reload(); pg.wait_for_timeout(800)
    out['v1_controlled']=pg.evaluate('!!navigator.serviceWorker.controller')
    out['v1_has_pause_btn']=pg.evaluate("!!document.getElementById('bPause')")
    # play a little on v1 so a save exists
    pg.tap('#bNew'); pg.wait_for_timeout(200); pg.keyboard.down('ArrowRight'); pg.wait_for_timeout(500); pg.keyboard.up('ArrowRight'); pg.wait_for_timeout(3500)
    out['v1_save_level']=pg.evaluate('__HK.S.level')
    # deploy v2 (what GitHub Pages will serve after the push)
    for f in ['index.html','sw.js']: shutil.copy('/Users/dan/Documents/Projects/hourglass-keep/'+f, SP+'/srv/'+f)
    # first launch after deploy (the user opens the app online): old page served from cache, new worker installs
    pg.goto('http://127.0.0.1:8766/'); pg.wait_for_timeout(2500)
    out['after_1st_open_has_pause_btn']=pg.evaluate("!!document.getElementById('bPause')")
    # second launch
    pg.goto('http://127.0.0.1:8766/'); pg.wait_for_timeout(1500)
    out['after_2nd_open_has_pause_btn']=pg.evaluate("!!document.getElementById('bPause')")
    out['caches']=pg.evaluate('caches.keys()')
    out['save_kept']=pg.evaluate("JSON.parse(localStorage.getItem('hourglass-keep-v1')).level")
    out['continue_label']=pg.inner_text('#bContinue')
    # offline launch on v2
    ctx.set_offline(True); pg.reload(); pg.wait_for_timeout(800)
    out['offline_v2']=pg.evaluate("!!document.getElementById('bPause')")
    pg.tap('#bContinue'); pg.wait_for_timeout(300); out['offline_mode']=pg.evaluate('__HK.mode'); out['offline_viewW']=round(pg.evaluate('__HK.viewW'))
    out['errs']=errs
    print(json.dumps(out,indent=1)); b.close()
