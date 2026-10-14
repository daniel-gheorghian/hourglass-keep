# lifttest.py: lifts. (a) the bot plays whole floors holding each lift kind (counterweight lift lift2d.. and chain-loop lift
# chn2d.., down and up, two and three storeys) with no damage, and must really have ridden it; (b) a counterweight lift called
# by the plate on the far landing; (c) a step into a chain-loop lift's shaft with no slab passing is an ordinary fall (2
# storeys hurt, 3 kill), and holding toward the shaft with no slab passing does not board; (d) a floor rebuilt for a checkpoint
# has every counterweight lift at its first end with its grating and mouth floor in step. Run from dev/tools.
from playwright.sync_api import sync_playwright
import sys,json
PER=int(sys.argv[1]) if len(sys.argv)>1 else 3
KINDS=['lift2d','lift3d','lift2u','lift3u','chn2d','chn3d','chn2u','chn3u']
FIND='''([kind,per])=>{const H=__HK,out=[];const lo=kind.startsWith('chn')?8:3;
 for(let n=lo;n<=27&&out.length<per;n+=2)for(let s=0;s<80;s++){const seed=60000+s*137+n*19,L=H.genLevel(n,seed,true);if(L.segs.some(q=>q.k==='turn-'+kind)){out.push([n,seed]);break;}}return out;}'''
RUN='''([n,seed,kind])=>{window.__hurts=[];let rode=0;const r=runBot(n,seed,{stop:H=>{if(H.P.state==='lift')rode++;return false;}});r.h=window.__hurts;r.rode=rode;return r;}'''
bad=0
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':844,'height':390}); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(300); pg.add_script_tag(path='bot.js')
    for k in KINDS:
        fl=pg.evaluate(FIND,[k,PER]);res=[]
        for n,seed in fl:
            r=pg.evaluate(RUN,[n,seed,k]);good=r.get('ok') is True and not r.get('hurt') and r['rode']>30
            if not good: bad+=1
            res.append((n,seed,'ok' if good else (r.get('why') or r.get('h'),r.get('rode'))))
        if not fl: bad+=1
        print('%-7s %d floors %s'%(k,len(fl),res))
    # (b) call from the far end
    fl=pg.evaluate('''()=>{const H=__HK,out=[];for(const kind of ['lift2d','lift3d','lift2u','lift3u'])for(let n=3;n<=20;n++){let hit=false;for(let s=0;s<80&&!hit;s++){const seed=61000+s*139+n*23,L=H.genLevel(n,seed,true);if(L.segs.some(q=>q.k==='turn-'+kind)){out.push([kind,n,seed]);hit=true;}}if(hit)break;}return out;}''')
    for kind,n,seed in fl:
        r=pg.evaluate('''([n,seed,kind])=>{const H=__HK,L=H.load(n,seed,true);const sg=L.segs.find(q=>q.k==='turn-'+kind);
          const f=L.lifts.find(q=>q.t==='lift'&&q.sc>=Math.min(sg.c0,sg.c1)&&q.sc<=Math.max(sg.c0,sg.c1)&&q.rT>=Math.min(sg.r0,sg.r1)&&q.rB<=Math.max(sg.r0,sg.r1));
          // the platform rests at the entry end: go the other way, from the exit landing (its plate is under his feet), so the plate must call it
          const up=f.y===f.yT, rr=up?f.rB:f.rT, s=up?f.sB:f.sT, from=f.sc+s, to=f.sc+(up?f.sT:f.sB);
          const ins={a:'lift',from,to,k:f.k,up:up,dir:-s};let rode=0,called=false,y0=f.y;
          const r=runBot(n,seed,{path:[ins],at:{c:from,r:rr,face:-s},stop:H=>{const g=H.L.lifts.find(q=>q.t==='lift'&&q.sc===f.sc&&q.rT===f.rT);if(H.P.state==='lift')rode++;else if(g.y!==y0&&rode===0)called=true;return false;}});
          const g=__HK.L.lifts.find(q=>q.t==='lift'&&q.sc===f.sc&&q.rT===f.rT);
          r.called=called;r.rode=rode;r.end=Math.abs(g.y-(up?g.yT:g.yB))<0.01;return r;}''',[n,seed,kind])
        good=r.get('ok')=='path done' and r['called'] and r['rode']>30 and r['end'] and not r.get('hurt')
        if not good: bad+=1
        print(' call %-6s n=%d seed=%d: %s'%(kind,n,seed,'ok' if good else r))
    # (c) a step into the empty shaft of a cycling lift
    fl=pg.evaluate('''()=>{const H=__HK,out=[];for(const kind of ['chn2d','chn3d'])for(let n=8;n<=27;n++){let hit=false;for(let s=0;s<80&&!hit;s++){const seed=62000+s*149+n*29,L=H.genLevel(n,seed,true);if(L.segs.some(q=>q.k==='turn-'+kind)){out.push([kind,n,seed]);hit=true;}}if(hit)break;}return out;}''')
    for kind,n,seed in fl:
        r=pg.evaluate('''([n,seed,kind])=>{const H=__HK,L=H.load(n,seed,true);const sg=L.segs.find(q=>q.k==='turn-'+kind);
          const f=L.lifts.find(q=>q.t==='chain'&&q.ca>=Math.min(sg.c0,sg.c1)-1&&q.cb<=Math.max(sg.c0,sg.c1)+1&&q.rT>=Math.min(sg.r0,sg.r1)&&q.rB<=Math.max(sg.r0,sg.r1));
          const l=H.chainLanding(f,0),P=H.P,key=l.ds>0?'r':'l';
          P.x=l.bx-l.ds*8;P.y=f.entryY;P.fallY=P.y;P.face=l.ds;P.state='stand';
          // hold toward the shaft while no slab is passing: it must not board
          let t=0,clear=()=>{for(let d=0;d<=0.7;d+=0.05)if(H.chainWin(f,0,H.gameTime+d)>=0)return false;return true;};
          while(t++<3000&&!clear())H.tick(1);
          H.setKey('kb',key,true);let boarded=false;
          for(let i=0;i<40&&H.P.state!=='dead';i++){H.tick(1);if(H.P.state==='lift')boarded=true;}
          H.setKey('kb',key,false);for(let i=0;i<300;i++)H.tick(1);
          return {hp:P.hp,max:H.S.maxHp,state:P.state,dead:P.state==='dead',k:f.k,boarded};}''',[n,seed,kind])
        good=not r['boarded'] and (r['dead'] if kind=='chn3d' else (not r['dead'] and r['hp']==r['max']-1))
        if not good: bad+=1
        print(' shaft step %s n=%d: %s %s'%(kind,n,'ok' if good else 'BAD',r))
    # (d) rebuilt for a checkpoint: every lift back at its first end, grating and mouth floor in step
    r=pg.evaluate('''()=>{const H=__HK,bad=[];let cnt=0;for(let n=3;n<=14;n++){H.startLevel(n,-1);let L=H.L;const k=L.cps.length?L.cps.length-1:-1;if(k<0)continue;H.startLevel(n,k);L=H.L;
        for(const f of L.lifts){if(f.t!=='lift')continue;cnt++;const top=f.y===f.yT,okb=L.base[f.rT*L.cols+f.sc]===(top?1:0),okg=f.cyc||(f.gT===(top?1:0)&&f.gB===(top?0:1));if(!okb||!okg||f.tgt!==null)bad.push([n,f.rT,f.rB]);}}return {cnt,bad};}''')
    good=not r['bad'] and r['cnt']>0
    if not good: bad+=1
    print(' checkpoint rebuild: %d lifts checked %s'%(r['cnt'],'ok' if good else r))
    print('FAILURES',bad,'errors',errs[:3]); b.close()
