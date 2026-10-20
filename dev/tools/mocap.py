# mocap.py: the CMU Graphics Lab Motion Capture Database's ASF/AMC files (round 23). The data used in this project was obtained from
# mocap.cs.cmu.edu. The database was created with funding from NSF EIA-0196217.
#
# ASF: the subject's skeleton. :units length L means bone lengths and the root's translation are in inches times L (CMU: 0.45), so
# metres = value / L * 0.0254. Each bone: a direction (unit vector, world frame at rest), a length, an axis (x y z degrees, order XYZ:
# the bone's local frame C), its dofs (rx ry rz in the order listed) and limits. :hierarchy gives parent -> children.
# AMC: per frame (120 fps) the root's TX TY TZ RX RY RZ and each bone's dof values in degrees.
# Forward kinematics (the CMU convention, as in the database's own amc viewer): for a bone, L = C * M * C^-1 with M = Rz*Ry*Rx of its
# dof angles (missing dofs 0); its world rotation is parent's * L; its end = start + length * world rotation * direction.
# The root: its rotation C * M * C^-1 the same way (axis from :root, usually XYZ 0 0 0), its position the translation. Y is up.
#
# The side view: sagittal(J, fwd) projects every joint onto the plane of forward (horizontal unit vector) and up: x = p.fwd, y = p.y.
# facing() reads the body's forward from the pelvis (the cross of the hip line and up) over a span of frames.
# params() turns one frame into this game's pose angles (dev/hourglass-keep.html, skel): angles from straight down, positive forward:
# lean (hip joints' middle -> shoulder joints' middle, from straight up), head (shoulders' middle -> the head's centre, less the lean),
# hF/kF and hB/kB (thigh from straight down; knee flexion = thigh - shin), aF/eF and aB/eB (upper arm from straight down; elbow =
# forearm - upper arm), and the foot's pitch, the hip joints' height over the floor (the lowest foot point of the clip's span).
# 'F' is the near side, drawn last; by default the subject's right limbs (front='r'), else the left.
#
# Usage (from dev/tools):
#   python3 mocap.py strip CLIP a b step [out.png] [front]    a stick-figure strip of frames a..b (side view, in metres)
#   python3 mocap.py bones SUBJ                                 bone lengths in cm
#   python3 mocap.py video CLIP frame [out.png]                 the clip's .mpg frame (ffmpeg; the video runs at 30 fps: frame/4)
import math, os, sys, subprocess
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, 'ref', 'cmu')


def _rot(ax, a):
    c, s = math.cos(a), math.sin(a)
    if ax == 'x':
        return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
    if ax == 'y':
        return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def euler(rx, ry, rz):  # degrees -> Rz*Ry*Rx
    return _rot('z', math.radians(rz)) @ _rot('y', math.radians(ry)) @ _rot('x', math.radians(rx))


class Skel:
    def __init__(self, path):
        self.bones = {}
        self.children = {}
        self.unit = 0.45
        self.root_order = ['TX', 'TY', 'TZ', 'RX', 'RY', 'RZ']
        self.root_axis = (0, 0, 0)
        sec = None
        cur = None
        lines = open(path, encoding='latin-1').read().split('\n')
        i = 0
        while i < len(lines):
            ln = lines[i].strip()
            i += 1
            if not ln or ln.startswith('#'):
                continue
            if ln.startswith(':'):
                sec = ln.split()[0][1:]
                if sec == 'units':
                    pass
                continue
            t = ln.split()
            if sec == 'units' and t[0] == 'length':
                self.unit = float(t[1])
            elif sec == 'root':
                if t[0] == 'order':
                    self.root_order = t[1:]
                elif t[0] == 'axis':
                    pass
                elif t[0] == 'orientation':
                    self.root_axis = tuple(float(v) for v in t[1:4])
            elif sec == 'bonedata':
                if t[0] == 'begin':
                    cur = {'dof': [], 'axis': (0, 0, 0)}
                elif t[0] == 'end':
                    self.bones[cur['name']] = cur
                elif t[0] == 'name':
                    cur['name'] = t[1]
                elif t[0] == 'direction':
                    cur['dir'] = np.array([float(v) for v in t[1:4]])
                elif t[0] == 'length':
                    cur['len'] = float(t[1])
                elif t[0] == 'axis':
                    cur['axis'] = tuple(float(v) for v in t[1:4])
                elif t[0] == 'dof':
                    cur['dof'] = t[1:]
            elif sec == 'hierarchy':
                if t[0] in ('begin', 'end'):
                    continue
                self.children[t[0]] = t[1:]
        for b in self.bones.values():
            b['C'] = euler(*b['axis'])
            b['Ci'] = b['C'].T
            b['m'] = b['len'] / self.unit * 0.0254  # metres
        self.rC = euler(*self.root_axis)

    def length_cm(self, name):
        return self.bones[name]['m'] * 100


def load_amc(path):
    frames = []
    cur = None
    for ln in open(path, encoding='latin-1'):
        ln = ln.strip()
        if not ln or ln.startswith('#') or ln.startswith(':'):
            continue
        t = ln.split()
        if len(t) == 1 and t[0].isdigit():
            cur = {}
            frames.append(cur)
            continue
        cur[t[0]] = [float(v) for v in t[1:]]
    return frames


def fk(sk, fr):
    """world joint positions (metres, Y up): J[name] = the bone's END; J['root'] = the root's position"""
    J = {}
    R = {}
    r = fr['root']
    o = dict(zip(sk.root_order, r))
    pos = np.array([o.get('TX', 0), o.get('TY', 0), o.get('TZ', 0)]) / sk.unit * 0.0254
    M = euler(o.get('RX', 0), o.get('RY', 0), o.get('RZ', 0))
    R['root'] = sk.rC @ M @ sk.rC.T
    J['root'] = pos
    stack = [('root', c) for c in sk.children.get('root', [])]
    while stack:
        par, name = stack.pop()
        b = sk.bones[name]
        v = fr.get(name, [])
        a = {'rx': 0.0, 'ry': 0.0, 'rz': 0.0}
        for d, x in zip(b['dof'], v):
            a[d] = x
        L = b['C'] @ euler(a['rx'], a['ry'], a['rz']) @ b['Ci']
        R[name] = R[par] @ L
        J[name] = J[par] + b['m'] * (R[name] @ b['dir'])
        stack.extend((name, c) for c in sk.children.get(name, []))
    J['_R'] = R
    return J


# joints by landmark (the bone whose END is the landmark)
LM = {
    'hipL': 'lhipjoint', 'hipR': 'rhipjoint', 'kneeL': 'lfemur', 'kneeR': 'rfemur', 'ankleL': 'ltibia', 'ankleR': 'rtibia',
    'ballL': 'lfoot', 'ballR': 'rfoot', 'toeL': 'ltoes', 'toeR': 'rtoes',
    'shL': 'lclavicle', 'shR': 'rclavicle', 'elbL': 'lhumerus', 'elbR': 'rhumerus', 'wriL': 'lradius', 'wriR': 'rradius',
    'handL': 'lhand', 'handR': 'rhand', 'waist': 'lowerback', 'chest': 'upperback', 'c7': 'thorax', 'neck': 'lowerneck',
    'skull': 'upperneck', 'crown': 'head',
}


def landmarks(J):
    P = {k: J[v] for k, v in LM.items()}
    P['root'] = J['root']
    P['headc'] = P['skull'] + (P['crown'] - P['skull']) * 0.45
    return P


def facing(sk, frames, a, b):
    """the body's mean forward over frames a..b: up x (right hip - left hip), horizontal"""
    acc = np.zeros(3)
    for i in range(a, b + 1):
        P = landmarks(fk(sk, frames[i]))
        lr = P['hipL'] - P['hipR']  # toward the subject's left
        f = np.cross(lr, np.array([0, 1.0, 0]))  # forward = left x up (checked against the travel of the run and walk clips)
        f[1] = 0
        acc += f / (np.linalg.norm(f) + 1e-9)
    acc[1] = 0
    return acc / np.linalg.norm(acc)


def project(P, fwd):
    return {k: (float(np.dot(v, fwd)), float(v[1])) for k, v in P.items() if isinstance(v, np.ndarray)}


def ang_down(a, b):  # the angle of a->b from straight down, positive forward (x)
    return math.atan2(b[0] - a[0], a[1] - b[1])


def wrap(x):
    while x > math.pi:
        x -= 2 * math.pi
    while x < -math.pi:
        x += 2 * math.pi
    return x


def params(Q, front='r', floor=None):
    """game pose angles from projected landmarks Q (x forward, y up, metres)"""
    F, B = ('R', 'L') if front == 'r' else ('L', 'R')
    mid = lambda a, b: ((Q[a][0] + Q[b][0]) / 2, (Q[a][1] + Q[b][1]) / 2)
    H = mid('hipL', 'hipR')
    S = mid('shL', 'shR')
    lean = math.atan2(S[0] - H[0], S[1] - H[1])
    head = wrap(math.atan2(Q['headc'][0] - S[0], Q['headc'][1] - S[1]) - lean)
    o = {'lean': lean, 'head': head}
    for side, tag in ((F, 'F'), (B, 'B')):
        th = ang_down(Q['hip' + side], Q['knee' + side])
        sh = ang_down(Q['knee' + side], Q['ankle' + side])
        o['h' + tag] = th
        o['k' + tag] = wrap(th - sh)
        ua = ang_down(Q['sh' + side], Q['elb' + side])
        fa = ang_down(Q['elb' + side], Q['wri' + side])
        if ua < -2.2:
            ua += 2 * math.pi  # (overhead: kept on the forward side of the wrap, as the game's poses are)
        o['a' + tag] = ua
        o['e' + tag] = wrap(fa - ua)
        o['ft' + tag] = math.atan2(Q['ball' + side][1] - Q['ankle' + side][1], Q['ball' + side][0] - Q['ankle' + side][0])
    if floor is not None:
        o['hipY'] = H[1] - floor
        o['lowY'] = min(Q['ankleL'][1], Q['ankleR'][1], Q['ballL'][1], Q['ballR'][1], Q['toeL'][1], Q['toeR'][1]) - floor
    o['H'] = H
    return o


class Clip:
    def __init__(self, name, subj=None):
        self.name = name
        self.subj = subj or name.split('_')[0]
        self.sk = Skel(os.path.join(REF, self.subj + '.asf'))
        self.frames = load_amc(os.path.join(REF, name + '.amc'))
        self._fk = {}

    def P(self, i):
        if i not in self._fk:
            self._fk[i] = landmarks(fk(self.sk, self.frames[i]))
        return self._fk[i]

    def side(self, a, b, fwd=None, front='r'):
        """projected landmarks and params for frames a..b in one sagittal plane; the floor = the lowest foot point in the span"""
        fwd = facing(self.sk, self.frames, a, b) if fwd is None else fwd
        Qs = [project(self.P(i), fwd) for i in range(a, b + 1)]
        floor = min(min(q[k][1] for k in ('ankleL', 'ankleR', 'ballL', 'ballR', 'toeL', 'toeR')) for q in Qs)
        return fwd, Qs, [params(q, front, floor) for q in Qs]


BONES_DRAW = [('hipL', 'kneeL'), ('kneeL', 'ankleL'), ('ankleL', 'ballL'), ('ballL', 'toeL'), ('hipR', 'kneeR'), ('kneeR', 'ankleR'),
              ('ankleR', 'ballR'), ('ballR', 'toeR'), ('root', 'waist'), ('waist', 'chest'), ('chest', 'c7'), ('c7', 'neck'), ('neck', 'skull'),
              ('skull', 'crown'), ('c7', 'shL'), ('c7', 'shR'), ('shL', 'elbL'), ('elbL', 'wriL'), ('wriL', 'handL'), ('shR', 'elbR'),
              ('elbR', 'wriR'), ('wriR', 'handR'), ('hipL', 'hipR'), ('root', 'hipL'), ('root', 'hipR')]


def draw_stick(dr, Q, ox, oy, sc, front='r', col_f=(200, 60, 40), col_b=(90, 110, 170), col_t=(40, 40, 40), w=2):
    F = 'R' if front == 'r' else 'L'
    for a, b in BONES_DRAW:
        side = a[-1] if a[-1] in 'LR' and a not in ('root',) else (b[-1] if b[-1] in 'LR' else '')
        col = col_t if side == '' or a == 'root' or (a, b) == ('hipL', 'hipR') else (col_f if side == F else col_b)
        dr.line([(ox + Q[a][0] * sc, oy - Q[a][1] * sc), (ox + Q[b][0] * sc, oy - Q[b][1] * sc)], fill=col, width=w)
    hc = Q['headc']
    r = 0.11 * sc
    dr.ellipse([ox + hc[0] * sc - r, oy - hc[1] * sc - r, ox + hc[0] * sc + r, oy - hc[1] * sc + r], outline=col_t, width=w)


def strip(name, a, b, step, out, front='r'):
    from PIL import Image, ImageDraw
    c = Clip(name)
    fwd, Qs, Ps = c.side(a, b, front=front)
    idx = list(range(0, b - a + 1, step))
    sc = 90
    cw = 150
    im = Image.new('RGB', (cw * len(idx) + 20, 260), 'white')
    dr = ImageDraw.Draw(im)
    floor = min(min(q[k][1] for k in ('ankleL', 'ankleR', 'toeL', 'toeR')) for q in Qs)
    for n, i in enumerate(idx):
        Q = Qs[i]
        H = Ps[i]['H']
        ox = 10 + cw * n + cw / 2 - H[0] * sc
        oy = 230 + floor * sc
        dr.line([(10 + cw * n, 230), (10 + cw * n + cw - 10, 230)], fill=(180, 180, 180))
        draw_stick(dr, Q, ox, oy, sc, front)
        dr.text((12 + cw * n, 236), '%s f%d' % (name, a + i), fill=(0, 0, 0))
    im.save(out)
    return out


def video_frame(name, frame, out):
    """the .mpg frame matching mocap frame (120 fps capture, 30 fps video: frame/4)"""
    mp = os.path.join(REF, name + '.mpg')
    t = frame / 120.0
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-ss', '%.3f' % t, '-i', mp, '-frames:v', '1', out], check=True)
    return out


def sheet(name, a, b, step, out, front='r', per=20):
    """a contact sheet: every step-th frame, each in its own pelvis-facing side view, per frames a row"""
    from PIL import Image, ImageDraw
    c = Clip(name)
    b = min(b, len(c.frames) - 1)
    idx = list(range(a, b + 1, step))
    sc, cw, rh = 60, 80, 150
    rows = (len(idx) + per - 1) // per
    im = Image.new('RGB', (cw * per + 10, rh * rows + 10), 'white')
    dr = ImageDraw.Draw(im)
    for n, i in enumerate(idx):
        fwd = facing(c.sk, c.frames, i, i)
        Q = project(c.P(i), fwd)
        H = ((Q['hipL'][0] + Q['hipR'][0]) / 2, 0)
        x0, y0 = 5 + cw * (n % per), 5 + rh * (n // per)
        ox, oy = x0 + cw / 2 - H[0] * sc, y0 + 125
        dr.line([(x0, oy), (x0 + cw - 6, oy)], fill=(200, 200, 200))
        draw_stick(dr, Q, ox, oy, sc, front, w=1)
        dr.text((x0 + 2, oy + 4), str(i), fill=(0, 0, 0))
    im.save(out)
    return out


if __name__ == '__main__':
    a = sys.argv[1:]
    if a[0] == 'strip':
        print(strip(a[1], int(a[2]), int(a[3]), int(a[4]), a[5] if len(a) > 5 else os.path.join(HERE, '_strip_%s.png' % a[1]), a[6] if len(a) > 6 else 'r'))
    elif a[0] == 'sheet':
        print(sheet(a[1], int(a[2]), int(a[3]), int(a[4]), a[5], a[6] if len(a) > 6 else 'r'))
    elif a[0] == 'bones':
        sk = Skel(os.path.join(REF, a[1] + '.asf'))
        for n, b in sk.bones.items():
            print('%-12s %6.1f cm' % (n, b['m'] * 100))
    elif a[0] == 'video':
        print(video_frame(a[1], int(a[2]), a[3] if len(a) > 3 else os.path.join(HERE, '_vid_%s_%s.png' % (a[1], a[2]))))
