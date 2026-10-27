# egyptr41e.py old.html new.html [outdir]: round 41e's pictures (owner: "Fix the spikes thing"): the sand lift's slab sinking its last
# 30 px into the spike pit and at rest, old | new, Classic and Torchlight. Uses egyptr41.py's floor finder and stepping.
# r41e_spikes.png: one row per distance of the slab's top over the pit's floor (30 ... 0 = at rest), columns old | new for each mode,
#   crops round the pit at 3x (3 screen px a world px), then a strip of the same at phone size (the device pixels of an iPhone, dsf 3).
# r41e_spikes.gif: the last storey in real time, Classic | Torchlight, new build, 3x.
# Run from dev/tools (Torchlight is software WebGL in headless Chromium unless the GPU flags are given: HK_GPU=1).
import io, os, sys
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright
import egyptr41 as R

a = sys.argv[1:]
H = [os.path.abspath(x) for x in a if x.endswith('.html')]
OLD, NEW = H[0], H[1]
OUTD = next((x for x in a if not x.endswith('.html')), os.path.join(R.HERE, 'egypt_themes'))
INK = (20, 16, 24)
BW, BH, ZK = 72, 64, 3  # the crop in world px round the pit (from 44 px over its floor to 20 under) and its scale
DS = [30, 24, 20, 16, 12, 8, 4, 2, 0]
SHOW = R.SHOW.replace('fy=f.yB;', 'fy=f.yP;').replace('H.cam.gy=fy', 'H.cam.gy=f.yB')
GPU = ['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'] if os.environ.get('HK_GPU') else []


def page(b, html, mode, dsf=3):
    pg = b.new_page(viewport={'width': 852, 'height': 393}, device_scale_factor=dsf)
    pg.errs = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e)))
    pg.goto('file://' + html)
    pg.wait_for_timeout(700)
    pg.evaluate("document.querySelectorAll('.screen').forEach(e=>e.hidden=true);document.body.classList.remove('panelOpen')")
    pg.evaluate("m=>{__HK.S.set.lightMode=m;window.__NOCARD=true;}", mode)
    pg.dsf = dsf
    return pg


def shot(pg, zk=ZK):
    q = pg.evaluate(SHOW)
    im = Image.open(io.BytesIO(pg.screenshot())).convert('RGB')
    d = pg.dsf
    ox, oy, k, fx, fy = q[0] * d, q[1] * d, q[2] * d, q[3], q[4]
    x0, y0 = ox + (fx - BW / 2) * k, oy + (fy - 44) * k
    c = im.crop((int(x0), int(y0), int(x0 + BW * k), int(y0 + BH * k)))
    return c if zk is None else c.resize((BW * zk, BH * zk), Image.LANCZOS)


def seq(pg, lift):
    # him off on the landing, then the slab's last 30 px, one picture (3x, phone) per distance
    pg.evaluate(R.LOAD, lift)
    off = 'r' if pg.evaluate('__F.mo||__F.sB') > 0 else 'l'
    pg.evaluate(R.STEP, ["P.state==='lift'", '', 60])
    pg.evaluate(R.STEP, ["f.y>=f.yB-20", '', 600])
    pg.evaluate(R.STEP, ["P.state!=='lift'&&P.state!=='step'", off, 120])
    out = []
    for D in DS:
        pg.evaluate(R.STEP, ["f.y>=f.yP-%g||f.s>=2" % D if D else "f.s>=2", '', 900])
        if not D:
            pg.evaluate(R.STEP, ['false', '', 20])
        out.append((D, shot(pg), shot(pg, None), pg.evaluate('__F.yP-__F.y')))
    return out


def label(im, t):
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 8 + 6 * len(t), 13), fill=(0, 0, 0))
    d.text((4, 1), t, fill=(250, 240, 215))


if __name__ == '__main__':
    os.makedirs(OUTD, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(args=GPU)
        cols, errs = {}, []
        lifts = None
        for mt, m in R.MODES:
            for tag, html in (('old', OLD), ('new', NEW)):
                pg = page(b, html, m)
                if lifts is None:
                    lifts = [pg.evaluate(R.FIND, False), pg.evaluate(R.FIND, True)]
                    print('lifts', lifts, flush=True)
                cols[(m, tag)] = [seq(pg, lf) for lf in lifts]
                errs += [(m, tag, e) for e in pg.errs[:3]]
                pg.close()
                print('done', m, tag, flush=True)
        keys = [(m, t) for _, m in R.MODES for t in ('old', 'new')]
        names = {('classic', 'old'): 'Classic, 41d', ('classic', 'new'): 'Classic, 41e', ('torch', 'old'): 'Torchlight, 41d', ('torch', 'new'): 'Torchlight, 41e'}
        rows = []
        cw = BW * ZK
        for li, lf in enumerate(lifts):
            for i, D in enumerate(DS):
                row = Image.new('RGB', (4 * (cw + 6), 18 + BH * ZK), INK)
                got = cols[keys[0]][li][i][3]
                t = ('floor %d seed %d: ' % (lf[0], lf[1]) if i == 0 else '') + ('the slab at rest among the spikes' if not D else 'the slab\'s top %.1f px over the pit\'s floor' % got)
                ImageDraw.Draw(row).text((6, 3), t, fill=(250, 240, 215))
                for j, k in enumerate(keys):
                    c = cols[k][li][i][1].copy()
                    label(c, names[k])
                    row.paste(c, (j * (cw + 6), 18))
                rows.append(row)
        # phone size: the device pixels, every distance side by side, one strip per build and mode (first lift)
        for k in keys:
            ims = [x[2] for x in cols[k][0]]
            w, h = ims[0].size
            row = Image.new('RGB', (len(ims) * (w + 4) + 120, h + 4), INK)
            ImageDraw.Draw(row).text((4, 4), names[k] + ', phone', fill=(250, 240, 215))
            for i, im in enumerate(ims):
                row.paste(im, (120 + i * (w + 4), 2))
            rows.append(row)
        W = max(r.width for r in rows)
        sheet = Image.new('RGB', (W, sum(r.height + 4 for r in rows)), INK)
        y = 0
        for r in rows:
            sheet.paste(r, (0, y)); y += r.height + 4
        out = os.path.join(OUTD, 'r41e_spikes.png')
        sheet.save(out, optimize=True)
        print('wrote', out, sheet.size)
        # the gif: new build, the slab's last storey frame by frame (every 2nd frame), Classic | Torchlight
        fr = {}
        for mt, m in R.MODES:
            pg = page(b, NEW, m, 2)
            pg.evaluate(R.LOAD, lifts[0])
            off = 'r' if pg.evaluate('__F.mo||__F.sB') > 0 else 'l'
            pg.evaluate(R.STEP, ["P.state==='lift'", '', 60])
            pg.evaluate(R.STEP, ["f.y>=f.yB-20", '', 600])
            pg.evaluate(R.STEP, ["P.state!=='lift'&&P.state!=='step'", off, 120])
            pg.evaluate(R.STEP, ["f.y>=f.yP-40", '', 600])
            L = []
            for i in range(30):
                L.append(shot(pg))
                pg.evaluate(R.STEP, ['false', '', 2])
            fr[m] = L
            errs += [(m, 'gif', e) for e in pg.errs[:3]]
            pg.close()
        frames = []
        for a1, a2 in zip(fr['classic'], fr['torch']):
            im = Image.new('RGB', (2 * cw + 6, BH * ZK), INK)
            im.paste(a1, (0, 0)); im.paste(a2, (cw + 6, 0)); frames.append(im)
        frames += [frames[-1]] * 10
        gif = os.path.join(OUTD, 'r41e_spikes.gif')
        frames[0].save(gif, save_all=True, append_images=frames[1:], duration=66, loop=0, optimize=True)
        print('wrote', gif, len(frames), 'frames')
        if errs:
            print('errors', errs)
        b.close()
