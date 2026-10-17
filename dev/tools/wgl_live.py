# wgl_live.py [torch|2d|saver] [floor] [secs] [file.html]: ?bench live on one floor; after every drawn frame the WebGL picture is
# read back, shifted into world coordinates (by the frame's camera), and kept: then each pixel's change from one drawn frame to the
# next is measured where the world did not move (a still prince excluded): steady light edges change little, waving ones a lot.
# Saves a strip image (world-aligned crops of consecutive frames) to wgl_live_<mode>.png.
import os, sys, base64
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
import wgl_env as E
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
arg = next((x for x in a if x in ('torch', '2d', 'saver', 'saver2d')), 'torch')
fl = next((x for x in a if x.isdigit() and int(x) < 40), '1')
secs = float(next((x for x in a if x.replace('.', '').isdigit() and float(x) >= 40), '0') or 0) or 6
html = next((x for x in a if x.endswith('.html')), os.path.join(HERE, '..', 'hourglass-keep.html'))
JS = r'''()=>{const H=__HK,S=window.__LS={n:0,pairs:0,sum:0,c8:0,c24:0,map:null,frame:null};let last=0,prev=null,pc=null,prev2=null,p2c=null;
  const tick=()=>{requestAnimationFrame(tick);const G=H.GLP;if(!G.gl||!G.used)return;if(G.lastR===last)return;last=G.lastR;
    const gl=G.gl,w=G.cv.width,h=G.cv.height,px=new Uint8Array(w*h*4);gl.readPixels(0,0,w,h,gl.RGBA,gl.UNSIGNED_BYTE,px);S.n++;S.w=w;S.h=h;
    const X0=H.XF,X=G.gls?{camD:X0.camD,camDY:X0.camDY}:(S.px0||{camD:X0.camD,camDY:X0.camDY});S.px0={camD:X0.camD,camDY:X0.camDY};if(!S.map)S.map=new Uint16Array(w*h); // (the v60 path shows the frame before: its camera)
    // (the camera moves in whole screen pixels: the last frame shifted by it lines the world up; rows run bottom-up in readPixels)
    if(prev&&prev.length===px.length&&Math.abs(X.camD-pc[0])<40&&Math.abs(X.camDY-pc[1])<40){const dx=X.camD-pc[0],dy=-(X.camDY-pc[1]);S.pairs++;const M=S.map;let cnt=0;
      for(let y=Math.max(0,-dy);y<Math.min(h,h-dy);y++)for(let x=Math.max(0,-dx);x<Math.min(w,w-dx);x++){const i=(y*w+x)*4,j=((y+dy)*w+x+dx)*4;
        const d=Math.max(Math.abs(px[i]-prev[j]),Math.abs(px[i+1]-prev[j+1]),Math.abs(px[i+2]-prev[j+2]));S.sum+=d;cnt++;if(d>8){S.c8++;M[y*w+x]++;}if(d>24)S.c24++;}S.cnt=(S.cnt||0)+cnt;S.frame=px;}
    if(prev2&&p2c&&Math.abs(X.camD-p2c[0])<40&&Math.abs(X.camDY-p2c[1])<40&&pc){const dx=X.camD-pc[0],dy=-(X.camDY-pc[1]),ex=X.camD-p2c[0],ey=-(X.camDY-p2c[1]);let fl=0,n=0; // (flicker: the picture away from the last frame and back to the one before it)
      for(let y=Math.max(0,-dy,-ey);y<Math.min(h,h-dy,h-ey);y+=2)for(let x=Math.max(0,-dx,-ex);x<Math.min(w,w-dx,w-ex);x+=2){const i=(y*w+x)*4,j=((y+dy)*w+x+dx)*4,k=((y+ey)*w+x+ex)*4;n++;
        if(Math.abs(px[i+1]-prev[j+1])>8&&Math.abs(px[i+1]-prev2[k+1])<=3)fl++;}S.fl=(S.fl||0)+fl;S.fn=(S.fn||0)+n;}
    prev2=prev;p2c=pc;prev=px;pc=[X.camD,X.camDY];};
  requestAnimationFrame(tick);}'''
with sync_playwright() as p:
    b = E.launch(p, True)
    VP = os.environ.get('VP', '852x393x2').split('x'); pg = b.new_page(viewport={'width': int(VP[0]), 'height': int(VP[1])}, device_scale_factor=float(VP[2])); E.setup(pg)
    pg.goto(E.url(html, '?bench' + ('' if arg == 'torch' else '=' + arg.replace('saver2d', 'saver&wgl=0')) + '&floors=' + fl)); pg.wait_for_timeout(4000)
    pre = os.environ.get('PRE', '')
    if pre: pg.evaluate('()=>{' + pre + '}')
    pg.evaluate(JS); pg.wait_for_timeout(int(secs * 1000))
    r = pg.evaluate('''()=>{const S=window.__LS,enc=u=>{let s='';for(let i=0;i<u.length;i+=0x8000)s+=String.fromCharCode.apply(null,u.subarray(i,i+0x8000));return btoa(s);};
      const m=new Uint8Array(S.w*S.h);if(S.map)for(let i=0;i<m.length;i++)m[i]=Math.min(255,S.map[i]*20);return {fl:S.fl||0,fn:S.fn||1,cnt:S.cnt||0,n:S.n,pairs:S.pairs,sum:S.sum,c8:S.c8,c24:S.c24,w:S.w,h:S.h,map:enc(m),frame:S.frame?enc(S.frame):''};}'''); b.close()
N = 1; P = max(1, r['cnt'] or 1)
print(arg, 'floor', fl, 'flicker (back and forth) %.4f%%' % (r['fl'] * 100 / r['fn']), 'drawn frames', r['n'], 'pairs compared (world-aligned)', r['pairs'], 'mean change %.3f, pixels changing by >8: %.4f%%, by >24: %.4f%%' % (r['sum'] / (N * P), r['c8'] * 100 / (N * P), r['c24'] * 100 / (N * P)))
m = np.frombuffer(base64.b64decode(r['map']), np.uint8).reshape(r['h'], r['w'])[::-1]; Image.fromarray(m).save(os.path.join(HERE, 'wgl_live_%s_%s_changes.png' % (arg, fl)))
if r['frame']: Image.fromarray(np.frombuffer(base64.b64decode(r['frame']), np.uint8).reshape(r['h'], r['w'], 4)[::-1, :, :3]).save(os.path.join(HERE, 'wgl_live_%s_%s_frame.png' % (arg, fl)))
