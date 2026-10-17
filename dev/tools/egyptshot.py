# egyptshot.py [file.html] [outdir] [before.html]: the pictures for egypt_themes.html. For each of the twelve themes it looks over
# the theme's four floors (seeds 1-6) for two spots where the prince can stand among the theme's look (windows or open arches
# onto its backdrop, hangings, lamps) and its traps, and photographs each in Torchlight and in Classic, a wide view (the game's
# own screen) and a close one (round the prince). With a before file (the v61 release) it also photographs the same spots for
# the five themes that were there before (the generator is unchanged, so the spots are the same). Writes shots.json beside
# the pictures; egyptpage.py builds the page from it. Run from dev/tools.
import json, os, sys
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
SRC = a[0] if len(a) > 0 else os.path.join(HERE, '..', 'hourglass-keep.html')
OUT = a[1] if len(a) > 1 else os.path.join(HERE, 'egypt_themes')
BEFORE = a[2] if len(a) > 2 else None
os.makedirs(OUT, exist_ok=True)
TRAPS = ['spikes', 'chomp', 'saw', 'pend', 'gate', 'vent', 'darter', 'loose', 'stone', 'lift', 'chain', 'bar', 'banner', 'hurtdrop', 'grate', 'closer', 'plate', 'low']
FIND = r'''([t,traps])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS){H.S.hints[id]=1;H.S.learned[id]=1;}const cand=[];
  for(let n=4*t+1;n<=4*t+4;n++)for(let sd=1;sd<=6;sd++){const L=H.load(n,500+sd,true);H.banner=null;const C=L.cols,F=(c,r)=>c<0||c>=C||r<0||r>=L.rows?null:L.feat[r*C+c];
    for(let r=1;r<L.rows-1;r++)for(let c=8;c<C-8;c++){if(!H.solidBelow(c,r)||!H.solidBelow(c-1,r)||!H.solidBelow(c+1,r)||F(c,r)||F(c-1,r)||F(c+1,r))continue;
      if(L.base[r*C+c]===undefined)continue;const ts=new Set();let look=0,lo=0,hi=0;
      for(let rr=r-1;rr<=r;rr++)for(let cc=c-6;cc<=c+6;cc++){const f=F(cc,rr);if(f&&traps.includes(f.t)){ts.add(f.t);if(cc<c)lo++;else hi++;}
        if(H.isOpenArch(cc,rr))look+=2;}
      for(const w of L.windows)if(Math.abs(w.c-c)<=6&&(w.r===r||w.r===r-1))look+=2;
      for(const h of L.hangings||[])if(Math.abs(h.c-c)<=6&&h.r===r&&h.state<3)look+=2;
      for(const q of L.torches)if(!q.broken&&Math.abs(q.c-c)<=6&&q.r===r)look+=1;
      if(!ts.size)continue;cand.push({n,seed:500+sd,c,r,ts:[...ts],score:ts.size*3+Math.min(look,8),face:hi>=lo?1:-1,name:H.themeName(n)});}}
  cand.sort((a,b)=>b.score-a.score);const pick=[];
  for(const q of cand){if(pick.length>=2)break;if(pick.some(p=>p.n===q.n&&p.seed===q.seed&&Math.abs(p.c-q.c)<20&&p.r===q.r))continue;
    if(pick.length===1){q.score+=q.ts.filter(x=>!pick[0].ts.includes(x)).length*2;}pick.push(q);}
  if(pick.length===2){const alt=cand.filter(q=>!(q.n===pick[0].n&&q.seed===pick[0].seed&&Math.abs(q.c-pick[0].c)<20&&q.r===pick[0].r)).map(q=>({q,s:q.score+q.ts.filter(x=>!pick[0].ts.includes(x)).length*2})).sort((a,b)=>b.s-a.s)[0];if(alt)pick[1]=alt.q;}
  return pick;}'''
PLACE = r'''([n,seed,c,r,face])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS){H.S.hints[id]=1;H.S.learned[id]=1;}H.load(n,seed,true);H.banner=null;const P=H.P;P.inv=1e9;
  P.x=c*32+16;P.y=(r+1)*64-4;P.fallY=P.y;P.vx=P.vy=0;P.state='stand';P.face=face;H.cam.snap=true;H.tick(2);P.x=c*32+16;P.y=(r+1)*64-4;P.state="stand";P.face=face;H.cam.snap=true;H.tick(1);H.banner=null;
  H.GLP&&(H.GLP.pipe=false);H.render();H.render();H.render();const X=H.XF,cv=[...document.querySelectorAll('canvas')].find(q=>q.getBoundingClientRect().width>0),R=cv.getBoundingClientRect();
  return {x:R.left+(P.x*X.VZ-X.camD)/cv.width*R.width,y:R.top+((P.y-30)*X.VZ-X.camDY)/cv.height*R.height,name:H.themeName(n)};}'''


def page(b, src, mode):
    pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=2)
    pg.errs = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e)))
    pg.goto('file://' + os.path.abspath(src))
    pg.wait_for_timeout(500)
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true)")
    pg.evaluate("m=>{__HK.S.set.lightMode=m;if(__HK.GLP)__HK.GLP.pipe=false;}", mode)
    return pg


def shoot(pg, q, stem):
    r = pg.evaluate(PLACE, [q['n'], q['seed'], q['c'], q['r'], q['face']])
    pg.wait_for_timeout(60)
    tmp = os.path.join(OUT, '_tmp.png')
    pg.screenshot(path=tmp)
    im = Image.open(tmp).convert('RGB')
    im.resize((im.width * 3 // 4, im.height * 3 // 4), Image.LANCZOS).save(os.path.join(OUT, stem + '_wide.jpg'), quality=86)
    cw, ch = 640, 400
    x0 = int(min(max(0, r['x'] * 2 - cw / 2), im.width - cw)); y0 = int(min(max(0, r['y'] * 2 - ch / 2), im.height - ch))
    im.crop((x0, y0, x0 + cw, y0 + ch)).save(os.path.join(OUT, stem + '_close.jpg'), quality=90)
    os.remove(tmp)
    return r['name']


man = {'themes': []}
with sync_playwright() as p:
    b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
    probe = page(b, SRC, 'torch')
    names = probe.evaluate("__HK.THEMES.map(t=>[t.name,t.style,t.look])")
    errs = []
    for t in range(12):
        picks = probe.evaluate(FIND, [t, TRAPS])
        ent = {'i': t, 'name': names[t][0], 'style': names[t][1], 'look': names[t][2], 'poses': []}
        for k, q in enumerate(picks):
            pose = {'n': q['n'], 'seed': q['seed'], 'c': q['c'], 'r': q['r'], 'traps': q['ts'], 'face': q['face'], 'shots': {}}
            for mode in ('torch', 'classic'):
                pg = page(b, SRC, mode)
                stem = 't%02d_p%d_%s' % (t, k, mode)
                pose['label'] = shoot(pg, q, stem)
                pose['shots'][mode] = stem
                errs += pg.errs
                pg.close()
                if BEFORE and t < 5:
                    pg = page(b, BEFORE, mode)
                    stem = 'b%02d_p%d_%s' % (t, k, mode)
                    pose['before_label'] = shoot(pg, q, stem)
                    pose['shots']['before_' + mode] = stem
                    errs += pg.errs
                    pg.close()
            ent['poses'].append(pose)
            print(t, ent['name'], q['n'], q['seed'], q['c'], q['r'], q['ts'], flush=True)
        man['themes'].append(ent)
    errs += probe.errs
    b.close()
man['errors'] = errs[:20]
json.dump(man, open(os.path.join(OUT, 'shots.json'), 'w'), indent=1)
print('errors', errs[:5])
print('saved', OUT)
