from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(300)
    r=pg.evaluate('''()=>{const H=__HK;const L=H.load(6,700582,true);const ins=L.path.find(a=>a.a==='crawl');
      const P=H.P;P.x=ins.from*32+16;P.y=(()=>{for(let r=0;r<L.rows;r++){if(L.base[r*L.cols+ins.from]===1&&L.feat[r*L.cols+ins.from+1]&&L.feat[r*L.cols+ins.from+1].t==='low')return (r+1)*64-4;}})();P.state='stand';P.face=1;
      const out=[];H.setKey('kb','d',true);H.tick(1);H.setKey('kb','d',false);out.push(P.state);
      H.setKey('kb','r',true);for(let i=0;i<20;i++){H.tick(1);out.push(P.state+':'+P.x.toFixed(1));}
      return {ins,out};}''')
    print(json.dumps(r)); b.close()
