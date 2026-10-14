from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(300)
    print(pg.evaluate('''()=>{let bad=0,tot=0;for(let n=1;n<=40;n++)for(let s=0;s<25;s++){const L=__HK.genLevel(n,s*31+n*7,false);tot++;const d=L.door;
      for(let c=d.c-3;c<=d.c+1;c++){const f=L.feat[d.r*L.cols+c];if(L.base[d.r*L.cols+c]!==1||(f&&f.t!=='xplate')){bad++;break;}}}return bad+' bad exits of '+tot;}'''))
    b.close()
