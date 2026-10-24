# r33step.py: round 33b, the careful step's keys from motion capture (owner after v78: "the tiptoe animation: research this also against the
# PoP animation"; round 32's rule: "keep the motion capture body and borrow PoP's structure").
# The data used in this project was obtained from mocap.cs.cmu.edu. The database was created with funding from NSF EIA-0196217.
#
# Writes the block of dev/hourglass-keep.html between '// <R33-STEP>' and '// </R33-STEP>' (after round 32's; never edit it by hand): MCS,
# one stride of CMU 139_29 ("Sneaking", subject 139, the clip round 23 took PS.step from) in the game's angles, keyed evenly over the stride:
#   window   the near (right) heel's lift at f383 to its next lift at f540 (157 frames, 1.31 s; the events below are found from the feet and
#            printed: right heel-off, toe-off, contact; left heel-off, toe-off, contact). The game plays the stride as one step-to (PoP's
#            structure): the near foot's swing is the lead foot's, the far foot's swing the trailing foot's, which sets down beside the lead
#   k        the body: lean, head, aF, eF, aB, eB (from straight down, positive forward, as MCP) and round 25a's sb, soF, soB, at NK keys
#   F, B     per key, each foot: s, the ball's progress from toe-off (0) to contact (1) along the floor; c, the foot's lowest point over the
#            floor (px; each landmark over its own floor, so a flat foot is 0); fp, its pitch against the clip's flat foot (rad, + toes up)
#   hy       per key, the hip's height under the clip's standing height (f140-160), px
#   ev       the events as fractions of the stride: [toe-off R, contact R, heel-off L, toe-off L, contact L]
#   hp       the hip's progress (0..1 of its travel over the stride) at each event: the game places each event where its own hip (P.x's ease)
#            has come as far
# How the game shapes it (feet placed on the floor by two-bone IK, PoP's toe-first plant and test foot, the hip's dip) is the game's: see
# 'Round 33b' in the source.
#   python3 r33step.py          write the block and print the keys
#   python3 r33step.py events   print the feet per frame over the window (the events' evidence)
# The clip is read from BVH (bvh.py): put 139_29.bvh in ref/cmu/ (not committed) or point CMU_BVH at a checkout of the cgspeed set's GitHub
# mirror (https://github.com/una-dinosauria/cmu-mocap, data/139/139_29.bvh).
import json, math, os, sys
import numpy as np
import mocap
import r32jump as J

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', 'hourglass-keep.html')
CLIP = '139_29'
A, B = 383, 540          # the stride: right heel-off to right heel-off
STAND = (140, 160)       # standing still before the first step
NK = 21
BODY = ['lean', 'head', 'aF', 'eF', 'aB', 'eB', 'sb', 'soF', 'soB']
FT = ('ankle', 'ball', 'toe')


def setup():
    c = J.clip(CLIP)
    f = c.facing(A, B)
    Q = {i: mocap.project(c.P(i), f) for i in range(STAND[0], B + 40)}
    fl = {s + k: sorted(Q[i][k + s][1] for i in range(A, B + 1))[int((B - A) * 0.03)] for s in 'LR' for k in FT}
    flat = J.foot_flat(c, A, B, f)
    return c, f, Q, fl, flat


def clear(Q, fl, i, s):
    """the foot's lowest point over the floor (m), each landmark over its own floor"""
    return min(Q[i][k + s][1] - fl[s + k] for k in FT)


def events(Q, fl):
    """heel-off (the ankle 1.2 cm up), toe-off (the ball 1.5 cm up), contact (after the swing's top, the foot's lowest point under 1.2 cm)"""
    ev = {}
    for s in 'RL':
        i = A if s == 'R' else A + 30
        while Q[i]['ankle' + s][1] - fl[s + 'ankle'] < 0.012:
            i += 1
        ho = i
        while Q[i]['ball' + s][1] - fl[s + 'ball'] < 0.015:
            i += 1
        to = i
        pk = max(range(to, to + 70), key=lambda j: clear(Q, fl, j, s))
        i = pk
        while clear(Q, fl, i, s) >= 0.012:
            i += 1
        ev[s] = (ho, to, i)
    return ev


def build():
    c, f, Q, fl, flat = setup()
    pxm = J.PXM
    ev = events(Q, fl)
    (hoR, toR, coR), (hoL, toL, coL) = ev['R'], ev['L']
    print('events (frames): R heel-off %d toe-off %d contact %d; L heel-off %d toe-off %d contact %d; stride %d-%d' % (hoR, toR, coR, hoL, toL, coL, A, B))
    fr = lambda i: (i - A) / (B - A)
    hip0 = np.mean([(Q[i]['hipL'][1] + Q[i]['hipR'][1]) / 2 for i in range(*STAND)]) - min(fl.values())
    ballx = lambda i, s: Q[i]['ball' + s][0]
    keys, FF, FB, HY = [], [], [], []
    flb = J.floor_of(c, A, B, f) + 0.01
    for j in range(NK):
        x = A + (B - A) * j / (NK - 1)
        q = J.at(c, x, f, flat, flb)
        keys.append({k: q[k] for k in BODY})
        i = int(round(x))
        for s, out, (ho, to, co), fpk in (('R', FF, ev['R'], 'fpF'), ('L', FB, ev['L'], 'fpB')):
            x0, x1 = ballx(to, s), ballx(co, s)
            if i <= to:
                sv = 0.0
            elif i >= co:
                sv = 1.0
            else:
                sv = min(1.0, max(0.0, (ballx(i, s) - x0) / (x1 - x0)))
            out.append([round(sv, 3), round(max(0.0, clear(Q, fl, i, s)) * pxm, 2), round(q[fpk], 3)])
        hh = (Q[i]['hipL'][1] + Q[i]['hipR'][1]) / 2 - min(fl.values())
        HY.append(round((hip0 - hh) * pxm, 2))
    for k in BODY[:6]:
        for j in range(1, len(keys)):
            while keys[j][k] - keys[j - 1][k] > math.pi:
                keys[j][k] -= 2 * math.pi
            while keys[j][k] - keys[j - 1][k] < -math.pi:
                keys[j][k] += 2 * math.pi
    # closed: the stride's drift (the head 9 to 19 degrees, the shoulders' offset) spread evenly over it, so a step ends as the next begins
    for k in BODY:
        d = keys[0][k] - keys[-1][k]
        for j in range(NK):
            keys[j][k] += d * j / (NK - 1)
    d = HY[0] - HY[-1]
    HY = [round(h + d * j / (NK - 1), 2) for j, h in enumerate(HY)]
    hipx = lambda i: (Q[i]['hipL'][0] + Q[i]['hipR'][0]) / 2
    hp = lambda i: (hipx(i) - hipx(A)) / (hipx(B) - hipx(A))
    return {'k': [{k: round(float(v), 3) for k, v in q.items()} for q in keys], 'F': FF, 'B': FB, 'hy': HY,
            'ev': [round(fr(t), 3) for t in (toR, coR, hoL, toL, coL)], 'hp': [round(hp(t), 3) for t in (toR, coR, hoL, toL, coL)], 'T': round((B - A) / 120.0, 3)}


def show(M):
    d = math.degrees
    print('stride %.2f s; events (u): R toe-off %.3f contact %.3f; L heel-off %.3f toe-off %.3f contact %.3f' % ((M['T'],) + tuple(M['ev'])))
    print('the hip\'s progress over the stride at those events: %s' % M['hp'])
    for j, q in enumerate(M['k']):
        print('%4.2f ' % (j / (NK - 1)) + ' '.join('%s %4.0f' % (a, d(q[a])) for a in BODY[:7]) + ' so %+.2f %+.2f' % (q['soF'], q['soB']) +
              ' | F s %.2f c %4.1f fp %4.0f | B s %.2f c %4.1f fp %4.0f | hip -%.1f' % (M['F'][j][0], M['F'][j][1], d(M['F'][j][2]), M['B'][j][0], M['B'][j][1], d(M['B'][j][2]), M['hy'][j]))


def emit():
    M = build()
    show(M)
    blk = '\n'.join(['// <R33-STEP> generated by dev/tools/r33step.py from the CMU motion capture database (mocap.cs.cmu.edu; created with funding',
                     '// from NSF EIA-0196217): the careful step\'s keys (round 33b). Do not edit by hand: change r33step.py and run it. One stride of 139_29',
                     '// (sneaking) from the near heel\'s lift to its next, evenly keyed: k the body (angles as MCP), F and B each foot [s the ball\'s progress',
                     '// from toe-off to contact, c the lowest point over the floor (px), fp the pitch (rad)], hy the hip under standing (px), ev the events',
                     '// (R toe-off, contact, L heel-off, toe-off, contact) as fractions of the stride, hp the hip\'s progress at each.',
                     'const MCS=' + json.dumps(M, separators=(',', ':')) + ';',
                     '// </R33-STEP>'])
    s = open(SRC, encoding='utf-8').read()
    a = s.find('// <R33-STEP>')
    if a >= 0:
        b = s.find('// </R33-STEP>')
        s = s[:a] + blk + s[b + len('// </R33-STEP>'):]
    else:
        i = s.find('// </R32-JUMP>') + len('// </R32-JUMP>')
        s = s[:i] + '\n' + blk + s[i:]
    open(SRC, 'w', encoding='utf-8').write(s)
    print('wrote', SRC)


def dump():
    c, f, Q, fl, flat = setup()
    for i in range(A - 6, B + 7, 3):
        print('f%d ' % i + ' | '.join('%s ank %4.1f ball %4.1f toe %4.1f x %6.1f' % (s, (Q[i]['ankle' + s][1] - fl[s + 'ankle']) * 100, (Q[i]['ball' + s][1] - fl[s + 'ball']) * 100,
                                                                                     (Q[i]['toe' + s][1] - fl[s + 'toe']) * 100, Q[i]['ball' + s][0] * 100) for s in 'RL'))


if __name__ == '__main__':
    if sys.argv[1:] and sys.argv[1] == 'events':
        dump()
    else:
        emit()
