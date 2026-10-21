# r23poses.py: round 23, the prince's body and poses from motion capture (owner: "Start from those clips and build the athletic teen prince
# body and scrap the current skeleton and proportions so that we don't get swayed in the wrong direction").
# The data used in this project was obtained from mocap.cs.cmu.edu. The database was created with funding from NSF EIA-0196217.
#
# It reads the CMU clips (mocap.py: ASF/AMC, forward kinematics, the side view), ANSUR II (the lean 17-20 year old men) and v69's contacts
# (r23grips.json: where a hand holds something), and writes the generated block of dev/hourglass-keep.html between the markers
# '// <R23-MOCAP>' and '// </R23-MOCAP>': the body (R23B: bone lengths and the drawing's widths) and every pose (MCP: single poses, and
# keyed cycles: the run, the walk, the stairs, the swing, the drink, the crawl, the climb). Each pose is the game's angles (skel: from
# straight down, positive forward) measured from one clip frame (or a short average) in the side view of the body's own facing;
# the flags that place a pose in the game (air, hy, hold, hb, mh, sw, kn) and the held hands are v69's, unchanged.
#   python3 r23poses.py          write the block, print the table of sources
#   python3 r23poses.py strips   also draw r23_moves' mocap strips (see egyptr23.py)
import json, math, os, re, sys, csv, statistics as st
import numpy as np
import mocap

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', 'hourglass-keep.html')
ANG = ['lean', 'head', 'aF', 'eF', 'aB', 'eB', 'hF', 'kF', 'hB', 'kB']

# ---------------- the body ----------------
# ANSUR II, men aged 17 to 20: the lean ones (BMI under 23, n=124) for the trunk's depths and lengths, all 422 for the limbs' girths and
# the chest (an athlete's muscle on a lean frame), medians in mm
def ansur():
    R = [r for r in csv.DictReader(open(os.path.join(HERE, 'ref', 'ansur2_ergonomics.csv'))) if r.get('gender') == 'Male' and 17 <= int(r['age']) <= 20]
    lean = [r for r in R if float(r['weightkg']) / 10 / ((float(r['stature']) / 1000) ** 2) < 23.0]
    med = lambda k, S=lean: st.median(float(r[k]) for r in S)
    return {k: med(k) for k in ('stature', 'cervicaleheight', 'suprasternaleheight', 'acromialheight', 'trochanterionheight', 'lateralmalleolusheight',
                                 'chestdepth', 'waistdepth', 'buttockdepth', 'neckcircumference', 'neckcircumferencebase', 'thighcircumference',
                                 'lowerthighcircumference', 'calfcircumference', 'anklecircumference', 'bicepscircumferenceflexed',
                                 'forearmcircumferenceflexed', 'wristcircumference', 'handlength', 'footlength')} | {'n': len(lean),
            'chestdepth_all': med('chestdepth', R)} | {k + '_all': med(k, R) for k in ('thighcircumference', 'lowerthighcircumference',
            'calfcircumference', 'bicepscircumferenceflexed', 'forearmcircumferenceflexed', 'chestdepth')}

SUBJ = ['09', '13', '14', '16']  # the run, jump-up and jump subjects: the clips most of the moves come from
HEADS = 6.5      # the figure's height in heads (see FIGURE_SPEC.md: the decision)
TALL = 50.9      # the skeleton's height for the head's scale; drawn standing (sole's lowest pixel to the hair's) it is 52.5, v69's 53.0 (the
                 # run's flight lifts him 2.6 px: its crown stays under v69's standing crown)
SOLE = 1.6       # the drawn figure's height over TALL: the sole's lowest pixel under the floor line and the hair over the skull
HEAD_R = 2.40    # the drawn head (chin to the hair's crown) in head radii (LEN.hd), as measured on the drawing (egyptr23.py body)
NECK_CUT = 1.0   # round 23d (owner, after 23c: "Too short, one pixel longer"; 23c cut 2.0); round 23c (owner: "1.28 is fine. Now make the neck 2px shorter and keep everything else as is"): the chin, and the whole
                 # head with it, sits this much nearer the shoulder joint than ANSUR's span (4.0 px, now 2.0); the body under the chin (the
                 # pit of the neck, C7, the trapezius, every width), the bones, poses, grips and hit boxes are unchanged
KM_DROP = 0.5    # round 23d: the nape point (NJ.km) comes down this much, half the cut: between round 23b's place (0.6 px over the chin, which
                 # would now be 3.61, 0.15 px over C7: too near to fold) and round 23c's (4.61, unmoved), so the back of the neck shows a little under
                 # the skull again with no fold (see FIGURE_SPEC.md, round 23d)


# ---------------- muscle bulk (round 23b) ----------------
# Owner: "Yeah needs to be bulkier. Add a bulk multiplier, but in the sense of more muscle. Give me three variants of him with the current size
# then more and more bulky". MUS is the upper arm's girth over round 23's (ANSUR II's median, 1.0); every other measure grows at its own rate
# per unit of the upper arm's (GROW), from ANSUR II's men aged 17 to 20 with a waist under the median share of the chest (lean, n=211),
# ranked by their limb and chest girths for stature: the ratios of the 97th to the 50th percentile group (see FIGURE_SPEC.md, round 23b).
# The joints (elbow, wrist, knee, ankle), the bones and the skeleton never change; the waist barely (no fat).
MUS = 1.65       # the game's level (round 24, owner after v70: "Still too lean: make it bulkier"): the middle of three stylised levels beyond the
                 # natural near-limit; round 23c-23d drew 1.28, round 23b 1.0. The levels (window.__MUS or __HK.setMus can pick one at run time):
LEVELS = [(1.0, 'round 23: ANSUR II medians, men 17-20'),
          (1.10, 'athletic: ANSUR II ~90th percentile of muscle among the lean, the frame taken out'),
          (1.18, 'strong: ANSUR II top 3-5% of the lean; a sprinter or gymnast (mesomorphy ~6)'),
          (1.28, 'natural near-limit: between McCallum\'s and Reeves\'s ratios (arm 1.21-1.31), FFMI ~24-25 (v70)'),
          (1.45, 'heroic 1 (round 24): a classical statue / Disney Hercules young hero; one step past v70'),
          (1.65, 'heroic 2 (round 24, the game): comic-book hero build, broad deltoids and lats, thick forearms and calves, narrow waist'),
          (1.85, 'heroic 3 (round 24): the bulkiest still agile; past it the arms meet the trunk (God of War territory)')]
NAT = 1.28       # round 24: up to the natural near-limit the measured rates (GROW); past it the stylised rates (GROW2), so 1.28 is v70's to the pixel
GROW = {'arm': 1.0, 'fore': 0.55, 'delt': 1.2, 'armLo': 0.85, 'thigh': 0.7, 'thighM': 0.7, 'lthigh': 0.6, 'calf': 0.55, 'soleus': 0.45,
        'neck': 0.55, 'neckB': 0.5, 'trap': 0.9, 'chest': 0.8, 'lowch': 0.75, 'seat': 0.6, 'waist': 0.12}
# round 24, the stylised range (per unit of the upper arm's growth past NAT): what comics and games enlarge on a heroic figure (Loomis's and
# Hampton's ideal: shoulders wider, deltoid caps, lats, a deep chest, forearms and calves as thick as the arm's rate, the waist held for the
# V-taper; see FIGURE_SPEC.md, round 24). Small sprites read bulk in the silhouette: every visible width must grow by ~0.6 px or more a level.
GROW2 = {'arm': 1.0, 'fore': 1.15, 'delt': 1.2, 'armLo': 1.0, 'thigh': 0.8, 'thighM': 0.8, 'lthigh': 0.75, 'calf': 0.95, 'soleus': 0.7,
         'neck': 0.6, 'neckB': 0.55, 'trap': 1.0, 'chest': 0.85, 'lowch': 1.0, 'seat': 0.6, 'waist': 0.06}
ROB_MUS = 1.28   # round 24: the robbers keep v70's widths (1.15 times the prince's at 1.28) whatever the prince's level
# the trunk's levels (U = 0 .14 .3 .46 .62 .76 .88 .96 1 from the hip joint to the shoulder joint): which measure grows there and the share of
# its growth in front (pectorals, the abdominal wall) against behind (glutes, lats, rhomboids and the trapezius)
TRUNK_G = [('seat', 0.15), ('seat', 0.2), ('waist', 0.5), ('waist', 0.5), ('lowch', 0.3), ('chest', 0.45), ('chest', 0.55), ('chest', 0.45), ('trap', 0.35)]
# round 24: the growth past NAT lays more of the upper back behind (rhomboids, the upper trapezius, teres: the back's line fills out from the
# nape to the lats as one slope; with TRUNK_G's shares a big rear deltoid stood out of a flat upper back as a step)
TRUNK_G2 = [('seat', 0.15), ('seat', 0.2), ('waist', 0.5), ('waist', 0.5), ('lowch', 0.4), ('chest', 0.3), ('chest', 0.35), ('chest', 0.3), ('trap', 0.25)]
MH = 0.6         # the muscle contour hints' strength at NAT (none at 1.0)
MH2 = 0.25       # round 24: and how much more by the last level (0.85 at 1.85)
DU = 0.1         # round 24: how far down the humerus the biceps' point (0.22 up to NAT) moves by the last level: the big deltoid tapers
# (cb: the calf's growth is laid behind the shank, the gastrocnemius' bulge; the shin's line stays)

def body():
    A = ansur()
    bl = {n: st.mean(mocap.Skel(os.path.join(mocap.REF, s + '.asf')).length_cm(n) for s in SUBJ) for n in
          ('lfemur', 'ltibia', 'lhumerus', 'lradius', 'lowerback', 'upperback', 'thorax')}
    # the shoulder joint over the hip joint in the subjects' rest pose (clavicle's end over the femur's head), cm
    tr = []
    for s in SUBJ:
        sk = mocap.Skel(os.path.join(mocap.REF, s + '.asf'))
        J = mocap.landmarks(mocap.fk(sk, {'root': [0, 0, 0, 0, 0, 0]}))
        tr.append((J['shL'][1] + J['shR'][1]) / 2 * 100 - (J['hipL'][1] + J['hipR'][1]) / 2 * 100)
    trunk = st.mean(tr)
    headH = (TALL + SOLE) / HEADS                         # chin to crown, px: a 6.5th of the height as drawn
    chin = A['stature'] - 228.0                            # mm (head height 228 mm: 0.13 of stature, Drillis & Contini)
    k = (TALL - headH) / chin                              # px per mm below the chin
    hip = A['trochanterionheight'] * k                     # the hip joint's height (the trochanter's top is level with it)
    s_leg = hip / (bl['lfemur'] + bl['ltibia'] + A['lateralmalleolusheight'] / 10)   # the legs: the subjects' thigh and shank, to the floor
    th = bl['lfemur'] * s_leg
    sh = hip - th
    to = trunk * s_leg
    jc = (chin - A['acromialheight'] + 40.0) * k           # shoulder joint to chin (the joint 40 mm under the acromion)
    hd = headH / HEAD_R
    nk = jc - NECK_CUT + 1.15 * hd - hd                    # skel: the head's centre nk+hd from the joint; the chin 1.15 r under it (round 23c: 2 px lower)
    ua = bl['lhumerus'] * s_leg
    fa = (bl['lradius'] + 0.4 * A['handlength'] / 10) * s_leg   # to the middle of the palm
    W = lambda mm: mm * k
    dia = lambda circ: circ / math.pi * k
    B = {'th': th, 'sh': sh, 'to': to, 'nk': nk, 'hd': hd, 'ua': ua, 'fa': fa}
    wid = {'chest': W(A['chestdepth_all']), 'waist': W(A['waistdepth']), 'seat': W(A['buttockdepth']), 'neck': dia(A['neckcircumference']),
           'neckB': dia(A['neckcircumferencebase']), 'thigh': dia(A['thighcircumference_all']), 'knee': dia(A['lowerthighcircumference_all']),
           'calf': dia(A['calfcircumference_all']), 'ankle': dia(A['anklecircumference']), 'arm': dia(A['bicepscircumferenceflexed_all']),
           'fore': dia(A['forearmcircumferenceflexed_all']), 'wrist': dia(A['wristcircumference']), 'foot': W(A['footlength']),
           'c7': (chin - A['cervicaleheight']) * k, 'pit': (chin - A['suprasternaleheight']) * k, 'jc': jc, 'jcH': jc - NECK_CUT}
    return B, wid, {'ansur': A, 'mocap_cm': bl, 'trunk_cm': trunk, 'px_per_mm': k, 'cm_per_px': 0.1 / k, 'headH': headH, 'leg_scale': s_leg}


# ---------------- poses ----------------
def rot_points(Q, a, about):
    """turn the side view so the direction a (from straight up, positive forward) becomes straight up"""
    out = {}
    for n, (x, y) in Q.items():
        dx, dy = x - about[0], y - about[1]
        r = math.hypot(dx, dy)
        t = math.atan2(dx, dy) - a
        out[n] = (about[0] + r * math.sin(t), about[1] + r * math.cos(t))
    return out


CL = {}


def clip(n):
    if n not in CL:
        CL[n] = mocap.Clip(n)
    return CL[n]


def fwd_of(c, i, w=30, span=None):
    a, b = span if span else (max(0, i - w), min(len(c.frames) - 1, i + w))
    return mocap.facing(c.sk, c.frames, a, b)


def at(n, i, front='r', w=0, span=None, turn=None, fwd=None):
    """the game's angles at clip n frame i (averaged over i-w..i+w), and the hip's height over the clip's floor (m)"""
    c = clip(n)
    f = fwd if fwd is not None else fwd_of(c, i, span=span)
    acc = {k: 0.0 for k in ANG}
    m = 0
    hipY = 0
    for j in range(i - w, i + w + 1):
        Q = mocap.project(c.P(j), f)
        H = ((Q['hipL'][0] + Q['hipR'][0]) / 2, (Q['hipL'][1] + Q['hipR'][1]) / 2)
        if turn is not None:
            a = turn(Q, H) if callable(turn) else turn
            Q = rot_points(Q, a, H)
        p = mocap.params(Q, front)
        for k in ANG:
            acc[k] += p[k]
        hipY += H[1]
        m += 1
    o = {k: v / m for k, v in acc.items()}
    o['_hipY'] = hipY / m
    return o


def floor_of(n, a, b, fwd):
    c = clip(n)
    return min(min(mocap.project(c.P(i), fwd)[k][1] for k in ('ankleL', 'ankleR', 'ballL', 'ballR', 'toeL', 'toeR')) for i in range(a, b + 1, 2))


# single poses: name -> (clip, frame, options, why)
SEL = {
    'stand':    ('79_38', 30, {'w': 20}, 'an actor standing at ease before drinking'),
    'crouch':   ('16_05', 110, {'w': 2}, 'standing broad jump: the deepest crouch before take-off'),
    'land':     ('16_05', 203, {'w': 2}, 'the landing of a standing broad jump, knees taking the weight'),
    'skid':     ('16_08', 114, {'w': 2}, 'run/jog, sudden stop: the braking step'),
    'jumpR':    ('49_04', 176, {'w': 1}, 'run, leap: the split at the top of the leap'),
    'jumpS':    ('16_05', 150, {'w': 2}, 'standing broad jump in flight, knees drawn up'),
    'fall':     ('90_16', 356, {'w': 2}, 'in the air, arms up'),
    'hang':     ('01_03', 1765, {'w': 6}, 'playground: holding a bar overhead, body straight (the video shows his feet still on the ground: a hang\'s shape; 01_09 f1700, a real hang, leans 0.8 rad back)'),
    'pull':     ('01_09', 1745, {'w': 3}, 'playground: hanging, the knees drawn up as the climb starts (no clip pulls up onto a ledge)'),
    'reach':    ('14_07', 1624, {'w': 2}, 'jump up to grab: arms overhead at the top'),
    'garde':    ('02_07', 1348, {'w': 4, 'front': 'l'}, 'swordplay: on guard, the lead (left) leg forward'),
    'windup':   ('02_07', 90, {'w': 3, 'front': 'l'}, 'swordplay: the blade raised'),
    'lunge':    ('02_08', 1174, {'w': 2, 'front': 'l'}, 'swordplay: the step and thrust, the lead knee bent'),
    'parry':    ('02_07', 1320, {'w': 3, 'front': 'l'}, 'swordplay: the blade across'),
    'hurt':     ('16_08', 100, {'w': 2}, 'derived: the sudden stop braced back (no clip of a blow)'),
    'dead':     ('90_16', 600, {'w': 10, 'lying': True}, 'fall on face: lying'),
    'step':     ('139_29', None, {}, 'sneaking: a careful step'),
    'turn':     ('16_08', 150, {'w': 4}, 'derived: the settle after the sudden stop (a turn is not in the side view)'),
    'lowStrike': ('02_07', 204, {'w': 2, 'front': 'l'}, 'swordplay: the chop at its lowest'),
    'jumpLow':  ('49_04', 164, {'w': 1, 'lowLean': True}, 'derived: the leap\'s legs at take-off, the trunk pitched forward under the ceiling'),
    'jumpLowS': ('16_05', 150, {'w': 1, 'lowLean': True}, 'derived: the standing jump\'s tuck, pitched forward under the ceiling'),
    'press':    ('81_14', 1745, {'w': 3}, 'climb backwards off a ledge, played backwards (a low ledge, on hands and knees): chest over the lip, one leg still hanging'),
    'kneelUp':  ('81_14', 1560, {'w': 3}, 'climb backwards off a ledge, played backwards: the second knee coming onto the floor'),
    'kneel':    ('81_14', 1430, {'w': 3}, 'climb backwards off a ledge, played backwards: on both knees, hands on the floor'),
    'kickPush': ('49_04', 160, {'w': 1}, 'derived: the leap\'s push-off (no clip of a wall kick)'),
    'kickTuck': ('16_05', 152, {'w': 1}, 'derived: the standing jump\'s tuck'),
    'kickReach': ('16_05', 182, {'w': 1}, 'derived: the standing jump reaching for the floor'),
    'slide':    ('01_09', 1750, {'w': 3}, 'playground: hanging with the knees drawn up'),
}

# poses that hold something (round 22b's hold/hb, kept): their hands go to v69's places (r23grips.json)
HOLD = {'hang': (1, 1), 'pull': (1, 1), 'reach': (1, 1), 'press': (1, 1), 'kneelUp': (1, 1), 'kneel': (1, 1), 'slide': (1, 1),
        'garde': (1, 0), 'windup': (1, 0), 'lunge': (1, 0), 'parry': (1, 0), 'lowStrike': (1, 0)}
FLAGS = ('air', 'hy', 'sw', 'rot', 'kn')


def grips():
    return json.load(open(os.path.join(HERE, 'r23grips.json')))['o']


def sig(n, a, b, f, key, front='r'):
    c = clip(n)
    out = []
    for i in range(a, b + 1):
        out.append(mocap.params(mocap.project(c.P(i), f), front)[key])
    return np.array(out)


def period(x, lo, hi):
    """the period (frames) of a signal: the best autocorrelation between lo and hi frames"""
    x = x - x.mean()
    best, bp = -1e9, lo
    for p in range(lo, hi + 1):
        v = np.dot(x[:-p], x[p:]) / (len(x) - p)
        if v > best:
            best, bp = v, p
    return bp


def cycle(n, i0, per, nkeys, front='r', fwd=None, turn=None):
    c = clip(n)
    f = fwd if fwd is not None else fwd_of(c, i0, span=(i0, i0 + per))
    keys = []
    for j in range(nkeys):
        x = i0 + per * j / nkeys
        a = int(math.floor(x))
        u = x - a
        pa = at(n, a, front, fwd=f, turn=turn)
        pb = at(n, a + 1, front, fwd=f, turn=turn)
        keys.append({k: pa[k] + (pb[k] - pa[k]) * u for k in pa})
    return keys, f


def clearance(n, i, f, floor):
    """the lowest foot point over the floor at frame i, px (the legs' scale)"""
    Q = mocap.project(clip(n).P(i), f)
    return min(Q[k][1] for k in ('ankleL', 'ankleR', 'ballL', 'ballR', 'toeL', 'toeR')) - floor


def unwrap_keys(keys):
    """keep each angle continuous round a cycle (no jumps of 2 pi between keys)"""
    for k in ANG:
        for j in range(1, len(keys)):
            while keys[j][k] - keys[j - 1][k] > math.pi:
                keys[j][k] -= 2 * math.pi
            while keys[j][k] - keys[j - 1][k] < -math.pi:
                keys[j][k] += 2 * math.pi
    return keys


def build():
    B, Wd, info = body()
    G = grips()
    pxm = info['leg_scale'] * 100          # px per metre of the subjects' body (the legs' scale)
    MCP = {}
    src = {}
    for name, (n, i, o, why) in SEL.items():
        v = G['PS.' + name]['p']
        if name == 'step':
            n, i = '139_29', 560
        if o.get('lying'):
            c = clip(n)
            f = fwd_of(c, 0, span=(0, 240))  # the plane he stood and fell in
            p = at(n, i, w=o.get('w', 0), fwd=f, turn=lambda Q, H: math.atan2(((Q['shL'][0] + Q['shR'][0]) / 2) - H[0], ((Q['shL'][1] + Q['shR'][1]) / 2) - H[1]))
            # the turn that made the trunk upright is the figure's rot (skel's frame turns with it)
            Q = mocap.project(c.P(i), f)
            H = ((Q['hipL'][0] + Q['hipR'][0]) / 2, (Q['hipL'][1] + Q['hipR'][1]) / 2)
            S = ((Q['shL'][0] + Q['shR'][0]) / 2, (Q['shL'][1] + Q['shR'][1]) / 2)
            rot = math.atan2(S[0] - H[0], S[1] - H[1])
            fl = floor_of(n, i - 20, i + 20, f)
            q = {k: round(p[k], 3) for k in ANG}
            q.update({'air': 1, 'hy': round((H[1] - fl) * pxm, 2), 'rot': round(rot, 3), 'sw': v['sw'], 'kn': 0})
        else:
            p = at(n, i, o.get('front', 'r'), w=o.get('w', 0))
            q = {k: round(p[k], 3) for k in ANG}
            for k in FLAGS:
                q[k] = v[k]
        if name in HOLD:
            q['hold'], q['hb'] = HOLD[name]
            g = G['PS.' + name]
            q.update({'gFx': g['gF'][0], 'gFy': g['gF'][1], 'gBx': g['gB'][0], 'gBy': g['gB'][1], 'gH': g['hipH']})
        MCP[name] = q
        src[name] = {'clip': n, 'frame': i, 'w': o.get('w', 0), 'why': why}
    # low leaps: the leap's shape, pitched forward until the crown is no higher than v69's (a ceiling at his height)
    for name in ('jumpLow', 'jumpLowS'):
        q = MCP[name]
        v = G['PS.' + name]['p']
        old = G['PS.' + name]
        # v69's head centre over the hip, and ours: lean forward (head forward, the face down) until ours is no higher
        oy = -old['hd'][1]
        def hy_of(l, h):
            a = l + h
            # (round 23c: measured with round 23's neck, so the leap's lean stays as it was and the shorter neck only lowers the head)
            return B['to'] * math.cos(l) + (B['nk'] + NECK_CUT + B['hd']) * math.cos(a) + 1.25 * B['hd'] * abs(math.cos(a))
        l = q['lean']
        while hy_of(l, q['head']) > oy + 1.25 * 4.6 * 0.95 - 0.6 and l < 1.4:
            l += 0.02
        src[name]['why'] += ' (lean %.2f -> %.2f)' % (q['lean'], l)
        q['lean'] = round(l, 3)
    MCK = {}
    # --- the run: 09_01, the subject's right foot down at frame 42, the next at 130 (88 frames, 0.73 s, 3.5 m/s) ---
    i0, per = 42, 88
    keys, f = cycle('09_01', i0, per, 16)
    fl = floor_of('09_01', i0, i0 + per, f) + 0.012
    for j, kq in enumerate(keys):
        x = i0 + per * j / 16
        kq['cl'] = max(0.0, clearance('09_01', int(round(x)), f, fl)) * pxm
    MCK['run'] = [{k: round(kq[k], 3) for k in ANG + ['cl']} for kq in unwrap_keys(keys)]
    src['run'] = {'clip': '09_01', 'frame': '42-130 (16 keys; right foot down at 42)', 'why': 'run'}
    # --- the walk: 16_15, right heel strike 80 to 211 ---
    i0, per = 80, 131
    keys, f = cycle('16_15', i0, per, 16)
    fl = floor_of('16_15', i0, i0 + per, f) + 0.012
    for j, kq in enumerate(keys):
        kq['cl'] = max(0.0, clearance('16_15', int(round(i0 + per * j / 16)), f, fl)) * pxm
    MCK['walk'] = [{k: round(kq[k], 3) for k in ANG + ['cl']} for kq in unwrap_keys(keys)]
    src['walk'] = {'clip': '16_15', 'frame': '80-211 (16 keys)', 'why': 'walk'}
    # --- the drink (DK's times, tilt and fill as before): picking the flask up from the floor is 81_14's crouch (no clip lifts a
    # flask off the floor), the rest 79_38 drinking water: the hand to the mouth at 180, the head going back to 360, lowered by 520 ---
    G = grips()
    DKF = [('79_38', 30, {}), ('81_14', 1300, {'hold': 1}), ('81_14', 1300, {'hold': 1}), ('81_14', 1255, {}), ('79_38', 180, {'hold': 1, 'mh': 0.15}),
           ('79_38', 220, {'hold': 1, 'mh': 1}), ('79_38', 300, {'hold': 1, 'mh': 1}), ('79_38', 320, {'hold': 1, 'mh': 1}), ('79_38', 360, {'hold': 1, 'mh': 1}),
           ('79_38', 440, {}), ('79_38', 520, {})]
    dk = []
    for i, (n, fr, fl) in enumerate(DKF):
        g = G['DK %d' % i]
        p = at(n, fr, w=3)
        q = {k: round(p[k], 3) for k in ANG}
        for k in FLAGS:
            q[k] = g['p'][k]
        q.update(fl)
        if fl.get('hold'):
            regrip(B, q, g)
        dk.append([g['t'], q, g['tilt'], g['fill']])
    MCK['drink'] = dk
    src['drink'] = {'clip': '79_38, 81_14', 'frame': ' '.join('%s:%d' % (n, f) for n, f, _ in DKF), 'why': 'drinking water; the flask picked up from a crouch'}
    # --- the crawl: 111_03 (weak: a pregnant woman crawling; its limb timing only): the right knee forward at 760 to the left knee's at
    # 990 is half a cycle, the other half the same with sides swapped; hands where her arms put them (on the floor) ---
    i0, per = 760, 230
    keys, f = cycle('111_03', i0, per, 8)
    sw = lambda q: {**q, 'hF': q['hB'], 'kF': q['kB'], 'hB': q['hF'], 'kB': q['kF'], 'aF': q['aB'], 'eF': q['eB'], 'aB': q['aF'], 'eB': q['eF']}
    MCK['crawl'] = [{k: round(q[k], 3) for k in ANG} for q in unwrap_keys(keys + [sw(q) for q in keys])]
    src['crawl'] = {'clip': '111_03', 'frame': '760-990 (8 keys, mirrored for the other half)', 'why': 'crawling (limb timing)'}
    # --- the swing on the bar: 43_02 (grip bar, swing body), one cycle 228-480; the body's angles in the frame of the line from the hip
    # to the hands (the rope), keyed by the swing's phase as swingPose reads it: atan2(angle, speed / its own frequency) ---
    c = clip('43_02')
    f = fwd_of(c, 240, span=(100, 400))
    a0, a1 = 228, 481
    th = []
    PP = []
    for i in range(a0 - 1, a1 + 2):
        Q = mocap.project(c.P(i), f)
        H = ((Q['hipL'][0] + Q['hipR'][0]) / 2, (Q['hipL'][1] + Q['hipR'][1]) / 2)
        Wh = ((Q['handL'][0] + Q['handR'][0]) / 2, (Q['handL'][1] + Q['handR'][1]) / 2)
        phi = math.atan2(Wh[0] - H[0], Wh[1] - H[1])
        th.append(-phi)
        PP.append(mocap.params(rot_points(Q, phi, H), 'r'))
    wm = 2 * math.pi / (a1 - a0)
    bins = {}
    for j in range(1, len(th) - 1):
        om = (th[j + 1] - th[j - 1]) / 2 * (a1 - a0) / (2 * math.pi)   # d(theta)/d(phase)
        ph = math.atan2(th[j], om) % (2 * math.pi)
        b = int(round(ph / (2 * math.pi) * 12)) % 12
        bins.setdefault(b, []).append(PP[j])
    SWK = []
    for b in sorted(bins):
        L = bins[b]
        m = lambda k: sum(x[k] for x in L) / len(L)
        SWK.append([round(b * 2 * math.pi / 12, 3), round((m('hF') + m('hB')) / 2, 3), round((m('kF') + m('kB')) / 2, 3), round(m('lean'), 3), round(m('head'), 3)])
    SWK.append([6.2832] + SWK[0][1:])
    MCK['swing'] = SWK
    src['swing'] = {'clip': '43_02', 'frame': '228-480 (one cycle, 12 phase bins)', 'why': 'grip bar, swing body'}
    return B, Wd, info, MCP, MCK, src


def free_hands(B, q):
    s, c = math.sin, math.cos
    sh = (B['to'] * s(q['lean']), -B['to'] * c(q['lean']))
    h = lambda a, e: (sh[0] + B['ua'] * s(a) + B['fa'] * s(a + e), sh[1] + B['ua'] * c(a) + B['fa'] * c(a + e))
    return h(q['aF'], q['eF']), h(q['aB'], q['eB'])


def hipH(B, q):
    """skel's hipH before any lift: the lowest foot on the ground, or hy in the air (lerp by air)"""
    s, c = math.sin, math.cos
    low = max(B['th'] * c(q['hF']) + B['sh'] * c(q['hF'] - q['kF']), B['th'] * c(q['hB']) + B['sh'] * c(q['hB'] - q['kB']))
    return low + (q['hy'] - low) * q['air']


def regrip(B, q, g):
    """v69's held hands, moved with the hip: on the ground the hip stands where the new legs put it (gameplay's places are the floor's)"""
    d = hipH(B, q) - g['hipH'] if q['air'] < 1 else 0.0
    q.update({'gFx': g['gF'][0], 'gFy': round(g['gF'][1] + d, 3), 'gBx': g['gB'][0], 'gBy': round(g['gB'][1] + d, 3)})
    if 'gM' in g:
        q.update({'gMx': g['gM'][0], 'gMy': round(g['gM'][1] + d, 3)})


def reach_fix(B, q, name, log):
    """a held hand out of the new arm's reach: turn the trunk toward it (lean) until both reach, in steps of 0.01 rad (up to 0.8);
    in the air skel lifts the body to a grip above the shoulder, so only a grip to the side or below needs the lean"""
    R = (B['ua'] + B['fa']) * 0.985
    def worst(l):
        sx, sy = B['to'] * math.sin(l), -B['to'] * math.cos(l)
        out = 0
        for gx, gy, w in ((q['gFx'], q['gFy'], q.get('hold', 0)), (q['gBx'], q['gBy'], q.get('hb', 0))):
            if w <= 0:
                continue
            dx, dy = gx - sx, gy - sy
            if q['air'] > 0 and dy < 0 and abs(dx) < R:
                continue
            out = max(out, math.hypot(dx, dy) - R)
        return out
    l0 = q['lean']
    if worst(l0) <= 0:
        return
    best = l0
    for k in range(1, 81):
        for l in (l0 + 0.01 * k, l0 - 0.01 * k):
            if worst(l) <= 0:
                best = l
                break
        else:
            continue
        break
    log.append('%s: lean %.2f -> %.2f to keep v69\'s grip' % (name, l0, best))
    q['lean'] = round(best, 3)


def grow(k, m):
    """a measure's factor at the bulk multiplier m (round 23b): 1 + its growth rate (GROW, per unit of the upper arm's) times (m - 1)"""
    return 1.0 + GROW[k] * (min(m, NAT) - 1.0) + GROW2[k] * max(0.0, m - NAT)   # round 24: GROW2 past the natural near-limit


def bulk(Wd, m):
    """the measured widths with m's muscle on them (round 23b): girths and depths grow at their own rates, the joints and bones not at all"""
    if m == 1.0:
        return dict(Wd)
    o = dict(Wd)
    for k in ('arm', 'fore', 'thigh', 'calf', 'neck', 'neckB'):
        o[k] = Wd[k] * grow(k, m)
    return o


def drawing(Wd, m=1.0):
    """the drawing's widths from the measured ones: a tube's fill is the measure less 0.75 px (its 1.25 px outline adds the rest).
    m: the muscle bulk multiplier (round 23b; 1.0 is round 23's body): the upper arm's girth times m, every other measure by its own rate"""
    o = 0.75
    r = lambda v: round(v, 2)
    W0 = Wd
    Wd = bulk(Wd, m)
    seat, waist, chest = W0['seat'], W0['waist'], W0['chest']
    # the trunk in profile round the line hip joint -> shoulder joint, at U = 0 .14 .3 .46 .62 .76 .88 .96 1 of it (ANSUR levels: the
    # iliac crest at 0.33, the chest at 0.82, the acromion at 1.08): depth, and the share of it in front of the line
    dep = [seat, seat * 0.97, waist, waist * 1.01, (waist + chest) / 2, chest * 0.98, chest, chest * 0.92, chest * 0.74]
    shf = [0.42, 0.43, 0.51, 0.51, 0.51, 0.52, 0.51, 0.48, 0.44]
    # round 23b: the muscle's depth at each level, px, laid in front (pectorals, the abdominal wall) or behind (glutes, lats, trapezius,
    # rhomboids) by where the muscle is (TRUNK_G: measure, its share in front)
    add = [(dep[i] * (grow(TRUNK_G[i][0], min(m, NAT)) - 1.0), TRUNK_G[i][1]) for i in range(len(dep))]
    ad2 = [(dep[i] * (grow(TRUNK_G2[i][0], m) - grow(TRUNK_G2[i][0], min(m, NAT))), TRUNK_G2[i][1]) for i in range(len(dep))]   # round 24
    Fo = [r(d * k - o / 2 + a * f + a2 * f2) for d, k, (a, f), (a2, f2) in zip(dep, shf, add, ad2)]
    BQ = [r(d * (1 - k) - o / 2 + a * (1 - f) + a2 * (1 - f2)) for d, k, (a, f), (a2, f2) in zip(dep, shf, add, ad2)]
    Bo = [r(b + a) for b, a in zip(BQ, [0, 0, 0, 0.1, 0.35, 0.3, 0.15, -0.3, -0.5])]   # arms up: the lats stand out, the scapulae turn up
    jc = Wd['jc']
    tr = W0['neckB'] * (grow('trap', m) - grow('neckB', m)) / 2   # round 23b: the trapezius over the neck's own growth, on the slope from C7 down
    NJ = {'th': [r(jc - Wd['pit']), r(-Wd['neckB'] / 2 + 0.1)], 'c7': [r(jc - Wd['c7']), r(Wd['neckB'] / 2 + 0.05)],
          'bk': [[r(jc - Wd['pit'] + 1.9), 0.1], [r(jc - Wd['c7']), r(Wd['neckB'] / 2 + 0.05)], [r((jc - Wd['c7']) * 0.62), r(Wd['neckB'] / 2 + 0.55 + tr * 0.7)],
                 [r((jc - Wd['c7']) * 0.3), r(Wd['neckB'] / 2 + 0.75 + tr)]],
          'km': [r(jc + 0.6 - KM_DROP), r(Wd['neck'] / 2 - 0.1)], 'nb': [r(jc - Wd['pit'] + 0.7), 0.15, r(Wd['neckB'] - o)], 'tp': [0.25, r(Wd['neck'] - o)],
          'dq': 0.2, 'hn': 0.85}
    # deltoid, biceps, above the elbow (brachialis and triceps), elbow (a joint: unchanged), forearm, wrist (a joint)
    arm = [W0['arm'] * 1.35 * grow('delt', m), Wd['arm'], W0['arm'] * 0.9 * grow('armLo', m), W0['wrist'] * 1.35, Wd['fore'], W0['wrist']]
    # thigh at the fold, the mid-thigh, above the knee (vastus medialis), the knee and ankle (joints: unchanged), the calf (gastrocnemius),
    # the lower calf (soleus)
    leg = [Wd['thigh'], W0['thigh'] * 0.97 * grow('thighM', m), W0['knee'] * 1.1 * grow('lthigh', m), W0['knee'], Wd['calf'], W0['calf'] * 0.8 * grow('soleus', m), W0['ankle']]
    T = lambda a, q: [r(max(0.9, v * q - o)) for v in a]
    return {'Fo': Fo, 'BQ': BQ, 'Bo': Bo, 'NJ': NJ, 'arm': T(arm, 1), 'armR': T(arm, 1.18), 'leg': T(leg, 1), 'legR': T(leg, 1.18),
            'fk': r((Wd['foot'] - 0.6) / 9.0), 'kilt': [r(Wd['thigh'] * 0.45 + 0.35), r(-(Wd['thigh'] * 0.47 + 0.35))],
            'RS': r(Wd['thigh'] / 2 + 0.35), 'chest': r(chest * grow('chest', m)), 'robK': 1.15} | ({'mh': r(MH * min(1.0, (m - 1.0) / (NAT - 1.0)) + MH2 * max(0.0, m - NAT) / (LEVELS[-1][0] - NAT)), 'cb': r((Wd['calf'] - W0['calf']) / 2), 'mus': m} if m > 1 else {}) | ({'du': r(0.22 + DU * (m - NAT) / (LEVELS[-1][0] - NAT))} if m > NAT else {})


def js(v):
    return json.dumps(v, separators=(',', ':'))


def emit():
    B, Wd, info, MCP, MCK, src = build()
    G = grips()
    fix = []
    for name, q in MCP.items():
        if name in HOLD:
            regrip(B, q, G['PS.' + name])
            reach_fix(B, q, name, fix)
            if src.get(name):
                src[name]['fix'] = [f for f in fix if f.startswith(name + ':')]
    for i, k in enumerate(MCK['drink']):
        if k[1].get('hold'):
            reach_fix(B, k[1], 'drink %d' % i, fix)
    # crawling: the palms on the floor (the hip over it by its height; a palm's centre 1.3 px up), where the arms reach forward
    for q in MCK['crawl']:
        q.update({'air': 0, 'hy': 24, 'kn': 1})
        h = hipH(B, q)
        (fx, fy), (bx, by) = free_hands(B, q)
        q.update({'hold': 1, 'hb': 1, 'gFx': round(fx, 3), 'gFy': round(h - 1.3, 3), 'gBx': round(bx, 3), 'gBy': round(h - 1.3, 3)})
    for f in fix:
        print('  grip:', f)
    D = drawing(Wd, MUS)
    DV = [None if m == MUS else drawing(Wd, m) for m, _ in LEVELS]   # the levels' tables (the game's own is R23D)
    Bj = {k: round(float(v), 3) for k, v in B.items()}
    lines = ['// <R23-MOCAP> generated by dev/tools/r23poses.py from the CMU motion capture database (mocap.cs.cmu.edu; created with funding',
             '// from NSF EIA-0196217), ANSUR II and v69\'s held hands (r23grips.json). Do not edit by hand: change r23poses.py and run it.',
             '// R23B: the skeleton (px; see dev/FIGURE_SPEC.md). R23D: the drawing\'s widths. MCP: single poses (the game\'s angles from the clips;',
             '// air, hy, sw, rot, kn and the held hands gF/gB as v69). MCK: keyed cycles (run, walk: 16 keys a cycle; cl the lowest foot\'s',
             '// clearance over the floor, px).',
             'const R23B=' + js(Bj) + ';',
             'const R23D=' + js(D) + ';',
             '// R23MUS, R23DV (round 23b): the muscle bulk levels (the upper arm\'s girth over ANSUR II\'s median) and their tables (null: R23D).',
             'const R23MUS=' + js([m for m, _ in LEVELS]) + ',R23DV=' + js(DV) + ';',
             '// R23DR (round 24): the robbers\' table, v70\'s level 1.28 whatever the prince\'s (they must not grow with him).',
             'const R23DR=' + js(drawing(Wd, ROB_MUS)) + ';',
             'const MCP=' + js(MCP) + ';',
             'const MCK=' + js(MCK) + ';',
             '// </R23-MOCAP>']
    s = open(SRC, encoding='utf-8').read()
    a = s.find('// <R23-MOCAP>')
    b = s.find('// </R23-MOCAP>')
    blk = '\n'.join(lines)
    if a >= 0:
        s = s[:a] + blk + s[b + len('// </R23-MOCAP>'):]
    else:
        i = s.find("const PK=['lean'")
        s = s[:i] + blk + '\n' + s[i:]
    open(SRC, 'w', encoding='utf-8').write(s)
    json.dump({'body': Bj, 'widths': {k: round(float(v), 3) for k, v in Wd.items()}, 'info': {k: v for k, v in info.items() if k != 'ansur'},
               'ansur': info['ansur'], 'src': src}, open(os.path.join(HERE, 'r23body.json'), 'w'), indent=1, default=float)
    json.dump({'levels': [{'m': m, 'basis': why, 'factors': {k: round(grow(k, m), 3) for k in GROW}, 'table': drawing(Wd, m)} for m, why in LEVELS],
               'grow': GROW, 'grow2': GROW2, 'nat': NAT, 'mus': MUS, 'trunk': TRUNK_G, 'cm_per_px': info['cm_per_px'], 'widths': {k: round(float(v), 3) for k, v in Wd.items()}},
              open(os.path.join(HERE, 'r23bulk.json'), 'w'), indent=1)
    print('R23B', Bj)
    for k, v in src.items():
        print('%-10s %-7s %-30s %s' % (k, v['clip'], v['frame'], v['why']))


if __name__ == '__main__':
    emit()
