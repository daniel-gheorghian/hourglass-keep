# wgl_gputime.py [file.html] [floor ...]: the GPU's own time for a Torchlight frame, by stage, from EXT_disjoint_timer_query_webgl2
# (Chromium with the GPU; this Mac's GPU, not the phone's: compare builds and paths here with each other). Bot play to tick 600,
# then 90 frames timed; prints the mean ms per stage: g2 (the new path's scene and masks: replay and resolves), upload (the v60
# path's copy of the 2D frame), passes (light map, relief, atmosphere, bloom, composite, storm). Pass `2d` for the v60 path; MSAA=1 or 2 for the
# new path's samples; INIT='js' run before the page's own script.
import os, sys
from playwright.sync_api import sync_playwright
import wgl_env as E
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
html = next((x for x in a if x.endswith('.html')), os.path.join(HERE, '..', 'hourglass-keep.html'))
FL = [int(x) for x in a if x.isdigit()] or [1, 10]
D2 = '2d' in a
JS = r'''async([n,d2])=>{const H=__HK;H.S.set.lightMode='torch';H.GLP.pipe=false;window.__HKnoauto=true;if(d2)H.GLFX.wgl=false;let k=0;
  runBot(n,9000+n,{fight:true,stop:h=>++k>=600});
  const gl=H.GLP.gl,X=gl.getExtension('EXT_disjoint_timer_query_webgl2');if(!X)return 'no timer query';
  const res={},pend=[],raf=()=>new Promise(r=>requestAnimationFrame(r));
  const PF=H.PF,op=PF.p;let cur=null,q=null,t0=null;
  // each PF.p(name) mark closes the stage that ran since the last mark: one query per stage
  const begin=()=>{q=gl.createQuery();gl.beginQuery(X.TIME_ELAPSED_EXT,q);};
  PF.p=function(name){if(q){gl.endQuery(X.TIME_ELAPSED_EXT);pend.push([name,q]);q=null;}begin();};
  for(let f=0;f<90;f++){H.tick(1);begin();H.render();if(q){gl.endQuery(X.TIME_ELAPSED_EXT);pend.push(['rest',q]);q=null;}await raf();
    for(let i=pend.length-1;i>=0;i--){const [nm,qq]=pend[i];if(gl.getQueryParameter(qq,gl.QUERY_RESULT_AVAILABLE)){const v=gl.getQueryParameter(qq,gl.QUERY_RESULT)/1e6;res[nm]=(res[nm]||0)+v;gl.deleteQuery(qq);pend.splice(i,1);}}}
  for(let w=0;w<30&&pend.length;w++){await raf();for(let i=pend.length-1;i>=0;i--){const [nm,qq]=pend[i];if(gl.getQueryParameter(qq,gl.QUERY_RESULT_AVAILABLE)){res[nm]=(res[nm]||0)+gl.getQueryParameter(qq,gl.QUERY_RESULT)/1e6;pend.splice(i,1);}}}
  PF.p=op;const o={};let tot=0;for(const k in res){o[k]=+(res[k]/90).toFixed(3);tot+=res[k]/90;}o.total=+tot.toFixed(3);return o;}'''
with sync_playwright() as p:
    b = E.launch(p, True)
    for n in FL:
        pg = b.new_page(viewport={'width': 852, 'height': 283}, device_scale_factor=2); E.setup(pg)
        if os.environ.get('INIT'): pg.add_init_script(os.environ['INIT'])
        if os.environ.get('MSAA'): pg.add_init_script('window.__HKmsaa=%s' % os.environ['MSAA'])
        pg.goto(E.url(html)); pg.wait_for_timeout(500); pg.add_script_tag(path=os.path.join(HERE, 'bot.js'))
        pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
        print('floor', n, '2d' if D2 else 'new', pg.evaluate(JS, [n, D2]), flush=True)
        pg.close()
    b.close()
