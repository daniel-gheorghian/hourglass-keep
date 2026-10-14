import json,sys
from playwright.sync_api import sync_playwright
JS=r'''([ns,seeds])=>{const H=__HK;let main=0,br=0,det=0,dbl=0,sec=0,amb=0;
 for(const n of ns)for(let s=0;s<seeds;s++){const L=H.load(n,1000+n*97+s*7919,true);const m=L.segs.filter(q=>q.k==='guard'||q.k==='skel').length;main+=m;br+=L.guards.length-m;
  for(const d of L.detours||[]){if(d.double)dbl++;else if(d.secret)sec++;else det++;}
  for(const o of L.dyn)if(o.f.amb)amb++;}
 return {main,br,det,dbl,sec,amb};}'''
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(300)
    print(sys.argv[1].split('/')[-1],json.dumps(pg.evaluate(JS,[list(range(4,31)),20])))
    b.close()
