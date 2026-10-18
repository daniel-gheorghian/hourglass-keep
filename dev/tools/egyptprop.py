# egyptprop.py [file.html] [outdir]: the pictures for the proposals on egypt_themes.html (second round): each theme's lamp
# (EGP.lamps: on a wall and standing or hanging in an opening, lit and unlit, Torchlight and Classic, beside the lamp it has now),
# the re-skinned traps (EGP.traps, EGP.plug) with the prince among them, and the title, floor card and HUD as Dawnward in the
# candidate fonts (the page's Google Fonts request is answered with the candidate's faces under the game's font names).
# Writes prop.json beside the pictures; egyptpage.py builds the page. Run from dev/tools; it needs the network for the fonts.
import io, json, os, re, sys, urllib.request
from playwright.sync_api import sync_playwright
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
SRC = a[0] if len(a) > 0 else os.path.join(HERE, '..', 'hourglass-keep.html')
OUT = a[1] if len(a) > 1 else os.path.join(HERE, 'egypt_themes')
os.makedirs(OUT, exist_ok=True)
JS = r'''window.__P={
  scr(x,y){const H=__HK,X=H.XF,cv=[...document.querySelectorAll('canvas')].find(q=>q.getBoundingClientRect().width>0),R=cv.getBoundingClientRect();
    return [R.left+(x*X.VZ-X.camD)/cv.width*R.width,R.top+(y*X.VZ-X.camDY)/cv.height*R.height];},
  load(n,seed){const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS){H.S.hints[id]=1;H.S.learned[id]=1;}H.load(n,seed,true);H.banner=null;return H.L;},
  stand(c,r,face){const H=__HK,P=H.P;P.inv=1e9;P.x=c*32+16;P.y=(r+1)*64-4;P.fallY=P.y;P.vx=P.vy=0;P.state='stand';P.face=face;H.cam.snap=true;H.tick(2);
    P.x=c*32+16;P.y=(r+1)*64-4;P.state='stand';P.face=face;H.cam.snap=true;H.tick(1);H.banner=null;},
  draw(){const H=__HK;H.GLP&&(H.GLP.pipe=false);H.render();H.render();H.render();}};'''
# a floor spot by the thing, the prince standing beside it on the same floor
FINDF = r'''([floors,kinds,want,gap])=>{const H=__HK,out=[];
  for(const [n,seed] of floors){const L=__P.load(n,seed),C=L.cols,F=(c,r)=>c<0||c>=C||r<0||r>=L.rows?null:L.feat[r*C+c];
    for(let r=1;r<L.rows-1&&out.length<want;r++)for(let c=10;c<C-10;c++){const f=F(c,r);if(!f||!kinds.includes(f.t))continue;
      for(const d of [-gap,gap,-gap-1,gap+1]){const pc=c+d;if(!H.solidBelow(pc,r)||F(pc,r)||F(pc-1,r)&&F(pc-1,r).t!=='plate'||F(pc+1,r)&&kinds.includes(F(pc+1,r).t)&&d<0&&false)continue;
        if(!H.solidBelow(pc,r))continue;out.push({n,seed,c,r,pc,face:d<0?1:-1,t:f.t,name:H.themeName(n)});break;}
      if(out.length&&out[out.length-1].n===n&&out[out.length-1].c===c)break;}
    if(out.length>=want)break;}
  return out;}'''
LAMPF = r'''([t])=>{const H=__HK;let wall=null,free=null;
  const F0=__HK.floorsOf(__HK.THEMES[t].look)[0];for(let n=F0;n<=F0+3&&!(wall&&free);n++)for(let sd=1;sd<=10&&!(wall&&free);sd++){const L=__P.load(n,700+sd);
    if(!wall)for(const q of L.torches){if(q.broken||H.lampFree(q))continue;if(H.solidBelow(q.c+2,q.r)&&!L.feat[q.r*L.cols+q.c+2]){wall={n,seed:700+sd,c:q.c,r:q.r};break;}}
    if(!free)for(let r=1;r<L.rows;r++)for(let c=10;c<L.cols-10;c++){if(!H.solidBelow(c,r)||L.feat[r*L.cols+c]||!H.solidBelow(c+2,r))continue;const q={c,r};if(!H.lampFree(q))continue;
      if(L.torches.some(o=>o.r===r&&Math.abs(o.c-c)<3)||L.cps.some(o=>o.r===r&&Math.abs(o.x/32-c)<4)||L.door.r===r&&Math.abs(L.door.c-c)<4)continue;free={n,seed:700+sd,c,r};break;}}
  return {wall,free};}'''
SHOWLAMP = r'''([q,isFree,lamps,unlit])=>{const H=__HK;H.EGP.lamps=lamps;H.EGP.unlit=unlit;const L=__P.load(q.n,q.seed);
  if(isFree){L.torches.push({c:q.c,r:q.r});H.clearRooms();}__P.stand(q.c+2,q.r,-1);__P.draw();
  return __P.scr(q.c*32+16,(q.r+1)*64-4-34);}'''
SHOW = r'''([q,flags,prep])=>{const H=__HK;Object.assign(H.EGP,flags);__P.load(q.n,q.seed);const L=H.L;
  if(prep==='spikes')for(const o of L.dyn)if(o.f.t==='spikes')o.f.ext=1;
  __P.stand(q.pc,q.r,q.face);
  if(prep==='spikes')for(const o of L.dyn)if(o.f.t==='spikes')o.f.ext=1;
  if(prep==='shake')for(const o of L.dyn)if(o.f.t==='loose'&&o.c===q.c&&o.r===q.r){o.f.s=1;o.f.tm=0.3;}
  if(prep==='chase'){const ch=L.ext.chase;ch.on=true;ch.wx=H.P.x-48;}
  const SURF=r=>(r+1)*64-4,C=L.cols,fo=L.dyn.find(o=>o.c===q.c&&o.r===q.r);
  if(prep==='fall'||prep==='rest'){let rr=q.r-1;while(rr>=0&&L.base[rr*C+q.c]!==2)rr--;const cy=(rr+1)*64;fo.f.s=prep==='fall'?2:3;
    if(prep==='fall')L.debris.push({x:q.c*32+16,y:cy+14+0.5*(SURF(q.r)-cy-14),vy:220,c:q.c,hitP:true,kind:'rock',y0:cy+14});else{L.rubble.add(q.r*C+q.c);H.clearRooms();}}
  if(prep==='give'){fo.f.s=2;L.base[q.r*C+q.c]=0;H.clearRooms();L.debris.push({x:q.c*32+16,y:SURF(q.r)+22,vy:230,c:q.c,hitP:true,kind:'slab',y0:SURF(q.r)});}
  if(prep==='high'||prep==='fall'||prep==='rest'){H.cam.y-=40;H.cam.gy-=40;}
  __P.draw();return __P.scr(q.c*32+16,(q.r+1)*64-(prep==='high'||prep==='fall'?62:prep==='rest'?40:prep==='give'?10:30));}'''
CHASEF = r'''([floors])=>{const H=__HK,out=[];for(const [n,seed] of floors){const L=__P.load(n,seed),ch=L.ext.chase;if(!ch)continue;
  for(let c=ch.c0+6;c<ch.c1-4;c++)for(let r=ch.rTop;r<=ch.rBot;r++)if(H.solidBelow(c,r)&&!L.feat[r*L.cols+c]&&H.solidBelow(c-3,r)){out.push({n,seed,c:c-3,r,pc:c,face:1,t:'chase',name:H.themeName(n)});return out;}}return out;}'''
SNAKEF = r'''([floors])=>{const H=__HK,out=[];for(const [n,seed] of floors){const L=__P.load(n,seed);for(const s of L.snakeSpecs){const c=Math.floor(s.x/32),pc=c-3;
  if(H.solidBelow(pc,s.r)&&!L.feat[s.r*L.cols+pc]){out.push({n,seed,c,r:s.r,pc,face:1,t:'snake',name:H.themeName(n)});break;}}if(out.length)break;}return out;}'''



# the water clock: the checkpoint reached (filled and draining) and not yet reached, a gate's running clock (the roundel and the HUD), the rewind
CLOCK = r"""([kind])=>{const H=__HK;
  if(kind==='lit'||kind==='dry'){for(const n of [9,17,29,5]){const L=__P.load(n,821);const cp=L.cps.find(c=>H.solidBelow(Math.floor(c.x/32)+2,c.r));if(!cp)continue;
      __P.stand(Math.floor(cp.x/32)+2,cp.r,-1);if(kind==='lit'){cp.on=true;cp.onAt=H.gameTime-3.4;}H.S.sands=kind==='lit'?3:1;H.mode='play';__P.draw();return {xy:__P.scr(cp.x,(cp.r+1)*64-30),n};}}
  if(kind==='gate'){for(const n of [6,7,10,11,14,18,22,26]){for(const sd of [821,822,823]){const L=__P.load(n,sd);const o=L.dyn.find(o=>o.f.t==='gate'&&o.f.dur>0&&!o.f.latch&&H.solidBelow(o.c-2,o.r));if(!o)continue;
      __P.stand(o.c-2,o.r,1);o.f.tm=o.f.dur*0.55;o.f.open=1;o.f.heldAt=-9;H.mode='play';__P.draw();return {xy:__P.scr(o.c*32+16,(o.r+1)*64-40),n};}}}
  if(kind==='rewind'){const L=__P.load(13,824);H.S.sands=3;const P=H.P;H.mode='play';P.inv=0;for(let k=0;k<240;k++){H.P.inv=1e9;H.tick(1);}
    try{H.P.inv=0;H.hurt(9,'fall');H.tick(50);H.startRewind();H.tick(18);}catch(e){return {err:String(e)};}H.render();H.render();return {xy:__P.scr(H.P.x,H.P.y-30),n:13,mode:H.mode};}
  return null;}"""


def newpage(b, mode, route=None):
    pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=2)
    pg.errs = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e)))
    if route:
        pg.route('**/fonts.googleapis.com/css2**', route)
    pg.goto('file://' + os.path.abspath(SRC))
    pg.wait_for_timeout(700)
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true)")
    pg.evaluate("m=>{__HK.S.set.lightMode=m;if(__HK.GLP)__HK.GLP.pipe=false;}", mode)
    pg.evaluate(JS)
    return pg


def grab(pg, xy, stem, cw=640, ch=400, wide=True):
    im = Image.open(io.BytesIO(pg.screenshot())).convert('RGB')
    if wide:
        im.resize((im.width * 3 // 4, im.height * 3 // 4), Image.LANCZOS).save(os.path.join(OUT, stem + '_wide.jpg'), quality=86)
    x0 = int(min(max(0, xy[0] * 2 - cw / 2), im.width - cw)); y0 = int(min(max(0, xy[1] * 2 - ch / 2), im.height - ch))
    im.crop((x0, y0, x0 + cw, y0 + ch)).save(os.path.join(OUT, stem + '_close.jpg'), quality=90)


man = {'lamps': [], 'traps': [], 'fonts': []}
errs = []
with sync_playwright() as p:
    b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
    pt, pc = newpage(b, 'torch'), newpage(b, 'classic')
    looks = pt.evaluate("__HK.THEMES.map(t=>[t.name,t.look])")
    # ---- lamps
    for t, (name, look) in enumerate(looks):
        q = pt.evaluate(LAMPF, [t])
        ent = {'look': look, 'name': name, 'shots': []}
        for kind in ('wall', 'free'):
            s = q[kind]
            if not s:
                continue
            for lab, pg, lamps, unlit in (('now', pt, False, False), ('torch', pt, True, False), ('classic', pc, True, False), ('unlit', pc, True, True)):
                stem = 'lamp_%s_%s_%s' % (look, kind, lab)
                xy = pg.evaluate(SHOWLAMP, [s, kind == 'free', lamps, unlit])
                grab(pg, xy, stem, 360, 260, wide=False)
                ent['shots'].append({'kind': kind, 'lab': lab, 'stem': stem, 'n': s['n'], 'seed': s['seed']})
        man['lamps'].append(ent)
        print('lamp', look, q, flush=True)
    for pg in (pt, pc):
        pg.evaluate("()=>{__HK.EGP.lamps=true;__HK.EGP.unlit=false;}")
    # ---- traps: (id, feature kinds, flags, prep, floors to look on)
    F = lambda ns: [[n, s] for n in ns for s in (801, 802, 803)]
    TR = [('portcullis', ['gate'], {'traps': True}, None, [F([6, 7, 26, 27]), F([18, 19, 41, 42])]),
          ('roofblock', ['stone'], {'traps': True}, ['fall', 'rest'], [F([2, 3, 4, 41, 42, 43]), F([21, 22, 23, 24])]),
          ('sandfloor', ['loose'], {'traps': True}, ['shake', 'give'], [F([10, 11, 30, 31]), F([45, 46, 47])]),
          ('stakes', ['spikes'], {'traps': True}, 'spikes', [F([14, 15, 34, 35]), F([5, 6, 7, 8])]),
          ('wellshaft', ['hurtdrop'], {}, None, [F([29, 30, 31, 32]), F([9, 10, 11, 12])]),
          ('snakes', None, {}, None, [F([21, 22, 23, 24]), F([37, 38, 39, 40])]),
          ('plug', None, {'plug': True}, 'chase', [F([41, 42, 43, 44, 45, 46, 47, 48]), F([6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16])])]
    for pg in (pt, pc):
        pg.evaluate("()=>{__HK.GLFX.storm2=false;__HK.GLFX.storm=false;}")  # (the plug is drawn in 2D in both modes)
    for tid, kinds, flags, prep, floorsets in TR:
        ent = {'id': tid, 'poses': []}
        for k, fs in enumerate(floorsets):
            if tid == 'plug':
                qs = pt.evaluate(CHASEF, [fs])
            elif tid == 'snakes':
                qs = pt.evaluate(SNAKEF, [fs])
            else:
                qs = pt.evaluate(FINDF, [fs, kinds, 1, 2])
            if not qs:
                print('no spot', tid, k); continue
            q = qs[0]
            pose = {'n': q['n'], 'seed': q['seed'], 'name': q['name'], 'shots': {}, 'state': {'fall': 'mid-fall', 'rest': 'fallen, resting', 'shake': 'giving way', 'give': 'just given way'}.get(prep[k] if isinstance(prep, list) else prep, '')}
            for lab, pg in (('torch', pt), ('classic', pc)):
                stem = 'trap_%s_%d_%s' % (tid, k, lab)
                xy = pg.evaluate(SHOW, [q, dict({'traps': True, 'plug': True}, **flags), prep[k] if isinstance(prep, list) else prep])
                grab(pg, xy, stem)
                pose['shots'][lab] = stem
            ent['poses'].append(pose)
            print('trap', tid, q, flush=True)
        man['traps'].append(ent)
    man['clock'] = []
    for kind, label in (('lit', 'checkpoint reached: filled, draining into its basin'), ('dry', 'checkpoint not yet reached; the HUD with one measure left'), ('gate', 'a timed gate: its clock in the roundel and the HUD'), ('rewind', 'the rewind: the water turns back')):
        ent = {'kind': kind, 'label': label, 'shots': {}}
        for lab, pg in (('torch', pt), ('classic', pc)):
            r = pg.evaluate(CLOCK, [kind])
            if not r or 'err' in r:
                print('clock', kind, lab, r); continue
            stem = 'clock_%s_%s' % (kind, lab)
            grab(pg, r['xy'], stem)
            ent['shots'][lab] = stem
            print('clock', kind, lab, r.get('n'), r.get('mode', ''), flush=True)
        if len(ent['shots']) == 2:
            man['clock'].append(ent)
    errs += pt.errs + pc.errs
    pt.close(); pc.close()
    # ---- Dawnward in the candidate fonts: the title, the floor card and the HUD with the floor's banner
    UA = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36'}
    CANDS = [('rokkitt', None, None, None, None),  # (the game as built: Rokkitt + Jost)
             ('marcellus', 'Marcellus', 'Marcellus', 'Jost', 'Jost:wght@400;600;800'),
             ('poiret', 'Poiret One', 'Poiret+One', 'Jost', 'Jost:wght@400;600;800'),
             ('now', 'Lalezar', 'Lalezar', 'Vazirmatn', 'Vazirmatn:wght@400;600;800')]  # (before: the v62 pair)
    for key, disp, dq, body, bq in CANDS:
        css = None
        if disp:
            req = urllib.request.Request('https://fonts.googleapis.com/css2?family=%s&family=%s&display=swap' % (dq, bq), headers=UA)
            css = urllib.request.urlopen(req, timeout=20).read().decode()
            css = css.replace("font-family: '%s'" % disp, "font-family: 'Rokkitt'").replace("font-family: '%s'" % body, "font-family: 'Jost'")
        route = (lambda c: (lambda r: r.fulfill(status=200, content_type='text/css', body=c)))(css) if css else None
        pg = newpage(b, 'torch', route)
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(600)
        # title
        pg.evaluate("()=>{document.getElementById('title').hidden=false;}")
        pg.wait_for_timeout(300)
        pg.screenshot(path=os.path.join(OUT, 'font_%s_title.png' % key))
        # the floor card
        pg.evaluate("""()=>{document.getElementById('title').hidden=true;const H=__HK;__P.load(8,901);__P.stand(20,H.L.start.r,1);__P.draw();
          const c=document.getElementById('card');c.hidden=false;document.getElementById('cEyebrow').textContent='Floor 8 cleared';document.getElementById('cTitle').textContent=H.themeName(8);
          document.getElementById('cNext').textContent='Next: Floor 9, '+H.themeName(9)+'.';}""")
        pg.wait_for_timeout(300)
        pg.screenshot(path=os.path.join(OUT, 'font_%s_card.png' % key))
        # the HUD and the floor's title banner
        pg.evaluate("""()=>{document.getElementById('card').hidden=true;document.body.classList.remove('panelOpen');const H=__HK;__P.load(29,902);__P.stand(Math.floor(H.L.start.x/32)+3,H.L.start.r,1);H.mode='play';H.intro=1.3;H.GLP&&(H.GLP.pipe=false);H.render();H.render();}""")
        pg.wait_for_timeout(200)
        im = Image.open(io.BytesIO(pg.screenshot())).convert('RGB')
        im.save(os.path.join(OUT, 'font_%s_hud.jpg' % key), quality=88)
        im.crop((0, 0, im.width, 120)).save(os.path.join(OUT, 'font_%s_hudtop.png' % key))
        man['fonts'].append({'key': key, 'display': disp, 'body': body})
        errs += pg.errs
        pg.close()
        print('font', key, flush=True)
    b.close()
for f in os.listdir(OUT):
    if f.startswith('font_') and f.endswith('.png'):
        Image.open(os.path.join(OUT, f)).convert('RGB').save(os.path.join(OUT, f[:-4] + '.jpg'), quality=88)
        os.remove(os.path.join(OUT, f))
man['errors'] = errs[:20]
json.dump(man, open(os.path.join(OUT, 'prop.json'), 'w'), indent=1)
print('errors', errs[:5])
