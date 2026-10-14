from playwright.sync_api import sync_playwright
JS='''()=>{let h=0;for(let n=1;n<=40;n++)for(let s=0;s<5;s++){const L=__HK.genLevel(n,s*7919+n,false);for(let i=0;i<L.base.length;i++)h=(Math.imul(h,31)+L.base[i]+(L.feat[i]?L.feat[i].t.length*7:0))|0;h=(h+L.guards.length*1000+L.snakeSpecs.length*17+L.path.length)|0;}return h;}'''
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page()
    for f in ['hk_v9_release.html','/Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html']:
        pg.goto('file://'+(f if f.startswith('/') else __import__('os').path.abspath(f))); pg.wait_for_timeout(300); print(f, pg.evaluate(JS), pg.evaluate('()=>__HK.S.gen'))
    b.close()
