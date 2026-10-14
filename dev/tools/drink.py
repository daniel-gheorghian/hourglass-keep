from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(300)
    r=pg.evaluate('''()=>{const H=__HK;const L=H.load(8,77,true);const P=H.P;P.hp=2;
      L.items.push({c:Math.floor(P.x/32),r:Math.floor((P.y-1)/64),x:P.x,type:'heal',taken:false});
      H.setKey('kb','g',true);H.tick(1);H.setKey('kb','g',false);H.tick(60);return {drank:L.items[L.items.length-1].taken,hp:P.hp};}''')
    print(json.dumps(r)); b.close()
