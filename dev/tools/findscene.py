from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); pg.goto('file://'+__import__('os').getcwd()+'/mock_game.html'); pg.wait_for_timeout(400)
    r=pg.evaluate('''()=>{const H=__HK,out=[];for(const n of [6,7,10,18]){for(let s=0;s<40;s++){const L=H.load(n,8000+s,true);
        for(const t of L.torches){const ws=L.windows.filter(w=>Math.abs(w.c-t.c)<7&&Math.abs(w.r-t.r)<=1);const flat=[...Array(9)].every((_,k)=>{const c=t.c-4+k;return L.base[t.r*L.cols+c]!==2&&(L.base[t.r*L.cols+c]===1||L.base[(t.r+1)*L.cols+c]===2)&&!L.feat[t.r*L.cols+c];});
          if(ws.length>=1&&flat){out.push({n,s:8000+s,tc:t.c,tr:t.r,w:ws.length});break;}}
        if(out.filter(o=>o.n===n).length)break;}}return out;}''')
    print(json.dumps(r)); b.close()
