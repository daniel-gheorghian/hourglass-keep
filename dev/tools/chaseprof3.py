from playwright.sync_api import sync_playwright
import json,sys
for src in sys.argv[1:]:
  with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2)
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.add_init_script("""(()=>{window.__q=[];window.requestAnimationFrame=cb=>{window.__q.push(cb);return 1;};})();""")
    pg.goto('file://'+src); pg.wait_for_timeout(500); pg.add_script_tag(path='bot.js')
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    out={}
    for n in [int(x) for x in __import__('os').environ.get('FLOORS','11').split(',')]:
      r=pg.evaluate('''(n)=>{const H=__HK;let ts=1000;const g=document.getElementById('game').getContext('2d');const ch=[],no=[];
        const res=runBot(n,777+n,{fight:false,stop:H2=>{const c=H.L.ext.chase,on=!!(c&&c.on&&(c.fade||0)<1);const q=window.__q;window.__q=[];
          const t0=performance.now();for(const cb of q)cb(ts);g.getImageData(0,0,1,1);const dt=performance.now()-t0;(on?ch:no).push(dt);return false;}});
        const st=a=>{if(!a.length)return null;a.sort((x,y)=>x-y);const q=p=>+a[Math.min(a.length-1,Math.floor(p*a.length))].toFixed(1);return {n:a.length,p50:q(.5),p95:q(.95),p99:q(.99),over16:+(100*a.filter(x=>x>16.7).length/a.length).toFixed(2)};};
        return {ok:res.ok,chase:st(ch),normal:st(no)};}''',n)
      out[n]=r
    print(src.split('/')[-1],json.dumps(out),errs[:2]); b.close()
