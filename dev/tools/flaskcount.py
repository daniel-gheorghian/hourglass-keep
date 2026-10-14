import json, sys
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page()
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(300)
    r=pg.evaluate('''()=>{const out=[];for(const n of [1,3,5,10,15,20,30]){let tot=0,maxScreen=0,heal=0,poison=0,life=0,K=30;const hashes=[];
      for(let s=0;s<K;s++){const L=__HK.genLevel(n,5000+s*77,false);tot+=L.items.length;
        for(const it of L.items){if(it.type==='heal')heal++;else if(it.type==='poison')poison++;else life++;}
        const cs=L.items.map(i=>i.c).sort((a,b)=>a-b);for(let i=0;i<cs.length;i++){let k=0;for(let j=i;j<cs.length&&cs[j]-cs[i]<13;j++)k++;maxScreen=Math.max(maxScreen,k);}
        let h=0;for(let i=0;i<L.base.length;i++)h=(h*31+L.base[i])|0;hashes.push(h);}
      out.push({n,cols:__HK.genLevel(n,5000,false).cols,avg:+(tot/K).toFixed(1),heal:+(heal/K).toFixed(1),poison:+(poison/K).toFixed(1),life:+(life/K).toFixed(2),maxOnScreen:maxScreen,hash:hashes.reduce((a,b)=>(a*7+b)|0,0)});}
      return out;}''')
    for x in r: print(json.dumps(x))
    b.close()
