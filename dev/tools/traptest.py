from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':844,'height':390}); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(300); pg.add_script_tag(path='bot.js')
    print(pg.evaluate('''()=>{const cnt={};let N=0;for(let n=5;n<=40;n++)for(let s=0;s<5;s++){N++;const L=__HK.genLevel(n,s*77+n,false);for(const a of L.path)if(['saw','darts','push','pull','wallrun','walljump','slide','swing'].includes(a.a))cnt[a.a]=(cnt[a.a]||0)+1;}for(const k in cnt)cnt[k]=(cnt[k]/N).toFixed(2);return JSON.stringify(cnt);}'''))
    cases=pg.evaluate('''()=>{const out={};for(let n=7;n<=30;n++)for(let s=0;s<30;s++){const L=__HK.genLevel(n,700+s,true);for(const a of L.path){if(['saw','darts','push','pull'].includes(a.a)&&(out[a.a]||[]).length<3&&!(out[a.a]||[]).some(q=>q[0]===n&&q[1]===700+s)){(out[a.a]=out[a.a]||[]).push([n,700+s]);}}}return out;}''')
    for k,lst in cases.items():
        for n,s in lst:
            r=pg.evaluate('([n,s])=>{const r=runBot(n,s,{});return {ok:r.ok,why:r.why,trace:r.trace,hurt:r.hurt,sec:Math.round((r.frames||0)/60),insJ:r.ins?JSON.stringify(r.ins):null};}',[n,s])
            print(k,n,s,json.dumps(r)[:420])
    print('hurts',pg.evaluate('window.__hurts||[]')[:12]); print('errors',errs); b.close()
