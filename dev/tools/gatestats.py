from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(300)
    print(pg.evaluate('''()=>{let up=0,down=0,closer=0,timed=0,N=0;for(let n=4;n<=40;n++)for(let s=0;s<5;s++){N++;const L=__HK.genLevel(n,s*101+n*3,false);
      for(const o of L.dyn){const f=o.f;if(f.t==='plate'&&f.latch){const g=L.dyn.find(q=>q.f===f.g);if(o.r<g.r)up++;else down++;}else if(f.t==='plate')timed++;if(f.t==='closer')closer++;}}
      return 'per floor (floors 4-40): gallery gates '+(up/N).toFixed(1)+', cellar gates '+(down/N).toFixed(1)+', timed gates '+(timed/N).toFixed(1)+' of which with a closing plate '+(closer/N).toFixed(1);}'''))
    b.close()
