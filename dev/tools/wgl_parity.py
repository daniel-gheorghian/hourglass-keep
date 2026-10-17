# wgl_parity.py [file.html] [only=name,...]: each drawing case drawn once by the real Canvas2D and once by the WebGL facade
# (G2D) at the same size, read back and compared (unit WGL). Prints per case: max and mean difference, the share of pixels off
# by more than 24 and the same away from edges; writes a sheet (2D | facade | diff x4) to wgl_parity/.
import sys, os, base64
import numpy as np
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright
import wgl_env as E
HERE = os.path.dirname(os.path.abspath(__file__))
html = next((x for x in sys.argv[1:] if x.endswith('.html')), os.path.join(HERE, '..', 'hourglass-keep.html'))
ONLY = ([x[5:] for x in sys.argv[1:] if x.startswith('only=')] or [''])[0].split(',')
OUT = os.path.join(HERE, 'wgl_parity'); os.makedirs(OUT, exist_ok=True)
CASES = {
 'rects': "g=>{g.fillStyle='#c33';g.fillRect(10.3,10.6,80.2,40.4);g.globalAlpha=.5;g.fillStyle='rgba(30,200,90,.8)';g.fillRect(40,30,90,50);g.globalAlpha=1;g.strokeStyle='#fff';g.lineWidth=1.3;g.strokeRect(5.5,60.5,100,30);}",
 'circles': "g=>{g.fillStyle='#e8c47f';g.beginPath();g.arc(50,50,30,0,6.2832);g.fill();g.fillStyle='rgba(80,90,255,.6)';g.beginPath();g.ellipse(90,60,40,15,.4,0,6.2832);g.fill();g.strokeStyle='#0b0812';g.lineWidth=2.5;g.beginPath();g.arc(140,60,25,.3,4,false);g.stroke();}",
 'concave': "g=>{g.fillStyle='#8f2f2a';g.beginPath();g.moveTo(10,10);g.lineTo(150,20);g.lineTo(80,40);g.lineTo(160,90);g.lineTo(20,100);g.closePath();g.fill();g.strokeStyle='#ff0';g.lineWidth=1;g.stroke();}",
 'star': "g=>{const R=40,px=80,py=60;g.fillStyle='rgba(255,230,150,.8)';g.beginPath();g.moveTo(px,py-R);g.lineTo(px+R*0.22,py-R*0.22);g.lineTo(px+R,py);g.lineTo(px+R*0.22,py+R*0.22);g.lineTo(px,py+R);g.lineTo(px-R*0.22,py+R*0.22);g.lineTo(px-R,py);g.lineTo(px-R*0.22,py-R*0.22);g.closePath();g.fill();}",
 'evenodd': "g=>{g.fillStyle='#4af';g.beginPath();g.rect(10,10,140,90);g.rect(40,30,60,40);g.fill('evenodd');g.fillStyle='#fa4';g.beginPath();g.arc(120,60,30,0,6.28);g.arc(120,60,15,0,6.28,true);g.fill();}",
 'selfx': "g=>{g.fillStyle='#9c6';g.beginPath();g.moveTo(10,10);g.lineTo(150,100);g.lineTo(150,10);g.lineTo(10,100);g.closePath();g.fill();g.fillStyle='#69c';g.beginPath();g.moveTo(20,60);g.bezierCurveTo(200,-40,-40,-40,140,60);g.closePath();g.fill('evenodd');}",
 'strokes': "g=>{g.strokeStyle='rgba(255,236,170,.55)';g.lineWidth=6;g.lineJoin='miter';g.beginPath();g.moveTo(10,90);g.lineTo(40,20);g.lineTo(70,90);g.lineTo(100,30);g.stroke();g.lineCap='round';g.lineJoin='round';g.strokeStyle='rgba(120,200,255,.6)';g.lineWidth=9;g.beginPath();g.moveTo(110,20);g.quadraticCurveTo(170,40,120,95);g.stroke();g.lineCap='square';g.lineJoin='bevel';g.lineWidth=4;g.strokeStyle='#fff';g.beginPath();g.moveTo(20,105);g.lineTo(150,105);g.lineTo(150,70);g.stroke();}",
 'dash': "g=>{g.strokeStyle='#ddd';g.lineWidth=2;g.setLineDash([4,3]);g.beginPath();g.moveTo(10,20);g.lineTo(150,40);g.lineTo(150,100);g.stroke();g.setLineDash([]);}",
 'linear': "g=>{const gr=g.createLinearGradient(10,0,150,30);gr.addColorStop(0,'rgba(255,0,0,1)');gr.addColorStop(.4,'#ff0');gr.addColorStop(1,'rgba(0,0,255,0)');g.fillStyle=gr;g.fillRect(0,0,160,110);}",
 'radial': "g=>{const gr=g.createRadialGradient(80,55,5,80,55,60);gr.addColorStop(0,'rgba(255,214,150,.9)');gr.addColorStop(1,'rgba(255,170,110,0)');g.fillStyle=gr;g.fillRect(0,0,160,110);const g2=g.createRadialGradient(40,40,0,60,50,40);g2.addColorStop(0,'#fff');g2.addColorStop(1,'rgba(0,0,0,0)');g.fillStyle=g2;g.beginPath();g.arc(55,50,40,0,6.3);g.fill();}",
 'xform': "g=>{g.save();g.translate(80,55);g.rotate(.5);g.scale(1.5,.7);g.fillStyle='#c8a';g.beginPath();g.arc(0,0,30,0,6.28);g.fill();const gr=g.createLinearGradient(-30,0,30,0);gr.addColorStop(0,'#000');gr.addColorStop(1,'#0f0');g.fillStyle=gr;g.fillRect(-20,-10,40,20);g.restore();}",
 'clip': "g=>{g.save();g.beginPath();g.rect(20.5,15.3,100,60);g.clip();g.save();g.beginPath();g.arc(70,50,40,0,6.28);g.clip();g.fillStyle='#f80';g.fillRect(0,0,160,110);g.restore();g.fillStyle='rgba(0,128,255,.5)';g.fillRect(0,0,160,110);g.restore();g.fillStyle='#fff';g.fillRect(120,80,30,20);}",
 'composite': "g=>{g.fillStyle='#406080';g.fillRect(0,0,160,110);g.globalCompositeOperation='lighter';g.fillStyle='rgba(200,100,50,.6)';g.beginPath();g.arc(60,50,35,0,6.28);g.fill();g.globalCompositeOperation='multiply';g.fillStyle='#c0ffc0';g.fillRect(70,30,80,60);g.globalCompositeOperation='destination-out';g.fillStyle='rgba(0,0,0,.5)';g.fillRect(10,80,40,20);g.globalCompositeOperation='source-over';}",
 'image': "g=>{const c=__HK.lightSprite('255,190,110');g.drawImage(c,10,10,60,60);g.globalAlpha=.6;g.drawImage(c,0,0,32,32,70,20,80,80);g.globalAlpha=1;g.globalCompositeOperation='lighter';g.drawImage(c,90,40,40,40);g.globalCompositeOperation='source-over';}",
 'path2d': "g=>{const p=new __HK.HKPath();p.moveTo(20,20);p.quadraticCurveTo(80,0,140,30);p.lineTo(120,90);p.arc(60,80,25,0,3.5,true);p.closePath();g.fillStyle='#7a5';g.fill(p);g.strokeStyle='#0b0812';g.lineWidth=1.25;g.stroke(p);g.save();g.translate(10,5);g.scale(.82,.82);g.fillStyle='#ae7';g.fill(p);g.restore();}",
 'downscale': "g=>{const H=__HK;if(!window.__SILC){const c=document.createElement('canvas');c.width=c.height=192;const x=c.getContext('2d');x.setTransform(2,0,0,2,0,0);H.drawFigureHD(x,48,80,1,Object.values(H.PS)[3],H.PAL_HERO,{mono:'#ff0000',hasSword:false,time:0});window.__SILC=c;}for(let i=0;i<6;i++)g.drawImage(__SILC,4+i*26.3,10+i*0.37,34-i*3,34-i*3);g.drawImage(__SILC,20,55,64,64);}",
 'figure': "g=>{const H=__HK;g.save();g.scale(2.4,2.4);H.drawFigureHD(g,35,44,1,H.PS.stand||Object.values(H.PS)[0],H.PAL_HERO,{hasSword:true,sword:true,time:3.2,lt:{dir:1,col:'255,188,100',k:.8}});g.restore();}",
 'figure2': "g=>{const H=__HK;const ps=Object.values(H.PS);g.save();g.scale(2.4,2.4);H.drawFigureHD(g,30,44,-1,ps[Math.min(ps.length-1,9)],H.PAL_HERO,{hasSword:true,sword:true,time:1.7,lt:{dir:-1,col:'150,175,255',k:.5}});H.drawFigureHD(g,52,44,1,ps[Math.min(ps.length-1,20)],H.PAL_HERO,{mono:'#ff0000',hasSword:false,time:0});g.restore();}",
}
W, H = 160 * 3, 110 * 3
RUN = r'''([src,W,Hh])=>{const H=__HK,draw=eval(src);
  const c=document.createElement('canvas');c.width=W;c.height=Hh;const g=c.getContext('2d');g.setTransform(3,0,0,3,0,0);draw(g);const a=g.getImageData(0,0,W,Hh).data;
  if(!H.GLS.ok){H.S.set.lightMode='torch';H.render();}
  const gl=H.GLS.gl,t=H.g2Target('test',1),F=new H.G2D(t);H.g2Begin();F.begin(W,Hh,[0,0,0,0]);F.setTransform(3,0,0,3,0,0);draw(F);H.GLS.rs=1;H.g2Replay();
  const px=new Uint8Array(W*Hh*4);gl.bindFramebuffer(gl.FRAMEBUFFER,t.rf);gl.readPixels(0,0,W,Hh,gl.RGBA,gl.UNSIGNED_BYTE,px);gl.bindFramebuffer(gl.FRAMEBUFFER,null);
  const enc=u=>{let s='';for(let i=0;i<u.length;i+=0x8000)s+=String.fromCharCode.apply(null,u.subarray(i,i+0x8000));return btoa(s);};
  return {a:enc(new Uint8Array(a.buffer)),b:enc(px),st:Object.assign({},H.GLS.stats)};}'''
with sync_playwright() as p:
    b = E.launch(p); pg = b.new_page(viewport={'width': 844, 'height': 390}); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: errs.append(m.text) if 'G2D' in m.text else None)
    E.setup(pg); pg.goto(E.url(html)); pg.wait_for_timeout(400)
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true)")
    rows = []
    for name, src in CASES.items():
        if ONLY != [''] and name not in ONLY: continue
        r = pg.evaluate(RUN, [src, W, H])
        A = np.frombuffer(base64.b64decode(r['a']), np.uint8).reshape(H, W, 4)
        B = np.frombuffer(base64.b64decode(r['b']), np.uint8).reshape(H, W, 4)[::-1]
        # compare premultiplied colours (what is composited), over a black background
        Af = A[..., :3].astype(np.int32) * A[..., 3:4] // 255; Bf = B[..., :3].astype(np.int32)
        d = np.abs(Af - Bf).max(axis=2); d = np.maximum(d, np.abs(A[..., 3].astype(np.int32) - B[..., 3].astype(np.int32)))
        g = Af.max(axis=2); pad = np.pad(g, 1, mode='edge')
        mx = np.maximum.reduce([pad[i:i + H, j:j + W] for i in range(3) for j in range(3)]); mn = np.minimum.reduce([pad[i:i + H, j:j + W] for i in range(3) for j in range(3)])
        flat = (mx - mn) < 24
        rows.append((name, int(d.max()), float(d.mean()), float((d > 24).mean() * 100), float(((d > 24) & flat).mean() * 100), r['st']))
        sh = Image.new('RGB', (W * 3 + 8, H), (40, 40, 40)); sh.paste(Image.fromarray(Af.clip(0, 255).astype(np.uint8)), (0, 0)); sh.paste(Image.fromarray(Bf.clip(0, 255).astype(np.uint8)), (W + 4, 0)); sh.paste(Image.fromarray(np.clip(d * 4, 0, 255).astype(np.uint8)).convert('RGB'), (W * 2 + 8, 0))
        sh.save(os.path.join(OUT, name + '.png'))
    for r in rows: print('%-10s max %3d mean %6.3f  >24 %6.3f%%  flat>24 %6.3f%%  %s' % r)
    print('errors', errs[:8]); b.close()
