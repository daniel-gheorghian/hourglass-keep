from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont
import base64,io,sys,json,os
# film a move: run the test bot until `pred` holds, then keep `count` frames every `every` ticks, cropped around the prince
# usage: motion.py out.png n seed "pred-js" [count] [every] [file] [cropW] [cropH] [dy]
out,n,seed,pred=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),sys.argv[4]
count=int(sys.argv[5]) if len(sys.argv)>5 else 10; every=int(sys.argv[6]) if len(sys.argv)>6 else 3
f=sys.argv[7] if len(sys.argv)>7 and sys.argv[7]!='-' else '/Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'
cw=int(sys.argv[8]) if len(sys.argv)>8 else 220; chh=int(sys.argv[9]) if len(sys.argv)>9 else 260; dy=int(sys.argv[10]) if len(sys.argv)>10 else -60
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2); pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+os.path.abspath(f)); pg.wait_for_timeout(400); pg.add_script_tag(path='bot.js')
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    res=pg.evaluate('''([n,seed,pred,count,every,cw,chh,dy])=>{const fr=[];let on=false,k=0;const P=()=>__HK.P;const test=new Function('H','P','return ('+pred+')');
      const r=runBot(n,seed,{fight:false,stop:H=>{if(!on&&test(H,H.P))on=true;if(!on)return false;if(k++%every)return false;H.render();const X=H.XF,p=H.P;
        const sx=Math.round(p.x*X.VZ-X.camD),sy=Math.round((p.y+dy)*X.VZ-X.camDY),c=document.getElementById('game'),o=document.createElement('canvas');o.width=cw*2;o.height=chh*2;
        o.getContext('2d').drawImage(c,sx-cw,sy-chh,cw*2,chh*2,0,0,cw*2,chh*2);fr.push({u:o.toDataURL('image/png'),s:p.state,t:+p.t.toFixed(2)});return fr.length>=count;}});
      return {ok:r.ok,why:r.why,fr};}''',[n,seed,pred,count,every,cw,chh,dy])
    b.close()
fr=res['fr']; print(res['ok'],res.get('why'),len(fr),errs[:2])
if fr:
    ims=[Image.open(io.BytesIO(base64.b64decode(x['u'].split(',')[1]))).convert('RGB') for x in fr]
    w,h=ims[0].size; sc=0.5; tw,th=int(w*sc),int(h*sc); cols=min(len(ims),6); rows=(len(ims)+cols-1)//cols
    sheet=Image.new('RGB',(cols*tw+(cols-1)*4,rows*(th+16)),(0,0,0)); d=ImageDraw.Draw(sheet)
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',11)
    for i,(im,x) in enumerate(zip(ims,fr)):
        X=(i%cols)*(tw+4);Y=(i//cols)*(th+16); sheet.paste(im.resize((tw,th)),(X,Y+16)); d.text((X+3,Y+2),f"{i} {x['s']} {x['t']}",fill=(230,220,180),font=font)
    sheet.save(out); print(sheet.size)
