from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page()
    pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(300)
    pg.add_script_tag(path='bot.js')
    # patch: real levels, guards removed, chompers frozen open, gates real
    pg.evaluate('''()=>{const H=__HK;const orig=H.load;H.load=function(n,s){const L=orig.call(H,n,s,false);
       for(const g of H.G){g.alive=false;g.gone=true;}
       for(const o of L.dyn){if(o.f.t==='chomp'){o.f.per=1e6;o.f.off=5e5;}}
       // rebuild bot path for guard segments already 'walk'
       return L;};}''')
    res=pg.evaluate('''()=>{const out=[];let ok=0,tot=0,gates=0;for(let n=3;n<=36;n++)for(let s=0;s<3;s++){const r=runBot(n,8000+n*37+s*5);tot++;if(r.ok===true)ok++;else out.push(r);
       }return {ok,tot,fails:out.slice(0,8)};}''')
    print(json.dumps(res)[:3000])
    b.close()
