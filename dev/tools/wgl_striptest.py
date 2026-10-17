# wgl_striptest.py [file.html]: rooms uploaded in strips (g2Warm) against their 2D canvases: each room texture is read back after
# its last strip and compared with the canvas, row band by row band (WK=1: WebKit). Prints the worst bands per room.
import os, sys, json
from playwright.sync_api import sync_playwright
import wgl_env as E
HERE = os.path.dirname(os.path.abspath(__file__))
html = next((x for x in sys.argv[1:] if x.endswith('.html')), os.path.join(HERE, '..', 'hourglass-keep.html'))
JS = r'''async()=>{const H=__HK,raf=()=>new Promise(r=>requestAnimationFrame(r));H.S.set.lightMode='torch';H.GLP.pipe=false;window.__HKfreeze=true;
  H.load(10,9010,false);H.render();
  // build every room of the floor in the background, then let the strip uploads run, one render a frame
  const out=[];for(let k=0;k<40;k++)for(let i=0;i<3;i++)H.roomWork();
  for(let f=0;f<400;f++){H.render();await raf();}
  const gl=H.GLP.gl,fb=gl.createFramebuffer();
  for(const [key,c] of H.roomCache){const e=H.GLS.tex.get(c);if(!e||e.part)continue;
    gl.bindFramebuffer(gl.FRAMEBUFFER,fb);gl.framebufferTexture2D(gl.FRAMEBUFFER,gl.COLOR_ATTACHMENT0,gl.TEXTURE_2D,e.t,0);
    const w=c.width,h=c.height,px=new Uint8Array(w*h*4);gl.readPixels(0,0,w,h,gl.RGBA,gl.UNSIGNED_BYTE,px);
    const d=c.getContext('2d').getImageData(0,0,w,h).data,bands=[];
    for(let y0=0;y0<h;y0+=40){let s=0,n=0;for(let y=y0;y<Math.min(h,y0+40);y++)for(let x=0;x<w;x+=3){const i=(y*w+x)*4;for(let k=0;k<4;k++){s+=Math.abs(px[i+k]-d[i+k]);}n+=4;}bands.push(+(s/n).toFixed(1));}
    out.push([key,e.st?'strips?':'',w,h,Math.max(...bands),bands.join(' ')]);}
  gl.bindFramebuffer(gl.FRAMEBUFFER,null);return out;}'''
with sync_playwright() as p:
    b = E.launch(p, True); pg = b.new_page(viewport={'width': 852, 'height': 283}, device_scale_factor=2); E.setup(pg)
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(E.url(html)); pg.wait_for_timeout(2000)
    for r in pg.evaluate(JS): print(r[0], r[2], r[3], 'worst band %.1f' % r[4], '|', r[5][:160])
    print('errors', errs[:3]); b.close()
