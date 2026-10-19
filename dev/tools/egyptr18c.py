# egyptr18c.py [new.html] [old.html] [outdir]: round 18c's pictures for egypt_themes.html: the jet stream hint made organic (fine
# grains of mixed size carried round drifting eddies, puffs, a faint haze, glints; see jetStream) against round 18a/18b's leaf-shaped
# streaks (old.html, default ../_r18b.html, made with git show f0713f8:dev/hourglass-keep.html), in the game at the phone's resolution
# (crops of the 1704 px canvas, i.e. 2x the game's pixels), Torchlight, two themes (the Halls of the West, the Green Hall of Osiris):
#  r18c_shaft.mp4  8 s at 30 fps: the kick shaft, 4 s standing at its foot, then the climb; before (left) and after (right)
#  r18c_swing.mp4  8 s: pumping the swing until it will carry him, the stream on the throw, then the throw; before (left), after (right)
#  r18c_sheet.png  stills: the shaft and the swing, before and after, Torchlight and Classic; the jump up to a ledge, after
# Writes r18c.json (floors, frame counts, errors). Needs ffmpeg (FFMPEG, default /usr/local/bin/ffmpeg). Hints are set unlearned.
# Run from dev/tools.
import json, os, shutil, subprocess, sys, tempfile
from playwright.sync_api import sync_playwright
from PIL import Image
import egyptr12 as R12
import egyptr18 as E
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
NEW = os.path.abspath(a[0] if len(a) > 0 else os.path.join(HERE, '..', 'hourglass-keep.html'))
OLD = os.path.abspath(a[1] if len(a) > 1 else os.path.join(HERE, '..', '_r18b.html'))
OUT = a[2] if len(a) > 2 else os.path.join(HERE, 'egypt_themes')
R12.OUT = OUT
FF = os.environ.get('FFMPEG', '/usr/local/bin/ffmpeg')
FPS, SEC = 30, 8
# the shaft driven by the bot's own generator, one tick at a time (gameTime runs on, so the stream is continuous)
SH0 = r"""([n,sd])=>{const H=__HK;__P.load(n,sd);const L=H.L,ins=L.path.find(a=>a.a==='walljump'),f=L.dyn.find(d=>d.f.t==='shaftfoot'&&d.c===ins.from);
 window.__G=botGen(n,sd,{path:[ins],at:{c:ins.from,r:f.r,face:ins.dir||1}});__G.next();H.S.learned.shaft=0;H.S.learned.walljump=0;H.cam.snap=true;H.tick(1);H.banner=null;
 const q=H.jetPlaces().shafts.find(s=>s.c===ins.from);return {x:ins.from*32+16,y:(q.p.by0+q.p.by1)/2-10,look:L.theme.look,name:H.themeName(n)};}"""
SHK = r"""([go,k,x,y])=>{const H=__HK;for(let i=0;i<k;i++){if(go&&window.__G){const r=__G.next();if(r.done)window.__G=null;}H.tick(1);}H.S.learned.shaft=0;H.banner=null;__P.draw();return __P.scr(x,y);}"""
PUMP = r"""(k)=>{const H=__HK,p=H.P,d=p.swOm>=0?(p.face>0?'r':'l'):(p.face>0?'l':'r');H.setKey('kb',d,true);H.tick(1);H.setKey('kb',d,false);H.tick(k-1);H.banner=null;__P.draw();}"""
THROW = r"""()=>{const H=__HK,p=H.P;let i=0;while(i<120&&!(p.swOm>0&&p.swTh>=0&&p.swTh<0.15)){H.tick(1);i++;}H.setKey('kb','j',true);H.tick(1);H.setKey('kb','j',false);return i;}"""


def video(frames, fn):
    d = tempfile.mkdtemp()
    for i, f in enumerate(frames):
        f.save(os.path.join(d, '%04d.png' % i))
    subprocess.run([FF, '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(d, '%04d.png'), '-vf', 'pad=ceil(iw/2)*2:ceil(ih/2)*2',
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-movflags', '+faststart', os.path.join(OUT, fn)], check=True)
    shutil.rmtree(d)


def shaft_frames(pg, n, sd, tag):
    q = pg.evaluate(SH0, [n, sd]); fr = []
    for k in range(FPS * SEC):
        xy = pg.evaluate(SHK, [k >= FPS * SEC // 2, 2, q['x'], q['y']])
        fr.append(R12.label(R12.crop(R12.shot(pg), xy, 300, 560), '%s, %s' % (q['name'], tag)))
    return fr


def swing_frames(pg, n, tag):
    q = pg.evaluate(E.SWING, [n, 0.5, 0.0]); fr = []
    for k in range(FPS * SEC):
        if k == FPS * 5:
            pg.evaluate(THROW)
        if k < FPS * 5 and k % 3 == 0:
            pg.evaluate(PUMP, 2)
        else:
            pg.evaluate(E.STEP, 2)
        xy = pg.evaluate(E.AT, [q['fx'] + q['D'] * 75, q['fy'] + 30])
        fr.append(R12.label(R12.crop(R12.shot(pg), xy, 760, 400), '%s, %s' % (q['name'], tag)))
    return fr


if __name__ == '__main__':
    J = {'errors': [], 'shafts': E.SHAFTS, 'swings': E.SWINGS, 'fps': FPS, 'sec': SEC}
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
        P = {(v, m): R12.page(b, src, m) for v, src in (('old', OLD), ('new', NEW)) for m in ('torch', 'classic')}
        TAG = {'old': 'before (18a)', 'new': 'after (18c)'}
        # ---- videos (Torchlight): rows the two themes, columns before and after
        rows = [[shaft_frames(P[(v, 'torch')], n, sd, TAG[v]) for v in ('old', 'new')] for n, sd in E.SHAFTS]
        video([R12.grid([c[k] for r in rows for c in r], 4) for k in range(FPS * SEC)], 'r18c_shaft.mp4')
        rows = [[swing_frames(P[(v, 'torch')], n, TAG[v]) for v in ('old', 'new')] for n in E.SWINGS]
        video([R12.grid([c[k] for r in rows for c in r], 2) for k in range(FPS * SEC)], 'r18c_swing.mp4')
        # ---- the contact sheet: the shaft mid-climb and the swing once it will carry him, before and after, both modes, 1:1; 2x crops
        t1, t2, t3 = [], [], []
        for n, sd in E.SHAFTS:
            for m in ('torch', 'classic'):
                for v in ('old', 'new'):
                    pg = P[(v, m)]; q = pg.evaluate(E.SHAFT, [n, sd, 40]); im = R12.shot(pg)
                    t1.append(R12.label(R12.crop(im, q['xy'], 300, 420), '%s, %s, %s' % (q['name'], m, TAG[v])))
                    t2.append(R12.label(E.up(R12.crop(im, q['xy'], 150, 210)), '2x, %s, %s' % (m, TAG[v])))
        for n in E.SWINGS:
            for m in ('torch', 'classic'):
                for v in ('old', 'new'):
                    pg = P[(v, m)]; q = pg.evaluate(E.SWING, [n, 0.85, 0.25])
                    t3.append(R12.label(R12.crop(R12.shot(pg), q['xy'], 760, 400), '%s, %s, %s' % (q['name'], m, TAG[v])))
        t4 = []
        for n, sd, k in E.JGRABS:
            for m in ('torch', 'classic'):
                q = P[('new', m)].evaluate(E.JG, [n, sd, k])
                t4.append(R12.label(R12.crop(R12.shot(P[('new', m)]), q['xy'], 560, 380), '%s, jump up to a ledge, %s, after (18c)' % (q['name'], m)))
        R12.stack([R12.grid(t1, 8), R12.grid(t2, 8), R12.grid(t3, 4), R12.grid(t4, 4)]).save(os.path.join(OUT, 'r18c_sheet.png'))
        for pg in P.values():
            J['errors'] += pg.errs
        json.dump(J, open(os.path.join(OUT, 'r18c.json'), 'w'), indent=1)
        print('errors', J['errors'][:5])
        b.close()
