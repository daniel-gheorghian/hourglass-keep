# bench.py [arg] [file]: runs the game's own ?bench (the bot plays six fixed floors live, 20 s each) in Chromium on this Mac's
# real GPU, at a phone's canvas size, and prints the table the phone shows. arg: torch (default), 75, auto, classic, saver (Battery saver on).
# Chrome's costs are not Safari's (it copies 2D canvases into WebGL inside one process): compare runs here with each other,
# and use the phone's own ?bench for the phone.
import os, sys
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
arg = a[0] if a and a[0] in ('torch', '75', 'auto', 'classic', 'saver') else ''
html = next((x for x in a if x.endswith('.html')), os.path.join(HERE, '..', 'hourglass-keep.html'))
url = 'file://' + os.path.abspath(html) + '?bench' + ('=' + arg if arg and arg != 'torch' else '')
with sync_playwright() as p:
    b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
    pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=2)
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(url)
    pg.wait_for_function('window.__BENCH_RESULT', timeout=400000, polling=1000)
    print(pg.evaluate('window.__BENCH_RESULT'))
    print('page errors', errs[:3])
    b.close()
