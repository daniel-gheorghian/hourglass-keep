# wgl_gpustats.py [file.html] [floor ...]: what one Torchlight frame asks of the GPU on the new path (WK=1: WebKit; VP=WxHxDPR,
# default the phone's 852x283x2): per target its size, MSAA samples and draws, and the frame's draws, vertices, uploads and
# overdraw of the scene target (the area of every drawn triangle over the target's area), averaged over 120 frames of bot play.
import os, sys
from playwright.sync_api import sync_playwright
import wgl_env as E
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
html = next((x for x in a if x.endswith('.html')), os.path.join(HERE, '..', 'hourglass-keep.html'))
FL = [int(x) for x in a if x.isdigit()] or [1, 10]
VP = os.environ.get('VP', '852x283x2').split('x')
JS = r'''([n])=>{const H=__HK;H.S.set.lightMode='torch';H.GLP.pipe=false;window.__HKnoauto=true;let k=0;
  runBot(n,9000+n,{fight:true,stop:h=>++k>=600});
  const G=H.GLS,acc={draws:0,verts:0,up:0,area:0,frames:0,tg:{}};let up0=G.stats.up||0;
  for(let f=0;f<120;f++){H.tick(1);H.render();
    acc.draws+=G.stats.draws;acc.verts+=G.stats.verts;acc.frames++;
    for(const t of G.T){const o=acc.tg[t.name]||(acc.tg[t.name]={w:t.w,h:t.h,S:t.S,ops:0,n:0,area:0});o.ops+=t.ops.length;o.n++;
      if(t===G.scene){let ar=0;const V=G.F32,I=G.I32;for(const op of t.ops){if(op.k!==0||!op.n)continue;for(let i=op.first;i<op.first+op.n;i+=3){const a=I[i]*7,b=I[i+1]*7,c=I[i+2]*7;ar+=Math.abs((V[b]-V[a])*(V[c+1]-V[a+1])-(V[c]-V[a])*(V[b+1]-V[a+1]))/2;}}o.area+=ar/(t.w0*t.h0);}}}
  acc.up=(G.stats.up||0)-up0;return acc;}'''
with sync_playwright() as p:
    b = E.launch(p, True)
    for n in FL:
        pg = b.new_page(viewport={'width': int(VP[0]), 'height': int(VP[1])}, device_scale_factor=float(VP[2])); E.setup(pg)
        pg.goto(E.url(html)); pg.wait_for_timeout(500); pg.add_script_tag(path=os.path.join(HERE, 'bot.js'))
        pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
        r = pg.evaluate(JS, [n]); F = r['frames']
        print('floor', n, 'draws/frame %.0f' % (r['draws'] / F), 'verts/frame %.0f' % (r['verts'] / F), 'uploads in %d frames: %d' % (F, r['up']))
        for k, o in r['tg'].items():
            print('   %-6s %4dx%-4d S%d used %3d/%d frames, ops/frame %.0f' % (k, o['w'], o['h'], o['S'] or 0, o['n'], F, o['ops'] / max(o['n'], 1)) + ('  scene overdraw %.2f' % (o['area'] / o['n']) if o['area'] else ''))
        pg.close()
    b.close()
