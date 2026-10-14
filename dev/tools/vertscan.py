# vertscan.py: per band of floors, how often each vertical move is used in turns, the plain-step share of turn storeys, and
# how many turns have an obstacle or guard on a landing, and how many floors hold a lift (ridden or cycling). Run from dev/tools.
from playwright.sync_api import sync_playwright
import json,sys
SRC=(sys.argv[1] if len(sys.argv)>1 else '') or '/Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'  # optionally another source to compare, and a seed count
SEEDS=int(sys.argv[2]) if len(sys.argv)>2 else 20
BANDS=[(1,2),(3,4),(5,8),(9,12),(13,18),(19,27)]
JS='''([lo,hi,SEEDS])=>{const H=__HK,cnt={},STEP=new Set(['turn-up','turn-down','turn-drop2']);let st=0,all=0,turns=0,withOb=0,floors=0,inRun={},fl={lift:0,cyc:0,any:0},nl=0;
 for(let n=lo;n<=hi;n++)for(let s=0;s<SEEDS;s++){const L=H.genLevel(n,30000+s*101+n*7,true);floors++;let g=null;{const a=L.segs.filter(q=>/^turn-lift/.test(q.k)).length,b=L.segs.filter(q=>/^turn-chn/.test(q.k)).length;if(a)fl.lift++;if(b)fl.cyc++;if(a||b)fl.any++;nl+=a+b;}
  const end=()=>{if(g){turns++;if(g.ob)withOb++;g=null;}};
  for(const q of L.segs){
   if(q.k.startsWith('turn-')){if(!g)g={ob:0};if(q.k!=='turn-gslot'){cnt[q.k]=(cnt[q.k]||0)+1;const h=Math.abs(q.r1-q.r0);all+=h;if(STEP.has(q.k))st+=h;}}
   else if(q.corr&&g)g.ob++;else end();}
  end();
  for(const a of L.path){if(a.a==='collapse'||a.a==='jgrab')inRun[a.a]=(inRun[a.a]||0)+1;}}
 return {cnt,stepShare:all?st/all:0,turns,withOb,floors,inRun,fl,nl};}'''
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+SRC); pg.wait_for_timeout(300)
    for lo,hi in BANDS:
        r=pg.evaluate(JS,[lo,hi,SEEDS]);c=r['cnt']
        print('floors %2d-%2d  turns/floor %.1f  stepShare %.2f  turns with a landing obstacle %d%%'%(lo,hi,r['turns']/r['floors'],r['stepShare'],round(100*r['withOb']/max(1,r['turns']))))
        print('    floors with a lift %d%% (counterweight %d%%, chain-loop %d%%), lifts per floor %.2f'%(round(100*r['fl']['any']/r['floors']),round(100*r['fl']['lift']/r['floors']),round(100*r['fl']['cyc']/r['floors']),r['nl']/r['floors']))
        print('    '+' '.join('%s:%d'%(k[5:],c[k]) for k in sorted(c)))
    print('errors',errs[:3]); b.close()
