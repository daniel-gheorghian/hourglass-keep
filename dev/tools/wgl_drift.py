# wgl_drift.py [floor] [minutes] [file.html]: live Torchlight play for a long time (?bench, the floor played again and again by
# the bot, fighting), logging every 30 s what could grow: live WebGL textures, buffers, framebuffers, renderbuffers (created minus
# deleted), canvases created, the game's caches (room pictures and their textures, relief copies, silhouettes, strip staging
# canvases, gradient rows), G2D vertices and ops, the JS heap (Chromium only: performance.memory), and the frame interval and
# work over the last 30 s. WK=1: WebKit; VP default the phone's 852x283x2.
import os, sys, time
from playwright.sync_api import sync_playwright
import wgl_env as E
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
FL = next((x for x in a if x.isdigit()), '1'); MIN = float(next((x for x in a[1:] if x.replace('.', '').isdigit()), '6'))
html = next((x for x in a if x.endswith('.html')), os.path.join(HERE, '..', 'hourglass-keep.html'))
VP = os.environ.get('VP', '852x283x2').split('x')
INIT = r'''(()=>{const L=window.__LIVE={tex:0,buf:0,fb:0,rb:0,canv:0,iv:[],wk:[]};const P=WebGL2RenderingContext.prototype;
  for(const [c,d,k] of [['createTexture','deleteTexture','tex'],['createBuffer','deleteBuffer','buf'],['createFramebuffer','deleteFramebuffer','fb'],['createRenderbuffer','deleteRenderbuffer','rb']]){
    const fc=P[c],fd=P[d];P[c]=function(...x){L[k]++;return fc.apply(this,x);};P[d]=function(o,...x){if(o)L[k]--;return fd.call(this,o,...x);};}
  const ce=Document.prototype.createElement;Document.prototype.createElement=function(t,...x){if(String(t).toLowerCase()==='canvas')L.canv++;return ce.call(this,t,...x);};
  let last=0;const f=t=>{if(last)L.iv.push(t-last);last=t;requestAnimationFrame(f);};requestAnimationFrame(f);})()'''
SNAP = r'''()=>{const H=__HK,L=__LIVE,G=H.GLS,iv=L.iv.splice(0),m=v=>v.length?v.reduce((a,b)=>a+b,0)/v.length:0,s=v=>v.slice().sort((a,b)=>a-b);
  const sv=s(iv);return {tex:L.tex,buf:L.buf,fb:L.fb,rb:L.rb,canv:L.canv,rooms:H.roomCache.size,gtex:G.tex.size,rel:H.GLREL.tex.size,stc:(H.G2UP.stc||[]).length,
    ramp:G.rampN,nv:G.nv,ni:G.ni,cap:G.cap,ops:G.stats.batches,draws:G.stats.draws,heap:performance.memory?Math.round(performance.memory.usedJSHeapSize/1e6):-1,
    iv:+m(iv).toFixed(1),p95:+(sv[Math.floor(sv.length*.95)]||0).toFixed(1),floor:H.L&&H.L.n,mode:H.mode,gls:H.GLP.gls};}'''
with sync_playwright() as p:
    b = E.launch(p, True)
    pg = b.new_page(viewport={'width': int(VP[0]), 'height': int(VP[1])}, device_scale_factor=float(VP[2])); E.setup(pg)
    pg.add_init_script(INIT)
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(E.url(html, '?bench&floors=' + ','.join([FL] * 40))); pg.wait_for_timeout(1500)
    pg.evaluate('__HK.BENCH.secs=1e9')
    t0 = time.time(); k = 0
    while time.time() - t0 < MIN * 60:
        pg.wait_for_timeout(30000); k += 1
        r = pg.evaluate(SNAP); print('%4ds' % (time.time() - t0), r, flush=True)
    print('errors', errs[:3]); b.close()
