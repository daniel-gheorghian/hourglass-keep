from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont
import os,sys
out=sys.argv[1] if len(sys.argv)>1 else 'ingame.png'
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2)
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+os.getcwd()+'/proto.html'); pg.wait_for_timeout(500); pg.add_script_tag(path='bot.js')
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    shots=[]
    def both(tag):
        for old in (1,0):
            pg.evaluate(f"window.__oldFig={old};__HK.render()"); pg.screenshot(path=f'ig_{tag}_{old}.png'); shots.append(f'ig_{tag}_{old}.png')
    pg.evaluate('''()=>{let k=0;return runBot(6,4106,{fight:true,stop:H=>{if(H.P.state==='garde'&&H.G.some(g=>g.alive&&Math.abs(g.x-H.P.x)<60)){k++;return k>30;}return false;}});}'''); both('fight')
    pg.evaluate('''()=>{let k=0;return runBot(10,4110,{fight:false,stop:H=>{if(H.P.state==='run'){k++;return k>40;}return false;}});}'''); both('run')
    pg.evaluate('''()=>{let k=0;return runBot(14,4114,{fight:false,stop:H=>{if(H.P.state==='hang'||H.P.state==='climb'){k++;return k>8;}return false;}});}'''); both('climb')
    ims=[Image.open(f) for f in shots]; w,h=ims[0].size
    sheet=Image.new('RGB',(2*w+10,3*h+20),(0,0,0))
    for i,im in enumerate(ims): sheet.paste(im,((i%2)*(w+10),(i//2)*(h+10)))
    sheet.resize((sheet.width//2,sheet.height//2)).save(out); print(errs); b.close()
