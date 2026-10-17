# wgl_benchprof.py [file.html] [secs]: a CPU profile of the live ?bench loop (this Mac's GPU), top functions by self time
import sys, os, time
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
html = next((x for x in sys.argv[1:] if x.endswith('.html')), os.path.join(HERE, '..', 'hourglass-keep.html'))
secs = next((float(x) for x in sys.argv[1:] if x.replace('.', '').isdigit()), 12)
with sync_playwright() as p:
    b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
    pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=2)
    pg.goto('file://' + os.path.abspath(html) + '?bench'); pg.wait_for_timeout(6000)
    cdp = pg.context.new_cdp_session(pg); cdp.send('Profiler.enable'); cdp.send('Profiler.setSamplingInterval', {'interval': 200}); cdp.send('Profiler.start')
    time.sleep(secs); prof = cdp.send('Profiler.stop')['profile']
    nodes = {nd['id']: nd for nd in prof['nodes']}; cnt = {}
    for s in prof['samples']: cnt[s] = cnt.get(s, 0) + 1
    self_t = {}
    for i, c in cnt.items():
        nd = nodes[i]; fn = nd['callFrame']['functionName'] or '(anon)'; key = fn + ':' + str(nd['callFrame']['lineNumber'])
        self_t[key] = self_t.get(key, 0) + c
    tot = sum(self_t.values()); idle = self_t.get('(idle):-1', 0); busy = tot - idle
    print('samples', tot, 'busy share %.1f%%' % (busy * 100 / tot))
    for k, v in sorted(self_t.items(), key=lambda kv: -kv[1])[:40]:
        if k.startswith('(idle)'): continue
        print('  %5.1f%% of busy  %s' % (v * 100 / busy, k))
    b.close()
