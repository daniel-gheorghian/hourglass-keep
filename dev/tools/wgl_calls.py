# wgl_calls.py [floor] [2d]: WebGL calls per frame during live ?bench play (WK=1: WebKit, VP default the phone's 852x283x2): every
# method of the WebGL context counted, plus the 2D canvases' getImageData; prints the mean per frame of each call over 300
# frames, the calls that can make the browser wait on the GPU first, and texture uploads by source size
import os, sys, json
from playwright.sync_api import sync_playwright
import wgl_env as E
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
FL = next((x for x in a if x.isdigit()), '1'); D2 = '2d' in a
html = next((x for x in a if x.endswith('.html')), os.path.join(HERE, '..', 'hourglass-keep.html'))
VP = os.environ.get('VP', '852x283x2').split('x')
INIT = r'''(()=>{window.__GC={};window.__GU={};const C=window.__GC,U=window.__GU;
  const wrap=(P,name)=>{for(const k of Object.getOwnPropertyNames(P)){const d=Object.getOwnPropertyDescriptor(P,k);if(!d||typeof d.value!=='function'||k==='constructor')continue;const f=d.value;
    P[k]=function(...x){C[name+k]=(C[name+k]||0)+1;if(k==='texImage2D'||k==='texSubImage2D'){const s=x[x.length-1];if(s&&s.width!==undefined){const key=k+' '+s.constructor.name+' '+s.width+'x'+s.height;U[key]=(U[key]||0)+1;}else{const v=x.find(q=>ArrayBuffer.isView(q));if(v){const key=k+' '+v.constructor.name+' '+x.slice(0,8).filter(q=>typeof q==='number').join(',');U[key]=(U[key]||0)+1;}}}return f.apply(this,x);};}};
  wrap(WebGL2RenderingContext.prototype,'');wrap(CanvasRenderingContext2D.prototype,'2d.');})()'''
with sync_playwright() as p:
    b = E.launch(p, True)
    pg = b.new_page(viewport={'width': int(VP[0]), 'height': int(VP[1])}, device_scale_factor=float(VP[2])); E.setup(pg)
    pg.add_init_script(INIT)
    pg.goto(E.url(html, '?bench' + ('=2d' if D2 else '') + '&floors=' + FL)); pg.wait_for_timeout(6000)
    r = pg.evaluate('''()=>new Promise(res=>{for(const k in __GC)delete __GC[k];for(const k in __GU)delete __GU[k];let n=0;const t0=performance.now();
      const f=()=>{if(++n<300)requestAnimationFrame(f);else res({C:__GC,U:__GU,ms:(performance.now()-t0)/300});};requestAnimationFrame(f);})''')
    C = r['C']; print('frame interval %.1f ms' % r['ms'])
    SYNC = ['getError', 'getParameter', 'checkFramebufferStatus', 'readPixels', 'fenceSync', 'clientWaitSync', 'getQueryParameter', 'getBufferSubData', 'finish', '2d.getImageData', 'getExtension', 'getShaderParameter', 'getProgramParameter', 'bufferData', 'texImage2D', 'texSubImage2D', 'renderbufferStorageMultisample', 'renderbufferStorage', 'createTexture', 'deleteTexture', 'createFramebuffer', 'generateMipmap', 'blitFramebuffer', 'invalidateFramebuffer', 'flush', 'bindFramebuffer', 'clear', 'drawArrays', 'drawElements', 'viewport', 'useProgram']
    for k in SYNC:
        if k in C: print('  %-32s %.2f / frame' % (k, C[k] / 300))
    print('uploads:'); [print('  %-50s %.2f / frame' % (k, v / 300)) for k, v in sorted(r['U'].items(), key=lambda x: -x[1])[:12]]
    print('top calls:', ', '.join('%s %.0f' % (k, v / 300) for k, v in sorted(C.items(), key=lambda x: -x[1])[:14]))
    b.close()
