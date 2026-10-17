# wgl_shots.py query n every_ms [file.html]: plays the page live (e.g. query '?bench&floors=10') and saves n WebGL frames, one every
# every_ms, as wgl_shot_NN.png (VP=WxHxDPR for the window; WK=1 for WebKit)
import os, sys, base64, time
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
import wgl_env as E
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
q = a[0]; n = int(a[1]); every = int(a[2])
html = next((x for x in a if x.endswith('.html')), os.path.join(HERE, '..', 'hourglass-keep.html'))
JS = r'''()=>new Promise(res=>{const H=__HK;let last=H.GLP.lastR;const t=()=>{const G=H.GLP;if(G.gl&&G.lastR!==last){const gl=G.gl,w=G.cv.width,h=G.cv.height,px=new Uint8Array(w*h*4);gl.readPixels(0,0,w,h,gl.RGBA,gl.UNSIGNED_BYTE,px);
  let s='';for(let i=0;i<px.length;i+=0x8000)s+=String.fromCharCode.apply(null,px.subarray(i,i+0x8000));res({w,h,px:btoa(s),rs:G.rs,gls:G.gls,XF:H.XF});}else requestAnimationFrame(t);};requestAnimationFrame(t);})'''
with sync_playwright() as p:
    b = E.launch(p, True); VP = os.environ.get('VP', '852x283x2').split('x')
    pg = b.new_page(viewport={'width': int(VP[0]), 'height': int(VP[1])}, device_scale_factor=float(VP[2])); E.setup(pg)
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(E.url(html, q)); pg.wait_for_timeout(int(os.environ.get('WAIT', '3000')))
    for i in range(n):
        r = pg.evaluate(JS)
        im = np.frombuffer(base64.b64decode(r['px']), np.uint8).reshape(r['h'], r['w'], 4)[::-1, :, :3]
        Image.fromarray(im).save(os.path.join(HERE, 'wgl_shot_%02d.png' % i)); print(i, r['w'], r['h'], 'rs', r['rs'], 'gls', r['gls'], r['XF'])
        time.sleep(every / 1000)
    print('errors', errs[:3]); b.close()
