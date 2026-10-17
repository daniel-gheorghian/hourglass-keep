# wgl_alloc.py [floor] [2d] [file.html]: how much JS memory a Torchlight frame allocates (garbage the phone has to collect: GC pauses
# are frame spikes), and where: Chrome's sampling heap profiler over 200 tick+render steps (all allocations, collected or not).
import sys, os
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
n = int(next((x for x in a if x.isdigit()), '5')); d2 = '2d' in a
html = next((x for x in a if x.endswith('.html')), os.path.join(HERE, '..', 'hourglass-keep.html'))
with sync_playwright() as p:
    b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
    pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=2)
    pg.goto('file://' + os.path.abspath(html)); pg.wait_for_timeout(300); pg.add_script_tag(path=os.path.join(HERE, 'bot.js'))
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    pg.evaluate("([n,d2])=>{const H=__HK;H.S.set.lightMode='torch';H.GLFX.wgl=!d2;H.GLP.pipe=false;let k=0;window.__G=botGen(n,9000+n,{fight:true});for(let i=0;i<600;i++){__G.next();H.tick(1);}for(let i=0;i<20;i++)H.render();}", [n, d2])
    cdp = pg.context.new_cdp_session(pg); cdp.send('HeapProfiler.enable'); cdp.send('HeapProfiler.startSampling', {'samplingInterval': 256, 'includeObjectsCollectedByMajorGC': True, 'includeObjectsCollectedByMinorGC': True})
    pg.evaluate("()=>{const H=__HK;for(let i=0;i<200;i++){__G.next();H.tick(1);H.render();}}")
    prof = cdp.send('HeapProfiler.stopSampling')['profile']; b.close()
tot = {}
def walk(nd):
    fn = (nd['callFrame']['functionName'] or '(anon)') + ':' + str(nd['callFrame']['lineNumber'])
    tot[fn] = tot.get(fn, 0) + nd['selfSize']
    for c in nd.get('children', []): walk(c)
walk(prof['head']); T = sum(tot.values())
print('floor', n, '2d' if d2 else 'webgl', 'allocated %.1f KB a frame' % (T / 200 / 1024))
for k, v in sorted(tot.items(), key=lambda kv: -kv[1])[:22]: print('  %6.1f KB/frame  %s' % (v / 200 / 1024, k))
