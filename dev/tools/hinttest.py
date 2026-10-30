# Hints until learned: python3 hinttest.py [lo [hi]]
# For each floor: with a fresh save, the bot plays the floor (the game's own input); every move its path uses is learned
# (jgrab, climb, crawl, tiptoe over spikes -> spikes, wallrun, slide -> banner, ...; round 48b: the kick shaft has no hint, nothing to learn). Then on the next floor the
# hint of a learned move never shows. A move hint that was not learned shows once a floor, again on the next floor, and
# never twice on one floor; an info hint shows once ever. lo = 1 also checks the old-save migration.
from playwright.sync_api import sync_playwright
import json, sys
lo = int(sys.argv[1]) if len(sys.argv) > 1 else 1
hi = int(sys.argv[2]) if len(sys.argv) > 2 else lo
f = '/Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'
ACT = {'jgrab': ['jgrab', 'gap'], 'climb': ['climb'], 'crawl': ['crawl'], 'tiptoe': ['spikes'],
       'wallrun': ['wallrun'], 'slide': ['banner'], 'swing': ['swing'], 'collapse': ['collapse'], 'drink': ['potion'], 'push': ['block'], 'pull': ['block'],
       'lift': ['lift'], 'chain': ['chain'], 'sandlift': ['sandfall']}  # (a chain lift is a 'lift' action with chn: it learns 'chain', not 'lift';
       # a sand lift's ride learns its own 'sandlift' from round 38b; round 41: getting off the bottomless one learns 'sandfall')
JS = r'''async ([n,seed,act])=>{const H=__HK,S=H.S,bad=[];
  const shows=(id,secs)=>{H.banner=null;H.hint(id);H.tick(160+Math.round((secs||1)*60));const b=H.banner;const r=!!(b&&b.kind==='hint'&&b.text===H.HINTS[id]);H.banner=null;H.tick(30);return r;};
  const note=m=>bad.push(m);
  // 1. a move hint that is not learned: shows once, not twice on the same floor, again on the next floor
  S.hints={};S.learned={};H.startLevel(n,-1);H.mode='play';
  if(!shows('climb'))note('climb hint did not show on a fresh save');
  if(shows('climb'))note('climb hint showed twice on one floor');
  if(S.learned.climb)note('climb learned too early');
  H.startLevel(n+1,-1);H.mode='play';
  if(!shows('jgrab'))note('jgrab hint did not show');
  H.startLevel(n+2,-1);H.mode='play';
  if(!shows('jgrab'))note('jgrab hint did not come back on the next floor');
  if(!shows('climb'))note('climb hint did not come back on a later floor');
  // 2. an info hint shows once ever
  if(!shows('cp'))note('info hint cp did not show');
  H.startLevel(n+3,-1);H.mode='play';
  if(shows('cp'))note('info hint cp showed again on a later floor');
  // 3. only one at a time: a second hint called while one is queued or showing is dropped
  H.banner=null;H.hint('gap');H.hint('drop');H.tick(30);
  if(H.banner&&H.banner.text===H.HINTS.drop)note('two hints queued at once');
  H.banner=null;H.tick(300);
  // 4. play the floor with the bot: the moves its path uses are learned, and their hints never show again
  S.hints={};S.learned={};
  const r=await runBot(n,seed,{});
  const kinds=new Set(H.L.path.map(a=>a.a==='lift'&&a.chn?'chain':a.a));
  return {bad,ok:r.ok===true,kinds:[...kinds],learned:Object.keys(S.learned)};}'''
JS2 = r'''([n])=>{const H=__HK,S=H.S,bad=[];
  const shows=id=>{H.banner=null;H.hint(id);H.tick(220);const b=H.banner;const r=!!(b&&b.kind==='hint'&&b.text===H.HINTS[id]);H.banner=null;H.tick(30);return r;};
  H.startLevel(n,-1);H.mode='play';
  for(const id of Object.keys(S.learned))if(shows(id))bad.push('learned move '+id+' showed its hint');
  for(const id of ['climb','gap','crawl','jgrab','lift','potion','wallrun'])if(!S.learned[id]&&!shows(id))bad.push('unlearned '+id+' did not show');
  return bad;}'''
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 844, 'height': 390}); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://' + f); pg.wait_for_timeout(300); pg.add_script_tag(path='bot.js')
    fails = []; checked = 0
    for n in range(lo, hi + 1):
        r = pg.evaluate(JS, [n, 700000 + n * 97, None])
        fails += ['floor %d: %s' % (n, m) for m in r['bad']]
        if not r['ok']: fails.append('floor %d: bot did not finish' % n)
        for a in r['kinds']:
            for want in ACT.get(a, []):
                checked += 1
                if want not in r['learned']: fails.append('floor %d: bot used %s but %s not learned (%s)' % (n, a, want, r['learned']))
        for m in pg.evaluate(JS2, [n]): fails.append('floor %d: %s' % (n, m))
        print('floor', n, 'actions', sorted(r['kinds']), 'learned', sorted(r['learned']))
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
    print('moves checked', checked, 'errors', errs[:3])
    for x in fails[:20]: print('FAIL', x)
    print('FAILURES', len(fails) + len(errs)); b.close()
sys.exit(1 if fails or errs else 0)
