# The Grab button names its action: python3 grablabel.py [lo [hi [seeds]]]  (ends with 'FAILURES n')
# 1. (lo = 1 only) scenes: the prince is put into each situation (flask, low blade, guard, snake, ledge in a fall, bar, banner,
#    block, spikes, dead with and without sands) and grabLabel() and the button text after the debounce are checked; the real
#    loop is run once to see the debounce in real time; the longest words are measured to fit the smallest button at phone sizes
#    (both handednesses), and screenshots of every label go to $VREVIEW_OUT/grablabel (or GL_OUT).
# 2. soak, floors lo..hi: the bot plays with fights; whenever Grab was held or tapped and an action happened (drink, strike,
#    thrust, draw, hang, swing, slide, push, pull, step), the label predicted in the 12 ticks (0.2 s) before must have named it.
#    A few 'Hang' misses in the air are tolerated (the finder looks 0.45 s ahead; a catch made far from a ledge by a flick of Grab
#    is not predicted); any other miss fails.
from playwright.sync_api import sync_playwright
import base64, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
HTML = 'file://' + os.path.abspath(os.path.join(HERE, '..', 'hourglass-keep.html'))
lo = int(sys.argv[1]) if len(sys.argv) > 1 else 1
hi = int(sys.argv[2]) if len(sys.argv) > 2 else lo
seeds = int(sys.argv[3]) if len(sys.argv) > 3 else 1
OUT = os.environ.get('GL_OUT') or os.path.join(os.environ.get('VREVIEW_OUT') or os.path.join(HERE, 'grablabel_out'), 'grablabel')
fails = []
def fail(m): fails.append(m); print('FAIL', m)

SCENES = r'''()=>{const H=__HK,bad=[],seen={};window.__HKfreeze=true;
  const TW=32,TH=64,SURF=r=>(r+1)*64-4,btn=document.getElementById('bGrab');let T=1000;
  const upd=()=>{T+=500;H.updateGrabLabel(T);T+=500;H.updateGrabLabel(T);}; // past both debounces
  const keys=ks=>{for(const k of ['l','r','u','d','j','g'])H.setKey('kb',k,ks.includes(k));};
  const stand=(c,r,face)=>{const P=H.P;P.state='stand';P.x=c*TW+16;P.y=SURF(r);P.fallY=P.y;P.face=face||1;P.vx=P.vy=0;P.t=0;P.foe=null;P.stumble=0;P.lowSword=false;P.jumpKind=null;P.autoGrab=false;P.peace=9;};
  const chk=(name,want,extra)=>{const got=H.grabLabel();upd();const txt=btn.textContent,dim=btn.classList.contains('dim');
    seen[name]=[got,txt,dim];
    if(got!==want)bad.push(name+': grabLabel '+got+' expected '+want);
    if(txt!==want)bad.push(name+': button reads '+txt+' expected '+want);
    if(dim!==(want==='Grab'))bad.push(name+': dim class '+dim+' for '+want);};
  const find=(pred,floors)=>{for(const n of floors)for(let s=0;s<8;s++){const L=H.load(n,500+s*37,true);const r=pred(L);if(r)return {n,s:500+s*37,r};}return null;};
  // plain floor: nothing to do -> Grab (dimmed)
  H.load(3,1234,true);keys([]);const L0=H.L;
  let sp=null;{const r0=L0.start.r,c0=Math.floor(L0.start.x/TW);stand(c0,r0,L0.start.face||1);sp={c:c0,r:r0};}
  chk('plain',"Grab");
  // flask under him, standing and crouched; poison too
  for(const type of ['heal','life','poison','big']){const P=H.P;stand(sp.c,sp.r);const it={c:sp.c,r:sp.r,x:P.x,type,taken:false};L0.items.push(it);chk('drink '+type,'Drink');
    P.state='crouch';chk('drink crouched '+type,'Drink');it.taken=true;chk('drink taken '+type,'Draw');}
  // pad held with a flask under him: the drink needs a pad at rest
  {stand(sp.c,sp.r);const it={c:sp.c,r:sp.r,x:H.P.x,type:'heal',taken:false};L0.items.push(it);keys(['r']);chk('flask, pad held','Grab');keys([]);it.taken=true;}
  // crouch: draw, thrust, tunnel
  {stand(sp.c,sp.r);const P=H.P;P.state='crouch';chk('crouch, no blade','Draw');P.lowSword=true;chk('crouch, low blade','Thrust');P.lowSword=false;P.state='stand';}
  // snake ahead: strike, standing and crouched; it beats a flask
  {stand(sp.c,sp.r);const P=H.P,sn={alive:true,r:sp.r,x:P.x+20,lo:0,hi:9999};H.SN.push(sn);chk('snake','Strike');P.state='crouch';chk('snake crouched','Strike');
    const it={c:sp.c,r:sp.r,x:P.x,type:'heal',taken:false};L0.items.push(it);chk('snake beats flask','Strike');it.taken=true;sn.alive=false;P.state='stand';chk('snake dead','Grab');}
  // in garde with a living guard: Strike; reeling: Grab
  {stand(sp.c,sp.r);const P=H.P;P.state='garde';P.foe={alive:true,x:P.x+40,y:P.y};chk('garde','Strike');P.stumble=0.4;chk('garde, stumbling','Grab');P.stumble=0;P.foe.alive=false;chk('garde, foe dead','Grab');P.foe=null;P.state='stand';}
  // dead: Rewind after 0.7 s with sands; Rise after 0.9 s without
  {stand(sp.c,sp.r);keys([]);H.tick(30);H.S.sands=3;H.hurt(99,'fall');
    if(H.mode!=='dead')bad.push('did not die');
    chk('dead, early','Grab');H.tick(50);chk('dead, sands','Rewind');
    H.S.sands=0;chk('dead, no sands, 0.8 s','Grab');H.tick(15);chk('dead, no sands','Rise');}
  return {bad,seen};}'''

# scenes needing a particular tile: found by scanning floors
FIND = r'''()=>{const H=__HK,bad=[],seen={};window.__HKfreeze=true;
  const TW=32,TH=64,HANG=57,SURF=r=>(r+1)*64-4,btn=document.getElementById('bGrab');let T=1000;
  const upd=()=>{T+=500;H.updateGrabLabel(T);T+=500;H.updateGrabLabel(T);};
  const keys=ks=>{for(const k of ['l','r','u','d','j','g'])H.setKey('kb',k,ks.includes(k));};
  const chk=(name,want)=>{const got=H.grabLabel();upd();const txt=btn.textContent;seen[name]=[got,txt];
    if(got!==want)bad.push(name+': grabLabel '+got+' expected '+want);if(txt!==want)bad.push(name+': button reads '+txt+' expected '+want);};
  const solid=(L,c,r)=>H.solidBelow(c,r);
  const air=(x,y,vy)=>{const P=H.P;P.state='air';P.x=x;P.y=y;P.fallY=y-20;P.vx=0;P.vy=vy;P.t=0;P.jumpKind=null;P.autoGrab=false;P.bar=null;P.lastBar=null;P.foe=null;};
  const got={};
  for(let n=1;n<=27;n++){for(let s=0;s<6;s++){const L=H.load(n,900+s*53,true);keys([]);
    const B=(c,r)=>L.base[r*L.cols+c];
    // a ledge: an open cell next to a solid-floored wall-less cell, the way findLedge reads it
    if(!got.ledge){for(let r=1;r<L.rows&&!got.ledge;r++)for(let c=1;c<L.cols-1&&!got.ledge;c++){
      for(const sg of [-1,1]){const hc=c+sg;if(B(c,r)===2||!solid(L,c,r))continue;
        if(!H.findLedge)continue;
        const xe=sg>0?(c+1)*TW:c*TW,hx=xe+sg*7,ys=SURF(r);
        air(hx,ys+HANG-30,60);const f=H.findLedge(H.P.y,true,H.P.y+60);
        if(f&&f.r===r&&f.c===c){got.ledge={n,s:900+s*53,c,r,sg,hx,ys};break;}}}
      if(got.ledge){const g=got.ledge;air(g.hx,g.ys+HANG-30,60);chk('ledge in a fall','Hang');
        // and pressing Grab there really catches it
        keys(['g']);H.tick(40);const st=H.P.state;keys([]);if(st!=='hang')bad.push('ledge: Grab did not hang, state '+st);
        // a fall far from any ledge column: Grab
        air(g.hx+TW*4,g.ys-200,60);const l2=H.grabLabel();seen['far from the ledge']=[l2];}}
    if(!got.bar){for(const o of L.dyn||[]){if(o.f.t==='bar'){got.bar=1;const f=o.f;air(f.x,f.y+HANG,0);chk('bar','Swing');
      keys(['g']);H.tick(2);const st=H.P.state;keys([]);if(st!=='swing')bad.push('bar: Grab did not swing, state '+st);break;}}}
    if(!got.banner){for(let r=0;r<L.rows&&!got.banner;r++)for(let c=0;c<L.cols&&!got.banner;c++){const f=L.feat[r*L.cols+c];
      if(f&&f.t==='banner'){air(c*TW+16,SURF(r)-10,80);const lab=H.grabLabel();if(lab==='Slide'){got.banner=1;chk('banner','Slide');
        keys(['g']);H.tick(3);const st=H.P.state;keys([]);if(st!=='slide')bad.push('banner: Grab did not slide, state '+st);}}}}
    if(!got.block&&L.ext&&L.ext.blocks&&L.ext.blocks.length){for(const bl of L.ext.blocks){
      for(const side of [-1,1]){const c=bl.c-side;if(!solid(L,c,bl.r)||L.base[bl.r*L.cols+c]===2)continue;
        const P=H.P;P.state='stand';P.x=side>0?bl.c*TW-10:(bl.c+1)*TW+10;P.y=SURF(bl.r);P.fallY=P.y;P.face=side;P.vx=P.vy=0;P.foe=null;P.stumble=0;P.peace=9;
        const canPush=H.blockCanMove(bl,side,'push'),canPull=H.blockCanMove(bl,-side,'pull');
        keys([]);if(canPush){chk('block, push','Push');got.block=1;}
        keys([side>0?'l':'r']);const pl=H.grabLabel();seen['block, pad away']=[pl,'canPull '+canPull];if(pl!==(canPull?'Pull':'Grab'))bad.push('block pull: '+pl+' canPull '+canPull);if(canPull)got.pull=1;keys([]);
        if(got.block)break;}if(got.block)break;}}
    if(!got.spikes){for(let r=0;r<L.rows&&!got.spikes;r++)for(let c=1;c<L.cols&&!got.spikes;c++){const f=L.feat[r*L.cols+c];
      if(f&&f.t==='spikes'&&solid(L,c-1,r)&&L.base[r*L.cols+c-1]!==2){const P=H.P;P.state='stand';P.x=c*TW-12;P.y=SURF(r);P.fallY=P.y;P.face=1;P.vx=P.vy=0;P.foe=null;P.stumble=0;P.peace=9;
        const lab=H.grabLabel();if(lab==='Step'){got.spikes=1;chk('spikes ahead','Step');P.face=-1;const back=H.grabLabel();seen['spikes behind']=[back];}}}}
    if(got.ledge&&got.bar&&got.banner&&got.block&&got.spikes)break;}
    if(got.ledge&&got.bar&&got.banner&&got.block&&got.spikes)break;}
  return {bad,seen,got};}'''

SOAK = r'''async ([n,seed,fight])=>{const H=__HK;const ring=[];const mis=[],cnt={},miss={};let acts=0;
  const orig=H.tick;const I=H.I;
  const NEED={drink:'Drink',lowStrike:'Strike',strike:'Strike',poke:'Thrust',hang:'Hang',swing:'Swing',slide:'Slide',push:'Push',pull:'Pull',step:'Step'};
  H.tick=function(k){for(let i=0;i<(k||1);i++){const P=H.P,pre=P.state,low=P.lowSword,gdown=!!I.g||(I.buf.g!==undefined&&H.gameTime-I.buf.g<=0.15);
    const pos0={x:P.x,y:P.y,face:P.face,hz:H.hazardEdge(64),st:P.state};const lab=H.grabLabel();ring.push(lab);if(ring.length>12)ring.shift();
    orig(1);const P2=H.P;if(P2!==P||!gdown)continue;
    let exp=null;
    if(pre!==P2.state&&NEED[P2.state]&&!(P2.state==='hang'&&pre!=='air')&&!(P2.state==='hang'&&!I.g)){
      if(P2.state==='swing'&&pre!=='air')continue;if(P2.state==='slide'&&pre!=='air')continue;
      if((P2.state==='push'||P2.state==='pull'||P2.state==='step')&&pre!=='stand')continue;
      if(P2.state==='strike'&&pre!=='garde')continue;
      exp=NEED[P2.state];}
    else if(pre==='crouch'&&P2.state==='crouch'&&!low&&P2.lowSword)exp='Draw';
    if(!exp)continue;
    if(exp==='Step'){ // announced only near spikes or an edge (two tiles ahead, or spikes underfoot); a step on open floor is by design not
      const L=H.L,c=Math.floor(pos0.x/32),r=Math.floor((pos0.y-1)/64);let hz=false;
      for(let k=0;k<=2;k++){const cc=c+k*pos0.face,f=L.feat[r*L.cols+cc];if(k&&L.base[r*L.cols+cc]===2)break;if(f&&f.t==='gate')break;if(f&&f.t==='spikes')hz=true;if(k&&!H.solidBelow(cc,r))hz=true;}
      if(!hz){cnt['Step on open floor']=(cnt['Step on open floor']||0)+1;continue;}}
    acts++;cnt[exp]=(cnt[exp]||0)+1;
    if(!ring.includes(exp)){miss[exp]=(miss[exp]||0)+1;if(mis.length<12){const L=H.L,c=Math.floor(P2.x/32),r=Math.floor((P2.y-1)/64),ft=[];for(let k=-1;k<=3;k++){const f=L.feat[r*L.cols+c+k*P2.face];ft.push(f?f.t:'.');}mis.push({exp,pre,post:P2.state,pos0:JSON.stringify(pos0),ring:ring.slice(-12).join(','),feats:ft.join(' '),face:P2.face});}}}};
  let r;try{r=await runBot(n,seed,{fight});}finally{H.tick=orig;}
  return {ok:r.ok===true,acts,cnt,miss,mis};}'''

REAL = r'''async ()=>{const H=__HK,btn=document.getElementById('bGrab'),out={};window.__HKfreeze=false;
  const TW=32,SURF=r=>(r+1)*64-4;const L=H.load(3,1234,true);const P=H.P,r=L.start.r,c=Math.floor(L.start.x/TW);P.x=c*TW+16;P.y=SURF(r);P.state='stand';P.peace=99;
  const sleep=ms=>new Promise(r=>setTimeout(r,ms));
  await sleep(700); // (the first frames of a new floor are slow)
  const it={c,r,x:P.x,type:'poison',taken:false};L.items.push(it);
  const t0=performance.now();let at=null,wrote=0;const mo=new MutationObserver(()=>{wrote++;});mo.observe(btn,{childList:true,characterData:true,subtree:true});
  for(let i=0;i<60;i++){await sleep(16);if(btn.textContent==='Drink'){at=performance.now()-t0;break;}}
  out.showsDrinkAfterMs=at;await sleep(200);out.writes=wrote;
  it.taken=true;const t1=performance.now();let back=null;
  for(let i=0;i<80;i++){await sleep(16);if(btn.textContent==='Grab'){back=performance.now()-t1;break;}}
  out.backToGrabMs=back;out.dim=btn.classList.contains('dim');window.__HKfreeze=true;return out;}'''

FIT = r'''([labels,lefty])=>{const H=__HK,btn=document.getElementById('bGrab');window.__HKfreeze=true;H.S.set.lefty=lefty;H.layout();
  const res=[];const cs=getComputedStyle(btn);
  for(const t of labels){H.glSet(t);const rg=document.createRange();rg.selectNodeContents(btn);const tr=rg.getBoundingClientRect(),br=btn.getBoundingClientRect();
    const lh=parseFloat(getComputedStyle(btn).fontSize);
    res.push({t,btn:Math.round(br.width),font:+getComputedStyle(btn).fontSize.replace('px',''),textW:+tr.width.toFixed(1),textH:+tr.height.toFixed(1),inner:+(br.width-4).toFixed(1),
      lk:getComputedStyle(btn).getPropertyValue('--lk')||'1',lines:Math.round(tr.height/(lh*1.0)),over:btn.scrollWidth>btn.clientWidth+0.5});}
  return res;}'''

LABELS = ['Grab', 'Rewind', 'Rise', 'Strike', 'Thrust', 'Drink', 'Draw', 'Swing', 'Hang', 'Slide', 'Push', 'Pull', 'Step']

with sync_playwright() as p:
    b = p.chromium.launch(); errs = []
    def page(w=844, h=390, scale=2):
        ctx = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=scale, has_touch=True, is_mobile=True)
        pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.add_init_script('try{localStorage.clear()}catch(e){}')
        pg.goto(HTML); pg.wait_for_timeout(400); return pg
    if lo == 1:
        pg = page()
        pg.add_script_tag(path=os.path.join(HERE, 'bot.js'))
        r = pg.evaluate(SCENES); [fail(x) for x in r['bad']]
        print('scenes', len(r['seen']), 'checked');
        r2 = pg.evaluate(FIND); [fail(x) for x in r2['bad']]
        print('found', r2['got'], '| checked', len(r2['seen']))
        for k in ('ledge', 'bar', 'banner', 'block', 'spikes'):
            if k not in r2['got']: fail('no %s scene found to test' % k)
        far = r2['seen'].get('far from the ledge')
        if far and far[0] == 'Hang': fail('far from the ledge still reads Hang')
        # the debounce in real time
        pg2 = page()
        rr = pg2.evaluate(REAL); print('real time', rr)
        if rr['showsDrinkAfterMs'] is None or not (100 <= rr['showsDrinkAfterMs'] <= 3000): fail('Drink did not show after ~0.15 s: %s' % rr)
        if rr['backToGrabMs'] is None or not (250 <= rr['backToGrabMs'] <= 3000): fail('Grab did not return after ~0.3 s: %s' % rr)
        if rr['writes'] > 2: fail('the button text was rewritten %s times for one change' % rr['writes'])
        # fit at phone sizes
        smallest = None
        for (w, h) in [(844, 390), (667, 375), (568, 320), (932, 430), (896, 414)]:
            for lefty in (False, True):
                pf = page(w, h, 1)
                res = pf.evaluate(FIT, [LABELS, lefty])
                for x in res:
                    # the word must sit on one line and fit inside the round button (80% of its width is the chord at the text line)
                    if x['textW'] > x['inner'] * 0.82 or x['over'] or x['textH'] > x['font'] * 2.2:
                        fail('fit %dx%d lefty=%s %s' % (w, h, lefty, x))
                if not lefty: print('fit %dx%d: button %dpx font %spx  ' % (w, h, res[0]['btn'], res[0]['font']) + ' '.join('%s %.0f/%d(lk %s)' % (x['t'], x['textW'], x['inner'], x['lk']) for x in res if x['t'] in ('Rewind', 'Strike', 'Thrust', 'Drink', 'Swing')))
                pf.context.close()
        # screenshots: every label, both handednesses, phone size
        os.makedirs(OUT, exist_ok=True)
        imgs = []
        for lefty in (False, True):
            ps = page(844, 390, 3)
            ps.evaluate('(l)=>{__HK.load(3,1234,true);document.querySelectorAll(".screen").forEach(e=>e.hidden=true);document.body.classList.remove(\"panelOpen\");__HK.S.set.lefty=l;__HK.layout();window.__HKfreeze=true;__HK.render();}', lefty)
            for t in LABELS:
                ps.evaluate('(t)=>{__HK.glSet(t)}', t)
                box = ps.evaluate('()=>{const r=document.getElementById("bGrab").getBoundingClientRect(),j=document.getElementById("bJump").getBoundingClientRect(),d=document.getElementById("pad").getBoundingClientRect();return [r,j,d].map(x=>({l:x.left,t:x.top,r:x.right,b:x.bottom}))}')
                g, j, d = box
                x0 = max(0, min(g['l'], j['l'], d['l']) - 8); x1 = min(844, max(g['r'], j['r'], d['r']) + 8)
                y0 = max(0, min(g['t'], j['t'], d['t']) - 8); y1 = min(390, max(g['b'], j['b'], d['b']) + 8)
                fn = os.path.join(OUT, 'grab-%s-%s.png' % (t.lower(), 'lefty' if lefty else 'righty'))
                data = ps.screenshot(clip={'x': x0, 'y': y0, 'width': x1 - x0, 'height': y1 - y0})
                open(fn, 'wb').write(data); imgs.append((t, lefty, base64.b64encode(data).decode()))
            ps.context.close()
        sheet = page(1300, 900, 1)
        html = '<body style="background:#222;color:#eee;font:12px sans-serif;margin:8px">' + ''.join(
            '<div style="display:inline-block;margin:4px;text-align:center">%s %s<br><img src="data:image/png;base64,%s" style="height:170px"></div>' % (t, 'left-handed' if l else 'right-handed', d) for t, l, d in imgs)
        sheet.set_content(html); sheet.wait_for_timeout(300)
        sheet.screenshot(path=os.path.join(OUT, 'sheet.png'), full_page=True)
        print('screenshots in', OUT)
    # soak
    pg = page(844, 390, 1)
    pg.add_script_tag(path=os.path.join(HERE, 'bot.js'))
    tot = {'acts': 0, 'cnt': {}, 'miss': {}}; mis = []
    for n in range(lo, hi + 1):
        for s in range(seeds):
            sd = 700000 + n * 97 + s * 13
            r = pg.evaluate(SOAK, [n, sd, True])
            tot['acts'] += r['acts']
            for k, v in r['cnt'].items(): tot['cnt'][k] = tot['cnt'].get(k, 0) + v
            for k, v in r['miss'].items(): tot['miss'][k] = tot['miss'].get(k, 0) + v
            for m in r['mis']: mis.append((n, sd, m))
            if not r['ok']: fail('floor %d seed %d: bot did not finish' % (n, sd))
    print('soak floors %d-%d: actions %d %s  misses %s' % (lo, hi, tot['acts'], tot['cnt'], tot['miss']))
    for n, sd, m in mis[:10]: print('  miss floor %d seed %d %s' % (n, sd, m))
    for k, v in tot['miss'].items():
        if k != 'Hang': fail('soak: %d %s actions were not announced' % (v, k))
        elif v > max(3, 0.1 * tot['cnt'].get('Hang', 0)): fail('soak: %d of %d Hang catches were not announced' % (v, tot['cnt'].get('Hang', 0)))
    if errs: fail('page errors %s' % errs[:3])
    b.close()
print('FAILURES', len(fails))
sys.exit(1 if fails else 0)
