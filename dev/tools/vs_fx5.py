# Batch 5 (visual fixes): progress through the repeating themes (dusk / night / dawn, the skyline sinking, wear) and the
# tapestry designs. vshots.py fx5 [id ...]
HALL = "const t=L.torches.filter(t=>!t.broken&&t.c>8&&V.walkway(t.c,t.r,1,4))[2];if(!t)return null;return V.near(t.c,t.r,2)"
WIN = "const w=L.windows.filter(w=>w.c>8&&V.near(w.c,w.r,2))[1];return w&&V.near(w.c,w.r,2)"
ARCH = "const a=[];for(let r=0;r<L.rows;r++)for(let c=9;c<L.cols-3;c++)if(V.isOpen&&V.isOpen(c,r)&&V.near(c,r,2))return V.near(c,r,2);return null"
SETS = [('dungeon', [1, 21, 41]), ('palace', [5, 25, 45]), ('tile', [9, 29, 32, 49]), ('forge', [13, 33, 53]), ('crypt', [17, 37, 57])]


def run(rig):
    for th, fl in SETS:
        for n in fl:
            rig.scene('F57-hall-%s-f%d' % (th, n), n, 8000, HALL, 'Corridor by a lamp, %s, floor %d.' % (th, n), 'progress', 'f57', tries=80, modes=('torch', 'classic') if n in (1, 21, 41, 32) else ('torch',))
            rig.scene('F57-win-%s-f%d' % (th, n), n, 8000, WIN, 'Window view, %s, floor %d.' % (th, n), 'progress', 'f57', tries=80, modes=('torch',))
