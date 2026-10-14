from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':844,'height':390}); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e))); pg.on('console',lambda m:errs.append('console:'+m.text) if m.type=='error' and 'ERR_' not in m.text else None)
    pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(400)
    r=pg.evaluate('''()=>{const out={};for(const n of [1,3,5,9,13,17,21,30]){const L=__HK.genLevel(n,1234+n,false);const ty={};for(const o of L.base?[]:[]);
        for(let i=0;i<L.feat.length;i++){const f=L.feat[i];if(f)ty[f.t+(f.plank?'P':'')]=(ty[f.t+(f.plank?'P':'')]||0)+1;}
        out[n]={cols:L.cols,rows:L.rows,guards:L.guards.length,skel:L.guards.filter(g=>g.skel).length,reinf:L.guards.filter(g=>g.reinf).length,snakes:L.snakeSpecs.length,cps:L.cps.length,feat:ty};}
      __HK.load(9,77,false);for(let i=0;i<120;i++)__HK.tick(1);__HK.render();return out;}''')
    for k,v in r.items(): print(k, json.dumps(v))
    print('errors', errs[:8]); b.close()
