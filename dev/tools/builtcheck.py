from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':844,'height':390}); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('http://localhost:8765/'); pg.wait_for_timeout(1500)
    print(pg.evaluate("()=>({mode:__HK.mode,gen:__HK.S.gen,sw:!!navigator.serviceWorker.controller||'pending'})"))
    L=pg.evaluate("()=>{const L=__HK.genLevel(9,5,false);return (L.detours||[]).length}")
    print('detours on floor 9 seed 5:',L,'errors',errs)
    b.close()
