# Architecture per theme: rooms, windows, breaches, doors, hourglass, secrets, slabs, galleries.
THEMES = [('dungeon', 3), ('palace', 7), ('tile', 11), ('forge', 15), ('crypt', 19)]
HALL = "const t=L.torches.filter(t=>t.c>8&&V.walkway(t.c,t.r,1,4))[2];if(!t)return null;return V.near(t.c,t.r,2)"
WIN = "const w=L.windows.filter(w=>w.c>8&&V.near(w.c,w.r,2))[1];return w&&V.near(w.c,w.r,2)"
BREACH = "const b=L.breaches.find(b=>V.near((b.c0+b.c1)>>1,b.r,3));return b&&V.near((b.c0+b.c1)>>1,b.r,3)"
DOOR = "const d=L.door;return V.near(d.c,d.r,3)"
ENTRY = "return {x:L.start.x,r:L.start.r,face:L.start.face||1}"
CP = "const c=L.cps.find(c=>V.near(c.c,c.r,3));return c&&V.near(c.c,c.r,3)"
SECRET = "const s=L.secret;return s&&V.near(s.c,s.r,3)"
FLOORSEC = "const t=L.torches.filter(t=>t.c>8&&V.walkway(t.c,t.r,1,4))[4];return t&&V.near(t.c,t.r,2)"


def run(rig):
    for i, (th, n) in enumerate(THEMES):
        sd = 8000 + 17 * i
        rig.scene('A-hall-' + th, n, sd, HALL, 'Corridor by a wall torch: room background, arches, pillars, floor, lighting (%s theme).' % th, 'architecture', 'arch-hall')
        rig.scene('A-window-' + th, n, sd, WIN, 'Wall window / light shaft in a corridor (%s).' % th, 'architecture', 'arch-wall')
        rig.scene('A-breach-' + th, n, sd, BREACH, 'A breach in the wall (crumbled opening showing a background beyond) (%s).' % th, 'architecture', 'arch-wall', tries=80, modes=('torch',))
        rig.scene('A-door-' + th, n, sd, DOOR, 'The exit door, closed (%s).' % th, 'architecture', 'arch-doors', modes=('torch',))
        rig.scene('A-dooropen-' + th, n, sd, DOOR, 'The exit door, open (%s).' % th, 'architecture', 'arch-doors', js='H.L.door.open=1', modes=('torch',))
        rig.scene('A-entry-' + th, n, sd, ENTRY, 'The entrance door / start of the floor (%s).' % th, 'architecture', 'arch-doors', modes=('torch',))
        rig.scene('A-hourglass-' + th, n, sd, CP, 'Checkpoint hourglass, untouched (%s).' % th, 'architecture', 'arch-cp', tries=80, modes=('torch',))
        rig.scene('A-hourglass-on-' + th, n, sd, CP, 'Checkpoint hourglass after touching (%s).' % th, 'architecture', 'arch-cp', tries=80, modes=('torch',),
                  js2='const c=H.L.cps.find(c=>!c.on&&Math.abs(c.x-H.P.x)<200);if(c)c.on=true')
        rig.scene('A-secret-' + th, [n, n - 1, n + 1, n - 2, n + 2, n - 3], sd, SECRET, 'A secret side passage with its hidden gold flask (%s).' % th, 'architecture', 'arch-secret', tries=40, modes=('torch',))
        rig.scene('A-slab-' + th, n, sd + 3, FLOORSEC, 'Close-up of the floor slab edge and joins, clean art (%s).' % th, 'architecture', 'arch-slab',
                  clip='js:V.box(s.x-90,(s.r+1)*64-60,s.x+90,(s.r+1)*64+36)', closeup=True, modes=('torch',))
