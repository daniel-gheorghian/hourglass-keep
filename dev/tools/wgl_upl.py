# wgl_upl.py: the cost of uploading a room-sized 2D canvas into WebGL in WebKit (Safari's engine), whole or in strips (WebGL2
# UNPACK_SKIP_ROWS on the canvas itself, or a strip drawn into a small canvas first)
from playwright.sync_api import sync_playwright
JS = r'''async()=>{const gl=document.createElement('canvas').getContext('webgl2');const out={};
const mk=(w,h)=>{const c=document.createElement('canvas');c.width=w;c.height=h;const g=c.getContext('2d');for(let i=0;i<400;i++){g.fillStyle='hsl('+i+',50%,50%)';g.fillRect(Math.random()*w,Math.random()*h,40,30);}return c;};
const raf=()=>new Promise(r=>requestAnimationFrame(r));
const t=gl.createTexture();gl.bindTexture(gl.TEXTURE_2D,t);gl.texStorage2D(gl.TEXTURE_2D,1,gl.RGBA8,944,566);let ms=[],e=0;
for(let k=0;k<5;k++){const c=mk(944,566);await raf();await raf();await raf();
  for(let s=0;s<4;s++){const a=performance.now();gl.pixelStorei(gl.UNPACK_SKIP_ROWS,s*142);gl.texSubImage2D(gl.TEXTURE_2D,0,0,s*142,944,Math.min(142,566-s*142),gl.RGBA,gl.UNSIGNED_BYTE,c);gl.finish();ms.push((performance.now()-a).toFixed(1));e|=gl.getError();}
  gl.pixelStorei(gl.UNPACK_SKIP_ROWS,0);}
out.skipRows=ms.join(' ');out.e=e;ms=[];
const st=document.createElement('canvas');st.width=944;st.height=142;const sg=st.getContext('2d');
for(let k=0;k<5;k++){const c=mk(944,566);await raf();await raf();await raf();
  for(let s=0;s<4;s++){sg.clearRect(0,0,944,142);sg.drawImage(c,0,s*142,944,142,0,0,944,142);await raf();await raf();const a=performance.now();gl.texSubImage2D(gl.TEXTURE_2D,0,0,s*142,944,142,gl.RGBA,gl.UNSIGNED_BYTE,st);gl.finish();ms.push((performance.now()-a).toFixed(1));}}
out.stripCanvas=ms.join(' ');
ms=[];for(let k=0;k<5;k++){const c=mk(944,566);await raf();await raf();await raf();const a=performance.now();gl.texSubImage2D(gl.TEXTURE_2D,0,0,0,944,566,gl.RGBA,gl.UNSIGNED_BYTE,c);gl.finish();ms.push((performance.now()-a).toFixed(1));}
out.whole=ms.join(' ');
ms=[];for(let k=0;k<5;k++){const c=mk(944,566);await raf();await raf();await raf();const bm=await createImageBitmap(c);await raf();const a=performance.now();gl.texSubImage2D(gl.TEXTURE_2D,0,0,0,944,566,gl.RGBA,gl.UNSIGNED_BYTE,bm);gl.finish();ms.push((performance.now()-a).toFixed(1));}
out.imageBitmap=ms.join(' ');
return out;}'''
with sync_playwright() as p:
    b = p.webkit.launch(); pg = b.new_page(); print(pg.evaluate(JS)); b.close()
