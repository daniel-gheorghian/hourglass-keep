# metaltest.py: checks of the Torchlight metal shader (unit MS).
#  1. GLFX.metal off renders exactly the frame of a build whose shaders carry no metal code (HK_NOMS, forced by too few texture units)
#  2. the sampler-limit fallback: under 8 texture units the metal code is left out, Torchlight still runs, one console note, no errors
#  3. a view without metal draws no mask and uploads nothing; a view with a gate draws and uploads it, and changes the frame
#  4. "Softer flashes" (calm) freezes the glints and lowers the strength; the painted highlights come back with the shader off
#  5. with --base FILE: GLFX.metal off is pixel-identical to FILE (the source before the unit) in the same scenes
# Prints one line per check and ends with 'FAILURES n'.
import os, sys, hashlib
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.abspath(os.path.join(HERE, '..', 'hourglass-keep.html'))
base = sys.argv[sys.argv.index('--base') + 1] if '--base' in sys.argv else None
fails = 0


def ok(name, cond, info=''):
    global fails
    print(('ok   ' if cond else 'FAIL ') + name + ('  ' + str(info) if info else ''))
    if not cond:
        fails += 1


# scenes: (floor, seed, js finding a spot near a dyn feature of this type, or None for anywhere)
SCENES = [(4, 9801, 'gate'), (8, 9501, 'saw'), (4, 9000, 'chomp'), (10, 9300, 'pend'), (9, 10814, None)]
SETUP = '''([n,s,t])=>{const H=__HK;window.__HKfreeze=true;window.__HKnoauto=true;document.querySelectorAll('.screen').forEach(e=>e.hidden=true);
  for(const id in H.HINTS)H.S.hints[id]=1;for(const id of H.HINT_MOVE)H.S.learned[id]=1;
  let a=s;Math.random=()=>{a=(a*16807)%2147483647;return a/2147483647;};
  const L=H.load(n,s,true);H.banner=null;let x=L.start.x,r=L.start.r;
  if(t){const o=L.dyn.find(o=>o.f.t===t);if(!o)return false;x=o.c*32-56;r=o.r;}
  const P=H.P;P.x=x;P.y=(r+1)*64-4;P.fallY=P.y;P.state='stand';P.inv=1e9;H.cam.snap=true;H.mode='play';
  for(let k=0;k<40;k++){P.x=x;P.y=(r+1)*64-4;P.state='stand';P.inv=1e9;H.tick(1);}H.S.set.lightMode='torch';H.GLFX.metal=false;for(let k=0;k<12;k++)H.render();return true;}''' # (a dozen frames first: the relief pass copies the rooms in view one a frame)
FRAME = '''([m,calm])=>{const H=__HK;H.GLFX.metal=m;H.S.set.calm=!!calm;let a=7;const R=Math.random;Math.random=()=>{a=(a*16807)%2147483647;return a/2147483647;};
  try{H.render();}finally{Math.random=R;}return {used:H.GLP.used,on:H.MS.on,ups:H.MS.ups||0,ok:H.MS.ok,paint:H.msPaint()};}'''


def page(br, path, maxtu=None):
    pg = br.new_page(viewport={'width': 844, 'height': 390})
    errs, logs = [], []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.on('console', lambda m: logs.append(m.text))
    if maxtu:
        pg.add_init_script('window.__HKmaxTU=%d' % maxtu)
    pg.add_init_script('try{localStorage.clear()}catch(e){}')
    pg.goto('file://' + path)
    pg.wait_for_timeout(400)
    return pg, errs, logs


def shot(pg):
    return hashlib.md5(pg.screenshot()).hexdigest()


with sync_playwright() as p:
    br = p.chromium.launch()
    A, ea, la = page(br, HTML)
    N, en, ln = page(br, HTML, maxtu=4)
    Bp = page(br, base)[0] if base else None
    for n, s, t in SCENES:
        for pg in [A, N] + ([Bp] if Bp else []):
            pg.evaluate(SETUP, [n, s, t])
        ra = A.evaluate(FRAME, [False, False]); ha = shot(A)
        N.evaluate(FRAME, [True, False]); hn = shot(N)
        ok('floor %d %s: metal off == no metal code' % (n, t or 'start'), ha == hn)
        if Bp:
            Bp.evaluate('''()=>{const H=__HK;let a=7;const R=Math.random;Math.random=()=>{a=(a*16807)%2147483647;return a/2147483647;};try{H.render();}finally{Math.random=R;}}''')
            ok('floor %d %s: metal off == the source before the unit' % (n, t or 'start'), ha == shot(Bp))
            CL = '''()=>{const H=__HK;H.S.set.lightMode='classic';if(H.GLFX)H.GLFX.metal=true;let a=7;const R=Math.random;Math.random=()=>{a=(a*16807)%2147483647;return a/2147483647;};try{H.render();}finally{Math.random=R;}H.S.set.lightMode='torch';}'''
            A.evaluate(CL); hc = shot(A); Bp.evaluate(CL)
            ok('floor %d %s: Classic unchanged from the source before the unit' % (n, t or 'start'), hc == shot(Bp))
            A.evaluate(FRAME, [False, False])
        rb = A.evaluate(FRAME, [True, False]); hb = shot(A)
        if t:
            ok('floor %d %s: mask drawn and uploaded, frame changed' % (n, t), rb['on'] == 1 and rb['ups'] > ra['ups'] and hb != ha, rb)
            ok('floor %d %s: painted highlights off with the shader, on without' % (n, t), rb['paint'] is False and ra['paint'] is True)
            u0 = A.evaluate('()=>Array.from(__HK.MS.U.slice(4,12))')
            A.evaluate(FRAME, [False, False])
            ok('floor %d %s: metal off again, same frame as before' % (n, t), shot(A) == ha)
            A.evaluate(FRAME, [True, True])
            u1 = A.evaluate('()=>Array.from(__HK.MS.U.slice(4,12))')
            ok('floor %d %s: calm freezes the glints and lowers the strength' % (n, t), u1[7] == 1 and u0[7] == 0 and u1[1] < u0[1] and u1[2] < u0[2], (u0, u1))
        else:
            ok('floor %d start: no metal in view, no mask, no upload' % n, rb['on'] == 0 and rb['ups'] == ra['ups'], rb)
            A.evaluate(FRAME, [False, False])
            ok('floor %d start: metal off again, same frame as before' % n, shot(A) == ha)
    st = N.evaluate('()=>({ok:__HK.MS.ok,why:__HK.MS.why,used:__HK.GLP.used,dead:!!__HK.GLP.dead})')
    notes = [x for x in ln if 'metal shader off' in x]
    ok('under 8 texture units: metal left out, Torchlight on, one note', st['ok'] is False and st['used'] and not st['dead'] and len(notes) == 1, (st, notes))
    A.evaluate(SETUP, [4, 9801, 'gate'])
    A.evaluate("()=>{const H=__HK;H.GLFX.metal=true;H.render();H.GLP.gl.getExtension('WEBGL_lose_context').loseContext();H.render();return 1}")
    A.wait_for_timeout(200)
    lost = A.evaluate("()=>{const H=__HK;H.render();H.render();return {mode:H.S.set.lightMode,dead:!!H.GLP.dead}}")
    ok('context lost on a metal frame: falls back to Classic', lost['dead'] and lost['mode'] == 'classic', lost)
    ok('no page errors', not ea and not en, (ea + en)[:3])
    br.close()
print('FAILURES', fails)
