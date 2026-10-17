# wgl_profwatch.py [secs] [file.html]: ?bench&prof live (WK=1: WebKit; VP=WxHxDPR), printing every 1.5 s the ?prof step, the frame
# clock and the WebGL state, to catch a step that stops the game (or a page error)
import os, sys
from playwright.sync_api import sync_playwright
import wgl_env as E
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
secs = int(next((x for x in a if x.isdigit()), '60'))
html = next((x for x in a if x.endswith('.html')), os.path.join(HERE, '..', 'hourglass-keep.html'))
with sync_playwright() as p:
    b = E.launch(p, True); VP = os.environ.get('VP', '852x283x2').split('x')
    pg = b.new_page(viewport={'width': int(VP[0]), 'height': int(VP[1])}, device_scale_factor=float(VP[2])); E.setup(pg)
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: errs.append('c:' + m.text))
    pg.add_init_script("window.__ERRS=[];window.addEventListener('error',e=>{window.__ERRS.push(String(e.message)+' @ '+((e.error&&e.error.stack)||'').slice(0,600))})")
    pg.goto(E.url(html, '?bench&prof&floors=' + os.environ.get('FL', '1'))); pg.wait_for_timeout(3000)
    for i in range(int(secs / 1.5)):
        pg.wait_for_timeout(1500)
        print(pg.evaluate('()=>{const H=__HK;return [H.PF.ix,H.PF.cur,H.GLP.dead,H.GLP.why,H.S.set.lightMode,H.GLP.lastR|0,H.mode,H.GLP.gls]}'), flush=True)
    print(errs[:10]); print('stacks', pg.evaluate('window.__ERRS')); b.close()
