from playwright.sync_api import sync_playwright
import sys,statistics as S
for f in sys.argv[1:]:
  with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); pg.goto('file://'+f); pg.wait_for_timeout(300)
    r=pg.evaluate('''()=>{const H=__HK,o={};const MOV=new Set(['flat','up','down','drop2']);for(const n of [3,4,5,6]){const a=[];for(let s=0;s<40;s++){const L=H.genLevel(n,11000+s*53,true);
      a.push(L.segs.filter(q=>!q.k.startsWith('turn-')&&!MOV.has(q.k)).length);}o[n]=a;}return o;}''')
    for n,a in r.items():
        a=sorted(a);print(f.split('/')[-1][:14],n,'mean',round(S.mean(a),1),'min',a[0],'p5',a[2],'p10',a[4])
    b.close()
