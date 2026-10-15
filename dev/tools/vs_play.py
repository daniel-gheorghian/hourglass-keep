# Side passages, galleries and cellars, forks (in play and as overviews), and typical play per floor band.
import json, base64, os
from vreplay import Planner
from vlib import OUT
D = lambda t, ex=None, w=3: "return V.dynSpot(L,%s,%s,%d)" % (json.dumps(t), json.dumps(ex) if ex else 'null', w)
BANDS = [('b1', [(1, 7, False), (2, 7, True), (4, 7, False), (5, 7, True)]), ('b2', [(6, 7, False), (8, 7, True), (10, 7, False), (12, 7, True)]),
         ('b3', [(13, 7, False), (15, 7, True), (17, 7, False), (19, 7, True)]), ('b4', [(21, 7, False), (23, 7, True), (26, 7, False), (30, 7, True)])]


def overview(rig, sid, what, topic, sheet, n, seed0, pred, tries=80):
    """pred returns {c0,c1,r0,r1} (tiles) for the picture; drawn from the room caches, clean art (no HUD)."""
    if not rig.want(sid):
        return
    r = None
    for nn in (n if isinstance(n, list) else [n]):
        r = rig.find(nn, seed0, pred, tries, False)
        if r:
            break
    if not r:
        print('NOT FOUND', sid); rig.missing.append(sid); return
    b = r['spot']
    u = rig.ev('([b])=>V.overview(b.c0,b.c1,b.r0,b.r1,1.5)', [b])
    fn = 'shots/%s.png' % sid
    open(os.path.join(OUT, fn), 'wb').write(base64.b64decode(u.split(',')[1]))
    meta = rig.meta()
    rig.add(id=sid, file=fn, topic=topic, sheet=sheet, what=what + ' (overview picture, clean art: rooms and moving parts, no HUD, prince not drawn).', repro='cd dev/tools && python3 vshots.py play ' + sid, closeup=True,
            label=sid, kind='shot', **meta)
    print('ok', sid, n, r['seed'])


def run(rig):
    S = rig.scene
    # side passages, galleries, cellars: the plate's place
    for i, (th, n) in enumerate((('palace', 8), ('tile', 12), ('crypt', 20))):
        S('Q-gallery-' + th, n, 14000 + i * 30, D('plate', "o.f.where==='above'&&!o.f.chain", 2), 'The plate of a gate sits in a gallery above (%s): prince beside the gallery plate.' % th, 'passages', 'passage-gallery', tries=200, modes=('torch',))
        S('Q-cellar-' + th, n, 14100 + i * 30, D('plate', "o.f.where==='below'&&!o.f.chain", 2), 'The plate of a gate sits in a cellar below (%s).' % th, 'passages', 'passage-gallery', tries=200, modes=('torch',))
        S('Q-further-' + th, n, 14200 + i * 30, D('plate', "o.f.where==='further on'", 2), 'The plate lies further on, with a guard to pass (%s).' % th, 'passages', 'passage-gallery', tries=200, modes=('torch',))
        S('Q-gateat-' + th, n, 14000 + i * 30, D('gate', "o.f.far&&o.f.latch&&o.f.pair===undefined", 3), 'The matching shut gate in the main corridor (%s).' % th, 'passages', 'passage-gallery', tries=200, modes=('torch',))
    for i, (th, n) in enumerate((('palace', 8), ('crypt', 20))):
        S('Q-chainplate-' + th, n, 14300 + i * 30, D('plate', "o.f.chain", 2), 'A plate reached by a chain of loose stones (%s).' % th, 'passages', 'passage-gallery', tries=200, modes=('torch',))
    # forks: in play at the fork top, and overviews
    for kd in (1, 2, 3, 4):
        S('Q-fork%d' % kd, [6, 9, 12, 15, 18], 14400 + kd * 40, "const q=L.forks.find(q=>q.v===%d&&V.near(q.H,q.rUp,3));return q&&V.near(q.H,q.rUp,3)" % kd, 'Fork kind %d, standing at its top (the hole / the way on).' % kd, 'forks', 'forks-play',
          tries=120, modes=('torch', 'classic') if kd == 4 else ('torch',))
        overview(rig, 'Q-forkview-%d' % kd, 'Fork kind %d seen whole (the short way below the long run).' % kd, 'forks', 'forks-view', [6, 9, 12, 15, 18], 14500 + kd * 40,
                 "const q=L.forks.find(q=>q.v===%d);if(!q)return null;return {c0:Math.min(q.H,q.Xl)-4,c1:Math.max(q.H,q.Xl)+5,r0:q.rUp-1,r1:q.rLow+1}" % kd, 120) if False else None
    for kd, flr in ((1, 7), (2, 7), (3, 10), (4, 9), (4, 12)):
        overview(rig, 'Q-forkview-%d-%d' % (kd, flr), 'Fork kind %d seen whole (floor %d).' % (kd, flr), 'forks', 'forks-view', flr, 14500 + kd * 40,
                 "const q=L.forks.find(q=>q.v===%d);if(!q)return null;return {c0:Math.min(q.H,q.Xl)-4,c1:Math.max(q.H,q.Xl)+5,r0:q.rUp-1,r1:q.rLow+1}" % kd, 150)
    # chambers whole
    for kind in ('collapse', 'jumpup', 'jumpdown', 'hgap', 'shaft2', 'up', 'down', 'drop2', 'lift2d', 'chn'):
        for th, flr in (('dungeon', [22, 23, 24, 21]), ('tile', [12, 11, 10, 9]), ('crypt', [20, 19, 18, 17])):
            overview(rig, 'Q-chamberview-%s-%s' % (kind, th), 'A two-column chamber with %s seen whole (%s).' % (kind, th), 'chambers', 'chambers-view', flr, 14800,
                     "const G=L.segs.find(q=>q.k.startsWith('turn-%s'));if(!G)return null;const gs=L.segs.filter(q=>q.k.startsWith('turn-')&&Math.abs(q.c0-G.c0)<=3&&Math.abs(q.r0-G.r0)<=4);let c0=1e9,c1=-1e9,r0=1e9,r1=-1e9;for(const q of gs){c0=Math.min(c0,q.c0,q.c1);c1=Math.max(c1,q.c0,q.c1);r0=Math.min(r0,q.r0,q.r1);r1=Math.max(r1,q.r0,q.r1)}return {c0:c0-4,c1:c1+5,r0:r0-1,r1:r1+1}" % kind, 150)
    # typical play
    P = Planner(rig, [(n, sd) for _, lst in BANDS for n, sd, f in lst if not f], [(n, sd) for _, lst in BANDS for n, sd, f in lst if f])
    for band, lst in BANDS:
        for n, sd, f in lst:
            for j, fr in enumerate((0.33, 0.68)):
                P.at('Y-%s-f%d-%d' % (band, n, j + 1), n, sd, f, fr + (0.04 * (n % 3)), 'Typical play, floor %d (%s), %.0f%% through the bot run.' % (n, 'bot fights guards' if f else 'bot does not fight', 100 * fr), 'typical play', 'typical-' + band)
    P.execute()
