# wgl_prof.py [floor] [secs] [pre=js] [file.html]: ?prof with the bench's bot on one floor (WK=1: WebKit); prints each stage's time
# a frame (every stage ends with gl.finish, so GPU work is counted where it is issued) and the per-step table ?prof draws.
import os, sys, time
from playwright.sync_api import sync_playwright
import wgl_env as E
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
fl = next((x for x in a if x.isdigit() and int(x) < 40), '1')
secs = int(next((x for x in a if x.isdigit() and int(x) >= 40), '45'))
pre = next((x[4:] for x in a if x.startswith('pre=')), '')
html = next((x for x in a if x.endswith('.html')), os.path.join(HERE, '..', 'hourglass-keep.html'))
with sync_playwright() as p:
    b = E.launch(p, True); pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=2); E.setup(pg)
    pg.goto(E.url(html, '?bench&prof&floors=' + fl)); pg.wait_for_timeout(2500)
    if pre: pg.evaluate('()=>{' + pre + '}')
    time.sleep(secs)
    r = pg.evaluate('()=>{const P=__HK.PF;return {stg:P.stg,res:P.res,steps:P.steps}}'); b.close()
print('stages (ms a frame, all effects on):', ', '.join('%s %.2f' % (k, v) for k, v in sorted((r['stg'] or {}).items(), key=lambda kv: -kv[1]) if v >= 0.05))
for k, nm in r['steps']:
    o = r['res'].get(k)
    if o and o['n']: print('  %-16s work %6.2f (%+.2f)  frame %6.2f (%+.2f)' % (nm, o['w'] / o['n'], o['d'] / o['n'], o['iv'] / o['n'], o['di'] / o['n']))
