# tapsheet.py out.png [lv]: every tapestry design in every theme (clean art, x6), as a sheet: tapestry check
import sys, base64
from playwright.sync_api import sync_playwright
out = sys.argv[1]; lv = int(sys.argv[2]) if len(sys.argv) > 2 else 0
JS = """([lv])=>{const st=['dungeon','palace','tile','forge','crypt'];const c=document.createElement('canvas');const Z=5,CW=44,CH=130;c.width=CW*Z*6;c.height=CH*Z*6;const g=c.getContext('2d');g.fillStyle='#161018';g.fillRect(0,0,c.width,c.height);g.scale(Z,Z);
  const TH=__HK.THEMES,tapCloth=__HK.tapCloth;let row=0;
  for(const s of st){const th=TH.find(t=>t.style===s);for(let k=0;k<7;k++){const long=k===5&&false,w=k===6?28:36+(k%2)*2,h=k===6?96:(k===5?72:64);g.save();g.translate(2+k*CW/ (1) ,0);g.restore();
    g.save();g.translate(k*CW+4,row*CH*0+ (st.indexOf(s)<5?0:0));g.restore();}}
  // layout 5 themes (rows) x 7 designs (cols)
  const c2=document.createElement('canvas');c2.width=CW*Z*7;c2.height=CH*Z*5;const g2=c2.getContext('2d');g2.fillStyle='#161018';g2.fillRect(0,0,c2.width,c2.height);g2.scale(Z,Z);
  st.forEach((s,ri)=>{const th=TH.find(t=>t.style===s);for(let k=0;k<7;k++){const w=k===6?28:36,h=k===6?100:(k===5?100:64);g2.save();g2.translate(k*CW+4,ri*CH+6);tapCloth(g2,th,k,0,0,w,h,0,lv);g2.strokeStyle='#000';g2.lineWidth=1;g2.strokeRect(0,0,w,h);g2.restore();}});
  return c2.toDataURL();}"""
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 844, 'height': 390})
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(400)
    print(pg.evaluate("typeof __HK.tapCloth"))
    u = pg.evaluate(JS, [lv])
    open(out, 'wb').write(base64.b64decode(u.split(',')[1])); b.close()
