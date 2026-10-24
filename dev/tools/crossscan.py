# crossscan.py [html]: round 36a's checks of the Crossing (the interlude at each change of theme). Run from dev/tools. For every theme's
# first crossing in floors 2-180, in Torchlight and in Classic, through the game's own flow (the card's Climb on):
#  - it starts (mode 'cross', the setting CROSS_LOOK names, or the plain stub) only where the theme changes, and never on floor 6;
#  - he does not move without the pad: 3 s with no input leave him where he started (and the pad's cue shows);
#  - Jump before 0.5 s does nothing; held Right he walks, then runs, passes the gust and reaches the doorway; the crossing ends and the
#    entry plays (P.state 'enter', then control);
#  - the save (localStorage), S, levelTime and the rewind ring are the same before and after it;
#  - a skip (Jump after 0.5 s) ends it within CROSS_SKIPF and a frame;
#  - never: with S.set.cross off, with ?cross=0, on Continue, Restart or a respawn, or under the bot (runBot plays floor 4 to the card);
#  - no page errors; the crossing's render (script ms a frame, crossRender) within budget: median HK_CROSS_MS (default 8 Classic, 40
#    Torchlight: software WebGL here) and its median within HK_CROSS_K (default 2.5) times a play frame's on the floor before.
# Prints one line per crossing and 'crossscan: ok' or 'crossscan: FAILURES n'.
import os, sys, statistics
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'hourglass-keep.html'))
BUD = {'classic': float(os.environ.get('HK_CROSS_MS_C', os.environ.get('HK_CROSS_MS', 8))), 'torch': float(os.environ.get('HK_CROSS_MS_T', os.environ.get('HK_CROSS_MS', 40)))}
KREL = float(os.environ.get('HK_CROSS_K', 2.5))
fails = []
def bad(msg): fails.append(msg); print('FAIL', msg)

# the floor before n, its play frame's cost, then the card and Climb on
BEGIN = r'''([n,mode])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS)H.S.hints[id]=1;H.S.set.lightMode=mode;H.S.set.cross=true;H.S.started=true;
  H.startLevel(n-1,-1,true);H.tick(60);const pm=[];for(let i=0;i<24;i++){H.tick(1);const t=performance.now();H.render();pm.push(performance.now()-t);}
  H.levelComplete();const save0=localStorage.getItem('hourglass-keep-v1');document.getElementById('bNext').click();
  const c=H.CR;const o={mode:H.mode,play:pm.slice(8).sort((a,b)=>a-b)[8],due:H.crossDue(n),saveCard:save0===localStorage.getItem('hourglass-keep-v1')};
  if(!c)return o;if(H.GLP)H.GLP.pipe=false;
  window.__X0={save:localStorage.getItem('hourglass-keep-v1'),S:JSON.stringify(H.S),lt:H.levelTime,rew:H.REW.length,level:H.S.level};
  return Object.assign(o,{set:c.set,look:c.look,tod:c.tod,name:H.themeName(n)});}'''
# a run of steps with a render every eighth one; keys held as given; returns where it stands
STEPS = r'''([k,keys])=>{const H=__HK;for(const q of ['l','r','u','d','j','g'])H.setKey('kb',q,keys.includes(q));const ms=[];let rk=0,gust=false,steps=0;
  for(let i=0;i<k&&H.CR;i++){H.crossStep(1/60);if(!H.CR)break;rk=Math.max(rk,H.CR.rk);gust=gust||H.CR.gust>=0;if(i%8===7){H.render();ms.push(H.CR.ms[H.CR.ms.length-1]);}}
  const c=H.CR;return {on:!!c,x:c?c.x:null,t:c?c.t:null,phase:c?c.phase:null,rk,gust,ms,cue:document.getElementById('pad').classList.contains('cue'),mode:H.mode};}'''
AFTER = r'''()=>{const H=__HK,X=window.__X0,L=H.L;return {mode:H.mode,state:H.P.state,enG:L.enG,gt:H.gameTime,last:H.crossLast,
  save:X.save===localStorage.getItem('hourglass-keep-v1'),S:X.S===JSON.stringify(H.S),lt:X.lt===H.levelTime,rew:H.REW.length===0&&X.rew===0,level:H.S.level===X.level};}'''

def page(b, q=''):
    pg = b.new_page(viewport={'width': 852, 'height': 393}); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e))); pg.goto('file://' + SRC + q); pg.wait_for_timeout(300); return pg, errs

with sync_playwright() as p:
    b = p.chromium.launch()
    pg, errs = page(b)
    fl = pg.evaluate('''()=>{const H=__HK,o={};for(let n=2;n<=180;n++){if(!H.crossDue(n))continue;const lk=H.themeOf(n).look;if(!o[lk])o[lk]=n;}return o;}''')
    want = pg.evaluate('()=>{const o={};for(const k in __HK.CROSS_LOOK)o[k]=__HK.CROSS_SETS[__HK.CROSS_LOOK[k].set]?__HK.CROSS_LOOK[k].set:"plain";return o;}')
    if len(fl) != 12: bad('themes with a crossing: %d of 12' % len(fl))
    due = pg.evaluate('()=>[...Array(60).keys()].map(i=>i+2).filter(n=>__HK.crossDue(n))')
    if due != [n for n in range(5, 62, 4)]: bad('crossings due on %s' % due)
    MS = {'classic': [], 'torch': []}
    for mode in ('torch', 'classic'):
        for lk, n in sorted(fl.items(), key=lambda q: q[1]):
            r = pg.evaluate(BEGIN, [n, mode]); tag = '%s floor %d %s' % (mode, n, lk)
            if r['mode'] != 'cross' or r.get('set') != want[lk]: bad('%s: no crossing or wrong setting %s' % (tag, r)); continue
            if not r['saveCard']: bad(tag + ': Climb on changed the save beyond startLevel')
            s1 = pg.evaluate(STEPS, [20, ['j']])                       # Jump at 0.33 s: too early, nothing
            s2 = pg.evaluate(STEPS, [170, []])                         # 3 s, no input
            if not s1['on'] or not s2['on'] or abs(s2['x'] - 60) > 0.01: bad('%s: moved or ended without the pad (%s, %s)' % (tag, s1['x'], s2['x']))
            if not s2['cue']: bad(tag + ': no pad cue while he waits')
            s3 = pg.evaluate(STEPS, [2400, ['r']])                     # Right held to the doorway
            if s3['on'] or s3['rk'] < 0.99 or not s3['gust']: bad('%s: Right held did not walk, run, pass the gust and end (%s)' % (tag, {k: s3[k] for k in ('on', 'x', 'phase', 'rk', 'gust')}))
            a = pg.evaluate(AFTER)
            if not (a['mode'] == 'play' and a['state'] == 'enter' and a['enG'] == a['gt'] and a['last'] and a['last']['reached'] and not a['last']['skipped']): bad('%s: the entry does not follow %s' % (tag, a))
            for k in ('save', 'S', 'lt', 'rew', 'level'):
                if not a[k]: bad('%s: %s changed by the crossing' % (tag, k))
            ctl = pg.evaluate('()=>{const H=__HK;H.setKey("kb","r",false);for(let i=0;i<120&&H.P.state==="enter";i++)H.tick(1);return H.P.state;}')
            if ctl == 'enter': bad(tag + ': no control after the entry')
            ms = [v for v in s2['ms'][4:] + s3['ms'] if v is not None]; md = statistics.median(ms); p95 = sorted(ms)[int(len(ms) * 0.95)]; MS[mode] += ms
            if md > BUD[mode] or md > KREL * max(r['play'], 0.5): bad('%s: %.2f ms a frame (budget %.1f, play %.2f x %.1f)' % (tag, md, BUD[mode], r['play'], KREL))
            # the skip
            r2 = pg.evaluate(BEGIN, [n, mode]); pg.evaluate(STEPS, [36, []]); sk = pg.evaluate(STEPS, [1, ['j']]); sk2 = pg.evaluate(STEPS, [int(60 * 0.25) + 2, []])
            a2 = pg.evaluate(AFTER)
            if sk2['on'] or not (a2['last'] and a2['last']['skipped']) or a2['state'] != 'enter' or not a2['save']: bad('%s: the skip %s %s' % (tag, sk2, a2))
            print('%-8s floor %3d %-8s %-8s %-5s %-44s render %.2f ms (p95 %.2f; play %.2f)  crossed in %.1f s' % (mode, n, lk, r['set'], ['dusk', 'night', 'dawn'][r['tod']], r['name'], md, p95, r['play'], a['last']['t']))
    # never: off in the menu, on Continue, Restart, a respawn, an ordinary floor, under the bot
    nv = pg.evaluate(r'''()=>{const H=__HK,o={};H.S.set.lightMode='classic';
      H.S.set.cross=false;H.startLevel(4,-1,true);H.levelComplete();document.getElementById('bNext').click();o.off=H.mode;H.S.set.cross=true;
      H.startLevel(5,-1,true);H.S.level=5;H.S.cp=-1;document.getElementById('bContinue').click();o.cont=H.mode;
      document.getElementById('bRestart').click();o.restart=H.mode;H.respawn();o.respawn=H.mode;
      H.startLevel(5,-1,true);H.levelComplete();document.getElementById('bNext').click();o.ordinary=H.mode;
      document.getElementById('tCross').click();o.toggle=H.S.set.cross;document.getElementById('tCross').click();o.toggle2=H.S.set.cross;return o;}''')
    if nv != {'off': 'play', 'cont': 'play', 'restart': 'play', 'respawn': 'play', 'ordinary': 'play', 'toggle': False, 'toggle2': True}: bad('never cases %s' % nv)
    pg.add_script_tag(path=os.path.join(HERE, 'bot.js'))
    bt = pg.evaluate('()=>{const H=__HK;const r=runBot(4,1234,{});const o={ok:r.ok,mode:H.mode,cr:!!H.CR,on:H.crossOn()};return o;}')
    if not (bt['ok'] and bt['mode'] == 'card' and not bt['cr'] and not bt['on']): bad('under the bot %s' % bt)
    if errs: bad('page errors %s' % errs[:3])
    pg.close()
    pg, errs = page(b, '?cross=0')
    q0 = pg.evaluate('''()=>{const H=__HK;H.startLevel(4,-1,true);H.levelComplete();document.getElementById('bNext').click();return {due:H.crossDue(5),mode:H.mode};}''')
    if q0 != {'due': False, 'mode': 'play'}: bad('?cross=0 %s' % q0)
    if errs: bad('page errors (?cross=0) %s' % errs[:3])
    b.close()
for m in MS:
    if MS[m]: print('%s: crossing render median %.2f ms, p95 %.2f ms over %d frames' % (m, statistics.median(MS[m]), sorted(MS[m])[int(len(MS[m]) * 0.95)], len(MS[m])))
print('crossscan: ok' if not fails else 'crossscan: FAILURES %d' % len(fails))
sys.exit(1 if fails else 0)
