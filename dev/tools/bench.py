# bench.py [arg] [file]: runs the game's own ?bench (the bot plays six fixed floors live, 20 s each) in Chromium on this Mac's
# real GPU, at a phone's canvas size, and prints the table the phone shows. arg: torch (default), 75, auto, classic, saver (Battery saver on).
# A list of floors (e.g. 1,17) benches only those (&floors=). The dropped-frame column (round 16d) is headed with its threshold and the
# screen's rate, '>20 ms @60Hz' here, '>10 ms @120Hz' on a ProMotion phone; bench_slow(txt) reads it back as (threshold, Hz, total %).
# Chrome's costs are not Safari's (it copies 2D canvases into WebGL inside one process): compare runs here with each other,
# and use the phone's own ?bench for the phone.
import os, sys
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
arg = a[0] if a and a[0] in ('torch', '75', 'auto', 'classic', 'saver', '2d') else ''
html = next((x for x in a if x.endswith('.html')), os.path.join(HERE, '..', 'hourglass-keep.html'))
fl = next((x for x in a if x.replace(',', '').isdigit()), '')
url = 'file://' + os.path.abspath(html) + '?bench' + ('=' + arg if arg and arg != 'torch' else '') + ('&floors=' + fl if fl else '')

def bench_slow(txt):
    import re
    m = re.search(r'>([\d.]+) ms @(\d+)Hz', txt); t = re.search(r'^all .*?(\d+)%', txt, re.M)
    return (float(m.group(1)), int(m.group(2)), int(t.group(1)) if t else None) if m else None
with sync_playwright() as p:
    b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
    pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=2)
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(url)
    pg.wait_for_function('window.__BENCH_RESULT', timeout=400000, polling=1000)
    txt = pg.evaluate('window.__BENCH_RESULT'); print(txt)
    print('dropped frames (threshold ms, Hz, all %):', bench_slow(txt))
    print('page errors', errs[:3])
    b.close()
