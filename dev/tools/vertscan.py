# vertscan.py: per band of floors, how often each vertical move is used in turns, the plain-step share of turn storeys, and
# how many turns have an obstacle or guard on a landing. Run from dev/tools.
from playwright.sync_api import sync_playwright
import json,sys
BANDS=[(1,2),(3,4),(5,8),(9,12),(13,18),(19,27)]
JS='''([lo,hi])=>{const H=__HK,cnt={},STEP=new Set(['turn-up','turn-down','turn-drop2']);let st=0,all=0,turns=0,withOb=0,floors=0,inRun={};
 for(let n=lo;n<=hi;n++)for(let s=0;s<20;s++){const L=H.genLevel(n,30000+s*101+n*7,true);floors++;let g=null;
  const end=()=>{if(g){turns++;if(g.ob)withOb++;g=null;}};
  for(const q of L.segs){
   if(q.k.startsWith('turn-')){if(!g)g={ob:0};if(q.k!=='turn-gslot'){cnt[q.k]=(cnt[q.k]||0)+1;const h=Math.abs(q.r1-q.r0);all+=h;if(STEP.has(q.k))st+=h;}}
   else if(q.corr&&g)g.ob++;else end();}
  end();
  for(const a of L.path){if(a.a==='collapse'||a.a==='jgrab')inRun[a.a]=(inRun[a.a]||0)+1;}}
 return {cnt,stepShare:all?st/all:0,turns,withOb,floors,inRun};}'''
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(300)
    for lo,hi in BANDS:
        r=pg.evaluate(JS,[lo,hi]);c=r['cnt']
        print('floors %2d-%2d  turns/floor %.1f  stepShare %.2f  turns with a landing obstacle %d%%'%(lo,hi,r['turns']/r['floors'],r['stepShare'],round(100*r['withOb']/max(1,r['turns']))))
        print('    '+' '.join('%s:%d'%(k[5:],c[k]) for k in sorted(c)))
    print('errors',errs[:3]); b.close()
