# Tapestries on the wall per theme (visual fixes, agent 4): vshots.py fx4 [id ...]
THEMES = [('dungeon', 3), ('palace', 7), ('tile', 11), ('forge', 15), ('crypt', 19)]
HANG = "const hs=L.hangings.filter(h=>h.state<=1&&h.k===%d);for(const h of hs){const s=V.near(h.c,h.r,2);if(s)return s;}return null"


def run(rig):
    for th, n in THEMES:
        for k in range(6):
            rig.scene('TAP-%s-%d' % (th, k), n, 15000 + 7 * k, HANG % k, 'A wall tapestry, design %d (%s).' % (k, th), 'theme', 'tap-%s' % th, tries=200, modes=('torch',))
