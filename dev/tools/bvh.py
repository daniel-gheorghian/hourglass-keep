# bvh.py (round 32): the CMU Graphics Lab Motion Capture Database in BVH (Bruce Hahne's cgspeed conversion, 120 fps, the same frame
# numbers as the .amc), read into the landmarks mocap.py uses, so mocap.project/params and r23poses' rules work on it unchanged.
# The data used in this project was obtained from mocap.cs.cmu.edu. The database was created with funding from NSF EIA-0196217.
#
# Why: mocap.cs.cmu.edu was out of reach from the round 32 session; the cgspeed BVH set is mirrored on GitHub
# (https://github.com/una-dinosauria/cmu-mocap, data/NNN/NN_MM.bvh). Put the files in ref/cmu/ (gitignored) or point CMU_BVH at a checkout.
# Checked against round 23's ASF/AMC numbers: 13_11 f196 and f252 and 49_04 f176 give MCP's jumpCrouch, jumpS and jumpR within a degree or two
# (r32jump.py check).
#
# BVH: Y up; each joint's channels in the order listed (cgspeed: Z Y X), its local rotation the product in that order; position = the
# parent's position + the parent's world rotation x OFFSET. A landmark is a joint's origin (the bone's start) or an End Site.
import math, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, 'ref', 'cmu')
ALT = os.environ.get('CMU_BVH', '/home/user/una-dinosauria/cmu-mocap/data')


def path_of(name):
    p = os.path.join(REF, name + '.bvh')
    if os.path.exists(p):
        return p
    s = name.split('_')[0]
    return os.path.join(ALT, '%03d' % int(s), name + '.bvh')


def _rot(ax, a):
    c, s = math.cos(a), math.sin(a)
    if ax == 'X':
        return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
    if ax == 'Y':
        return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


class BVH:
    def __init__(self, path):
        tok = open(path).read().split()
        self.joints = []   # (name, parent index, offset, channels)
        self.ends = {}     # joint index -> End Site offset
        i = 0
        stack = []
        cur = None
        while tok[i] != 'MOTION':
            t = tok[i]
            if t in ('ROOT', 'JOINT'):
                self.joints.append([tok[i + 1], stack[-1] if stack else -1, None, []])
                cur = len(self.joints) - 1
                i += 2
            elif t == 'End':
                cur = ('end', stack[-1])
                i += 2
            elif t == '{':
                stack.append(cur)
                i += 1
            elif t == '}':
                stack.pop()
                i += 1
            elif t == 'OFFSET':
                v = np.array([float(x) for x in tok[i + 1:i + 4]])
                if isinstance(cur, tuple):
                    self.ends[cur[1]] = v
                else:
                    self.joints[cur][2] = v
                i += 4
            elif t == 'CHANNELS':
                n = int(tok[i + 1])
                self.joints[cur][3] = tok[i + 2:i + 2 + n]
                i += 2 + n
            else:
                i += 1
        # stack held ints for joints; End Site entries push a tuple, popped at their '}'
        i += 1
        n = int(tok[i + 1])
        self.dt = float(tok[i + 4])
        i += 5
        nc = sum(len(j[3]) for j in self.joints)
        self.frames = np.array([float(x) for x in tok[i:i + n * nc]]).reshape(n, nc)
        self.idx = {j[0]: k for k, j in enumerate(self.joints)}

    def fk(self, f):
        v = self.frames[f]
        R, Pp, E = [None] * len(self.joints), [None] * len(self.joints), {}
        c = 0
        for k, (name, par, off, ch) in enumerate(self.joints):
            pos = np.zeros(3)
            M = np.eye(3)
            for q in ch:
                x = v[c]
                c += 1
                if q.endswith('position'):
                    pos['XYZ'.index(q[0])] = x
                else:
                    M = M @ _rot(q[0], math.radians(x))
            if par < 0:
                Pp[k] = pos + off
                R[k] = M
            else:
                Pp[k] = Pp[par] + R[par] @ off
                R[k] = R[par] @ M
            if k in self.ends:
                E[name] = Pp[k] + R[k] @ self.ends[k]
        J = {self.joints[k][0]: Pp[k] for k in range(len(self.joints))}
        return J, E, {self.joints[k][0]: R[k] for k in range(len(self.joints))}


# the BVH joint whose ORIGIN is each landmark of mocap.LM (cgspeed keeps CMU's bones: LeftUpLeg starts at the end of lhipjoint, ...)
LMB = {'hipL': 'LeftUpLeg', 'hipR': 'RightUpLeg', 'kneeL': 'LeftLeg', 'kneeR': 'RightLeg', 'ankleL': 'LeftFoot', 'ankleR': 'RightFoot',
       'ballL': 'LeftToeBase', 'ballR': 'RightToeBase', 'shL': 'LeftArm', 'shR': 'RightArm', 'elbL': 'LeftForeArm', 'elbR': 'RightForeArm',
       'wriL': 'LeftHand', 'wriR': 'RightHand', 'waist': 'Spine', 'chest': 'Spine1', 'c7': 'Neck', 'neck': 'Neck1', 'skull': 'Head'}


class Clip:
    """the landmarks of a CMU clip from its BVH, in metres (mocap.Clip's P(i) and facing)"""
    def __init__(self, name):
        self.name = name
        self.b = BVH(path_of(name))
        self.n = len(self.b.frames)
        # units: scale so that the mean thigh is CMU's (the subjects' femur ~0.42 m): only metres for heights, angles are scale-free
        J, E, _ = self.b.fk(0)
        th = (np.linalg.norm(J['LeftLeg'] - J['LeftUpLeg']) + np.linalg.norm(J['RightLeg'] - J['RightUpLeg'])) / 2
        self.k = 0.419 / th
        self._P = {}

    def P(self, i):
        if i not in self._P:
            J, E, R = self.b.fk(i)
            P = {k: J[v] * self.k for k, v in LMB.items()}
            P['toeL'] = E['LeftToeBase'] * self.k
            P['toeR'] = E['RightToeBase'] * self.k
            P['crown'] = E['Head'] * self.k
            P['handL'] = E.get('LeftHandIndex1', E.get('LeftFingerBase', J['LeftHand'])) * self.k
            P['handR'] = E.get('RightHandIndex1', E.get('RightFingerBase', J['RightHand'])) * self.k
            P['root'] = J['Hips'] * self.k
            P['headc'] = P['skull'] + (P['crown'] - P['skull']) * 0.45
            P['_R'] = R
            self._P[i] = P
        return self._P[i]

    def facing(self, a, b):
        acc = np.zeros(3)
        for i in range(a, b + 1):
            P = self.P(i)
            f = np.cross(P['hipL'] - P['hipR'], np.array([0, 1.0, 0]))
            f[1] = 0
            acc += f / (np.linalg.norm(f) + 1e-9)
        acc[1] = 0
        return acc / np.linalg.norm(acc)
