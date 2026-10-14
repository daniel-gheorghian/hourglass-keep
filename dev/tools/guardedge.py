from playwright.sync_api import sync_playwright
JS=r'''()=>{let bad=[],tot=0;const solid=(L,c,r)=>{const b=L.base[r*L.cols+c];if(b===1)return true;if(b===2)return false;return r+1<L.rows&&L.base[(r+1)*L.cols+c]===2;};
 for(let n=1;n<=40;n++)for(let s=0;s<5;s++){const L=__HK.genLevel(n,s*7919+n*3,false);
  for(const g of L.guards){if(g.skel)continue;tot++;
    // a player pressed against the guard at either end of its range must be standing on solid floor
    for(const x of [g.lo-18,g.hi+18]){const c=Math.floor(x/32);if(!solid(L,c,g.r)||L.base[g.r*L.cols+c]===2)bad.push(n+':'+s+' x'+Math.round(x)+' c'+c);}}}
 return {guards:tot,unsafe:bad.length,examples:bad.slice(0,8)};}'''
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page();pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html');pg.wait_for_timeout(300);print(pg.evaluate(JS));b.close()
