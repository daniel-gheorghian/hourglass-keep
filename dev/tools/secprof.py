from playwright.sync_api import sync_playwright
import json,os,sys
src=sys.argv[1]
s=open(src).read()
marks=[("  // 1. the back plane, cell by cell\n","bp"),("  // 2. side faces","side"),("  // 3. front faces of walls","front"),("  if(!(all||stage===2))return;","end1"),("  // 4. floors: walking surface","floor")]
for m,k in marks:
    assert m in s,k
    s=s.replace(m,"  window.__T=window.__T||{};{const _n=performance.now();if(window.__lk)window.__T[window.__lk]=(window.__T[window.__lk]||0)+_n-window.__lt;window.__lk='"+k+"';window.__lt=_n;}\n"+m,1)
i=s.index("// a point on a floor's walking surface");j=s.rindex("}",0,i)
s=s[:j]+"{const _n=performance.now();if(window.__lk)window.__T[window.__lk]=(window.__T[window.__lk]||0)+_n-window.__lt;window.__lk=null;}"+s[j:]
open('dbg_sec2.html','w').write(s)
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2); pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+os.path.abspath('dbg_sec2.html')); pg.wait_for_timeout(500)
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    r=pg.evaluate('''()=>{const H=__HK,out={};for(const n of [3,15]){H.load(n,4242,true);window.__T={};
        for(let k=0;k<40;k++){H.P.x=(40+k*4)*32;H.cam.snap=true;H.tick(1);for(let i=0;i<6;i++){H.roomWork();window.__lk=null;}}
        out[n]=Object.fromEntries(Object.entries(window.__T).map(([a,b])=>[a,+b.toFixed(0)]));}return out;}''')
    print(src.split('/')[-1],json.dumps(r),errs[:2]); b.close()
