# wgl_rampkeys.py file.html floor: the gradient rows made new during 5 s of live ?bench play, from a copy whose g2RampRow pushes
# each new key into window.__RK (WK=1: WebKit); prints how many per second and the commonest key shapes
import os, sys, re, collections
from playwright.sync_api import sync_playwright
import wgl_env as E
HERE = os.path.dirname(os.path.abspath(__file__))
html, n = sys.argv[1], sys.argv[2]
with sync_playwright() as p:
    b = E.launch(p, True); pg = b.new_page(viewport={'width': 852, 'height': 283}, device_scale_factor=2); E.setup(pg)
    pg.goto(E.url(html, '?bench&floors=' + n)); pg.wait_for_timeout(1500); pg.evaluate('__HK.BENCH.secs=1e9'); pg.wait_for_timeout(6500)
    pg.evaluate('window.__RK=[]'); pg.wait_for_timeout(int(os.environ.get('SECS','5'))*1000); r = pg.evaluate('window.__RK')
    print(len(r) / int(os.environ.get('SECS','5')), 'new rows a second')
    c = collections.Counter(re.sub(r'[\d.]+', '#', k) for k in r)
    for k, v in c.most_common(10): print(v, k)
    for k in r[:6]: print('  e.g.', k)
    b.close()
