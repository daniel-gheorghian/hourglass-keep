from playwright.sync_api import sync_playwright
import json
H='''(legacyArg)=>{const out={};for(let n=1;n<=40;n++)for(let s=0;s<5;s++){const seed=s*7919+n;const L=__HK.genLevel(n,seed,false,legacyArg);let h=0;
  for(let i=0;i<L.base.length;i++)h=(Math.imul(h,31)+L.base[i]+(L.feat[i]?L.feat[i].t.length*7:0))|0;
  const segs={};for(const a of L.path)segs[a.a]=(segs[a.a]||0)+1;
  out[n+':'+s]={h,cols:L.cols,chase:!!L.ext.chase,guards:L.guards.length,gates:L.dyn.filter(o=>o.f.t==='gate').length,acts:L.path.length,detours:(L.detours||[]).length};}return out;}'''
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page()
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/tools/hk_v16_release.html');pg.wait_for_timeout(300);old=pg.evaluate(H,False)
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html');pg.wait_for_timeout(300);new=pg.evaluate(H,False);leg=pg.evaluate(H,True)
    b.close()
same_nochase=sum(1 for k in old if not old[k]['chase'] and old[k]['h']==new[k]['h']);nochase=sum(1 for k in old if not old[k]['chase'])
legacy_same=sum(1 for k in old if old[k]['h']==leg[k]['h'])
chasek=[k for k in new if new[k]['chase']]
print('floors without a chase identical to the live version: %d/%d'%(same_nochase,nochase))
print('legacy layouts identical to the live version: %d/%d'%(legacy_same,len(old)))
import statistics as st
def avg(d,keys,f): return st.mean(d[k][f] for k in keys)
oldchase=[k for k in old if old[k]['chase']]
print('chase floors before: %d, after: %d (a chase floor only changes size, so the set should match)'%(len(oldchase),len(chasek)))
both=[k for k in chasek if k in oldchase]
for f in ['cols','acts','guards','gates','detours']:
    print('  %-8s live %.1f -> new %.1f'%(f,avg(old,both,f),avg(new,both,f)))
nonchase=[k for k in old if not old[k]['chase'] and int(k.split(':')[0])>=6]
print('reference, floors 6-40 without a chase: acts %.1f, guards %.1f'%(avg(old,nonchase,'acts'),avg(old,nonchase,'guards')))
