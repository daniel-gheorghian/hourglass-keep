# whole-floor map: walls dark, open space light, floors as lines, traps coloured, the route's runs numbered
from playwright.sync_api import sync_playwright
import base64,sys,os
f=sys.argv[1]; out=sys.argv[2]; n=int(sys.argv[3]); seed=int(sys.argv[4]); tw=int(sys.argv[5]) if len(sys.argv)>5 else 4
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+os.path.abspath(f)); pg.wait_for_timeout(300)
    u=pg.evaluate('''([n,seed,tw])=>{const H=__HK,L=H.genLevel(n,seed,true),th=tw*2,cv=document.createElement('canvas');cv.width=L.cols*tw;cv.height=L.rows*th;const g=cv.getContext('2d');
      g.fillStyle='#2a2630';g.fillRect(0,0,cv.width,cv.height);
      const col={spikes:'#e04040',loose:'#e0a020',chomp:'#ff60ff',gate:'#60c0ff',plate:'#60ff90',closer:'#ff9060',xplate:'#ffffff',low:'#8080ff',stone:'#c08040',pend:'#c060ff',vent:'#ff7020',saw:'#ff3080',darter:'#ffff40',banner:'#d04070',bar:'#80ffff',trigger:'#60ff90',shaftfoot:'#ffffff',sanctum:'#ffd060'};
      for(let r=0;r<L.rows;r++)for(let c=0;c<L.cols;c++){const b=L.base[r*L.cols+c];if(b===2)continue;g.fillStyle=b===1?'#cfc6b4':'#8d8576';g.fillRect(c*tw,r*th,tw,th);
        const below=r+1<L.rows?L.base[(r+1)*L.cols+c]:2;if(b===1||below===2){g.fillStyle='#4a3f30';g.fillRect(c*tw,r*th+th-2,tw,2);}
        const ft=L.feat[r*L.cols+c];if(ft&&col[ft.t]){g.fillStyle=col[ft.t];g.fillRect(c*tw,r*th+th*0.45,tw,th*0.4);}}
      for(const gd of L.guards){g.fillStyle=gd.skel?'#ffffff':'#ff2020';g.beginPath();g.arc(gd.x/32*tw,(gd.r+0.5)*th,tw*0.9,0,7);g.fill();}
      for(const it of L.items){g.fillStyle=it.type==='life'?'#ffd700':it.type==='big'?'#ff4060':'#ff8080';g.fillRect(it.c*tw,it.r*th+2,tw,th-4);}
      for(const cp of L.cps){g.strokeStyle='#40ff40';g.lineWidth=2;g.strokeRect(cp.c*tw-1,cp.r*th,tw+2,th);}
      g.fillStyle='#00ff00';g.fillRect(L.start.x/32*tw-tw,L.start.r*th,tw*2,th);g.fillStyle='#ffffff';g.fillRect(L.door.c*tw-tw,L.door.r*th,tw*3,th);
      g.font='bold '+(th*1.6)+'px sans-serif';g.fillStyle='#ffe060';(L.runsInfo||[]).forEach((ri,i)=>{g.fillText((i+1)+(ri.dir>0?'→':'←'),ri.c0*tw,(ri.row-1.2)*th);});
      return [cv.toDataURL(),L.cols,L.rows];}''',[n,seed,tw])
    open(out,'wb').write(base64.b64decode(u[0].split(',')[1])); print(u[1:],errs[:3]); b.close()
