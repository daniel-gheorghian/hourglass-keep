# wgl_floorprof.py n [ticks] [2d] [file.html]: a CPU profile of 60 Torchlight renders at the start of floor n (after ticks game
# steps, default 0), top functions by self time; real GPU (ANGLE-Metal). '2d': the v60 path.
import sys, os
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
n = int(a[0]); ticks = int(a[1]) if len(a) > 1 and a[1].isdigit() else 0
d2 = '2d' in a
html = next((x for x in a if x.endswith('.html')), os.path.join(HERE, '..', 'hourglass-keep.html'))
with sync_playwright() as p:
    b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
    pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=2)
    pg.goto('file://' + os.path.abspath(html)); pg.wait_for_timeout(300)
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    pg.evaluate("([n,t,d2])=>{const H=__HK;H.S.set.lightMode='torch';H.GLFX.wgl=!d2;H.GLP.pipe=false;H.load(n,9000+n,false);H.tick(t);H.render();H.render();}", [n, ticks, d2])
    cdp = pg.context.new_cdp_session(pg); cdp.send('Profiler.enable'); cdp.send('Profiler.setSamplingInterval', {'interval': 100}); cdp.send('Profiler.start')
    ms = pg.evaluate("()=>{const H=__HK,gl=H.GLP.gl,t=performance.now();for(let i=0;i<60;i++){H.tick(1);H.render();}gl.finish();return (performance.now()-t)/60;}")
    prof = cdp.send('Profiler.stop')['profile']
    nodes = {nd['id']: nd for nd in prof['nodes']}; cnt = {}
    for s in prof['samples']: cnt[s] = cnt.get(s, 0) + 1
    st = {}
    for i, c in cnt.items():
        nd = nodes[i]; k = (nd['callFrame']['functionName'] or '(anon)') + ':' + str(nd['callFrame']['lineNumber']); st[k] = st.get(k, 0) + c
    tot = sum(st.values()); print('floor', n, 'ms per tick+render (with finish): %.2f' % ms)
    for k, v in sorted(st.items(), key=lambda kv: -kv[1])[:25]: print('  %5.1f%%  %s' % (v * 100 / tot, k))
    b.close()
