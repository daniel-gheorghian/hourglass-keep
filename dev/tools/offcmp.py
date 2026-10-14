from playwright.sync_api import sync_playwright
from PIL import Image, ImageChops
import os
def shot(src,path,off):
  with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2)
    pg=ctx.new_page(); pg.goto('file://'+src); pg.wait_for_timeout(500)
    pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
    pg.evaluate('''(off)=>{const H=__HK;if(off)H.S.set.gfx={light:false,atmo:false,grade:false,hero:false,fx:false,hd:false,bg:false};const L=H.load(10,8000,true);H.P.x=120*32-30;H.P.y=6*64-4;H.P.state='stand';H.cam.snap=true;H.tick(2);for(let i=0;i<30;i++)H.roomWork&&H.roomWork();H.render();}''',off)
    pg.screenshot(path=path); b.close()
shot(os.getcwd()+'/hk_v23_release.html','oc_a.png',False); shot('/Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html','oc_b.png',True)
a=Image.open('oc_a.png').convert('RGB');b=Image.open('oc_b.png').convert('RGB');d=ImageChops.difference(a,b);print('diff bbox',d.getbbox())
