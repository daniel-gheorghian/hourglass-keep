# egyptr17.py [new.html] [outdir]: round 17's pictures for egypt_themes.html: the gold sparkle where the climb (ascent) or the drop
# (descent) to a secret passage's gold flask starts, in the game at the phone's resolution (crops of the 1704 px canvas):
#  r17_cue.png  an ascent and a descent in two themes, Torchlight and Classic, at 1:1 and at 2x (a smaller crop enlarged, smoothed)
#  r17_cue.gif  the ascent and the descent in Torchlight, 0.1 s a frame
# Writes r17.json (the floors used and a scan of floors 1-48 for cues found). Run from dev/tools.
import json, os, sys
from playwright.sync_api import sync_playwright
from PIL import Image
import egyptr12 as R12
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
NEW = os.path.abspath(a[0] if len(a) > 0 else os.path.join(HERE, '..', 'hourglass-keep.html'))
OUT = a[1] if len(a) > 1 else os.path.join(HERE, 'egypt_themes')
R12.OUT = OUT
FIND = r"""([lo,hi,dn,look])=>{for(let n=lo;n<=hi;n++)for(const sd of [4400+n,801,802,803,804,805,806,807,808]){const L=__P.load(n,sd);if(look&&L.theme.look!==look)continue;
  const q=__HK.secretCues()[0];if(q&&q.dn===dn&&!q.it.alc)return [n,sd,L.theme.look,L.theme.name];}return null;}"""
SCAN = r"""([lo,hi])=>{const o={floors:0,secret:0,up:0,down:0,alcove:0,none:0};for(let n=lo;n<=hi;n++){const L=__P.load(n,4400+n);o.floors++;
  const lf=L.items.find(it=>it.type==='life');if(!lf){o.none++;continue;}const q=__HK.secretCues()[0];
  if(!q){o.none++;continue;}if(q.it.alc)o.alcove++;else{o.secret++;if(q.dn)o.down++;else o.up++;}}return o;}"""
POSE = r"""([n,sd])=>{const H=__HK;const L=__P.load(n,sd),q=H.secretCues()[0];
  const r=q.dn?L.secret.r:q.it.alc?q.it.r+1:L.secret.r+1;
  __P.stand(q.dn?Math.floor((q.x-q.s*40)/32):(q.s>0?Math.floor(q.x/32)+1:Math.floor(q.x/32)-2),r,q.dn?q.s:-q.s);H.tick(30);__P.draw();
  return [__P.scr(q.x,q.ys-6),q.dn];}"""
STEP = r"""()=>{const H=__HK;H.tick(6);H.banner=null;__P.draw();}"""


def up(im, k=2):
    return im.resize((im.width * k, im.height * k), Image.LANCZOS)


if __name__ == '__main__':
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
        P = {m: R12.page(b, NEW, m) for m in ('torch', 'classic')}
        pt = P['torch']
        scan = pt.evaluate(SCAN, [1, 48])
        cases = []
        for look in ('nun', 'west'):
            for dn in (False, True):
                f = pt.evaluate(FIND, [3, 60, dn, look])
                if f: cases.append(f + [dn])
        print('cases', cases, 'scan', scan)
        tiles1, tiles2 = [], []
        for n, sd, look, name, dn in cases:
            for m in ('torch', 'classic'):
                pg = P[m]
                xy, _ = pg.evaluate(POSE, [n, sd])
                im = R12.shot(pg)
                lab = '%s, floor %d, %s, %s' % (name, n, 'descent' if dn else 'ascent', m)
                tiles1.append(R12.label(R12.crop(im, (xy[0], xy[1] - 20), 360, 240), lab + ', 1:1'))
                tiles2.append(R12.label(up(R12.crop(im, xy, 180, 120)), lab + ', 2x'))
        R12.stack([R12.grid(tiles1, 4), R12.grid(tiles2, 4)]).save(os.path.join(OUT, 'r17_cue.png'))
        sel = [c for c in cases if c[2] == 'nun'][:2] or cases[:2]
        cols = []
        for n, sd, look, name, dn in sel:
            xy = pt.evaluate(POSE, [n, sd])[0]; fr = []
            for k in range(26):
                pt.evaluate(STEP)
                fr.append(R12.label(R12.crop(R12.shot(pt), xy, 300, 200), '%s %s' % (name, 'descent' if dn else 'ascent')))
            cols.append(fr)
        frames = [R12.grid([c[k] for c in cols], len(cols)).convert('P', palette=Image.ADAPTIVE, colors=200) for k in range(26)]
        R12.gif(frames, 'r17_cue.gif', 100)
        errs = P['torch'].errs + P['classic'].errs
        json.dump({'cases': cases, 'scan': scan, 'errors': errs[:5]}, open(os.path.join(OUT, 'r17.json'), 'w'), indent=1)
        print('errors', errs[:5])
        b.close()
