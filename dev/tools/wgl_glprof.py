# wgl_glprof.py [file.html] [pre=js]: which WebGL calls take the script's time in a Torchlight frame (this Mac's GPU): every
# method of the context is wrapped and timed over 200 renders (pipe off), per method: total ms per frame and calls per frame.
import sys, os
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
html = next((x for x in sys.argv[1:] if x.endswith('.html')), os.path.join(HERE, '..', 'hourglass-keep.html'))
PRE = ([x[4:] for x in sys.argv[1:] if x.startswith('pre=')] or [''])[0]
RUN = r'''([n,seed,cond])=>{const H=__HK;%s;H.S.set.lightMode='torch';H.GLP.pipe=false;window.__HKnoauto=true;
  let k=0;runBot(n,seed,{fight:true,stop:h=>++k>=cond});
  for(let i=0;i<10;i++)H.render();const gl=H.GLP.gl;gl.finish();const T={},C={};
  const P=Object.getPrototypeOf(gl);for(const m of Object.getOwnPropertyNames(P)){const d=Object.getOwnPropertyDescriptor(P,m);if(typeof d.value!=='function'||m==='constructor')continue;const f=d.value;
    gl[m]=function(...a){const t=performance.now();const r=f.apply(this,a);T[m]=(T[m]||0)+performance.now()-t;C[m]=(C[m]||0)+1;return r;};}
  const N=200,t0=performance.now();for(let i=0;i<N;i++)H.render();const tot=(performance.now()-t0)/N;
  const out=Object.keys(T).map(m=>[m,T[m]/N,C[m]/N]).sort((a,b)=>b[1]-a[1]).slice(0,16);return {tot,out,gls:H.GLP.gls};}''' % PRE
with sync_playwright() as p:
    b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
    for (n, seed, cond) in [(5, 9105, 1200), (14, 9114, 700)]:
        pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=2)
        pg.goto('file://' + os.path.abspath(html)); pg.wait_for_timeout(300); pg.add_script_tag(path=os.path.join(HERE, 'bot.js'))
        pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
        r = pg.evaluate(RUN, [n, seed, cond])
        print('floor', n, 'render %.2f ms (gls %s)' % (r['tot'], r['gls']))
        for m, t, c in r['out']: print('   %-28s %6.3f ms  %5.1f calls' % (m, t, c))
        pg.close()
    b.close()
