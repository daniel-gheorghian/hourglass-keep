import json, sys, re
from playwright.sync_api import sync_playwright
SP=sys.argv[1]
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390})
    pg=ctx.new_page(); out={}
    pg.goto('http://127.0.0.1:8767/'); pg.wait_for_timeout(1200); pg.reload(); pg.wait_for_timeout(800)
    # ship a v3 with a visible marker
    h=open(SP+'/srv2/index.html').read().replace('<title>Hourglass Keep</title>','<title>Hourglass Keep</title><meta name="build" content="v3">')
    open(SP+'/srv2/index.html','w').write(h)
    sw=open(SP+'/srv2/sw.js').read().replace("hourglass-keep-v2","hourglass-keep-v3"); open(SP+'/srv2/sw.js','w').write(sw)
    pg.goto('http://127.0.0.1:8767/'); pg.wait_for_timeout(3000)
    out['single_open_is_v3']=pg.evaluate("!!document.querySelector('meta[name=build]')")
    out['on_title']=pg.is_visible('#title')
    print(json.dumps(out)); b.close()
