# wgl_maskcmp.py base.html new.html outdir [quick]: as wgl_cmp.py, but compares the mask atlas (effect mask, beam occluders, metal) the
# shaders read, instead of the picture. (Below: wgl_cmp.py's notes.) The same exact game states rendered in Torchlight by two builds, compared pixel
# by pixel. Each state: a floor played by the bot (fighting) up to a tick or a condition (a fight, a lift, the storm, a beam,
# a dissolve, a rewind), then the same clock and the same random numbers for every render, GLP.pipe=false (frames sent at
# once), rendered 14 times so both builds have every room's relief copy in place, and the WebGL canvas read back.
# Reports per state: max and mean abs difference (0-255, over RGB), the share of pixels off by more than 8 and by more than
# 24, and the same counted away from edges (pixels whose 3x3 neighbourhood in the base image varies by less than 24: a
# difference there is not antialiasing). Writes diff images and a contact sheet of the worst crops to outdir.
import sys, os, base64, json
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
A, B, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
QUICK = 'quick' in sys.argv[4:]
ONLY = [x[5:] for x in sys.argv[4:] if x.startswith('only=')]
PRE = ([x[4:] for x in sys.argv[4:] if x.startswith('pre=')] or [''])[0]
os.makedirs(OUT, exist_ok=True)
# (name, floor, seed, condition js (H)=>bool or tick count, extra js after reaching it)
S = []
for n in ([1, 5, 10, 14, 17, 22] if QUICK else [1, 3, 5, 7, 9, 11, 13, 14, 15, 17, 19, 21, 22, 23, 25, 27]):
    for k in ([700] if QUICK else [400, 1500]):
        S.append(('f%02d_t%d' % (n, k), n, 9000 + n, k, ''))
COND = {
  'fight': "H=>H.P&&H.P.foe&&H.P.foe.alive&&Math.abs(H.P.foe.x-H.P.x)<70",
  'lift': "H=>H.L.lifts.length&&H.L.lifts.some(f=>Math.abs((f.c0!==undefined?f.c0:f.c)*32-H.P.x)<200&&Math.abs((f.y||f.yT||0)-H.P.y)<200)",
  'storm': "H=>H.L.ext.chase&&H.L.ext.chase.on&&Math.abs(H.L.ext.chase.wx-H.P.x)<260",
  'dissolve': "H=>H.G.some(g=>!g.alive&&!g.gone&&g.t>H.DISS.t0+0.4&&Math.abs(g.x-H.P.x)<250)",
  'gate': "H=>H.L.dyn.some(o=>(o.f.t==='gate'||o.f.t==='saw'||o.f.t==='chomp'||o.f.t==='pend')&&Math.abs(o.c*32-H.P.x)<150&&Math.abs(o.r*64-H.P.y)<130)",
  'beam': "H=>H.ryOps().some(o=>Math.abs(o.x-H.P.x)<220&&Math.abs(o.y-H.P.y)<160)",
}
for n in ([5, 14, 22] if QUICK else [5, 8, 12, 14, 18, 22, 26]):
    for c in COND: S.append(('f%02d_%s' % (n, c), n, 9100 + n, c, ''))
S.append(('f09_rewind', 9, 9209, 'fight', 'rewind'))
S.append(('f16_rewind', 16, 9216, 900, 'rewind'))
S.append(('f20_dark', 20, 9220, 1200, 'lowlife'))
for (n, sd) in ((25, 9100), (26, 9100), (14, 9100), (22, 9100)): S.append(('f%02d_stormon' % n, n, sd, 2, 'stormset'))
for (n, fr) in ((5, 0.3), (8, 0.55), (12, 0.8)): S.append(('f%02d_middiss%02d' % (n, fr * 100), n, 9100 + n, 'dissolve', 'mid%s' % fr))

RUN = r'''([n,seed,cond,extra])=>{const H=__HK;H.S.set.lightMode='torch';H.GLP.pipe=false;window.__HKnoauto=true;
  let T=1e6;H.setClock(()=>T); // (a clock that only moves with the game: every effect that reads it is the same in both builds)
  let k=0;const f=typeof cond==='number'?null:eval(%s[cond]);
  const r=runBot(n,seed,{fight:true,stop:h=>{++k;T+=1000/60;if(f?(k>200&&f(h)):k>=cond)return true;if(k>9000)return true;return false;}});
  let a=12345;const rnd=()=>{a=(a+0x6D2B79F5)>>>0;let t=Math.imul(a^(a>>>15),1|a);t=(t+Math.imul(t^(t>>>7),61|t))^t;return((t^(t>>>14))>>>0)/4294967296;};
  const tk=m=>{Math.random=rnd;for(let i=0;i<m;i++){T+=1000/60;H.tick(1);}};
  if(extra==='rewind'){tk(30);H.startRewind&&H.startRewind();tk(8);}
  if(extra==='lowlife'){H.P.hp=1;tk(40);}
  if(extra.startsWith('mid')){const fr=+extra.slice(3);for(const g of H.G)if(!g.alive&&!g.gone&&g.t>H.DISS.t0){g.t=H.DISS.t0+H.DISS.dur*fr;}}
  if(extra==='stormset'){const L=H.L,c=L.ext.chase;if(c){let sp=null;for(let cc=c.c0+6;cc<c.c1-4&&!sp;cc++)for(let r=c.rTop+1;r<c.rBot;r++)if(H.solidBelow(cc,r)&&H.solidBelow(cc-1,r)&&H.solidBelow(cc-2,r)&&H.solidBelow(cc-3,r)){sp={x:cc*32+16,r};break;}
    if(sp){const P=H.P;P.x=sp.x;P.y=(sp.r+1)*64-4;P.fallY=P.y;P.state='stand';P.inv=1e9;P.face=1;H.cam.snap=true;H.mode='play';c.on=true;c.done=false;c.t=1;c.wx=P.x-45;tk(20);P.x=sp.x;c.wx=P.x-45;H.cam.snap=true;}}}
  %s
  for(let i=0;i<14;i++){a=12345;Math.random=rnd;T+=1000/60;H.render();}
  const g=H.GLP.gl,GP=H.GLP,tex=GP.atl&&GP.gls?GP.atl.t:GP.mtex,w=GP.atl&&GP.gls?GP.atl.w:H.GLA.w,h=GP.atl&&GP.gls?GP.atl.h:H.GLA.h,px=new Uint8Array(w*h*4);
  const fb=g.createFramebuffer();g.bindFramebuffer(g.FRAMEBUFFER,fb);g.framebufferTexture2D(g.FRAMEBUFFER,g.COLOR_ATTACHMENT0,g.TEXTURE_2D,tex,0);g.readPixels(0,0,w,h,g.RGBA,g.UNSIGNED_BYTE,px);g.bindFramebuffer(g.FRAMEBUFFER,null);g.deleteFramebuffer(fb);
  let s='';const CH=0x8000;for(let i=0;i<px.length;i+=CH)s+=String.fromCharCode.apply(null,px.subarray(i,i+CH));
  return {w,h,k,ok:r.ok,mode:H.mode,px:btoa(s),on:H.shaderOn()};}''' % (json.dumps(COND), PRE)

def grab(html):
    out = {}
    with sync_playwright() as p:
        b = p.chromium.launch(); errs = []
        for (name, n, seed, cond, extra) in S:
            ctx = b.new_context(viewport={'width': 852, 'height': 393}, device_scale_factor=2); pg = ctx.new_page()
            pg.on('pageerror', lambda e: errs.append(name + ': ' + str(e)))
            pg.goto('file://' + os.path.abspath(html)); pg.wait_for_timeout(300); pg.add_script_tag(path=os.path.join(HERE, 'bot.js'))
            pg.evaluate("window.__HKfreeze=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.getElementById('app').classList.add('overlay')")
            r = pg.evaluate(RUN, [n, seed, cond, extra])
            a = np.frombuffer(base64.b64decode(r['px']), dtype=np.uint8).reshape(r['h'], r['w'], 4)[::-1, :, :3].copy()
            out[name] = (a, r['k'], r['on'])
            ctx.close()
        b.close()
    return out, errs

S = [x for x in S if not ONLY or any(o in x[0] for o in ONLY[0].split(','))]
ra, ea = grab(A); rb, eb = grab(B)
rows = []; crops = []
for (name, *_r) in S:
    a, ka, oa = ra[name]; b, kb, ob = rb[name]
    if a.shape != b.shape: rows.append((name, 'shape', a.shape, b.shape)); continue
    d = np.abs(a.astype(np.int16) - b.astype(np.int16)).max(axis=2)
    g = a.astype(np.int16).max(axis=2)
    pad = np.pad(g, 1, mode='edge'); mx = np.maximum.reduce([pad[i:i + g.shape[0], j:j + g.shape[1]] for i in range(3) for j in range(3)]); mn = np.minimum.reduce([pad[i:i + g.shape[0], j:j + g.shape[1]] for i in range(3) for j in range(3)])
    flat = (mx - mn) < 24
    st = dict(name=name, ticks=(ka, kb), max=int(d.max()), mean=float(d.mean()), p8=float((d > 8).mean() * 100), p24=float((d > 24).mean() * 100), flat24=float(((d > 24) & flat).mean() * 100), flatmax=int((d * flat).max()))
    rows.append(st)
    if d.max() > 0:
        Image.fromarray(np.clip(d * 8, 0, 255).astype(np.uint8)).save(os.path.join(OUT, name + '_diff.png'))
        y, x = np.unravel_index(np.argmax(d), d.shape); y0 = max(0, min(a.shape[0] - 120, y - 60)); x0 = max(0, min(a.shape[1] - 160, x - 80))
        crops.append((st['max'], name, a[y0:y0 + 120, x0:x0 + 160], b[y0:y0 + 120, x0:x0 + 160], np.clip(d[y0:y0 + 120, x0:x0 + 160] * 8, 0, 255).astype(np.uint8)))
    Image.fromarray(b).save(os.path.join(OUT, name + '_new.png')); Image.fromarray(a).save(os.path.join(OUT, name + '_base.png'))
for r in rows: print(r)
crops.sort(key=lambda c: -c[0])
if crops:
    sel = crops[:12]; sheet = Image.new('RGB', (160 * 3 * 2 + 10, (120 + 14) * ((len(sel) + 1) // 2)), (40, 40, 40))
    for i, (m, name, ca, cb, cd) in enumerate(sel):
        X = (i % 2) * (160 * 3 + 10); Y = (i // 2) * 134
        sheet.paste(Image.fromarray(ca), (X, Y + 14)); sheet.paste(Image.fromarray(cb), (X + 160, Y + 14)); sheet.paste(Image.fromarray(cd).convert('RGB'), (X + 320, Y + 14))
        from PIL import ImageDraw; ImageDraw.Draw(sheet).text((X + 2, Y + 1), '%s max %d (base | new | diff x8)' % (name, m), fill=(255, 255, 160))
    sheet.save(os.path.join(OUT, 'sheet.png'))
M = [r for r in rows if isinstance(r, dict)]
print('ALL: states %d, max %d, mean of means %.4f, worst p24 %.3f%%, worst flat24 %.4f%%, worst flatmax %d' % (len(M), max(r['max'] for r in M), sum(r['mean'] for r in M) / len(M), max(r['p24'] for r in M), max(r['flat24'] for r in M), max(r['flatmax'] for r in M)))
print('errors', ea[:5], eb[:5])
