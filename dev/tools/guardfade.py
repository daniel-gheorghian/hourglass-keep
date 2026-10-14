from playwright.sync_api import sync_playwright
from PIL import Image
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2)
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(400); pg.add_script_tag(path='bot.js')
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    r=pg.evaluate('''()=>runBot(6,4242,{fight:true,stop:H=>H.G.some(g=>!g.alive&&!g.gone&&g.state==='dying')})''')
    print(r.get('ok'))
    ims=[]
    for i,n in enumerate([0,40,25,12,10,30]):
        info=pg.evaluate('''(n)=>{const H=__HK;H.tick(n);H.render();const g=H.G.find(g=>!g.alive&&g.state==='dying');return {t:g?+g.t.toFixed(2):null,gone:g?g.gone:null};}''',n)
        print(i,info); pg.screenshot(path=f'gf{i}.png'); ims.append(Image.open(f'gf{i}.png').resize((844,390)))
    w,h=ims[0].size; sheet=Image.new('RGB',(3*w,2*h),(20,16,28))
    for i,im in enumerate(ims): sheet.paste(im,((i%3)*w,(i//3)*h))
    sheet.resize((sheet.width*2//3,sheet.height*2//3)).save('guardfade.png'); print(errs); b.close()
