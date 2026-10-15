# vreplay.py: shots and strips taken from replayed bot runs (see vlib.js V.scan / V.replayInit).
# Plan every shot first (episodes come from cached scans), then replay each run once, capturing at ascending frames.
import os
from vlib import OUT


class Planner:
    def __init__(self, rig, floors, fights, limit=60 * 600):
        self.rig = rig
        self.scans = {}
        for fight, lst in ((False, floors), (True, fights)):
            for n, sd in lst:
                r = rig.scan(n, sd, fight, limit=limit)
                print('scan', n, sd, 'fight' if fight else '', r['res'].get('ok'), r['frames'], r.get('secs'))
                self.scans[(n, sd, fight)] = r
        self.jobs = {}
        self.plan = []

    def eps(self, tag, minlen=0, prefer_fight=None, nth=0, skip_keys=()):
        c = []
        for key, r in self.scans.items():
            if key in skip_keys:
                continue
            for e in r['eps'].get(tag, []):
                c.append((key, e))
        if not c:
            return None
        c.sort(key=lambda x: (-(x[1]['f1'] - x[1]['f0'] >= minlen), (x[0][2] != prefer_fight) if prefer_fight is not None else 0, x[0][0]))
        return c[min(nth, len(c) - 1)]

    def _add(self, key, **cap):
        self.jobs.setdefault(key, []).append(cap)

    def shot(self, sid, tag, what, topic, sheet=None, closeup_sheet=None, modes=('torch',), minlen=6, prefer_fight=None, nth=0, at=0.5, full=True, close=True):
        rig = self.rig
        if not rig.want(sid):
            return
        c = self.eps(tag, minlen, prefer_fight, nth)
        if not c:
            print('NO EPISODE', tag); rig.missing.append(sid); return
        (n, sd, fight), e = c
        mid = e['f0'] + max(1, int((e['f1'] - e['f0']) * at))
        outf, outc = [], []
        if full:
            self._add((n, sd, fight), frame=mid, modes=modes, clip=None, out=outf)
        if close:
            self._add((n, sd, fight), frame=mid, modes=('torch',), clip=(70, 95, 22), out=outc)
        self.plan.append(('shot', sid, what, topic, sheet, closeup_sheet, tag, n, sd, fight, outf, outc, mid))

    def strip(self, sid, tag, what, topic, sheet, pre, post, cnt, cap=0, minlen=6, prefer_fight=None, nth=0, crop=(60, 85, 20), modes=('torch',)):
        rig = self.rig
        if not rig.want(sid):
            return
        c = self.eps(tag, minlen, prefer_fight, nth)
        if not c:
            print('NO EPISODE', tag); rig.missing.append(sid); return
        (n, sd, fight), e = c
        f0, f1 = e['f0'] - pre, e['f1'] + post
        if cap and f1 - f0 > cap:
            f1 = f0 + cap
        f0 = max(1, f0)
        frames = [int(round(f0 + (f1 - f0) * i / (cnt - 1))) for i in range(cnt)]
        outs = []
        for fr in frames:
            o = []
            self._add((n, sd, fight), frame=fr, modes=('torch',), clip=crop, out=o)
            outs.append((fr, o))
        self.plan.append(('strip', sid, what, topic, sheet, tag, n, sd, fight, outs, f0))

    def execute(self):
        rig = self.rig
        for (n, sd, fight), caps in self.jobs.items():
            rig.replay_pass(n, sd, fight, self.scans[(n, sd, fight)]['rec'], caps)
            print('pass', n, sd, fight, len(caps))
        for p in self.plan:
            if p[0] == 'shot':
                _, sid, what, topic, sheet, csheet, tag, n, sd, fight, outf, outc, mid = p
                repro = 'cd dev/tools && python3 vshots.py %s %s' % (rig.group, sid)
                src = 'replayed bot run: floor %d seed %d frame %d, %s' % (n, sd, mid, 'fight mode' if fight else 'no-fight')
                for png, m, meta in outf:
                    fn = 'shots/%s-%s.png' % (sid, m)
                    open(os.path.join(OUT, fn), 'wb').write(png)
                    rig.add(id='%s-%s' % (sid, m), file=fn, topic=topic, sheet=sheet, what='%s (state %s; %s).' % (what, tag, src), repro=repro, closeup=False, label=sid, kind='shot', **meta)
                for png, m, meta in outc:
                    fn = 'shots/%sC-%s.png' % (sid, m)
                    open(os.path.join(OUT, fn), 'wb').write(png)
                    rig.add(id='%sC-%s' % (sid, m), file=fn, topic=topic, sheet=csheet, what='Closeup (clean art): %s (%s).' % (what, src), repro=repro, closeup=True, label=sid, kind='shot', **meta)
            else:
                _, sid, what, topic, sheet, tag, n, sd, fight, outs, f0 = p
                frames = [(o[0][0], '%+.2fs' % ((fr - f0) / 60)) for fr, o in outs]
                meta = outs[0][1][0][2]
                rig.strip(sid, '%s (%s; bot run floor %d seed %d from frame %d, %s; clean-art closeup round the prince).' % (what, tag, n, sd, f0, 'fight mode' if fight else 'no-fight'),
                          topic, sheet, frames, 'torch', dict(floor=meta['floor'], seed=meta['seed'], theme=meta['theme'], style=meta['style'], state=meta['state']))


def _at(self, sid, n, sd, fight, frac, what, topic, sheet, modes=('torch',)):
    rig = self.rig
    if not rig.want(sid):
        return
    r = self.scans.get((n, sd, fight))
    if not r:
        return
    fr = max(5, int(r['frames'] * frac))
    out = []
    self._add((n, sd, fight), frame=fr, modes=modes, clip=None, out=out)
    self.plan.append(('shot', sid, what, topic, sheet, None, 'typical play', n, sd, fight, out, [], fr))


Planner.at = _at
