# wgl_relcmp.py base.html new.html outdir [n:ticks ...]: one exact game state per floor (bot to a tick, frozen clock) rendered in
# Torchlight by two builds at phone size (VP=WxHxDPR, default 568x189x3; WK=1: WebKit), reading back the final frame, the relief
# factor (half size) and the light map (quarter size). Writes each, and their differences with the contrast raised (x8), as PNGs,
# RS=0.5: the scene's render scale (GLP.rs). Prints a blockiness score per image: the mean jump between neighbouring pixels across 4-pixel cell borders against inside them.
import sys, os, base64
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
import wgl_env as E
HERE = os.path.dirname(os.path.abspath(__file__))
A, B, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
ST = [tuple(int(v) for v in x.split(':')) for x in sys.argv[4:]] or [(1, 700), (10, 700)]
os.makedirs(OUT, exist_ok=True)
VP = os.environ.get('VP', '568x189x3').split('x')
RUN = r'''([n,seed,tick])=>{const H=__HK;H.S.set.lightMode='torch';H.GLP.pipe=false;window.__HKnoauto=true;
  let T=1e6;H.setClock(()=>T);let k=0;
  runBot(n,seed,{fight:true,stop:h=>{++k;T+=1000/60;return k>=tick;}});
  let a=12345;const rnd=()=>{a=(a+0x6D2B79F5)>>>0;let t=Math.imul(a^(a>>>15),1|a);t=(t+Math.imul(t^(t>>>7),61|t))^t;return((t^(t>>>14))>>>0)/4294967296;};
  H.GLP.rs=%s;for(let i=0;i<30;i++){a=12345;Math.random=rnd;T+=1000/60;H.render();}
  const g=H.GLP.gl,rd=(f,w,h)=>{g.bindFramebuffer(g.FRAMEBUFFER,f);const px=new Uint8Array(w*h*4);g.readPixels(0,0,w,h,g.RGBA,g.UNSIGNED_BYTE,px);
    let s='';for(let i=0;i<px.length;i+=0x8000)s+=String.fromCharCode.apply(null,px.subarray(i,i+0x8000));return {w,h,px:btoa(s)};};
  const w=H.GLP.cv.width,h=H.GLP.cv.height,R=H.GLREL,o={fin:rd(null,w,h),gls:H.GLP.gls,rel:R&&R.fb&&R.on?rd(R.fb.f,R.fw,R.fh):null,map:rd(H.GLP.fb.map.f,Math.ceil(w/4),Math.ceil(h/4))};
  g.bindFramebuffer(g.FRAMEBUFFER,null);return o;}''' % os.environ.get('RS', '1')
def img(r):
    return np.frombuffer(base64.b64decode(r['px']), np.uint8).reshape(r['h'], r['w'], 4)[::-1, :, :3].astype(np.int32)
def block(a, c=4):  # jumps across cell borders (every c-th column) over jumps inside cells: 1 for a smooth image, higher for blocks
    d = np.abs(np.diff(a.mean(2), axis=1)); b = d[:, c - 1::c].mean(); i = np.delete(d, np.s_[c - 1::c], axis=1).mean()
    return b / max(i, 1e-6)
def grab(html):
    out = {}
    with sync_playwright() as p:
        b = E.launch(p, True); errs = []
        for (n, t) in ST:
            ctx = b.new_context(viewport={'width': int(VP[0]), 'height': int(VP[1])}, device_scale_factor=float(VP[2])); pg = ctx.new_page()
            pg.on('pageerror', lambda e: errs.append(str(e))); E.setup(pg); pg.goto(E.url(html)); pg.wait_for_timeout(500)
            pg.add_script_tag(path=os.path.join(HERE, 'bot.js'))
            pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
            r = pg.evaluate(RUN, [n, 9000 + n, t]); out[(n, t)] = r; print(html[-22:], n, t, 'gls', r['gls'], 'relief', bool(r['rel']), flush=True)
            ctx.close()
        b.close(); print('errors', errs[:3])
    return out
ra = grab(A); rb = grab(B)
for k in ST:
    for part in ('fin', 'rel', 'map'):
        if not ra[k][part] or not rb[k][part]: print(k, part, 'missing'); continue
        a = img(ra[k][part]); b = img(rb[k][part]); nm = 'f%02d_t%d_%s' % (k[0], k[1], part)
        Image.fromarray(a.astype(np.uint8)).save(os.path.join(OUT, nm + '_a.png')); Image.fromarray(b.astype(np.uint8)).save(os.path.join(OUT, nm + '_b.png'))
        d = np.abs(a - b); Image.fromarray(np.clip(d * 8, 0, 255).astype(np.uint8)).save(os.path.join(OUT, nm + '_d8.png'))
        cb = 2 if part == 'fin' else 1
        print(nm, 'size', a.shape[1], a.shape[0], 'mean diff %.2f' % d.mean(), 'max', d.max(), '>8: %.2f%%' % ((d.max(2) > 8).mean() * 100),
              'blockiness a %.2f b %.2f' % (block(a, 4 * cb if part == 'fin' else 2), block(b, 4 * cb if part == 'fin' else 2)))
