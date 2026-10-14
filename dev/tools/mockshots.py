from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont
import base64, io, json, sys, os
scenes=[dict(n=7,s=8000,tc=249,tr=6,dx=-58,opt=dict()),dict(n=18,s=8000,tc=51,tr=3,dx=-50,opt=dict(ambient='rgb(48,66,70)',warm='160,255,210',cool='170,230,255',haze='70,110,110',fog='120,170,160'))]
labels=['Now (v23)','+ Lighting','+ Depth & atmosphere','+ Lit hero & material']
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2)
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+os.getcwd()+'/mock_game.html'); pg.wait_for_timeout(500); pg.add_script_tag(path='mock.js')
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    for si,sc in enumerate(scenes):
        pg.evaluate('''(sc)=>{const H=__HK;H.load(sc.n,sc.s,true);H.P.x=sc.tc*32+16+sc.dx;H.P.y=(sc.tr+1)*64-4;H.P.fallY=H.P.y;H.P.state='stand';H.P.face=1;H.cam.snap=true;H.tick(2);
          H.setKey('kb','r',true);H.tick(14);H.setKey('kb','r',false);H.cam.snap=true;H.tick(1);}''',sc)
        ims=[]
        for st in range(4):
            d=pg.evaluate('([st,opt])=>mockFrame(st,Object.assign({t:3},opt))',[st,sc['opt']])
            im=Image.open(io.BytesIO(base64.b64decode(d.split(',')[1]))).convert('RGB'); ims.append(im)
            im.save(f'mock{si}_{st}.png')
        w,h=ims[0].size; sheet=Image.new('RGB',(2*w+12,2*h+12+2*44),(16,13,22)); dr=ImageDraw.Draw(sheet)
        try: font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',30)
        except: font=ImageFont.load_default()
        for i,im in enumerate(ims):
            x=(i%2)*(w+12); y=(i//2)*(h+12+44)
            dr.text((x+8,y+6),labels[i],fill=(240,220,170),font=font); sheet.paste(im,(x,y+44))
        sheet.resize((sheet.width//2,sheet.height//2)).save(f'mocksheet{si}.png')
    print(errs); b.close()
