# stormfair.py lo hi [seeds]: the sandstorm's front is where it kills (unit ST).
# Death is P.x < wx+4. On every chase floor in lo..hi (seeds tried until one has a chase), with the prince on a storm row and the
# storm 20 to 90 px behind him, 200 frames apart in game time, in Classic and in Torchlight: at every storm row, from the feet
# up to the waist, the dust's alpha must first reach .55 within 6 px of the kill line, and nothing denser than .25 may lie
# beyond wx+10 (the veil and grains ahead stay thin). Uses __HK.stormProbe (Classic: the 2D layer drawn alone; Torchlight:
# the shader's own buffer). Prints one line per floor and ends with 'FAILURES n'. (egypt: the chase is drawn as granite plugs by default,
# their leading face at wx, on the same rows and speed; this checks the storm's look, EGP.plug=false, which the shader still draws.)
# Torchlight frames are sent to WebGL at once (GLP.pipe=false): the test moves the storm tens of px between single frames, and
# the game's one-frame-late picture (v52) would show the frame before; in play the storm pass reads the storm where it is.
import os, sys
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
HTML = 'file://' + os.path.abspath(os.path.join(HERE, '..', 'hourglass-keep.html'))
a = [x for x in sys.argv[1:]]
lo = int(a[0]) if a else 6
hi = int(a[1]) if len(a) > 1 else 27
nseeds = int(a[2]) if len(a) > 2 else 1
FRAMES, TORCH_EVERY = 200, 5
fails = 0
SETUP = '''([n,s])=>{const H=__HK;H.EGP.plug=false;window.__HKfreeze=true;window.__HKnoauto=true;H.GLP.pipe=false;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);
  for(const id in H.HINTS)H.S.hints[id]=1;for(const id of H.HINT_MOVE)H.S.learned[id]=1;
  const L=H.load(n,s,true);H.banner=null;const c=L.ext.chase;if(!c)return null;
  let sp=null;for(let cc=c.c0+6;cc<c.c1-4&&!sp;cc++)for(let r=c.rTop+1;r<c.rBot;r++)if(H.solidBelow(cc,r)&&H.solidBelow(cc-1,r)&&H.solidBelow(cc-2,r)&&H.solidBelow(cc-3,r)){sp={x:cc*32+16,r};break;}
  if(!sp)return null;window.__sp=sp;const P=H.P;P.x=sp.x;P.y=(sp.r+1)*64-4;P.fallY=P.y;P.state='stand';P.inv=1e9;P.face=1;H.cam.snap=true;H.mode='play';H.tick(2);
  c.on=true;c.done=false;c.t=1;return {theme:L.theme.name,rTop:c.rTop,rBot:c.rBot,row:sp.r};}'''
STEP = '''([k,torch])=>{const H=__HK,P=H.P,c=H.L.ext.chase,sp=window.__sp,d=20+70*((k*37)%11)/10;
  P.x=sp.x;P.y=(sp.r+1)*64-4;P.state='stand';P.inv=1e9;P.vx=P.vy=0;c.wx=P.x-d;H.tick(1);P.x=sp.x;P.y=(sp.r+1)*64-4;c.wx=P.x-d;
  const res=[];res.push(H.stormProbe(false));if(torch){H.S.set.lightMode='torch';H.cam.snap=true;H.render();res.push(H.stormProbe(true));}
  let worst=0,ahead=0,missing=0,n=0,gl=null;
  for(const q of res){if(q.gl===false&&!q.rows){gl=false;continue;}if(q.gl)gl=true;for(const r of q.rows){n++;if(r.cross===null){missing++;continue;}worst=Math.max(worst,Math.abs(r.cross));ahead=Math.max(ahead,r.ahead);}}
  return {worst,ahead,missing,n,gl};}'''
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 844, 'height': 390}, device_scale_factor=3)
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(HTML); pg.wait_for_timeout(300)
    for n in range(lo, hi + 1):
        info = None
        for s in range(9100, 9100 + 40):
            info = pg.evaluate(SETUP, [n, s])
            if info:
                break
        if not info:
            print('floor %d: no chase' % n); continue
        tried = 0
        worst = ahead = 0; missing = samples = 0; gl_frames = 0
        for k in range(FRAMES):
            r = pg.evaluate(STEP, [k, k % TORCH_EVERY == 0])
            worst = max(worst, r['worst']); ahead = max(ahead, r['ahead']); missing += r['missing']; samples += r['n']
            if r['gl']: gl_frames += 1
        ok = worst <= 6 and ahead <= 0.255 and missing == 0 and gl_frames > 0
        if not ok: fails += 1
        print('%s floor %d seed %d (%s, rows %d-%d): front at the feet within %.1f px of the kill line, densest beyond wx+10 %.2f, %d samples, %d without a front, %d Torchlight frames'
              % ('ok  ' if ok else 'FAIL', n, s, info['theme'], info['rTop'], info['rBot'], worst, ahead, samples, missing, gl_frames))
    if errs:
        fails += 1; print('page errors', errs[:3])
    b.close()
print('FAILURES', fails)
