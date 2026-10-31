# No hint messages, learned moves and the gate cue (rounds 49a, 50e): python3 hinttest.py [lo [hi]]
# Round 49a (owner: "drop all hint messages, rely only on subtle graphic hints") took out every hint banner and every message that
# told the player what to do or what happened out of sight; round 50e (owner: "the current animation is distracting pulling the screen like
# that") took out the camera glance: a gate is heard where it stands, the view shudders a little, grit sifts on its side and he lifts his
# head. For each floor this checks:
#  1. the bot plays it with a fresh save (the game's own input) and no banner ever shows (H.banner stays null every tick), the moves
#     its path uses are still learned (S.learned: the jet streams read it); the gate cues it set off are counted;
#  2. the gate cue: on the floor as the game starts it (startLevel), the prince is put on each remote plate (one with `where`: a timed
#     gate's, a P4 race's, a loop's violet plate): exactly one cue (GCUE.log), its sound played at the gate (Snd.playAt's x, y the gate's),
#     the grit over it in view or at the view's edge toward it out of view; the view never moves toward the gate (it stays within 6 px of
#     its rest by him every frame for GC_D + 1 s); standing still he lifts his head (TELL.k 'listen') and P.x, P.y and his state are those
#     of a run with the look off; the gate's timer runs at the game's own rate; no banner; the same plate again while its gate is open
#     gives no second cue. And none of the glance is left (GLN never counts).
# lo = 1 also checks the old-save migration of learned moves.
from playwright.sync_api import sync_playwright
import json, sys
lo = int(sys.argv[1]) if len(sys.argv) > 1 else 1
hi = int(sys.argv[2]) if len(sys.argv) > 2 else lo
f = '/Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'
ACT = {'jgrab': ['jgrab', 'gap'], 'climb': ['climb'], 'crawl': ['crawl'], 'tiptoe': ['spikes'],
       'wallrun': ['wallrun'], 'slide': ['banner'], 'swing': ['swing'], 'collapse': ['collapse'], 'drink': ['potion'], 'push': ['block'], 'pull': ['block'],
       'lift': ['lift'], 'chain': ['chain'], 'sandlift': ['sandfall']}  # (a chain lift is a 'lift' action with chn: it learns 'chain', not 'lift';
       # getting off a sand lift learns 'sandfall'; a kick shaft learns 'shaft' at the Y out of its top since round 49a)
BOT = r'''async ([n,seed])=>{const H=__HK,S=H.S;S.hints={};S.learned={};const g0=H.GCUE.n;let banners=[];
  const r={value:runBot(n,seed,{stop:H=>{const b=H.banner;if(b&&!banners.includes(b.text))banners.push(b.text);return false;}})};
  const kinds=new Set(H.L.path.map(a=>a.a==='lift'&&a.chn?'chain':a.a));
  return {ok:r.value&&r.value.ok===true,kinds:[...kinds],learned:Object.keys(S.learned),banners,cues:H.GCUE.n-g0,glances:H.GLN.n};}'''
GLANCE = r'''([n])=>{const H=__HK,S=H.S,out=[];S.hints={};S.learned={};
  H.startLevel(n,-1);H.mode='play';H.tick(2);const L=H.L,TW=32,SURF=r=>(r+1)*64-4,RH=192,snd=[],pa=H.Snd.playAt;
  H.Snd.playAt=function(nm,x,y,a){snd.push([nm,x,y]);return pa.call(this,nm,x,y,a);};
  try{const plates=L.dyn.filter(o=>o.f.t==='plate'&&o.f.where);
  for(const o of plates){const f=o.f,go=L.dyn.find(q=>q.f===f.g);if(!go)continue;
    const res={c:o.c,r:o.r,latch:!!f.latch,fwd:!!f.fwd,bad:[]};out.push(res);
    // stand him on plain floor beside the plate (either side), let the view settle, then step him onto the plate, then off again
    const P=H.P;for(const e of H.G)e.x=-9999;for(const e of H.SN)e.x=-9999;P.inv=1e9;
    const place=x=>{P.x=x;P.y=SURF(o.r);P.fallY=P.y;P.vx=P.vy=0;P.state='stand';H.cam.snap=true;H.tick(6);return P.state==='stand'&&P.y===SURF(o.r)&&Math.abs(P.x-x)<1;};
    let side=0;for(const s of [-1,1]){P.face=-s;if(place((o.c+s)*TW+16)&&!(H.L.dyn.some(q=>q.c===o.c+s&&q.r===o.r))){side=s;break;}}
    if(!side){res.skip='no plain floor beside it';continue;}
    H.tick(90);H.GCUE.log=[];snd.length=0;const gx=go.c*TW+16,gy=SURF(go.r)-30,cam=H.cam,vw=H.viewW;
    const inView=gx>cam.x+8&&gx<cam.x+vw-8&&gy>cam.y-20&&gy<cam.y+RH+10;res.inView=inView;
    P.x=o.c*TW+16;H.tick(1);P.x=(o.c+side)*TW+16;H.tick(1);const tm0=f.g.tm;
    const cues=H.GCUE.log.slice();res.cue=cues.length;
    if(cues.length!==1)res.bad.push(cues.length+' cues for one plate');
    else{const q=cues[0];if(q.k!=='gate'||Math.abs(q.x-gx)>0.5||Math.abs(q.y-gy)>0.5)res.bad.push('cue at '+q.x+','+q.y+' for the gate at '+gx+','+gy);
      if(q.m!==(inView?0:gx>cam.x&&gx<cam.x+vw?0:1))res.bad.push('grit mode '+q.m+' with the gate '+(inView?'in':'out of')+' view');}
    const so=snd.filter(e=>e[0]==='gopen');if(so.length!==1||Math.abs(so[0][1]-gx)>0.5||Math.abs(so[0][2]-gy)>0.5)res.bad.push('gate sound '+JSON.stringify(so));
    let dmax=0,ban=null,lis=0,xy=[];const T=Math.round((H.GC_D.gate+1)*60);
    for(let k=0;k<T;k++){H.tick(1);const c=H.cam,rest=Math.min(Math.max(P.x-vw/2+P.face*vw*0.17,-vw*0.15),L.cols*TW-vw*0.85);dmax=Math.max(dmax,Math.abs(c.x-rest));
      if(H.TELL.k==='listen')lis++;xy.push(P.x,P.y,P.state);if(H.banner)ban=H.banner.text;
      if(k===59&&!f.latch&&tm0>1.2){const want=tm0-1;if(Math.abs(f.g.tm-want)>0.02)res.bad.push('timer '+f.g.tm.toFixed(3)+' after 1 s, wanted '+want.toFixed(3));}}
    res.cam=Math.round(dmax);res.listen=lis;
    if(dmax>6)res.bad.push('the view moved '+Math.round(dmax)+' px off its rest');
    if(ban)res.bad.push('banner: '+ban);
    if(lis<20)res.bad.push('head lifted only '+lis+' frames');
    if(xy.some((v,i)=>i%3<2?Math.abs(v-xy[i%3])>1e-9:v!=='stand'))res.bad.push('he moved or changed state while listening');
    // the same plate again: no second cue (its gate still open)
    const n1=H.GCUE.n;if(f.g.open>0.5){P.x=o.c*TW+16;H.tick(30);P.x=(o.c+side)*TW+16;H.tick(30);if(H.GCUE.n!==n1)res.bad.push('a second cue for the same plate with its gate open');}}
  if(H.GLN.n)out.push({c:-1,r:-1,bad:['a glance counted']});}
  finally{H.Snd.playAt=pa;H.GCUE.log=null;}
  return out;}'''
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 844, 'height': 390}); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://' + f); pg.wait_for_timeout(300); pg.add_script_tag(path='bot.js')
    fails = []; checked = 0; cues = 0; plates = 0; bcues = 0
    for n in range(lo, hi + 1):
        r = pg.evaluate(BOT, [n, 700000 + n * 97])
        if not r['ok']: fails.append('floor %d: bot did not finish' % n)
        for t in r['banners']: fails.append('floor %d: a banner showed while the bot played: %r' % (n, t))
        bcues += r['cues']
        if r['glances']: fails.append('floor %d: a glance counted' % n)
        for a in r['kinds']:
            for want in ACT.get(a, []):
                checked += 1
                if want not in r['learned']: fails.append('floor %d: bot used %s but %s not learned (%s)' % (n, a, want, r['learned']))
        gl = pg.evaluate(GLANCE, [n])
        for q in gl:
            plates += 1; cues += q.get('cue', 0)
            for m in q['bad']: fails.append('floor %d plate %d,%d: %s' % (n, q['c'], q['r'], m))
        print('floor', n, 'actions', sorted(r['kinds']), 'learned', sorted(r['learned']), 'cues in play', r['cues'], 'remote plates',
              [(q['c'], q['r'], 'latch' if q.get('latch') else 'fwd' if q.get('fwd') else 'timed', 'cue %d %s view, view off rest %d px, listened %d frames' % (q.get('cue', 0), 'in' if q.get('inView') else 'out of', q.get('cam', 0), q.get('listen', 0))) for q in gl if q['c'] >= 0 and 'skip' not in q], 'skipped', sum(1 for q in gl if 'skip' in q))
    if lo == 1:
        # an old save (no learned set) on floor 6 with 4 hearts: climb, gap, drop and potion are known, jgrab and wallrun are not
        cx = b.new_context(viewport={'width': 844, 'height': 390}); p2 = cx.new_page()
        p2.add_init_script("""if(!localStorage.getItem('seeded')){localStorage.setItem('seeded','1');localStorage.setItem('hourglass-keep-v1',JSON.stringify({v:1,gen:9,chaseLen:1,lifeTaken:[],level:6,maxHp:4,deaths:0,time:0,floorTime:0,floorDeaths:0,seed:5,cp:-1,started:true,hints:{},set:{sound:true,saver:false,lefty:false,calm:false}}));}""")
        p2.goto('file://' + f); p2.wait_for_timeout(300)
        L = p2.evaluate("()=>__HK.S.learned")
        for k in ('climb', 'gap', 'drop', 'potion'):
            if not L.get(k): fails.append('migration: %s not learned for an old save past floor 2' % k)
        for k in ('jgrab', 'wallrun', 'crawl'):
            if L.get(k): fails.append('migration: %s wrongly learned' % k)
        cx.close()
    print('moves checked', checked, 'remote plates', plates, 'cues', cues, 'cues while the bot played', bcues, 'errors', errs[:3])
    for x in fails[:20]: print('FAIL', x)
    print('FAILURES', len(fails) + len(errs)); b.close()
sys.exit(1 if fails or errs else 0)
