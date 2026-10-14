from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(300)
    print(pg.evaluate('''()=>{let N=0,D=0,gal=0,cel=0,chain=0,amb=0,lens=[],kinds={},cols=0;for(let n=4;n<=40;n++)for(let s=0;s<5;s++){N++;const L=__HK.genLevel(n,s*101+n*3,false);cols+=L.cols;
      for(const d of L.detours||[]){D++;d.gal?gal++:cel++;if(d.chain)chain++;if(d.amb)amb++;lens.push(d.len);for(const k of d.kinds)kinds[k]=(kinds[k]||0)+1;}}
      lens.sort((a,b)=>a-b);return JSON.stringify({perFloor:(D/N).toFixed(2),gal,cel,chain,amb,lenMin:lens[0],lenMed:lens[lens.length>>1],lenMax:lens[lens.length-1],detourColShare:(lens.reduce((a,b)=>a+b,0)/cols).toFixed(3),kinds});}'''))
    print('errors',errs[:5]); b.close()
