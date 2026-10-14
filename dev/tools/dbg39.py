from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(300)
    print(pg.evaluate(r'''()=>{const L=__HK.load(27,702645,true);const B=(c,r)=>'.=#'[L.base[r*L.cols+c]];const o=[];
      o.push(JSON.stringify(L.loops));
      for(let r=53;r<=59;r++){let s='';for(let c=256;c<=276;c++){const f=L.feat[r*L.cols+c];s+=f?(f.t[0].toUpperCase()):B(c,r);}o.push(r+' '+s);}
      const i=L.path.findIndex(a=>a.a==='walk'&&a.c===266);o.push(JSON.stringify(L.path.slice(Math.max(0,i-6),i+3)));
      const gs=L.dyn.filter(d=>d.f.t==='gate'&&d.r===57&&d.c>250&&d.c<280).map(d=>[d.c,d.r,d.f.loop,d.f.pair,d.f.latch,d.f.far]);o.push(JSON.stringify(gs));
      const pl=L.dyn.filter(d=>d.f.t==='plate'&&d.f.loop).map(d=>[d.c,d.r]);o.push('loopplates '+JSON.stringify(pl));
      return o.join('\n');}'''))
    b.close()
