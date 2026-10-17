# wgl_scroll.py [file.html] [floors]: the camera still, then scrolling slowly (0.37 world px a frame, sideways and down), the same
# frames drawn by the new path and by the v60 path (GLFX.wgl=false) of one build, pipe off, the same clock and random numbers.
# Per frame: the difference between the two paths (mean, share off by >24, away from edges). Edge motion one path has and the
# other has not shows as frames whose difference jumps; also each path's own frame-to-frame change at edges is printed.
import sys, os, base64
import numpy as np
from playwright.sync_api import sync_playwright
import wgl_env as E
HERE = os.path.dirname(os.path.abspath(__file__))
html = next((x for x in sys.argv[1:] if x.endswith('.html')), os.path.join(HERE, '..', 'hourglass-keep.html'))
fls = [int(x) for x in (next((x for x in sys.argv[1:] if x.replace(',', '').isdigit()), '5,14,17,22')).split(',')]
RUN = r'''([n,wgl,K])=>{const H=__HK;H.S.set.lightMode='torch';H.GLP.pipe=false;window.__HKnoauto=true;H.GLFX.wgl=wgl;
  let T=1e6;H.setClock(()=>T);let k=0;runBot(n,9300+n,{fight:false,stop:h=>{++k;T+=1000/60;return k>=600;}});
  let a=777;const rnd=()=>{a=(a+0x6D2B79F5)>>>0;let t=Math.imul(a^(a>>>15),1|a);t=(t+Math.imul(t^(t>>>7),61|t))^t;return((t^(t>>>14))>>>0)/4294967296;};
  const c=H.cam,x0=c.x,y0=c.y,out=[];
  for(let i=0;i<K;i++){const s=i<6?0:(i-6)*0.37;c.x=x0+s;c.y=y0+s*0.5;for(let r=0;r<3;r++){a=777;Math.random=rnd;H.render();}
    const g=H.GLP.gl,w=H.GLP.cv.width,h=H.GLP.cv.height,px=new Uint8Array(w*h*4);g.readPixels(0,0,w,h,g.RGBA,g.UNSIGNED_BYTE,px);
    let s2='';for(let j=0;j<px.length;j+=0x8000)s2+=String.fromCharCode.apply(null,px.subarray(j,j+0x8000));out.push(btoa(s2));}
  return {w:H.GLP.cv.width,h:H.GLP.cv.height,out};}'''
K = 22
with sync_playwright() as p:
    b = E.launch(p, 'gpu' in sys.argv[1:])
    for n in fls:
        res = {}
        for wgl in (True, False):
            pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=2)
            E.setup(pg); pg.goto(E.url(html)); pg.wait_for_timeout(300); pg.add_script_tag(path=os.path.join(HERE, 'bot.js'))
            pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
            r = pg.evaluate(RUN, [n, wgl, K]); pg.close()
            res[wgl] = [np.frombuffer(base64.b64decode(x), np.uint8).reshape(r['h'], r['w'], 4)[::-1, :, :3].astype(np.int16) for x in r['out']]
        A, B = res[True], res[False]
        print('floor', n)
        for i in range(K):
            d = np.abs(A[i] - B[i]).max(axis=2)
            g = B[i].max(axis=2); pad = np.pad(g, 1, mode='edge'); H_, W_ = g.shape
            mx = np.maximum.reduce([pad[y:y + H_, x:x + W_] for y in range(3) for x in range(3)]); mn = np.minimum.reduce([pad[y:y + H_, x:x + W_] for y in range(3) for x in range(3)])
            flat = (mx - mn) < 24
            ma = np.abs(A[i] - A[i - 1]).max(axis=2).mean() if i else 0; mb = np.abs(B[i] - B[i - 1]).max(axis=2).mean() if i else 0
            print('  frame %2d %s  paths differ: mean %.3f  >24 %.4f%%  flat>24 %.4f%%   frame-to-frame change: new %.3f  v60 %.3f' % (i, 'still ' if i < 6 else 'scroll', d.mean(), (d > 24).mean() * 100, ((d > 24) & flat).mean() * 100, ma, mb))
    b.close()
