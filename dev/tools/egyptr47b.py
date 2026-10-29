# egyptr47b.py old.html new.html [outdir] [nogif]: round 47b's pictures (owner: "the courts - the background they show isn't in sync with what
# the windows show, different scenery and it is moving way too fast"; chose C, one horizon per storey). For Napata, Aksum, Meroe and the gardens
# (Shali, Kerma) at dusk, night and dawn, on a low floor (under 61) and a high one (over 100): a court with a window of the same storey beside it
# (the window within 7 cells), Classic, the camera at rest centred between them. Writes r47b_<look>_phone.png (old | new at the phone's size, a row
# for each hour and floor) and r47b_<look>_3x.png (the band from the court's top to its floor with the window, 3x), and unless nogif
# r47b_pan_<look>.gif for Napata and Shali (the camera panning 288 px across the court and the window: old over new, half size). Run from dev/tools.
import io, os, sys, unicodedata
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
a = [x for x in sys.argv[1:]]
OLD, NEW = os.path.abspath(a[0]), os.path.abspath(a[1])
OUTD = next((x for x in a[2:] if x != 'nogif'), os.path.join(HERE, 'egypt_themes')); GIF = 'nogif' not in a
LOOKS = ['napata', 'aksum', 'meroe', 'shali', 'deffufa']
FIND = r'''([looks])=>{const H=__HK,res={};for(let n=3;n<=180;n++){const look=H.themeOf(n).look;if(!looks.includes(look))continue;const tod=Math.floor((n-1)/20)%3,band=n<=60?'low':n>100?'high':'';
  if(!band)continue;const key=look+'|'+tod+'|'+band;if(res[key])continue;
  for(let s=1;s<=6&&!res[key];s++){const L=H.genLevel(n,s,true);for(const k of L.courts){if(k.k==='well')continue;const w=L.windows.find(w=>w.r===k.r-1&&(w.c<k.c0?k.c0-w.c:w.c-k.c1)>=1&&(w.c<k.c0?k.c0-w.c:w.c-k.c1)<=7);
    if(w){res[key]={n,s,r:k.r,c0:k.c0,c1:k.c1,wc:w.c,name:H.themeName(n),tod,look,band};break;}}}}return res;}'''
SETUP = r'''([n,seed])=>{const H=__HK;for(const id in H.HINTS){H.S.hints[id]=1;H.S.learned[id]=1;}H.S.windDeaths={};const L=H.load(n,seed,true);H.banner=null;
  const P=H.P;P.inv=1e9;for(const e of H.G)e.x=-9999;for(const s of H.SN)s.x=-9999;P.x=-9999;P.state='stand';H.mode='play';
  let q=12345;Math.random=()=>{q=(q*16807)%2147483647;return q/2147483647;};for(const kk of ['l','r','u','d','j','g'])H.setKey('kb',kk,false);H.tick(5);P.x=-9999;return 1;}'''
SHOW = r'''([fx,fy])=>{const H=__HK;H.banner=null;let T=1e6;H.setClock(()=>T);H.setGT(50);H.cam.x=fx-H.viewW/2;H.cam.y=fy-115.2;H.cam.gy=fy;
  window.__HKfreeze=true;document.body.classList.add('panelOpen');const pd=document.getElementById('pad');if(pd)pd.style.display='none';
  for(let i=0;i<3;i++)H.render();const X=H.XF,cv=[...document.querySelectorAll('canvas')].find(c=>c.getBoundingClientRect().width>0),R=cv.getBoundingClientRect(),k=X.VZ/cv.width*R.width;
  return [R.left-X.camD/cv.width*R.width,R.top-X.camDY/cv.height*R.height,k];}'''
def page(b, html):
    pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=2); pg.goto('file://' + html); pg.wait_for_timeout(700)
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.body.classList.remove('panelOpen');__HK.S.set.lightMode='classic'"); return pg
def label(im, t):
    t = unicodedata.normalize('NFKD', t).encode('ascii', 'ignore').decode(); d = ImageDraw.Draw(im); d.rectangle((0, 0, 8 + 6 * len(t), 13), fill=(0, 0, 0)); d.text((4, 1), t, fill=(250, 240, 215))
os.makedirs(OUTD, exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = page(b, NEW); cases = pg.evaluate(FIND, [LOOKS]); pg.close()
    for look in LOOKS:
        ks = sorted(k for k in cases if k.startswith(look + '|'))
        if not ks: continue
        phones, crops = [], []
        for key in ks:
            c = cases[key]; fy = (c['r'] + 1) * 64 - 4; xc = (c['c0'] + c['c1'] + 1) * 16; xw = c['wc'] * 32 + 16; fx = (xc + xw) / 2; hr = ['dusk', 'night', 'dawn'][c['tod']]
            row_p, row_c = [], []
            for tag, html in (('v88', OLD), ('47b', NEW)):
                pg = page(b, html); pg.evaluate(SETUP, [c['n'], c['s']]); q = pg.evaluate(SHOW, [fx, fy]); im = Image.open(io.BytesIO(pg.screenshot())).convert('RGB'); pg.close()
                ph = im.resize((852, 393), Image.LANCZOS); label(ph, '%s | %s | %s, floor %d seed %d' % (tag, c['name'], hr, c['n'], c['s'])); row_p.append(ph)
                ox, oy, k = q[0] * 2, q[1] * 2, q[2] * 2; x0 = min(c['c0'] * 32, c['wc'] * 32) - 20; x1 = max((c['c1'] + 1) * 32, c['wc'] * 32 + 32) + 20; y0 = (c['r'] - 1) * 64 - 12; y1 = fy + 8
                cr = im.crop((int(ox + x0 * k), int(oy + y0 * k), int(ox + x1 * k), int(oy + y1 * k))).resize((int((x1 - x0) * 3), int((y1 - y0) * 3)), Image.LANCZOS)
                label(cr, '%s | %s | %s floor %d' % (tag, c['name'], hr, c['n'])); row_c.append(cr)
            phones.append(row_p); crops.append(row_c)
        for rows, fn in ((phones, 'r47b_%s_phone.png' % look), (crops, 'r47b_%s_3x.png' % look)):
            w = max(r[0].width for r in rows); h = sum(r[0].height + 6 for r in rows); S = Image.new('RGB', (2 * w + 6, h), (20, 16, 24)); y = 0
            for r in rows: S.paste(r[0], (0, y)); S.paste(r[1], (w + 6, y)); y += r[0].height + 6
            S.save(os.path.join(OUTD, fn), optimize=True); print('wrote', fn, S.size)
        if GIF and look in ('napata', 'shali'):
            key = ks[0]; c = cases[key]; fy = (c['r'] + 1) * 64 - 4; fx = ((c['c0'] + c['c1'] + 1) * 16 + c['wc'] * 32 + 16) / 2; fr = {}
            for tag, html in (('v88', OLD), ('47b', NEW)):
                pg = page(b, html); pg.evaluate(SETUP, [c['n'], c['s']]); fr[tag] = []
                for i in range(0, 37):
                    pg.evaluate(SHOW, [fx + (i - 18) * 8, fy]); im = Image.open(io.BytesIO(pg.screenshot())).convert('RGB').resize((426, 197), Image.LANCZOS); label(im, '%s | camera %+d px' % (tag, (i - 18) * 8)); fr[tag].append(im)
                pg.close()
            out = []
            for i in list(range(37)) + list(range(36, -1, -1)):
                S = Image.new('RGB', (426, 400), (20, 16, 24)); S.paste(fr['v88'][i], (0, 0)); S.paste(fr['47b'][i], (0, 203)); out.append(S.convert('P', palette=Image.ADAPTIVE))
            fn = os.path.join(OUTD, 'r47b_pan_%s.gif' % look); out[0].save(fn, save_all=True, append_images=out[1:], duration=60, loop=0); print('wrote', fn)
    b.close()
