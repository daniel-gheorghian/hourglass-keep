# wgl_cliplog.py file.html floor: the clips of one Torchlight frame (target, contours, points, first points), from a copy whose
# _clip logs into window.__CL (WK=1: WebKit)
import os, sys
from playwright.sync_api import sync_playwright
import wgl_env as E
HERE = os.path.dirname(os.path.abspath(__file__))
html, n = sys.argv[1], int(sys.argv[2])
with sync_playwright() as p:
    b = E.launch(p, True); pg = b.new_page(viewport={'width': 852, 'height': 283}, device_scale_factor=2); E.setup(pg)
    pg.goto(E.url(html)); pg.wait_for_timeout(500); pg.add_script_tag(path=os.path.join(HERE, 'bot.js'))
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    r = pg.evaluate('''([n])=>{const H=__HK;H.S.set.lightMode='torch';H.GLP.pipe=false;window.__HKnoauto=true;let k=0;runBot(n,9000+n,{fight:true,stop:h=>++k>=600});
      H.tick(1);H.render();window.__CL=[];H.tick(1);H.render();const o=window.__CL;window.__CL=null;return o;}''', [n])
    for x in r: print(x)
    b.close()
