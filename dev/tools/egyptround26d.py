# egyptround26d.py: round 26d's section of egypt_themes.html: the sand wells under rows of three or more cracked slabs give way as one
# body of sand, each slab in its own way (owner: "the domino sand effect needs to be more organic and less mechanically domino. On two
# columns of sand it works, on more than two it doesn't"). Pictures from egyptr26d.py (r26d_sand.png, r26d_sand.gif).
import html
E = html.escape


def fig(img, f, cap):
    return '<figure>%s<figcaption>%s</figcaption></figure>' % (img(f, cap), E(cap))


def links(L):
    return '<ul>' + ''.join('<li><a href="%s">%s</a></li>' % (E(u), E(t)) for t, u in L) + '</ul>'


SOURCES = [
    ('USGS Water Science School, sinkholes: cover-subsidence (sand ravelling down into the void, a gradual sag) and cover-collapse '
     '(the cover spalls, an arch forms, the cavity climbs by progressive roof collapse)', 'https://www.usgs.gov/water-science-school/science/sinkholes'),
    ('Sinclair and Stewart, USGS WRI 85-4126, sinkhole types in west-central Florida', 'https://pubs.usgs.gov/wri/1985/4126/report.pdf'),
    ('Freyssingeas, Dalbe, Geminard (ENS Lyon, PRE 2011): a silo\'s crater in dry grains keeps one angle; in cohesive grains it grows by single '
     'avalanches and is not symmetric, while the outflow stays steady', 'https://www.ens-lyon.fr/PHYSIQUE/teams/matiere-complexite/research-topics/soft-matter/granular-materials/avalanches-in-cohesive-granular-matter'),
    ('Surface depression with double-angle geometry during the discharge of grains from a silo (arXiv 1703.10605): grains leave the free '
     'surface in continuous or intermittent avalanches down to the angle of repose; funnel flow with stagnant sand at the walls', 'https://arxiv.org/pdf/1703.10605'),
    ('Staron, Lagree, Popinet, The granular silo as a continuum plastic flow: the hour-glass vs the clepsydra (Beverloo: the rate does not '
     'depend on the height of the fill)', 'https://arxiv.org/pdf/1211.5916'),
    ('The Sands of Time Run Faster Near the End (arXiv 1602.05627): the funnel-shaped surface changes the flow only at the very end',
     'https://ar5iv.arxiv.org/html/1602.05627'),
    ('Edwards, Sand Rendering in Journey (GDC 2013): three years of work on sand that reads as many grains, not a surface',
     'https://gdcvault.com/play/1017742/Sand-Rendering-in'),
    ('Guerrette, The Tricks Up Our Sleeves (GDC 2012, Uncharted 3): the desert\'s sand given life by particles and vector fields; sand that '
     '"displaces and flows, almost like a liquid"', 'https://www.gdcvault.com/browse/gdc-12/play/1015655'),
    ('Indiana Jones and the Great Circle (preview): a tomb room filling with sand as a set piece', 'https://godisageek.com/2024/08/indiana-jones-and-the-great-circle-looks-authentic-and-awesome-hands-off-preview/'),
    ('SideFX, Voronoi fracture: uneven pieces from uneven seed points, fused irregularly; even pieces read as a grid',
     'https://www.sidefx.com/docs/houdini/dyno/voronoifracture.html'),
    ('Follow-through and overlapping action: parts move at their own rates, offset in time, not in lock step',
     'https://rebusfarm.net/blog/follow-through-and-overlapping-action-the-animation-principle-that-prevents-stiff-motion'),
]

FOUND = ('Looked at in game first: rows of cracked slabs over one pit are two slabs (294 on floors 3 to 30, seeds 801-803), three over a pit two '
         'storeys deep (25) or five, the side passage\'s chain (37); none of four. Their timing is the game\'s and stays: he sets a row off at his '
         'running pace (a slab every 0.32 s), a chain counts down a slab every 0.36 s. What read as a machine, in the strips: (1) the sand\'s '
         'surface was one ruler-straight slope at exactly the angle of repose from the first crater to the far wall, its foot stepping one '
         'slab further at each break; (2) once drained, the heaps between the outlets were identical sharp triangles, a saw blade; (3) every '
         'slab leaned on its far edge by the same small angle, so the row stood as an even staircase, and each went the same way: whole, '
         'turning about the same edge at the same rate, one after another at equal intervals; (4) nothing happened between the breaks: no '
         'sand ran through the seams of the slabs still standing and no dust rose from the holes. With two slabs there is one break of each '
         'kind (the first folds in two, the second tips into it), so nothing repeats and it reads well.')
FIX = [
    'One body that sags: over the rows of three or more (two keep round 21b\'s look exactly) the level sinks most over each outlet that has '
    'opened (a soft dip growing over 0.3 s), with a low swell over the rest; the craters, the level and the heaps are joined by soft '
    'maximum and minimum (the blend\'s slope is a mix of the two, never steeper), so the brink is rounded and the toe eases out. A crater is '
    'a funnel, at the angle of repose at its throat and flattening outward (no straight run); each outlet sits a few px off the slab\'s middle '
    'and its wall has its own steepness (0.86 to 1 of the angle of repose), and slumps flatter in four small avalanches at moments of its '
    'own (only ever flatter: the sand never comes back). The heaps left between outlets are low rounded mounds, each at its own slope.',
    'Each slab its own: how far it leans on the sand it has lost, how soon it starts, and how it tips on as its break nears (0.14 to 0.30 rad) '
    'are seeded numbers of its column and row. Most (85%) break across their own flaw as they tip: a crack at its own place across the slab '
    'with its own kinks, the piece over the hole turning down on the crack while the far piece still rests on the next slab; when it lets go, '
    'the far piece hangs on the rim a moment (to 0.11 s) and turns at its own rate, the near piece goes first. The first slab of a row folds '
    'in two halves of unequal size turning unequally.',
    'Between the breaks: sand runs through the seams and the crack of a slab before it goes (from a moment of its own, a chain\'s slab a '
    'little before its countdown ends), beating unevenly, most at the side it is losing; small lit tongues of loosened sand slide down the '
    'crater walls while the well runs, each wall on its own beat; dust tumbles out of each hole as its slab goes, each cloud its own size.',
    'Look only: every slab breaks exactly when it did (f.s, f.tm, the 0.5 s, DROP_G), the hit boxes and the bot are unchanged. The surface is '
    'still found by wellSolve from the slabs\' own clocks (the angle of repose, and the sand left equal to what was there less what ran out); '
    'every seeded number is a hash of the slab\'s column and row: a rewind gives the same picture. No allocation a frame (the crack\'s points '
    'in one array, its numbers cached once per slab); both modes; the relief is rubbed over the sand as before (glRelWell).',
]
TESTS = ('wellscan floors 3 to 30, three seeds: ok (slope never over the angle of repose, the sand never grows back, every slab breaks at 0.5 s, '
         'and the rewind gives the same surface for the first row of two and now also for the longest row of three or more). rendersmoke floors 7 '
         'to 9, both modes: no errors (0.65 ms/frame). run2 floors 3 to 6: 4 of 4 passed, 0 runs with damage (0.04 ms/frame). rewindrooms: '
         'FAILURES 0. A rewind half way through the chain of five, in both modes, puts back the same slabs, pieces and sand.')


def sections(D, REL, img):
    return ['<section class="card" id="r26d"><h2>Round 26d: sand that gives way as one body</h2>'
            '<p>Owner: "the domino sand effect needs to be more organic and less mechanically domino. On two columns of sand it works, on more '
            'than two it doesn\'t."</p>'
            '<h3>What was found</h3><p>' + E(FOUND) + '</p>'
            '<h3>The fix</h3><ul>' + ''.join('<li>%s</li>' % E(t) for t in FIX) + '</ul>'
            '<h3>Research</h3><p>Sand under a cover does not fail cell by cell: in cover-subsidence it ravels down into the void and the surface '
            'sags as one broad dip; in cover-collapse the cover spalls, arches and gives way piece by piece. A draining silo or hourglass runs at '
            'a steady rate whatever stands above (Beverloo) and opens a funnel-shaped crater whose walls stand at the angle of repose and grow '
            'by intermittent avalanches, not a fixed, clean cone, and stagnant sand stays by the walls. Fractured stone reads as natural when its '
            'pieces are uneven (uneven seeds, irregular fusing); a regular grid of equal pieces reads as made. Games that sell flowing sand (Journey, '
            'Uncharted 3\'s desert) layer many small, independently timed motions over the big shape. Animation\'s overlapping action is the same '
            'idea: parts move at their own rates, offset in time. Here the play\'s rhythm is fixed (his pace, the chain\'s countdown), so the variety '
            'is in how each slab and each wall moves within it.</p>' + links(SOURCES) +
            fig(img, 'r26d_sand.png', 'Before | after, Torchlight and Classic, a frame every 0.1 s (five slabs: 0.2 s) from the first slab set off: '
                'two slabs (unchanged), three slabs two storeys deep set off at his running pace, the side passage\'s chain of five') +
            fig(img, 'r26d_sand.gif', 'In game (Torchlight), before | after: floor 5\'s side passage armed, the prince runs across the row of five '
                'as it gives way behind him') +
            '<h3>Tests</h3><p>' + E(TESTS) + '</p>'
            '<p class="meta">Retired to keep the page at 505 pictures: round 8\'s gate-clock pictures of the two clock concepts not built, '
            'r8_clock_B_gate.png and r8_clock_C_gate.png.</p></section>']
