from playwright.sync_api import sync_playwright
import json,os,sys
for src in sys.argv[1:]:
  s=open(src).read()
  s=s.replace("window.__HK={","window.__WC=(...a)=>wallCell(...a);window.__BC=(...a)=>backCell(...a);window.__HK={",1)
  open('wcb.html','w').write(s)
  with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); pg.goto('file://'+os.path.abspath('wcb.html')); pg.wait_for_timeout(400)
    r=pg.evaluate('''()=>{const H=__HK,out={};for(const n of [3,15]){H.load(n,4242,true);const th=H.L.theme;const c=document.createElement('canvas');c.width=760;c.height=460;const g=c.getContext('2d');g.setTransform(2.4,0,0,2.4,0,0);
       let t=performance.now();for(let k=0;k<300;k++)__WC(g,(k%10)*32,0,40+k,3,th);const wc=(performance.now()-t)/300;
       t=performance.now();for(let k=0;k<300;k++){g.save();g.beginPath();g.rect((k%10)*32,0,32,64);g.clip();__BC(g,(k%10)*32,0,40+k,3,th);g.restore();}const bc=(performance.now()-t)/300;
       out[n]={wallCell_ms:+wc.toFixed(3),backCell_ms:+bc.toFixed(3)};}return out;}''')
    print(src.split('/')[-1],json.dumps(r)); b.close()
