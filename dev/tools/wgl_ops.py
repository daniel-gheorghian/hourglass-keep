# wgl_ops.py floor ... : the scene target's biggest draws of one Torchlight frame on the new path (WK=1: WebKit, the phone's
# 852x283 at dpr 2): each op's area (clipped to the screen, by its triangles' boxes) over the screen's, its kind, composite mode, shader mode and texture
import os, sys
from playwright.sync_api import sync_playwright
import wgl_env as E
HERE = os.path.dirname(os.path.abspath(__file__))
JS = r'''([n])=>{const H=__HK;H.S.set.lightMode='torch';H.GLP.pipe=false;window.__HKnoauto=true;let k=0;
  runBot(n,9000+n,{fight:true,stop:h=>++k>=600});H.tick(1);H.render();
  const G=H.GLS,t=G.scene,V=G.F32,I=G.I32,out=[];
  for(const op of t.ops){let ar=0;const f=op.k===0?op.first:op.cf,nn=op.k===0?op.n:op.cn;if(nn)for(let i=f;i<f+nn;i+=3){const a=I[i]*7,b=I[i+1]*7,c=I[i+2]*7;const A=Math.abs((V[b]-V[a])*(V[c+1]-V[a+1])-(V[c]-V[a])*(V[b+1]-V[a+1]))/2,x0=Math.min(V[a],V[b],V[c]),x1=Math.max(V[a],V[b],V[c]),y0=Math.min(V[a+1],V[b+1],V[c+1]),y1=Math.max(V[a+1],V[b+1],V[c+1]),bb=(x1-x0)*(y1-y0),cb=Math.max(0,Math.min(x1,t.w0)-Math.max(x0,0))*Math.max(0,Math.min(y1,t.h0)-Math.max(y0,0));ar+=bb>0?A*cb/bb:0;}
    const m=nn?V[I[f]*7+5]:-1;out.push([+(ar/(t.w0*t.h0)).toFixed(3),op.k,op.op,Math.round(m%8),op.tex?(op.tex.isTgt?'T:'+op.tex.name:(op.tex.width+'x'+op.tex.height+(op.tex._room?' room':''))):'',nn,op.tag||'']);}
  return out;}'''
with sync_playwright() as p:
    b = E.launch(p, True)
    for n in [int(x) for x in sys.argv[1:]]:
        pg = b.new_page(viewport={'width': 852, 'height': 283}, device_scale_factor=2); E.setup(pg)
        pg.goto(E.url(os.path.join(HERE, '..', 'hourglass-keep.html'))); pg.wait_for_timeout(500); pg.add_script_tag(path=os.path.join(HERE, 'bot.js'))
        pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
        r = pg.evaluate(JS, [n]); print('floor', n, 'total area', round(sum(x[0] for x in r), 2), 'ops', len(r))
        for x in sorted(r, key=lambda x: -x[0])[:14]: print('  ', x)
        pg.close()
    b.close()
