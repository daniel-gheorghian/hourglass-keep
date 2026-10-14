import json, sys
from playwright.sync_api import sync_playwright
src=sys.argv[1]
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':844,'height':390}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+src); pg.wait_for_timeout(400); pg.add_script_tag(path='bot.js')
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true)")
    r=pg.evaluate('''()=>{const H=__HK;const res=[];
      for(const n of [1,5,9,14,20]){let tot=0,samples=0,worst=0,ok=0,runs=0;
        for(let s=0;s<3;s++){let k=0;
          const r=runBot(n,4400+n*31+s*7,{stop:(H)=>{ if((k++)%20)return false;
            const L=H.L,cam=H.cam,vw=H.viewW,vy=(cam.y!==undefined?cam.y:cam.ry*192);
            let wall=0,area=0;for(let y=vy+4;y<vy+192;y+=8)for(let x=cam.x+4;x<cam.x+vw;x+=8){area++;const c=Math.floor(x/32),r=Math.floor(y/64);
              const inLvl=c>=0&&c<L.cols&&r>=0&&r<L.rows;const b=inLvl?L.base[r*L.cols+c]:2;if(b===2)wall++;}
            const f=wall/area;tot+=f;samples++;worst=Math.max(worst,f);return false;}});
          runs++;if(r.ok===true)ok++;}
        res.push({n,wallShare:Math.round(100*tot/samples),worst:Math.round(100*worst),finished:ok+'/'+runs});}
      return res;}''')
    for x in r: print(json.dumps(x))
    print('errors',errs[:3]); b.close()
