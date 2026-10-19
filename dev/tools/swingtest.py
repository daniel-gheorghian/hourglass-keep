# swingtest.py [lo hi]: the swing bar is a trapeze (v57). Per floor with a bar (the first of a few seeds that has one), on the bar's
# own pit: left alone the swing comes to rest within 4.5 s; holding one way never swings him past 0.25 rad; pumping in step takes a
# standing catch (0.35) to 0.8 within 3.5 s and never past SW_MAX; a running catch (the bot's run-up) is already over SW_CLEAR (the
# owner chose that a good run clears at once); letting go from 0.4 never reaches the far side, from SW_MAX at 0 to 0.3 rad going
# forward he lands on the far floor (c+5 to c+7, never beyond); and a snapshot taken mid-swing (what the rewind keeps) brings back
# his angle and speed and the chains' angle and speed. Round 16b (a press is a pump): from a still hang, a press each way 0.2 s after
# each turn brings the cue (P.swRdy) within 2 s; mashing (a press every 0.1 s) never reaches SW_CLEAR. Ends with 'FAILURES n'.
import os, sys
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
HTML = 'file://' + os.path.abspath(os.path.join(HERE, '..', 'hourglass-keep.html'))
a = sys.argv[1:]
lo = int(a[0]) if a else 6
hi = int(a[1]) if len(a) > 1 else lo + 3
JS = r'''(n)=>{const H=__HK;window.__HKfreeze=true;window.__HKnoauto=true;for(const id in H.HINTS){H.S.hints[id]=1;H.S.learned[id]=1;}
 let L=null,o=null,SD=0;for(let sd=1;sd<=25&&!o;sd++){SD=7100+sd;L=H.load(n,SD,true);H.banner=null;o=L.dyn.find(q=>q.f.t==='bar');}
 if(!o)return {skip:'no bar'};
 let f=o.f;const RL=()=>{L=H.load(n,SD,true);H.banner=null;o=L.dyn.find(q=>q.f.t==='bar');f=o.f;};
 const D=L.base[o.r*L.cols+o.c+2]===L.base[o.r*L.cols+o.c]?1:-1,FW=D>0?'r':'l',BK=D>0?'l':'r',c=o.c-2*D,r=o.r,P=()=>H.P;
 const clr=()=>['l','r','j','d','u','g'].forEach(k=>H.setKey('kb',k,false)),amp=()=>H.swAmp(P().swTh,P().swOm),bad=[],res={seed:SD};
 const hold=(th,om)=>{RL();clr();const p=P();p.x=f.x;p.y=f.y+57;p.vx=0;p.vy=0;p.state='air';p.autoGrab=true;p.face=D;p.fallY=p.y;p.inv=1e9;f.ps=0;f.pw=0;H.tick(1);
   p.swTh=th;p.swOm=om;return p.state==='swing';};
 if(!hold(0,0))return {seed:SD,bad:['no catch under the bar']};
 // rest
 hold(0.85,0);let k=0;while(k<600&&!(P().swOm===0&&Math.abs(P().swTh)<0.03)){H.tick(1);k++;}res.rest=+(k/60).toFixed(2);if(k/60>4.5)bad.push('rest '+res.rest+' s');
 // one way
 for(const a0 of [0,0.5]){hold(a0,0);H.setKey('kb',FW,true);let mx=0;for(let i=0;i<360;i++){H.tick(1);if(i>150)mx=Math.max(mx,amp());}clr();res['oneWay'+a0]=+mx.toFixed(2);if(mx>0.25)bad.push('one way from '+a0+': '+mx.toFixed(2));}
 // pump
 hold(0,0.35*H.SW_W);k=0;let mx=0;while(k<600){const om=P().swOm;H.setKey('kb',FW,om>=0);H.setKey('kb',BK,om<0);H.tick(1);k++;const A=amp();mx=Math.max(mx,A);if(A>=0.8&&res.pump===undefined)res.pump=+(k/60).toFixed(2);}clr();
 res.pumpMax=+mx.toFixed(2);if(res.pump===undefined||res.pump>3.5)bad.push('pump to 0.8: '+res.pump);if(mx>H.SW_MAX+0.02)bad.push('pumped past the cap '+mx.toFixed(2));
 // (round 16b) from a still hang, a press each way 0.2 s after each turn: the cue (P.swRdy) within 2 s; mashing (a press every 0.1 s) never gets there
 {hold(0,0);k=0;let want=0,last=0,due=[[1,1]];while(k<300&&!P().swRdy){const om=P().swOm,sg=Math.abs(om)>0.05?Math.sign(om):0;if(sg&&sg!==last){last=sg;due.push([k+12,sg]);}
   while(due.length&&due[0][0]<=k)want=due.shift()[1];H.setKey('kb',FW,want>0);H.setKey('kb',BK,want<0);H.tick(1);k++;}clr();
  res.cue=P().swRdy?+(k/60).toFixed(2):null;if(res.cue===null||res.cue>2)bad.push('cue from a still hang: '+res.cue);}
 {hold(0,0);let m2=0;for(let i=0;i<300;i++){const w=Math.floor(i/6)%2;H.setKey('kb',FW,!w);H.setKey('kb',BK,!!w);H.tick(1);m2=Math.max(m2,amp());}clr();
  res.mash=+m2.toFixed(2);if(m2>=H.SW_CLEAR)bad.push('mashing reached '+m2.toFixed(2));}
 // running catch (the bot's run-up)
 {RL();clr();const p=P();p.x=(c-2*D)*32+16;p.y=(r+1)*64-4;p.fallY=p.y;p.state='stand';p.face=D;p.inv=1e9;f.ps=0;f.pw=0;H.tick(2);H.setKey('kb',FW,true);
  k=0;while(k<300&&!(p.state==='run'&&(p.x-(c*32+16-44*D))*D>=0)){H.tick(1);k++;}H.setKey('kb','j',true);H.tick(1);H.setKey('kb','j',false);
  k=0;while(k<120&&P().state!=='swing'){if(P().state==='air')H.setKey('kb',FW,false);H.tick(1);k++;}clr();
  res.runCatch=P().state==='swing'?+amp().toFixed(2):P().state;if(!(res.runCatch>=H.SW_CLEAR))bad.push('running catch '+res.runCatch);}
 // releases
 const rel=(A,tr)=>{hold(-A,0);k=0;while(k<200&&!(P().swOm>0&&P().swTh>=tr)){H.tick(1);k++;}if(P().swTh>A-0.02)return null;
   H.setKey('kb','j',true);H.tick(1);H.setKey('kb','j',false);k=0;while(k<240&&!['stand','land','landHurt','hang','dead','run','crouch'].includes(P().state)){H.tick(1);k++;}
   return {st:P().state,col:(Math.floor(P().x/32)-c)*D};};
 for(const tr of [-0.2,0,0.2,0.35]){const q=rel(0.4,tr);if(q&&(q.st!=='dead'&&q.st!=='landHurt'&&q.col>=4))bad.push('0.4 at '+tr+' reached '+q.st+q.col);}
 res.full=[];for(const tr of [0,0.1,0.2,0.3]){const q=rel(H.SW_MAX,tr);res.full.push(q?q.st+q.col:'-');if(!q||!(q.st==='land'||q.st==='stand'||q.st==='run'||q.st==='hang')||q.col<4||q.col>7)bad.push('full at '+tr+': '+(q?q.st+q.col:'none'));}
 // snapshot mid-swing
 {hold(0,0.5*H.SW_W);for(let i=0;i<50;i++){const om=P().swOm;H.setKey('kb',FW,om>=0);H.setKey('kb',BK,om<0);H.tick(1);}clr();
  const s0=H.snapAll(),v0=[P().swTh,P().swOm,f.ps,f.pw];for(let i=0;i<70;i++)H.tick(1);H.applySnap(s0);const v1=[P().swTh,P().swOm,f.ps,f.pw];
  for(let i=0;i<70;i++)H.tick(1);H.applySnap(s0);for(let i=0;i<20;i++)H.tick(1);const v2=[P().swTh,P().swOm];H.applySnap(s0);for(let i=0;i<20;i++)H.tick(1);const v3=[P().swTh,P().swOm];
  if(v0.some((x,i)=>Math.abs(x-v1[i])>1e-9))bad.push('snapshot '+v0.map(x=>x.toFixed(3))+' -> '+v1.map(x=>x.toFixed(3)));
  if(v2.some((x,i)=>Math.abs(x-v3[i])>1e-9))bad.push('replay after a snapshot differs');}
 res.bad=bad;return res;}'''
fails = 0
with sync_playwright() as p:
    b = p.chromium.launch()
    for n in range(lo, hi + 1):
        pg = b.new_page()
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(HTML); pg.wait_for_timeout(300)
        r = pg.evaluate(JS, n)
        if 'skip' in r:
            print('skip', n, r['skip'])
        else:
            ok = not r['bad'] and not errs
            fails += 0 if ok else 1
            print('ok  ' if ok else 'BAD ', n, r, errs[:2])
        pg.close()
    b.close()
print('FAILURES', fails)
