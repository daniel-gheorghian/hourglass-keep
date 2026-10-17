import sys, os
from playwright.sync_api import sync_playwright
import wgl_env as E
HERE = os.path.dirname(os.path.abspath(__file__))
html = next((x for x in sys.argv[1:] if x.endswith('.html')), os.path.join(HERE, '..', 'hourglass-keep.html'))
js = next((x for x in sys.argv[1:] if not x.endswith('.html')), "()=>{const H=__HK;H.S.set.lightMode='torch';H.render();return [H.GLP.on,H.GLP.dead,H.GLP.why,!!H.GLP.sceneG,H.shaderOn()]}")
with sync_playwright() as p:
    b = E.launch(p); pg = b.new_page(viewport={'width': 844, 'height': 390}, device_scale_factor=2); errs = []; E.setup(pg)
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.on('console', lambda m: print('console:', m.text))
    pg.goto(E.url(html)); pg.wait_for_timeout(1500)
    pg.add_script_tag(path=os.path.join(HERE, 'bot.js'))
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    print(pg.evaluate(js)); print('errors', errs[:5]); b.close()
