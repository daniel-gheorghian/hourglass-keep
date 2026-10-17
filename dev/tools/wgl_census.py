# wgl_census.py [file] [floors]: which Canvas2D features the Torchlight scene and its masks use (for the GL facade's scope).
# Plays floors with the bot (fighting), renders in Torchlight every 6th tick, and records every call on the scene's 2D context
# and the mask contexts: methods, composite modes, style kinds, fill rules, clip, drawImage sources (by the drawing site).
import sys, os, json
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
html = next((x for x in sys.argv[1:] if x.endswith('.html')), os.path.join(HERE, '..', 'hourglass-keep.html'))
fl = [int(x) for x in sys.argv[1:] if x.isdigit()] or [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27]
JS = r'''
window.__CEN={calls:{},ops:{},styles:{},rules:{},imgs:{},props:{},sites:{}};
window.__inst=function(ctx,tag){if(ctx.__inst)return;ctx.__inst=1;const C=__CEN;
  const bump=(o,k)=>{o[k]=(o[k]||0)+1;};
  const site=()=>{const s=(new Error().stack||'').split('\n');for(let i=3;i<s.length;i++){const m=s[i].match(/at (\S+)/);if(m&&m[1]!=='Object.<computed>'&&m[1]!=='ctx.<computed>')return m[1];}return '?';};
  const P=CanvasRenderingContext2D.prototype;
  for(const k of Object.getOwnPropertyNames(P)){const d=Object.getOwnPropertyDescriptor(P,k);
    if(typeof d.value==='function'&&k!=='constructor'){const f=d.value;
      ctx[k]=function(...a){bump(C.calls,tag+' '+k);
        if(/^(fill|stroke|fillRect|strokeRect|drawImage|fillText|strokeText|putImageData|clearRect)$/.test(k)){bump(C.ops,tag+' '+k+' '+this.globalCompositeOperation);
          if(k==='fill'||k==='fillRect'||k==='fillText'){const s=this.fillStyle;bump(C.styles,tag+' fill '+(typeof s==='string'?'color':s.constructor.name));}
          if(k==='stroke'||k==='strokeRect'){const s=this.strokeStyle;bump(C.styles,tag+' stroke '+(typeof s==='string'?'color':s.constructor.name)+' cap='+this.lineCap+' join='+this.lineJoin+(this.getLineDash().length?' dash':''));}
          if(this.filter&&this.filter!=='none')bump(C.props,tag+' filter '+this.filter);
          if(this.shadowBlur||this.shadowOffsetX||this.shadowOffsetY)bump(C.props,tag+' shadow');}
        if(k==='fill'||k==='clip'){const r=a.find(x=>typeof x==='string')||'nonzero',p=a.find(x=>x instanceof Path2D);bump(C.rules,tag+' '+k+' '+r+(p?' Path2D':''));}
        if(k==='stroke'&&a[0] instanceof Path2D)bump(C.rules,tag+' stroke Path2D');
        if(k==='drawImage'){const s=a[0];const kind=s instanceof HTMLCanvasElement?'canvas':s.constructor.name;const key=tag+' '+site()+' '+kind+' '+(s.width+'x'+s.height)+' args'+a.length;bump(C.imgs,key);}
        if(k==='clip'||k==='createLinearGradient'||k==='createRadialGradient'||k==='createPattern'||k==='getImageData'||k==='putImageData'||k==='fillText'||k==='createConicGradient'||k==='arcTo'||k==='bezierCurveTo'||k==='roundRect')bump(C.sites,tag+' '+k+' @'+site());
        if(k==='createRadialGradient'&&(a[0]!==a[3]||a[1]!==a[4]))bump(C.sites,tag+' radial-noncentred @'+site());
        if(k==='createRadialGradient'&&a[2]>0)bump(C.sites,tag+' radial-r0>0 @'+site());
        return f.apply(this,a);};}}
  0;
};0;
'''
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 844, 'height': 390}, device_scale_factor=2); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://' + os.path.abspath(html)); pg.wait_for_timeout(400); pg.add_script_tag(path=os.path.join(HERE, 'bot.js'))
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    pg.evaluate(JS)
    for n in fl:
        r = pg.evaluate('''(n)=>{const H=__HK;H.S.set.lightMode='torch';H.render();const G=H.GLP;__inst(G.sceneG,'scene');if(G.mkG)__inst(G.mkG,'mask');let k=0;
          const r=runBot(n,777+n,{fight:true,stop:H=>{if(k>5000)return true;if(++k%15===0){H.render();const G=H.GLP;if(H.MS.g)__inst(H.MS.g,'metal');if(H.GLC.ocG)__inst(H.GLC.ocG,'occ');}if(k%60===0)for(let i=0;i<3;i++)H.roomWork();return false;}});return [r.ok,r.why,k];}''', n)
        print('floor', n, r, flush=True)
    cen = pg.evaluate('__CEN')
    for sec in ('calls', 'ops', 'styles', 'rules', 'props', 'sites', 'imgs'):
        print('==', sec)
        for k, v in sorted(cen[sec].items(), key=lambda kv: -kv[1]): print('%8d  %s' % (v, k))
    print('errors', errs[:5]); b.close()
