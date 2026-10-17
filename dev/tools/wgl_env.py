# wgl_env.py: the browser for the wgl_* tools. WK=1 in the environment: Playwright's WebKit (Safari's engine: its 2D canvas,
# its WebGL through ANGLE-Metal, its GPU process), the page served over http://127.0.0.1:8765 (run `python3 -m http.server 8765
# --bind 127.0.0.1` in dev/) with Google Fonts blocked (the stylesheet would hold the page's script). Otherwise Chromium.
import os
HERE = os.path.dirname(os.path.abspath(__file__))
WK = bool(os.environ.get('WK'))
def launch(p, gpu=False):
    if WK: return p.webkit.launch()
    return p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist']) if gpu else p.chromium.launch()
def url(html, q=''):
    if WK: return 'http://127.0.0.1:8765/' + os.path.relpath(os.path.abspath(html), os.path.join(HERE, '..')) + q
    return 'file://' + os.path.abspath(html) + q
def setup(pg):
    if WK: pg.route('**/*', lambda r: r.abort() if 'fonts.g' in r.request.url else r.continue_())
