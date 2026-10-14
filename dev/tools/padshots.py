from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont
import sys
# same floor, same depth into it, old vs new: a wide view of the corridor
files=[('v30 (before)','v30_hooks.html'),('v31 (after)','/home/claude/hourglass-keep.html')]
scenes=[(9,4242,0.22),(14,5151,0.4),(22,777,0.55)]
rows=[]
with sync_playwright() as p:
    b=p.chromium.launch()
    for label,f in files:
        ctx=b.new_context(viewport={'width':1600,'height':390},device_scale_factor=1); pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.goto('file://'+(f if f.startswith('/') else __import__('os').path.abspath(f))); pg.wait_for_timeout(500)
        pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
        ims=[]
        for i,(n,sd,fr) in enumerate(scenes):
            pg.evaluate('''([n,sd,fr])=>{const H=__HK;const L=H.load(n,sd,true);const ws=L.path.filter(a=>a.a==='walk');const a=ws[Math.floor(ws.length*fr)];
              let r=0;for(let rr=0;rr<L.rows;rr++)if(L.base[rr*L.cols+a.c]===1&&(rr===0||L.base[(rr-1)*L.cols+a.c]!==1)){r=rr;}
              const P=H.P;P.x=a.c*32+16;P.y=(r+1)*64-4;P.fallY=P.y;P.state='stand';P.face=1;H.cam.snap=true;H.tick(2);P.x=a.c*32+16;H.cam.snap=true;H.tick(20);H.render();}''',[n,sd,fr])
            pg.screenshot(path=f'pad_{label[:3]}_{i}.png'); ims.append(Image.open(f'pad_{label[:3]}_{i}.png').convert('RGB'))
        rows.append((label,ims)); print(label,errs[:2]); ctx.close()
    b.close()
w,h=rows[0][1][0].size; pad=28
sheet=Image.new('RGB',(w,len(scenes)*2*(h+pad)),(14,12,18)); d=ImageDraw.Draw(sheet)
try: font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',18)
except: font=None
y=0
for i,(n,sd,fr) in enumerate(scenes):
    for label,ims in rows:
        d.text((10,y+4),f'Floor {n} — {label}',fill=(240,220,170),font=font); sheet.paste(ims[i],(0,y+pad)); y+=h+pad
sheet.save('pacing_compare.png'); print(sheet.size)
