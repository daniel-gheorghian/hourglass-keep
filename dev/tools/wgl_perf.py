# wgl_perf.py [file.html] [prof]: script time of a Torchlight frame on this Mac's GPU, the scene drawn by WebGL (GLS) against
# the 2D scene copied (GLFX.wgl=false), in the same states (floors played by the bot to a tick, renders with pipe off).
# Prints per state: ms per render (script only) and with gl.finish (script + GPU), vertices and draws. 'prof': a CPU profile
# of the GLS renders (top functions by self time).
import sys, os, json
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
html = next((x for x in sys.argv[1:] if x.endswith('.html')), os.path.join(HERE, '..', 'hourglass-keep.html'))
PROF = 'prof' in sys.argv[1:]
PRE = ([x[4:] for x in sys.argv[1:] if x.startswith('pre=')] or [''])[0]
ST = [(5, 9105, 1200)] if PROF else [(5, 9105, 1200), (14, 9114, 700), (22, 9122, 2500), (9, 9109, 'fight'), (17, 9117, 'fight')]
RUN = r'''([n,seed,cond,wgl,N,fin])=>{const H=__HK;%s;H.S.set.lightMode='torch';H.GLP.pipe=false;window.__HKnoauto=true;H.GLFX.wgl=wgl;
  let k=0;const f=cond==='fight'?(h=>h.P&&h.P.foe&&h.P.foe.alive&&Math.abs(h.P.foe.x-h.P.x)<70):null;
  runBot(n,seed,{fight:true,stop:h=>{++k;return f?(k>200&&f(h))||k>9000:k>=cond;}});
  for(let i=0;i<10;i++)H.render();const gl=H.GLP.gl;gl.finish();
  let t0=performance.now();for(let i=0;i<N;i++){H.render();if(fin)gl.finish();}const ms=(performance.now()-t0)/N;
  return {ms,verts:H.GLS.stats.verts,draws:H.GLS.stats.draws,batches:H.GLS.stats.batches,gls:H.GLP.gls};}''' % PRE
with sync_playwright() as p:
    b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
    for (n, seed, cond) in ST:
        out = []
        for wgl in (False, True):
            pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=2)
            pg.goto('file://' + os.path.abspath(html)); pg.wait_for_timeout(300); pg.add_script_tag(path=os.path.join(HERE, 'bot.js'))
            pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
            if PROF and wgl:
                cdp = pg.context.new_cdp_session(pg); cdp.send('Profiler.enable'); cdp.send('Profiler.setSamplingInterval', {'interval': 100})
            r1 = pg.evaluate(RUN, [n, seed, cond, wgl, 1 if PROF and wgl else 200, False])
            if PROF and wgl:
                cdp.send('Profiler.start'); pg.evaluate("()=>{for(let i=0;i<300;i++)__HK.render();}"); prof = cdp.send('Profiler.stop')['profile']
                self_t = {}; nodes = {nd['id']: nd for nd in prof['nodes']}; cnt = {}
                for s in prof['samples']: cnt[s] = cnt.get(s, 0) + 1
                for i, c in cnt.items():
                    nd = nodes[i]; fn = nd['callFrame']['functionName'] or '(anon)'; key = fn + ':' + str(nd['callFrame']['lineNumber'])
                    self_t[key] = self_t.get(key, 0) + c
                tot = sum(self_t.values())
                print('profile floor', n, 'top self time:')
                for k, v in sorted(self_t.items(), key=lambda kv: -kv[1])[:28]: print('  %5.1f%%  %s' % (v * 100 / tot, k))
            r2 = pg.evaluate(RUN.replace('runBot(n,seed', 'false&&runBot(n,seed'), [n, seed, cond, wgl, 200, True])
            out.append((wgl, round(r1['ms'], 2), round(r2['ms'], 2), r1['verts'], r1['draws'], r1['batches'], r1['gls']))
            pg.close()
        print('floor', n, cond, ' | '.join('%s: %.2f ms script, %.2f ms with finish (verts %d, draws %d, batches %d, gls %s)' % ((('GLS' if o[0] else '2D '),) + tuple(o[1:])) for o in out), flush=True)
    b.close()
