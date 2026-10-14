from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':844,'height':390}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(300)
    r=pg.evaluate('''()=>{const H=__HK;let n=1;for(;n<30;n++){H.startLevel(n,-1);if(H.L.items.some(i=>i.type==='heal'))break;}
      const it=H.L.items.find(i=>i.type==='heal');const P=H.P;P.hp=1;P.x=it.x;P.y=(it.r+1)*64-4;P.state='stand';
      H.setKey('kb','g',true);H.tick(1);H.setKey('kb','g',false);H.tick(60);const hp=P.hp;
      H.snapshotResume();const R=JSON.parse(JSON.stringify(H.S.resume));
      H.startLevel(n,-1);H.applyResume(R);
      return {floor:n,hpAfterDrink:hp,takenAt:R.takenAt,flaskStillGone:H.L.items.find(i=>i.c===it.c&&i.r===it.r).taken};}''')
    print(json.dumps(r), errs); b.close()
