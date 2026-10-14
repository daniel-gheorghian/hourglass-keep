from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':844,'height':390}); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(300); pg.add_script_tag(path='bot.js')
    print(pg.evaluate('''()=>{let N=0,ch=0,sec=0,life=0;for(let n=3;n<=40;n++)for(let s=0;s<5;s++){N++;const L=__HK.genLevel(n,s*77+n,false);if(L.ext.chase)ch++;if(L.detours&&L.detours.some(d=>d.secret))sec++;if(L.items.some(i=>i.type==='life'))life++;}return 'per floor: chase '+(ch/N).toFixed(2)+', secret passage '+(sec/N).toFixed(2)+', floors with a gold flask '+(life/N).toFixed(2);}'''))
    cases=pg.evaluate('''()=>{const out=[];for(let n=6;n<=40&&out.length<12;n+=3)for(let s=0;s<20;s++){const L=__HK.genLevel(n,900+s,true);if(L.ext.chase&&(n%3!==0||L.detours.some(d=>d.secret))){out.push([n,900+s]);break;}}return out;}''')
    for n,s in cases:
        r=pg.evaluate('([n,s])=>{window.__dash=[];const r=runBot(n,s,{});const d=(window.__dash||[])[0];return {ok:r.ok,why:r.why,ins:r.ins?JSON.stringify(r.ins).slice(0,120):null,trace:r.trace,hurt:r.hurt,dash:d,maxHp:__HK.S.maxHp};}',[n,s])
        d=r.get('dash') or {}
        info=d.get('info') or {}
        wallT=None
        if info: wallT=round((info['len']*32+128)/info['v']+0.7,1)
        print(n,s,r['ok'],r.get('why'),r.get('ins'),'| chase len',info.get('len'),'bot',d.get('took'),'s, sand arrives',wallT,'s, est',round(info.get('estT',0),1),'| hurt',r.get('hurt'))
    print('errors',errs); b.close()
