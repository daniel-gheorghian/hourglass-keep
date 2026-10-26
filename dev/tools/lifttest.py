# lifttest.py: lifts. (a) the bot plays whole floors holding each lift kind (counterweight lift lift2d.. and chain-loop lift
# chn2d.., down and up, two and three storeys) with no damage, and must really have ridden it; (b) a counterweight lift called
# by the plate on the far landing; (c) a step into a chain-loop lift's shaft with no slab passing is an ordinary fall (2
# storeys hurt, 3 kill), and holding toward the shaft with no slab passing does not board; (d) a floor rebuilt for a checkpoint
# has every counterweight lift at its first end with its grating and mouth floor in step; (e) a ride ends standing, with the
# Down (or Up) held for it still held (no crouch at the bottom); (f) a paternoster's slab is solid wherever he is in its shaft:
# falling onto a rising slab he lands on it and rides, jumping up into one stops his rise, one coming down on him at the
# shaft's foot shoves him aside, and in none of it is he ever drawn inside a slab; (h) the sand lift (round 41b: a spike pit under its foot): missed, stepped
# off, jumped off, the window's ends.
# lifttest.py [per] [file.html]. Run from dev/tools.
from playwright.sync_api import sync_playwright
import sys,json,os
PER=int(sys.argv[1]) if len(sys.argv)>1 and sys.argv[1].isdigit() else 3
SRC=next((x for x in sys.argv[1:] if x.endswith('.html')),os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','hourglass-keep.html'))
KINDS=['lift2d','lift3d','lift2u','lift3u','chn2d','chn3d','chn2u','chn3u','sand3','sand4']
FIND='''([kind,per])=>{const H=__HK,out=[];const lo=kind.startsWith('chn')?8:3;
 for(let n=lo;n<=27&&out.length<per;n+=2)for(let s=0;s<80;s++){const seed=60000+s*137+n*19,L=H.genLevel(n,seed,true);if(L.segs.some(q=>q.k==='turn-'+kind)){out.push([n,seed]);break;}}return out;}'''
RUN='''([n,seed,kind])=>{window.__hurts=[];let rode=0;const r=runBot(n,seed,{stop:H=>{if(H.P.state==='lift')rode++;return false;}});r.h=window.__hurts;r.rode=rode;return r;}'''
bad=0
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':844,'height':390}); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    INSLAB='''()=>{window.__inSlab=f=>{const H=__HK,P=H.P;if(P.state==='lift'||P.state==='dead')return false;for(let i=0;i<f.n;i++){const q=H.chainPos(f,i,H.gameTime);
      if(Math.abs(q.x-P.x)<12&&q.y<P.y-2&&q.y+8>P.y-50)return true;}return false;};}'''
    pg.goto('file://'+os.path.abspath(SRC)); pg.wait_for_timeout(300); pg.add_script_tag(path='bot.js'); pg.evaluate(INSLAB)
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
          const f=L.lifts.find(q=>q.t==='lift'&&!q.sand&&q.sc>=Math.min(sg.c0,sg.c1)&&q.sc<=Math.max(sg.c0,sg.c1)&&q.rT>=Math.min(sg.r0,sg.r1)&&q.rB<=Math.max(sg.r0,sg.r1));
          // the platform rests at the entry end: go the other way, from the exit landing (its plate is under his feet), so the plate must call it
          const up=f.y===f.yT, rr=up?f.rB:f.rT, s=up?f.sB:f.sT, from=f.sc+s, to=f.sc+(up?f.sT:f.sB);
          const ins={a:'lift',from,to,k:f.k,up:up,dir:-s};let rode=0,called=false,y0=f.y;
          const r=runBot(n,seed,{path:[ins],at:{c:from,r:rr,face:-s},stop:H=>{const g=H.L.lifts.find(q=>q.t==='lift'&&q.sc===f.sc&&q.rT===f.rT);if(H.P.state==='lift')rode++;else if(g.y!==y0&&rode===0)called=true;return false;}});
          const g=__HK.L.lifts.find(q=>q.t==='lift'&&q.sc===f.sc&&q.rT===f.rT);
          r.called=called;r.rode=rode;r.end=Math.abs(g.y-(up?g.yT:g.yB))<0.01;return r;}''',[n,seed,kind])
        good=r.get('ok')=='path done' and r['called'] and r['rode']>30 and r['end'] and not r.get('hurt')
        if not good: bad+=1
        print(' call %-6s n=%d seed=%d: %s'%(kind,n,seed,'ok' if good else r))
    # (h) round 16a, the sand lift; round 41 (41b), the trap: stepping onto its slab starts it with no key held. Then, for each of sand3 and
    # sand4: (h1) nothing pressed: the slab sinks past the foot to the spike pit's floor a storey under it and he is impaled there (dead, cause
    # spikes, 64 px under the floor), the slab at rest (f.s 2), the foot a hole and the top an open hole; (h2) the arrow toward the foot's open
    # mouth (f.mo, the way on) held from the start: he steps off as it opens, standing on the landing, unhurt; (h3) Jump pressed (and Up held)
    # once the slab is 40 px under the floor: he catches the lip and climbs out, unhurt; (h4) the window's ends: the step at its first frame (the
    # slab still over the floor), a Jump at SAND_WE - 6 px (read after the frame: the slab moves 2.3 px a frame) still saves him, at SAND_WE + 2
    # it is too late
    SANDT='''([n,seed,kind,mode,arg])=>{const H=__HK,L=H.load(n,seed,true),sg=L.segs.find(q=>q.k==='turn-'+kind);
          const f=L.lifts.find(q=>q.sand&&q.sc>=Math.min(sg.c0,sg.c1)&&q.sc<=Math.max(sg.c0,sg.c1)&&q.rT>=Math.min(sg.r0,sg.r1)&&q.rB<=Math.max(sg.r0,sg.r1));
          const P=H.P,hp=P.hp,key=(k,v)=>H.setKey('kb',k,v),side=(f.mo||f.sB)>0?'r':'l';P.inv=0;P.x=f.sc*32+16;P.y=f.yT;P.fallY=P.y;P.vx=0;P.face=f.mo||f.sB;P.state='stand';
          let rode=0,t=0,dOff=null,tOff=null,jumped=false;
          if(mode==='step')key(side,true);
          while(t++<60*14){H.tick(1);if(P.state==='lift')rode++;const d=f.y-f.yB;
            if(dOff===null&&rode>0&&P.state!=='lift'&&P.state!=='dead'){dOff=+d.toFixed(1);tOff=+(rode/60).toFixed(2);}
            if(mode==='jump'&&!jumped&&P.state==='lift'&&d>=arg){key('u',true);key('j',true);H.tick(1);key('j',false);jumped=true;}
            if(P.state==='dead'&&mode!=='none')break;
            if((mode==='step'||mode==='jump')&&dOff!==null&&P.state==='stand'&&P.y===f.yB)break;
            if(mode==='none'&&P.state==='dead')break;}
          key(side,false);key('u',false);
          const exitC=Math.floor(P.x/32);
          return {rode,st:P.state,cause:P.cause||null,y:+(P.y-f.yB).toFixed(1),hp:P.hp===hp,fs:f.s,dOff,tOff,exitC,sc:f.sc,sB:f.mo||f.sB,top:L.base[f.rT*L.cols+f.sc],foot:L.base[f.rB*L.cols+f.sc],secs:+(rode/60).toFixed(2),ms:f.ms};}'''
    for kind in ['sand3','sand4']:
        fl=pg.evaluate(FIND,[kind,1])
        if not fl: bad+=1; print(' sand %s: no floor'%kind); continue
        n,seed=fl[0]
        r=pg.evaluate(SANDT,[n,seed,kind,'none',0])
        good=r['rode']>30 and r['st']=='dead' and r['cause']=='spikes' and abs(r['y']-64)<0.5 and r['fs']==2 and r['top']==0 and r['foot']==0
        if not good: bad+=1
        print(' sand %-6s n=%d seed=%d miss: %s'%(kind,n,seed,'ok, impaled %.0f px under the floor after %s s'%(r['y'],r['secs']) if good else r))
        r=pg.evaluate(SANDT,[n,seed,kind,'step',0])
        good=r['st']=='stand' and r['hp'] and r['y']==0 and r['dOff'] is not None and r['dOff']<0 and r['exitC']==r['sc']+r['sB']
        if not good: bad+=1
        print(' sand %-6s n=%d seed=%d step: %s'%(kind,n,seed,'ok, off with the slab %.1f px over the floor at %s s'%(-r['dOff'],r['tOff']) if good else r))
        for d,want in ((40,True),(54,True),(62,False)):
            r=pg.evaluate(SANDT,[n,seed,kind,'jump',d])
            ok2=(r['st']=='stand' and r['hp'] and r['y']==0) if want else (r['st']=='dead')
            if not ok2: bad+=1
            print(' sand %-6s n=%d seed=%d jump at %d px: %s'%(kind,n,seed,d,('ok, '+('out' if want else 'too late, lost')) if ok2 else r))
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
          H.setKey('kb',key,true);let boarded=false,caught=false,inside=0,wasAir=false;
          for(let i=0;i<40&&H.P.state!=='dead';i++){H.tick(1);if(H.P.state==='air')wasAir=true;if(H.P.state==='lift'&&!wasAir)boarded=true;}
          H.setKey('kb',key,false);
          for(let i=0;i<300;i++){H.tick(1);if(P.state==='air')wasAir=true;if(P.state==='lift'&&wasAir)caught=true;inside+=window.__inSlab(f)?1:0;}
          return {hp:P.hp,max:H.S.maxHp,state:P.state,dead:P.state==='dead',k:f.k,boarded,caught,inside};}''',[n,seed,kind])
        # it does not board at the landing; it falls, and either a slab rising below catches him (a slab is solid) or he
        # reaches the foot as an ordinary fall (2 storeys hurt, 3 kill); never inside a slab
        good=not r['boarded'] and r['inside']==0 and (r['caught'] or (r['dead'] if kind=='chn3d' else (not r['dead'] and r['hp']==r['max']-1)))
        if not good: bad+=1
        print(' shaft step %s n=%d: %s %s'%(kind,n,'ok' if good else 'BAD',r))
    # (d) rebuilt for a checkpoint: every lift back at its first end, grating and mouth floor in step
    r=pg.evaluate('''()=>{const H=__HK,bad=[];let cnt=0;for(let n=3;n<=14;n++){H.startLevel(n,-1);let L=H.L;const k=L.cps.length?L.cps.length-1:-1;if(k<0)continue;H.startLevel(n,k);L=H.L;
        for(const f of L.lifts){if(f.t!=='lift')continue;cnt++;const top=f.y===f.yT,okb=L.base[f.rT*L.cols+f.sc]===(top?1:0),okg=f.cyc||(f.gT===(top?1:0)&&f.gB===(top?0:1));if(!okb||!okg||f.tgt!==null)bad.push([n,f.rT,f.rB]);}}return {cnt,bad};}''')
    good=not r['bad'] and r['cnt']>0
    if not good: bad+=1
    print(' checkpoint rebuild: %d lifts checked %s'%(r['cnt'],'ok' if good else r))
    # (e) a ride ends standing: Down (Up) held through the ride and after it, both counterweight kinds, both directions
    for kind in ['lift2d','lift3d','lift2u','lift3u']:
        fl=pg.evaluate(FIND,[kind,1])
        if not fl: bad+=1; print(' stand %s: no floor'%kind); continue
        n,seed=fl[0]
        r=pg.evaluate('''([n,seed,kind])=>{const H=__HK,L=H.load(n,seed,true);const sg=L.segs.find(q=>q.k==='turn-'+kind);
          const f=L.lifts.find(q=>q.t==='lift'&&!q.sand&&q.sc>=Math.min(sg.c0,sg.c1)&&q.sc<=Math.max(sg.c0,sg.c1)&&q.rT>=Math.min(sg.r0,sg.r1)&&q.rB<=Math.max(sg.r0,sg.r1));
          const P=H.P,down=f.y===f.yT,key=down?'d':'u';P.x=f.sc*32+16;P.y=f.y;P.fallY=P.y;P.state='stand';P.vx=0;P.inv=1e9;
          H.setKey('kb',key,true);let rode=0,t=0;while(t++<60*12&&!(P.state==='stand'&&rode>10&&Math.abs(f.y-(down?f.yB:f.yT))<0.01)){H.tick(1);if(P.state==='lift')rode++;}
          const arrived=P.state;let crouched=false;for(let i=0;i<40;i++){H.tick(1);if(P.state!=='stand')crouched=P.state;}
          H.setKey('kb',key,false);for(let i=0;i<5;i++)H.tick(1);
          let again=null;if(down){H.setKey('kb','d',true);for(let i=0;i<6;i++)H.tick(1);again=P.state;H.setKey('kb','d',false);} // (a fresh Down still crouches)
          return {rode,arrived,crouched,again,end:Math.abs(f.y-(down?f.yB:f.yT))<0.01};}''',[n,seed,kind])
        good=r['rode']>10 and r['arrived']=='stand' and not r['crouched'] and r['end'] and (r['again'] in (None,'crouch'))
        if not good: bad+=1
        print(' stand %-6s n=%d: %s'%(kind,n,'ok' if good else r))
    # (f) a paternoster's slabs are solid in its shaft
    for kind in ['chn2d','chn3u']:
        fl=pg.evaluate(FIND,[kind,1]);n,seed=fl[0]
        r=pg.evaluate('''([n,seed,kind])=>{const H=__HK,out={};
          const setup=()=>{const L=H.load(n,seed,true),sg=L.segs.find(q=>q.k==='turn-'+kind);H.P.inv=1e9;
            return L.lifts.find(q=>q.t==='chain'&&q.ca>=Math.min(sg.c0,sg.c1)-1&&q.cb<=Math.max(sg.c0,sg.c1)+1&&q.rT>=Math.min(sg.r0,sg.r1)&&q.rB<=Math.max(sg.r0,sg.r1));};
          const H_=f=>f.yB-f.yT,sOf=(f,i)=>(((H.CHAIN_V*H.gameTime+f.off+i*f.pitch)%f.per)+f.per)%f.per;
          // wait until a slab is low on the rising (entry) strand, with room above it
          const wait=(f,ok)=>{for(let t=0;t<3000;t++){for(let i=0;i<f.n;i++)if(ok(sOf(f,i),i))return i;H.tick(1);}return -1;};
          // 1. falling onto a rising slab: lands on it and rides it
          {const f=setup(),P=H.P,i=wait(f,s=>s>20&&s<H_(f)-60);const q=H.chainPos(f,i,H.gameTime);
            P.x=q.x;P.y=q.y-40;P.fallY=P.y;P.vx=0;P.vy=0;P.state='air';P.jumpKind=null;P.autoGrab=false;let inside=0,hp=P.hp;
            for(let t=0;t<90&&P.state!=='lift';t++){H.tick(1);inside+=window.__inSlab(f)?1:0;}
            out.feet={state:P.state,slab:P.slab===i,hp:P.hp===hp,inside};}
          // 2. jumping up into a slab coming down the exit strand: his rise stops under it; never inside it
          {const f=setup(),P=H.P,i=wait(f,s=>s>H_(f)+32+40&&s<H_(f)+32+80);const q=H.chainPos(f,i,H.gameTime);
            P.x=q.x;P.y=q.y+90;P.fallY=P.y;P.vx=0;P.vy=-330;P.state='air';P.jumpKind='stand';let inside=0,bumped=false,y0=P.y;
            for(let t=0;t<60&&P.state==='air';t++){const py=P.y;H.tick(1);inside+=window.__inSlab(f)?1:0;}
            out.head={inside,rose:y0-P.y};}
          // 3. standing at the foot of the exit strand as a slab comes down: shoved aside, never inside
          {const f=setup(),P=H.P,xX=f.c1*32+16,clear=()=>{for(let k=0;k<f.n;k++){const q=H.chainPos(f,k,H.gameTime);if(Math.abs(q.x-xX)<20&&q.y>f.yB-70)return false;}return true;},i=wait(f,s=>s>H_(f)+32+H_(f)-88&&s<H_(f)+32+H_(f)-80&&clear());
            P.x=xX;P.y=f.yB;P.fallY=P.y;P.vx=0;P.vy=0;P.state='stand';P.face=1;let inside=0,shoved=false;
            let first=null;for(let t=0;t<200;t++){H.tick(1);if(window.__inSlab(f)){inside++;if(!first)first=[t,P.state,P.x,P.y,[0,1,2,3].map(k=>{const q=H.chainPos(f,k,H.gameTime);return [q.x,q.y|0];})];}if(P.state==='step')shoved=true;}
            if(first)out.first=first;
            out.shove={inside,shoved,out:Math.floor(P.x/32)!==f.c1||P.state==='lift',state:P.state};}
          return out;}''',[n,seed,kind])
        good=r['feet']['state']=='lift' and r['feet']['slab'] and r['feet']['hp'] and r['feet']['inside']==0 and r['head']['inside']==0 and r['shove']['inside']==0 and r['shove']['out'] and r['shove']['shoved']
        if not good: bad+=1
        print(' slabs solid %s n=%d: %s'%(kind,n,'ok' if good else r))
    # (g) a counterweight lift's platform halfway down its shaft holds him when he drops onto it (the shaft is open above)
    for kind in ['lift2d','lift3u']:
        fl=pg.evaluate(FIND,[kind,1]);n,seed=fl[0]
        r=pg.evaluate('''([n,seed,kind])=>{const H=__HK,L=H.load(n,seed,true),sg=L.segs.find(q=>q.k==='turn-'+kind);
          const f=L.lifts.find(q=>q.t==='lift'&&!q.sand&&q.sc>=Math.min(sg.c0,sg.c1)&&q.sc<=Math.max(sg.c0,sg.c1)&&q.rT>=Math.min(sg.r0,sg.r1)&&q.rB<=Math.max(sg.r0,sg.r1));
          const P=H.P;P.inv=1e9;f.y=Math.round((f.yT+f.yB)/2);f.py=f.y;L.base[f.rT*L.cols+f.sc]=0;f.gT=0;f.gB=0;
          P.x=f.sc*32+16;P.y=f.y-50;P.fallY=P.y;P.vx=0;P.vy=0;P.state='air';P.jumpKind=null;P.autoGrab=false;const hp=P.hp;
          for(let t=0;t<120;t++)H.tick(1);return {state:P.state,on:Math.abs(P.y-f.y)<0.5,hp:P.hp===hp};}''',[n,seed,kind])
        good=r['state']=='stand' and r['on'] and r['hp']
        if not good: bad+=1
        print(' platform solid %s n=%d: %s'%(kind,n,'ok' if good else r))
    print('FAILURES',bad,'errors',errs[:3]); b.close()
