# wgl_trace.py [arg] [floors] [file.html]: ?bench on this Mac's GPU for the given floors (default 17) and prints each floor's
# first seconds frame by frame (only the dropped frames, over 1.2 refresh intervals: 20 ms at 60 Hz, round 16d; with what happened in them),
# then the bench table.
# arg: torch (default), 2d, saver, classic. Columns: ms since the floor's first frame, frame interval, script work, rooms built,
# textures uploaded.
import os, sys, json
from playwright.sync_api import sync_playwright
import wgl_env as E
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
arg = next((x for x in a if x in ('torch', '2d', 'saver', 'classic', 'auto')), 'torch')
fl = next((x for x in a if x.replace(',', '').isdigit()), '17')
html = next((x for x in a if x.endswith('.html')), os.path.join(HERE, '..', 'hourglass-keep.html'))
url = E.url(html, '?bench' + ('' if arg == 'torch' else '=' + arg) + '&floors=' + fl)
with sync_playwright() as p:
    b = E.launch(p, True)
    pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=2)
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    E.setup(pg); pg.goto(url)
    pg.wait_for_function('window.__BENCH_RESULT', timeout=600000, polling=1000)
    tr = pg.evaluate('window.__BENCH_TRACE'); thr = pg.evaluate('window.__HK.BENCH.thr||20')
    for n, rows in tr.items():
        slow = [r for r in rows if r[1] > thr or r[2] > 6]
        print('floor', n, 'first 6 s:', len(rows), 'frames,', len(slow), 'over %g ms or 6 ms of work, worst' % thr, max([r[1] for r in rows] or [0]), 'ms; in the first second:', sum(r[1] for r in rows if r[0] < 1000) / max(1, len([r for r in rows if r[0] < 1000])), 'ms mean')
        for r in slow[:40]: print('   t %5d  iv %6.1f  work %6.1f  rooms %d  uploads %d' % tuple(r))
    print(pg.evaluate('window.__BENCH_RESULT')); print('errors', errs[:3]); b.close()
