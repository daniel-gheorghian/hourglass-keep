# r32jump.py: round 32, the jumps' keys from motion capture (owner: "The current one is too stiff too mechanical"; after the research:
# "Do everything; keep the motion capture body and borrow PoP's structure").
# The data used in this project was obtained from mocap.cs.cmu.edu. The database was created with funding from NSF EIA-0196217.
#
# Writes the block of dev/hourglass-keep.html between '// <R32-JUMP>' and '// </R32-JUMP>' (after round 23's block; never edit either by
# hand): MCJ, keyed sequences in the game's angles (skel: from straight down, positive forward; extras sb, soF/soB, fpF/fpB as round 25a;
# cl the lowest foot's clearance over the floor, px, as the run's keys), measured in the side view of the body's own facing:
#   tk   127_21 f56-81   run, jump, stop, run (subject 127): the take-off foot's stance, from its strike to toe-off: the gather (tall
#                        and narrow, the free knee folded under him at f62-68) and the push-off (the free knee driven up to 79 degrees,
#                        the take-off leg straightening behind) -- PoP1's frames 38 and 39 (SDLPoP seqtbl.c runjump)
#   D    127_21 f81-129  the flight of that running long jump, toe-off to the lead foot's strike: the split, the far arm forward and up,
#                        the near arm back against the lead leg (the arms opposed, as a runner's), the trunk from 12 degrees forward to 13
#                        back as the lead leg reaches for the floor
#   rl   127_21 f129-177 its landing: the lead foot strikes, the trail foot comes down 0.1 s later, the knees take him down and he rises
#   sw   13_11 f150-240  the standing (forward) jump's wind-up: both arms swing back (fullest f178-186), the knees sink (deepest f214),
#                        the arms swing through and the legs drive him off (toe-off f240)
#   sf   13_11 f240-289  its flight, toe-off to the strike
#   sl   13_11 f289-349  its landing: down to f310 (the hip 0.19 m under standing), up again by f350
#   Dlow, sfLow          D and sf pitched forward by round 23's low-leap rule (the crown no higher than PS.jumpLow's / PS.jumpLowS's)
# Each sequence: u 0..1 keys (tk, D, sf: evenly over the span) or [t, key] (rl, sw, sl: t seconds from the span's first frame).
# How the game plays them (timing, the dive, the squash) is the game's: see 'Round 32' in the source.
#   python3 r32jump.py          write the block and print the keys
#   python3 r32jump.py check    compare this reader with round 23's MCP (the same frames of 13_11, 49_04, 16_05)
# The clips are read from BVH (bvh.py; mocap.cs.cmu.edu was out of reach in round 32, the cgspeed BVH set is mirrored on GitHub).
import json, math, os, re, sys
import numpy as np
import mocap, bvh

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', 'hourglass-keep.html')
ANG = ['lean', 'head', 'aF', 'eF', 'aB', 'eB', 'hF', 'kF', 'hB', 'kB']
X25 = ['sb', 'soF', 'soB', 'fpF', 'fpB']
PXM = json.load(open(os.path.join(HERE, 'r23body.json')))['info']['leg_scale'] * 100   # px a metre (round 23's legs' scale)
CL = {}


def clip(n):
    if n not in CL:
        CL[n] = bvh.Clip(n)
    return CL[n]


def pitch_of(R3, fwd):
    u = R3 @ np.array([0, 1.0, 0])
    return math.atan2(float(u @ fwd), float(u[1]))


def floor_of(c, a, b, f):
    return min(min(mocap.project(c.P(i), f)[k][1] for k in ('ankleL', 'ankleR', 'ballL', 'ballR', 'toeL', 'toeR')) for i in range(a, b + 1))


def foot_flat(c, a, b, f):
    out = []
    Qs = [mocap.project(c.P(i), f) for i in range(a, b + 1)]
    for s in 'LR':
        amin = min(q['ankle' + s][1] for q in Qs)
        bmin = min(q['ball' + s][1] for q in Qs)
        for q in Qs:
            if q['ankle' + s][1] < amin + 0.015 and q['ball' + s][1] < bmin + 0.015:
                out.append(math.atan2(q['ball' + s][1] - q['ankle' + s][1], q['ball' + s][0] - q['ankle' + s][0]))
    return float(np.median(out))


def one(c, i, f, flat, fl):
    P = c.P(i)
    Q = mocap.project(P, f)
    p = mocap.params(Q, 'r')
    R = P['_R']
    sm = (Q['shL'][0] + Q['shR'][0]) / 2
    q = {k: p[k] for k in ANG}
    q.update({'sb': pitch_of(R['Spine1'], f) - pitch_of(R['Hips'], f), 'soF': (Q['shR'][0] - sm) * PXM, 'soB': (Q['shL'][0] - sm) * PXM,
              'fpF': p['ftF'] - flat, 'fpB': p['ftB'] - flat,
              'cl': max(0.0, min(Q[k][1] for k in ('ankleL', 'ankleR', 'ballL', 'ballR', 'toeL', 'toeR')) - fl) * PXM})
    return q


def at(c, x, f, flat, fl):
    a = int(math.floor(x))
    u = x - a
    A, B = one(c, a, f, flat, fl), one(c, a + 1, f, flat, fl)
    return {k: A[k] + (B[k] - A[k]) * u for k in A}


def unwrap(keys):
    for k in ANG:
        for j in range(1, len(keys)):
            while keys[j][k] - keys[j - 1][k] > math.pi:
                keys[j][k] -= 2 * math.pi
            while keys[j][k] - keys[j - 1][k] < -math.pi:
                keys[j][k] += 2 * math.pi
    return keys


def rnd(q):
    return {k: round(float(v), 3) for k, v in q.items()}


# clip, span for the side view and the floor, the frames where the feet are flat (the foot's pitch)
CLIPS = {'127_21': ((40, 200), (150, 200)), '13_11': ((150, 350), (130, 160))}


def setup(n):
    c = clip(n)
    span, flat = CLIPS[n]
    f = c.facing(*span)
    fl = floor_of(c, span[0], span[1], f) + 0.01
    return c, f, foot_flat(c, flat[0], flat[1], f), fl


def even(n, a, b, k):
    c, f, flat, fl = setup(n)
    return unwrap([at(c, a + (b - a) * j / (k - 1), f, flat, fl) for j in range(k)])


def timed(n, a, b, step):
    c, f, flat, fl = setup(n)
    ks = unwrap([one(c, i, f, flat, fl) for i in range(a, b + 1, step)])
    return [[round((i - a) / 120.0, 4), q] for i, q in zip(range(a, b + 1, step), ks)]


def src_consts():
    s = open(SRC, encoding='utf-8').read()
    B = json.loads(re.search(r'const R23B=(\{[^;]*\});', s).group(1))
    m = re.search(r'const MCP=(\{.*?\});\n', s).group(1)
    return s, B, json.loads(m)


def crown(B, l, h):
    a = l + h
    return B['to'] * math.cos(l) + (B['nk'] + B['hd']) * math.cos(a) + 1.25 * B['hd'] * abs(math.cos(a))


def low(B, ks, ref):
    """round 23's low-leap rule: the trunk pitched forward until the head's top over the hip is no higher than ref's"""
    lim = crown(B, ref['lean'], ref['head'])
    out = []
    for q in ks:
        r = dict(q)
        l = r['lean']
        while crown(B, l, r['head']) > lim and l < 1.4:
            l += 0.02
        r['lean'] = l
        out.append(r)
    return out


def check():
    _, B, MCP = src_consts()
    for name, n, i, w in (('jumpCrouch', '13_11', 196, 2), ('jumpS', '13_11', 252, 2), ('jumpR', '49_04', 176, 1), ('land', '16_05', 203, 2)):
        c = clip(n)
        f = c.facing(max(0, i - 30), min(c.n - 1, i + 30))
        acc = {k: 0.0 for k in ANG}
        for j in range(i - w, i + w + 1):
            p = mocap.params(mocap.project(c.P(j), f), 'r')
            for k in ANG:
                acc[k] += p[k] / (2 * w + 1)
        print('%-10s %s f%d  ' % (name, n, i) + ' '.join('%s %+.1f' % (k, math.degrees(acc[k] - MCP[name][k])) for k in ANG), '(deg, BVH less round 23)')


def build():
    s, B, MCP = src_consts()
    J = {}
    J['tk'] = [rnd(q) for q in even('127_21', 56, 81, 7)]
    D = even('127_21', 81, 129, 9)
    J['D'] = [rnd(q) for q in D]
    J['Dlow'] = [rnd(q) for q in low(B, D, MCP['jumpLow'])]
    J['rl'] = [[t, rnd(q)] for t, q in timed('127_21', 129, 177, 4)]
    J['sw'] = [[t, rnd(q)] for t, q in timed('13_11', 150, 240, 6)]
    sf = even('13_11', 240, 289, 9)
    J['sf'] = [rnd(q) for q in sf]
    J['sfLow'] = [rnd(q) for q in low(B, sf, MCP['jumpLowS'])]
    J['sl'] = [[t, rnd(q)] for t, q in timed('13_11', 289, 349, 4)]
    return s, J


def show(J):
    d = math.degrees
    for k, ks in J.items():
        print('==', k)
        for j, q in enumerate(ks):
            t = None
            if isinstance(q, list):
                t, q = q
            print(('%5.3f ' % t if t is not None else '%5d ' % j) + ' '.join('%s %4.0f' % (a, d(q[a])) for a in ANG) +
                  '  sb %3.0f so %+.2f %+.2f fp %4.0f %4.0f cl %4.1f' % (d(q['sb']), q['soF'], q['soB'], d(q['fpF']), d(q['fpB']), q['cl']))


def emit():
    s, J = build()
    show(J)
    blk = '\n'.join(['// <R32-JUMP> generated by dev/tools/r32jump.py from the CMU motion capture database (mocap.cs.cmu.edu; created with funding',
                     '// from NSF EIA-0196217): the jumps\' keys (round 32). Do not edit by hand: change r32jump.py and run it. tk, D, rl: 127_21 (run, jump:',
                     '// the take-off stance, the flight, the landing); sw, sf, sl: 13_11 (forward jump: wind-up, flight, landing); Dlow, sfLow: pitched',
                     '// forward for a ceiling at his height. Angles as MCP; cl the lowest foot over the floor (px); rl, sw, sl: [s from the first frame, key].',
                     'const MCJ=' + json.dumps(J, separators=(',', ':')) + ';',
                     '// </R32-JUMP>'])
    a = s.find('// <R32-JUMP>')
    if a >= 0:
        b = s.find('// </R32-JUMP>')
        s = s[:a] + blk + s[b + len('// </R32-JUMP>'):]
    else:
        i = s.find('// </R23-MOCAP>') + len('// </R23-MOCAP>')
        s = s[:i] + '\n' + blk + s[i:]
    open(SRC, 'w', encoding='utf-8').write(s)
    print('wrote', SRC)


if __name__ == '__main__':
    if sys.argv[1:] and sys.argv[1] == 'check':
        check()
    else:
        emit()
