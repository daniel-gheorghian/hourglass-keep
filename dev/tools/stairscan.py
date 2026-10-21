# stairscan.py [file.html] [lo hi] [out.png]: the prince's feet on the exit stairs (round 16c, owner: "check the step height in every theme").
# For every floor lo..hi (default 1..48: all twelve themes and the five drawing styles), seed 4400+n, Classic: the exit door open, the
# prince climbing (state 'exit') planted on treads 1..4 in turn. Measured from the render, at the canvas's own resolution: his lowest pixel
# inside the doorway (a frame with him against one without him, LIFT_DBG.rider) and, in the frame without him, the tread's front edge
# below that pixel (drawDoor's tread edge; the render's strongest change of colour going down that column within 1.5 px of it is printed as 'drawn',
# so the treads are checked too) and the edge behind it
# (the riser's top, one tread up). A foot lands on the tread when it lies between the tread's front edge and its back edge (SY above).
# Also measured: how far his lowest pixel moves sideways while he stands planted on a tread (a sliding foot). Prints a line per style,
# the worst floor, and ALL OK or FAILURES n. Run from dev/tools.
# (round 26f) The feet are measured facing right and facing left (v72 drifted him onto the left jamb facing left: P.exX took his facing),
# with the exit's look (whitening, fade) off (EXF.look) so the feet stay measurable. Then 'clip': the whole exit played from Up pressed 14 px
# off the doorway's middle, both facings, Classic and Torchlight, each frame from the first rise (exS > EX_CUT) against the same frame
# without him: no pixel of his above the opening's head (doorHead: the lintel's line, or the round arch) or outside its jambs; and he
# ends facing right, never left of the doorway's middle. Then 'entry' (no render): a fresh floor (startLevel(n,-1,true)) gives control
# within 0.7 s at his start, the leaf is down by 1 s with its thud; a respawn, a checkpoint start and a rewind never play it again, and no
# rewind snapshot holds it; the bot plays a floor from its entry (opts.entry).
import io, os, sys
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
SRC = os.path.abspath(next((x for x in a if x.endswith('.html')), os.path.join(HERE, '..', 'hourglass-keep.html')))
NUM = [int(x) for x in a if x.isdigit()]
LO, HI = (NUM + [1, 48])[:2] if len(NUM) >= 2 else (1, 48)
OUT = next((x for x in a if x.endswith('.png')), None)
SHOW = r'''([n,tr,ff,hide])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS)H.S.hints[id]=1;
  if(window.__n!==n){H.load(n,4400+n,true);window.__n=n;}const L=H.L,d=L.door,P=H.P;H.banner=null;d.opening=true;d.open=1;H.levelCompleteHook=()=>{};
  P.inv=1e9;P.state='exit';P.exTt=0;P.face=ff<0?-1:1;ff=Math.abs(ff);P.x=d.x;P.y=(d.r+1)*64-4;P.vx=P.vy=0;H.EXF.look=false;
  for(let k=0;k<16;k++){P.t=0;P.exS=tr+ff;H.tick(1);} // (round 26f: 16 frames, so a turn to the stairs (EX_TURN) and the pose have settled)
  H.cam.x=d.x-H.viewW/2;H.cam.y=(d.r+1)*64-64*1.6;H.cam.gy=H.cam.y;H.mode='play';H.GLP&&(H.GLP.pipe=false);H.LIFT_DBG.rider=hide;
  H.render();H.render();H.LIFT_DBG.rider=false;H.EXF.look=true;const X=H.XF,cv=[...document.querySelectorAll('canvas')].find(c=>c.getBoundingClientRect().width>0),R=cv.getBoundingClientRect();
  const sx=R.width/cv.width,sy=R.height/cv.height;
  const xc=d.x+8,yb=(d.r+1)*64-4-4,rdy=8*0.45,SY=8*0.22,RS=6.2;
  return {VZ:X.VZ,camD:X.camD,camDY:X.camDY,sx,sy,left:R.left,top:R.top,x0:xc-12,x1:xc+12,yb,rdy,SY,RS,exY:P.exY,exS:P.exS,st:L.theme.style,th:H.themeName(n),look:L.theme.look,face:P.face,exX:P.exX};}'''
# (round 26f) the exit played whole: k frames on, then the frame (and HIDE's frame without him); the opening's head and jambs in world px
CLIP0 = r'''([n,mode,face])=>{const H=__HK;window.__HKfreeze=true;for(const id in H.HINTS)H.S.hints[id]=1;H.S.set.lightMode=mode;
  H.load(n,4400+n,true);window.__n=-1;const L=H.L,d=L.door,P=H.P;H.banner=null;d.opening=true;d.open=1;
  P.inv=1e9;P.face=face;P.x=d.x-face*14;P.y=(d.r+1)*64-4;P.vx=P.vy=0;P.state='stand';P.t=0;H.tick(3);P.state='exit';P.t=0;P.exS=0;P.sword=false;H.mode='play';
  if(H.GLP)H.GLP.pipe=false;const c=Math.floor(d.x/32),r=d.r,ctop=r*64+Math.max(H.ceilOff(c,r),H.ceilOff(c+1,r)),xc=d.x+8;
  return {x0:xc-12,x1:xc+12,y0:ctop+6,ctop,yb:(r+1)*64-8,kind:L.theme.style==='dungeon'?'round':'point',st:L.theme.style};}'''
CLIPF = r'''([k])=>{const H=__HK,L=H.L,d=L.door,P=H.P;for(let i=0;i<k;i++){if(H.mode==='play')H.tick(1);}const done=H.mode!=='play';
  document.querySelectorAll('.screen').forEach(e=>e.hidden=true);H.mode='play';
  H.cam.x=d.x-H.viewW/2;H.cam.y=(d.r+1)*64-64*1.6;H.cam.gy=H.cam.y;H.render();H.render();const X=H.XF,cv=[...document.querySelectorAll('canvas')].find(c=>c.getBoundingClientRect().width>0),R=cv.getBoundingClientRect();
  return {VZ:X.VZ,camD:X.camD,camDY:X.camDY,sx:R.width/cv.width,sy:R.height/cv.height,left:R.left,top:R.top,exS:P.exS||0,cut:H.EX_CUT,face:P.face,px:P.x+(P.exX||0),dx:d.x,done};}'''
ENTRY = r'''([lo,hi])=>{const H=__HK,out=[];window.__HKfreeze=true;for(const id in H.HINTS)H.S.hints[id]=1;
  for(let n=lo;n<=hi;n++){const bad=[];H.startLevel(n,-1,true);const L=H.L,P=H.P;if(P.state!=='enter')bad.push('no entry');
    let f=0;while(P.state==='enter'&&f<120){H.tick(1);f++;}const ctl=f/60;if(ctl>0.7)bad.push('control at '+ctl.toFixed(2));if(Math.abs(P.x-L.start.x)>0.01)bad.push('not at his start');
    while(f<60){H.tick(1);f++;}if(H.entryOpen()!==0||L.enS!==2)bad.push('leaf not down');
    while(f<180){H.tick(1);f++;}if(H.REW.some(q=>q.P.state==='enter'))bad.push('a rewind snapshot holds the entry');
    H.die('spikes');H.startRewind();let g=0;while(H.mode==='rewind'&&g<2000){H.tick(1);g++;}if(P!==H.P&&0){}if(H.P.state==='enter'||H.entryOpen()!==0)bad.push('the rewind played it');
    H.respawn();if(H.P.state==='enter'||H.entryOpen()!==0)bad.push('the respawn played it');
    if(H.L.cps.length){H.startLevel(n,0,true);if(H.P.state==='enter'||H.entryOpen()!==0)bad.push('the checkpoint start played it');}
    H.startLevel(n,-1);if(H.P.state==='enter')bad.push('startLevel without entry played it');
    out.push([n,ctl,bad]);H.mode='play';}
  H.S.level=1;return out;}'''
BOTE = r'''([n,seed])=>{const r=runBot(n,seed,{entry:true});return [r.ok,r.why||'',r.hurt||0];}'''


def page(b):
    pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=2)
    pg.errs = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e)))
    pg.goto('file://' + SRC)
    pg.wait_for_timeout(700)
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.body.classList.remove('panelOpen')")
    pg.evaluate("()=>{__HK.S.set.lightMode='classic';}")
    return pg


HIDE = "()=>{const H=__HK;H.LIFT_DBG.rider=true;H.render();H.render();H.LIFT_DBG.rider=false;}"


def grab(pg, n, tr, ff, hide):
    if hide:  # (the same moment without him: no tick between the two frames, so nothing else has moved)
        pg.evaluate(HIDE); return None, Image.open(io.BytesIO(pg.screenshot())).convert('RGB')
    r = pg.evaluate(SHOW, [n, tr, ff, False])
    return r, Image.open(io.BytesIO(pg.screenshot())).convert('RGB')


def lum(p):
    return 0.3 * p[0] + 0.59 * p[1] + 0.11 * p[2]


if __name__ == '__main__':
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
        pg = page(b)
        res, fails, tiles = {}, 0, []
        for n in range(LO, HI + 1):
            worst = 0
            for tr, fc in [(t, f) for f in (1, -1) for t in (1, 2, 3, 4)]:
                foots = []
                for ff in (0.05, 0.3, 0.5):  # (planted: the climb's rise starts at 0.55 of a tread)
                    r, im = grab(pg, n, tr, ff * fc, False); _, im0 = grab(pg, n, tr, ff * fc, True)
                    if r['face'] != 1 or r['exX'] < 0:
                        fails += 1; print('floor %d facing %d: not turned to the stairs (face %d, exX %.1f)' % (n, fc, r['face'], r['exX']))
                    A, B0 = im.load(), im0.load()
                    # screen px of world (x,y): canvas px = x*VZ-camD; screenshot px = (left + canvas*sx)*2
                    W = lambda x, y: (int((r['left'] + (x * r['VZ'] - r['camD']) * r['sx']) * 2), int((r['top'] + (y * r['VZ'] - r['camDY']) * r['sy']) * 2))
                    k = 2 * r['VZ'] * r['sy']  # screenshot px per world px
                    (X0, Y0), (X1, Y1) = W(r['x0'] + 1, r['yb'] - 60), W(r['x1'] - 1, r['yb'] + 8)
                    low = None
                    for y in range(Y1, Y0, -1):
                        for x in range(X0, X1):
                            u, v = A[x, y], B0[x, y]
                            if abs(u[0] - v[0]) + abs(u[1] - v[1]) + abs(u[2] - v[2]) > 40:
                                low = (x, y); break
                        if low: break
                    if not low:
                        continue
                    foots.append(low)
                    # the tread under him (tread tr-1): drawDoor's front edge, then the strongest edge within 6 px of it in the frame without him
                    kk = tr - 1; top = r['yb'] - r['rdy'] - kk * r['SY'] - (kk + 1) * r['RS']
                    _, ty = W(0, top); best, by = -1, ty
                    for y in range(int(ty - 1.5 * k), int(ty + 1.5 * k) + 1):
                        g = abs(lum(B0[low[0], y + 1]) - lum(B0[low[0], y - 1]))
                        if g > best: best, by = g, y
                    edge = ty / k; foot = low[1] / k  # (world px, relative: drawDoor's edge, checked against the render below)
                    res.setdefault('drawn', []).append((by - ty) / k)  # (the drawn edge's offset from drawDoor's formula, from the render)
                    gap = foot - edge  # >0: the foot below the tread's front edge (sunk into the riser); <-SY: floating over it
                    res.setdefault(r['st'], []).append(gap)
                    bad = gap > 0.5 or gap < -(r['SY'] + 0.5)
                    if bad:
                        fails += 1
                    worst = max(worst, abs(gap + r['SY'] / 2))
                    if OUT and n in (1, 5, 13, 17, 25) and ff == 0.3 and tr in (1, 3):
                        cx, cy = low; c = im.crop((cx - 90, cy - 150, cx + 90, cy + 40)); ImageDraw.Draw(c).line((0, by - cy + 150, 180, by - cy + 150), fill=(0, 255, 120))
                        ImageDraw.Draw(c).text((3, 3), '%d %s t%d gap %.1f' % (n, r['st'], tr, gap), fill=(255, 240, 160)); tiles.append(c)
                if len(foots) > 1:
                    sl = (max(f[0] for f in foots) - min(f[0] for f in foots)) / k
                    res.setdefault('slide', []).append(sl)
                    if sl > 1.5:
                        fails += 1; print('slide %d %s tread %d facing %d: %.1f px' % (n, r['st'], tr, fc, sl))
            print('floor %2d %-7s %-24s worst off the tread middle %.1f px' % (n, r['st'], r['th'][:24], worst), flush=True)
        for st, v in sorted(res.items()):
            print('%-8s n %3d  mean %.2f  min %.2f  max %.2f' % (st, len(v), sum(v) / len(v), min(v), max(v)))
        print('(gap: foot minus the tread\'s front edge, world px; on the tread is between %.2f and 0)' % -(8 * 0.22))
        # (round 26f) the cut at the opening, both modes and facings, the exit played whole
        import numpy as np
        cl = {}
        for n in range(LO, HI + 1):
            for mode in ('classic', 'torch'):
                for fc in (1, -1):
                    g = pg.evaluate(CLIP0, [n, mode, fc]); worst, frames, last = 0.0, 0, None
                    while True:
                        r = pg.evaluate(CLIPF, [4])
                        if r['done']: last = r; break
                        last = r
                        if r['exS'] <= r['cut']: continue
                        im = Image.open(io.BytesIO(pg.screenshot())).convert('RGB'); pg.evaluate(HIDE); im0 = Image.open(io.BytesIO(pg.screenshot())).convert('RGB')
                        frames += 1
                        W = lambda x, y: ((r['left'] + (x * r['VZ'] - r['camD']) * r['sx']) * 2, (r['top'] + (y * r['VZ'] - r['camDY']) * r['sy']) * 2)
                        (X0, Y0), (X1, Y1) = W(g['x0'] - 14, g['ctop'] - 16), W(g['x1'] + 18, g['yb'] + 6)
                        X0, Y0, X1, Y1 = int(X0), int(Y0), int(X1), int(Y1)
                        D = np.abs(np.asarray(im, dtype=np.int16)[Y0:Y1, X0:X1] - np.asarray(im0, dtype=np.int16)[Y0:Y1, X0:X1]).sum(axis=2)
                        ys, xs = np.nonzero(D > 40)
                        if len(xs):
                            wx = (((xs + X0 + 0.5) / 2 - r['left']) / r['sx'] + r['camD']) / r['VZ']
                            wy = (((ys + Y0 + 0.5) / 2 - r['top']) / r['sy'] + r['camDY']) / r['VZ']
                            xc = (g['x0'] + g['x1']) / 2
                            head = np.full(wx.shape, g['y0'] + 2.0) if g['kind'] != 'round' else g['y0'] + 12 - np.sqrt(np.maximum(0.0, 144 - (wx - xc) ** 2))
                            over = np.maximum(np.maximum(g['x0'] - wx, wx - g['x1']), head - wy)
                            worst = max(worst, float(over.max()))
                    bad = worst > 0.75 or last['face'] != 1 or last['px'] < last['dx'] - 0.5
                    if bad:
                        fails += 1
                    cl.setdefault(g['st'], []).append(worst)
                    print('clip floor %2d %-7s %-7s facing %2d: %2d frames, furthest outside the opening %.2f px, ends facing %d %s' % (n, g['st'], mode, fc, frames, worst, last['face'], 'FAIL' if bad else ''), flush=True)
        for st, v in sorted(cl.items()):
            print('clip %-8s n %3d  worst %.2f px (tolerance 0.75: antialiasing at 2x)' % (st, len(v), max(v)))
        # (round 26f) the entry: control, the leaf, never played again
        for n, ctl, bad in pg.evaluate(ENTRY, [LO, HI]):
            if bad: fails += 1
            print('entry floor %2d: control at %.2f s %s' % (n, ctl, ', '.join(bad) if bad else 'ok'))
        pg.add_script_tag(path=os.path.join(HERE, 'bot.js'))
        for n in (3, 8):
            ok, why, hurt = pg.evaluate(BOTE, [n, 101])
            if ok is not True or hurt: fails += 1
            print('bot from the entry, floor %d: %s %s hurt %d' % (n, ok, why, hurt))
        print('errors', pg.errs[:3])
        if pg.errs: fails += 1
        print('ALL OK' if not fails else 'FAILURES %d' % fails)
        if OUT and tiles:
            sh = Image.new('RGB', (5 * 182, ((len(tiles) + 4) // 5) * 192), (20, 16, 24))
            for i, c in enumerate(tiles):
                sh.paste(c, ((i % 5) * 182, (i // 5) * 192))
            sh.save(OUT); print('wrote', OUT)
        b.close()
