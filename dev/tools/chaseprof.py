from playwright.sync_api import sync_playwright
import json,sys
src=sys.argv[1] if len(sys.argv)>1 else '/Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2)
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.add_init_script("""(()=>{const ce=document.createElement.bind(document);window.__cv=0;document.createElement=function(t,...a){if(String(t).toLowerCase()==='canvas')window.__cv++;return ce(t,...a);};})();""")
    pg.goto('file://'+src); pg.wait_for_timeout(500); pg.add_script_tag(path='bot.js')
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay');__HK.layout&&__HK.layout()")
    for n in [8,11,14]:
        r=pg.evaluate('''(n)=>{const H=__HK;const st={chase:[],norm:[],cvChase:0,cvNorm:0,fr:{chase:0,norm:0},storm:[]};let lastCv=window.__cv;
          const res=runBot(n,777+n,{fight:false,stop:H=>{const ch=H.L.ext.chase,on=!!(ch&&ch.on&&(ch.fade||0)<1);
            const t0=performance.now();H.render();const dt=performance.now()-t0;const d=window.__cv-lastCv;lastCv=window.__cv;
            if(on){st.chase.push(dt);st.cvChase+=d;st.fr.chase++;}else{st.norm.push(dt);st.cvNorm+=d;st.fr.norm++;}return false;}});
          const q=(a,p)=>{if(!a.length)return 0;const s=a.slice().sort((x,y)=>x-y);return +s[Math.min(s.length-1,Math.floor(p*s.length))].toFixed(2);};
          const av=a=>a.length?+(a.reduce((x,y)=>x+y,0)/a.length).toFixed(2):0;
          return {n,ok:res.ok,chaseFrames:st.fr.chase,normFrames:st.fr.norm,
            chase:{avg:av(st.chase),p95:q(st.chase,.95),p99:q(st.chase,.99),max:q(st.chase,1),roomBuildsPerSec:+(st.cvChase/(st.fr.chase/60||1)).toFixed(2)},
            normal:{avg:av(st.norm),p95:q(st.norm,.95),p99:q(st.norm,.99),max:q(st.norm,1),roomBuildsPerSec:+(st.cvNorm/(st.fr.norm/60||1)).toFixed(2)}};}''',n)
        print(json.dumps(r))
    print('errors',errs); b.close()
