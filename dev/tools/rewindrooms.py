# rewindrooms.py [lo hi]: after a rewind the room pictures show the floor as it was (v53: a rewind redraws only the rooms whose
# tiles or rubble changed, instead of every room on every step). Per floor: play a moment, knock a hole in a floor tile in view
# (and drop rubble on another), draw the rooms with the change, rewind to before it, let the rooms be redrawn, and compare the
# room's picture with one drawn from scratch. Ends with 'FAILURES n'.
import os, sys
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
HTML = 'file://' + os.path.abspath(os.path.join(HERE, '..', 'hourglass-keep.html'))
a = sys.argv[1:]
lo = int(a[0]) if a else 3
hi = int(a[1]) if len(a) > 1 else lo + 2
JS = r'''(n)=>{const H=__HK;window.__HKfreeze=true;window.__HKnoauto=true;for(const id in H.HINTS)H.S.hints[id]=1;
  const L=H.load(n,9000+n,true);H.banner=null;const P=H.P;P.inv=1e9;
  for(let k=0;k<180;k++){P.inv=1e9;H.tick(1);}H.render();
  const C=L.cols,pr=Math.floor((P.y-1)/64);let hole=-1,rub=-1;
  for(let dc=3;dc<9&&(hole<0||rub<0);dc++)for(const s of [1,-1]){const c=Math.floor(P.x/32)+dc*s,i=pr*C+c;if(c<0||c>=C)continue;
    if(L.base[i]===1&&hole<0){hole=i;continue;}if(L.base[i]===1&&rub<0&&i!==hole)rub=i;}
  if(hole<0)return {skip:'no floor tile near'};
  const FLOOR=L.base[hole],rx=Math.floor((hole%C)/10),ry=Math.floor(pr/3),key=rx+','+ry;
  const pix=c=>{const g=c.getContext('2d');return g.getImageData(0,0,c.width,c.height).data;};
  const before=pix(H.roomCanvas(rx,ry));
  L.base[hole]=0;if(rub>=0)L.rubble.add(rub);H.clearRooms();H.render();const changed=pix(H.roomCanvas(rx,ry));
  let diffChange=0;for(let i=0;i<before.length;i+=4)if(before[i]!==changed[i]||before[i+1]!==changed[i+1])diffChange++;
  H.S.sands=3;H.startRewind();let k=0;while(H.mode==='rewind'&&k<600){H.tick(1);H.render();k++;}
  for(let j=0;j<60;j++){H.render();H.roomWork();}
  const after=pix(H.roomCanvas(rx,ry));H.clearRooms();const fresh=pix(H.roomCanvas(rx,ry));
  let bad=0;for(let i=0;i<fresh.length;i++)if(Math.abs(fresh[i]-after[i])>2)bad++;
  return {restored:L.base[hole]===FLOOR,rubbleGone:rub<0||!L.rubble.has(rub),diffChange,bad,steps:k};}'''
fails = 0
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 844, 'height': 390})
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(HTML); pg.wait_for_timeout(300)
    for n in range(lo, hi + 1):
        r = pg.evaluate(JS, n)
        ok = 'skip' in r or (r['restored'] and r['rubbleGone'] and r['diffChange'] > 0 and r['bad'] == 0)
        if not ok: fails += 1
        print(('ok  ' if ok else 'FAIL') + ' floor %d %s' % (n, r))
    if errs:
        fails += 1; print('page errors', errs[:3])
    b.close()
print('FAILURES', fails)
