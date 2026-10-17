# liftkick.py: no wall kick in a lift's shaft (owner, v59: "Lifts: should not allow to do wall jumps"). For each kind of lift
# going up (counterweight lift2u/lift3u, chain-loop chn2u/chn3u): (a) the bot's own wall-jump routine, started in the shaft,
# must not climb it (he never reaches the top landing without riding); (b) put in the air against each wall of the shaft,
# at every storey, Jump must not plant or kick. And the same two checks in an ordinary kick shaft (shaft2/shaft3) must still
# climb and kick. Run from dev/tools: python3 liftkick.py [file]
from playwright.sync_api import sync_playwright
import sys,os
SRC=sys.argv[1] if len(sys.argv)>1 else os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','hourglass-keep.html')
KINDS=['lift2u','lift3u','chn2u','chn3u','shaft2','shaft3']
FIND='''(kind)=>{const H=__HK;const lo=kind.startsWith('chn')?8:3;
 for(let n=lo;n<=27;n++)for(let s=0;s<80;s++){const seed=70000+s*131+n*17,L=H.genLevel(n,seed,true);if(L.segs.some(q=>q.k==='turn-'+kind))return [n,seed];}return null;}'''
# the shaft of the segment: columns, rows and the side its top ledge lies on
SHAFT='''const H=__HK,L=H.load(n,seed,true),sg=L.segs.find(q=>q.k==='turn-'+kind),c0=Math.min(sg.c0,sg.c1),c1=Math.max(sg.c0,sg.c1),rT=Math.min(sg.r0,sg.r1),rB=Math.max(sg.r0,sg.r1);let sh;
 if(kind.startsWith('shaft')){const ins=L.path.find(a=>a.a==='walljump'&&a.from>=c0&&a.from<=c1);sh={ca:ins.from,cb:ins.from,rT,rB,dir:ins.dir||1,from:ins.from,k:ins.k};}
 else{const f=L.lifts.find(q=>q.ca>=c0-1&&q.cb<=c1+1&&q.rT>=rT&&q.rB<=rB);
   sh=f.t==='lift'?{ca:f.sc,cb:f.sc,rT:f.rT,rB:f.rB,dir:f.sT,from:f.sc,k:f.k}:{ca:f.ca,cb:f.cb,rT:f.rT,rB:f.rB,dir:f.dx,from:f.c1,k:f.k};}'''
BOT='''([n,seed,kind])=>{'''+SHAFT+'''
 let rode=0,top=false;const ins={a:'walljump',from:sh.from,k:sh.k,dir:sh.dir};
 const r=runBot(n,seed,{path:[ins],at:{c:sh.from,r:sh.rB,face:sh.dir},stop:H=>{if(H.P.state==='lift')rode++;
   if(H.P.state==='stand'&&Math.floor(H.P.y/64)<=sh.rT&&rode===0)top=true;return false;}});
 return {why:r.ok||r.why,rode,top,sh};}'''
AIR='''([n,seed,kind])=>{'''+SHAFT+'''
 let tries=0,kicks=0;
 for(let r=sh.rT;r<=sh.rB;r++)for(let c=sh.ca;c<=sh.cb;c++)for(const sd of [1,-1]){
   H.load(n,seed,true);const P=H.P;P.x=c*32+16+sd*9.5;P.y=r*64+40;P.fallY=P.y;P.state='air';P.vx=0;P.vy=-60;P.jumpKind='stand';P.autoGrab=false;P.face=sd;
   if(H.L.base[r*H.L.cols+c+sd]!==2)continue; // (only where a wall is really there)
   tries++;H.setKey('kb','j',true);H.tick(2);H.setKey('kb','j',false);
   let k=false;for(let i=0;i<30;i++){if(H.P.plant||H.P.jumpKind==='kick')k=true;H.tick(1);}
   if(k)kicks++;}
 return {tries,kicks};}'''
bad=0
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':844,'height':390}); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+os.path.abspath(SRC)); pg.wait_for_timeout(300); pg.add_script_tag(path='bot.js')
    for kind in KINDS:
        fl=pg.evaluate(FIND,kind)
        if not fl: bad+=1;print('%-7s no floor'%kind);continue
        n,seed=fl
        a=pg.evaluate(BOT,[n,seed,kind]); c=pg.evaluate(AIR,[n,seed,kind])
        if kind.startswith('shaft'): good=a['top'] and c['kicks']>0
        else: good=not a['top'] and c['kicks']==0 and c['tries']>0
        if not good: bad+=1
        print('%-7s n=%d seed=%d  bot climbs by kicks: %-5s  air kicks %d/%d  %s'%(kind,n,seed,a['top'],c['kicks'],c['tries'],'ok' if good else 'BAD %s'%a))
    print('ALL OK' if not bad and not errs else 'FAILURES %d errors %s'%(bad,errs[:3])); b.close()
