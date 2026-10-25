#!/usr/bin/env python3
# sawceil.py [file.html] [lo hi] [seeds] [nobot]: a saw under a ceiling at his height becomes spikes (round 38c; the rule is in buildLevel's
# end: the low leap cannot clear a blade). For floors lo..hi (default 1-48) and seeds 1..seeds (default 3), genLevel(n, seed, true):
#  1 no saw is left with stone or a floor over its slot (the cells over columns a-1..b+1 of the blade's run, as buildLevel tests);
#  2 every saw that became spikes (found as the spikes appended to L.dyn after the row-major fill) has spikes on each tile of its run,
#    a 'tiptoe' bot action over it (L.path or a fork's short way) and no 'saw' action, and no seg still names it a saw;
#  3 unless 'nobot', the bot plays each such floor (runBot) and must pass with no damage.
# Prints the floors with a conversion, then 'sawceil: ok' or 'sawceil: FAIL n'. Run from dev/tools (it loads bot.js by a relative path).
import os, sys, json
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
SRC = os.path.abspath(next((x for x in a if x.endswith('.html')), os.path.join(HERE, '..', 'hourglass-keep.html')))
NUM = [int(x) for x in a if x.isdigit()]
LO, HI = (NUM[0], NUM[1]) if len(NUM) >= 2 else (1, 48)
NS = NUM[2] if len(NUM) > 2 else 3
BOT = 'nobot' not in a
JS = r'''([n,s])=>{delete window.__FEAT;delete window.__PZ;const L=__HK.genLevel(n,s,true),cols=L.cols,bad=[],conv=[];
  const roofOver=(r,a,b)=>{if(r<1)return true;for(let c=a-1;c<=b+1;c++)if(L.base[(r-1)*cols+c]!==0)return true;return false;};
  const acts=[...L.path];for(const f of L.forks||[])for(const x of f.sc||[])acts.push(x);
  let prev=-1,brk=-1;for(let i=0;i<L.dyn.length;i++){const o=L.dyn[i],k=o.r*cols+o.c;if(k<prev&&brk<0)brk=i;prev=k;
    if(o.f.t==='saw'){const a=Math.floor(o.f.x0/32),b=Math.floor(o.f.x1/32);if(roofOver(o.r,a,b))bad.push('saw under a roof at '+o.c+','+o.r);}}
  if(brk>=0){const sp=L.dyn.slice(brk).filter(o=>o.f.t==='spikes');
    for(let i=0;i<sp.length;){let j=i;while(j+1<sp.length&&sp[j+1].r===sp[i].r&&sp[j+1].c===sp[j].c+1)j++;
      const r=sp[i].r,a=sp[i].c,b=sp[j].c;conv.push([a,b,r]);i=j+1;
      if(!roofOver(r,a,b))bad.push('spikes appended at '+a+'-'+b+','+r+' with no roof (not a converted saw?)');
      for(let c=a;c<=b;c++){const f=L.feat[r*cols+c];if(!f||f.t!=='spikes')bad.push('no spikes at '+c+','+r);}
      const lo=a-1,hi=b+1,over=x=>Math.min(x.from,x.to)<=a&&Math.max(x.from,x.to)>=b;
      if(!acts.some(x=>x.a==='tiptoe'&&over(x)))bad.push('no tiptoe over '+a+'-'+b+','+r);
      if(acts.some(x=>x.a==='saw'&&Math.min(x.from,x.to)>=lo-1&&Math.max(x.from,x.to)<=hi+1))bad.push('a saw action left over '+a+'-'+b+','+r);
      if((L.segs||[]).some(q=>q.k==='saw'&&q.r0===r&&Math.min(q.c0,q.c1)<=a&&Math.max(q.c0,q.c1)>=b))bad.push('a saw seg left at '+a+'-'+b+','+r);}}
  return {bad,conv};}'''
fails = []; found = []
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 844, 'height': 390}); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://' + SRC); pg.wait_for_timeout(500)
    for n in range(LO, HI + 1):
        for s in range(1, NS + 1):
            r = pg.evaluate(JS, [n, s])
            for m in r['bad']: fails.append('floor %d seed %d: %s' % (n, s, m))
            if r['conv']: found.append((n, s, r['conv']))
    for n, s, cv in found: print('floor %d seed %d: saw -> spikes %s' % (n, s, ' '.join('%d-%d,%d' % tuple(x) for x in cv)))
    if BOT and found:
        pg.add_script_tag(path=os.path.join(HERE, 'bot.js'))
        for n, s, cv in found:
            r = pg.evaluate('([n,s])=>{const r=runBot(n,s,{});return {ok:r.ok,hurt:r.hurt,why:r.why||r.reason||null,frames:r.frames};}', [n, s])
            print('  bot floor %d seed %d: ok %s hurt %s frames %s' % (n, s, r['ok'], r['hurt'], r['frames']))
            if r['ok'] is not True or r['hurt']: fails.append('floor %d seed %d: bot %s' % (n, s, json.dumps(r)))
    b.close()
for f in fails[:20]: print(f)
if errs: print('errors', errs[:5]); fails.append('page errors')
print('conversions %d on %d of %d floors' % (sum(len(x[2]) for x in found), len(found), (HI - LO + 1) * NS))
print('sawceil: ok' if not fails else 'sawceil: FAIL %d' % len(fails))
sys.exit(1 if fails else 0)
