from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':844,'height':390})
    errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(300)
    out=pg.evaluate('''()=>{const H=__HK;const S=H.S;
      // find a floor with a gold flask under the player's save seed
      let n=3;for(;n<60;n+=3){H.startLevel(n,-1);if(H.L.items.some(i=>i.type==='life'))break;}
      const res={floor:n};
      const it=H.L.items.find(i=>i.type==='life');
      res.maxBefore=S.maxHp;
      const P=H.P;P.x=it.x;P.y=(it.r+1)*64-4;P.state='stand';P.face=1;
      H.setKey('kb','g',true);H.tick(1);H.setKey('kb','g',false);H.tick(60);
      res.maxAfterDrink=S.maxHp;res.state=P.state;
      // die and rise, then check the flask
      P.y=H.L.rows*64+300;P.state='air';P.vy=10;H.tick(5);res.mode=H.mode;
      H.tick(200);
      res.modeAfter=H.mode;
      res.flaskBackAfterDeath=H.L.items.filter(i=>i.type==='life'&&!i.taken).length;
      // try drinking at the same spot again
      const it2=H.L.items.find(i=>i.type==='life');const P2=H.P;P2.x=it2.x;P2.y=(it2.r+1)*64-4;P2.state='stand';
      H.setKey('kb','g',true);H.tick(1);H.setKey('kb','g',false);H.tick(60);
      res.maxAfterSecondTry=S.maxHp;res.lifeTaken=S.lifeTaken;
      return res;}''')
    print(json.dumps(out), errs)
    b.close()
