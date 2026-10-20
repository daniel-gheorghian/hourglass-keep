# egyptround21b.py: round 21b's section of egypt_themes.html (built in): the sand under cracked slabs, which carried the wall's art and
# stood in vertical walls between slabs. Pictures from egyptr21b.py.
import html
E = html.escape


def links(src):
    return '<ul>' + ''.join('<li><a href="%s">%s</a></li>' % (E(u), E(l)) for l, u in src) + '</ul>'


def fig(img, f, cap):
    return '<figure>%s<figcaption>%s</figcaption></figure>' % (img(f, cap), E(cap))


def sections(D, REL, img):
    return ['<section class="card" id="r21b"><h2>Round 21b (built in): sand that looks like sand, and a row of slabs that drains as one body</h2>'
            '<p>Two bugs from the owner\'s phone, both about the sand under cracked slabs (round 16a\'s sand well: a pit walled in on both sides under '
            'a loose slab). Look only: when each slab gives way, how it falls, every hit box and timing, the generator and the bot are unchanged.</p>'
            # ---- 1
            '<h3>1. "Sand has wall motif"</h3>'
            '<p><b>Which fill</b>: the owner\'s picture is the sand well under a row of five cracked slabs (a side passage\'s chain, floor 5 has the same). '
            'The sand lift\'s column had the same fault. <b>Cause</b>, two parts. In Torchlight the relief pass, which embosses the stone by reading the room\'s '
            'static picture, read the back wall\'s courses and friezes behind the sand and raked the lamp light across them on the sand\'s face: the arcade frieze '
            'and the wall\'s joints stood out on it (the sand itself is drawn opaque; switching the relief off removed the art). In both modes the sand was drawn '
            'cell by cell with ruled lines every 9 px across each cell and a seam at each cell\'s edge: courses of masonry.</p>'
            '<p><b>Fix</b>: the relief is rubbed back over the sand in view (<code>glRelWell</code>, <code>glRelBox</code>, as a stone slab already was: cell by '
            'cell from the sand\'s surface down to the shaft\'s floor; the sand lift\'s column too), so only the wall above the sand keeps its relief. The sand\'s '
            'cut face is one tile of sand per theme (<code>sandTex</code>, 64 world px at 4 px each, so it stays smooth at the phone\'s scale and at GLP.rs 0.5): '
            'fine grains (pale quartz, darker lithic and iron-stained grains, a few dark heavy minerals), a soft mottling of packing, and faint, broken, nearly '
            'level laminae where it settled as it was poured (thin dark fine-grained bands as in sand cross-sections, never even courses). A row of slabs is drawn '
            'as one face with no seams; it is darkened toward the shaft\'s floor by one cached ramp, and at rest it has settled 1.5 px under the slabs, in their '
            'shadow. No gradient or canvas is made per frame.</p>' +
            fig(img, 'r21b_rest.png', 'At rest: the chain of five (floor 5) and three slabs over a two-storey pit (floor 7), Torchlight at rs 1 and 0.5 and '
                'Classic, then the face at 2x, then the sand lift\'s column: before (v68) and after') +
            # ---- 2
            '<h3>2. "The edge between them cannot be vertical; the sand doesn\'t hold up like that"</h3>'
            '<p><b>Cause</b>: each slab\'s cell had its own column of sand that drained on its own clock (a flat level falling at <code>WELL_V</code>), so a drained '
            'cell stood beside a full one behind a vertical wall of sand (and the wall\'s art showed on it).</p>'
            '<p><b>How sand behaves</b>: dry sand cannot stand steeper than its angle of repose (about 34 degrees; a slope pushed past it fails in an avalanche '
            'that leaves it at that angle). A flat-floored silo emptying through one outlet runs in funnel flow: the sand over the outlet flows in a core, a '
            'crater opens at the surface with walls at the angle of repose, the surface of the whole volume sinks as its edges slide into the crater, and the '
            'sand that lies below the angle of repose from the outlet (the stagnant zones in the corners) stays as heaps. The rate through the outlet is steady '
            'whatever stands above it (Beverloo). A slab resting on sand and on the next slab at its far edge, whose sand goes on the near side, pivots on the far '
            'edge into the hole: a domino toward the first hole. Shadowed slopes look darker; flowing grains streak down the crater walls.</p>'
            '<p><b>Fix</b> (<code>wellGroup</code>, <code>wellSolve</code>, <code>drawWellGroup</code>): the slabs side by side over one pit are one body of sand. '
            'Each slab opens the outlet under it when it is triggered (as before); <code>wellSolve</code> finds the surface every frame from the slabs\' own '
            'clocks alone (state and time: a rewind or a respawn restores it): over each open outlet a crater, its walls never steeper than the angle of repose '
            '(<code>WELL_SL</code> 0.67), the residual heaps at that angle, and the level of all the rest, set so the sand left equals the sand there was less '
            'what has run out (bisection over 2 px samples, no allocation). The whole volume runs out in the time one storey of a cell took before, so the shaft '
            'under a broken slab is clear when it falls. The surface is drawn seen from above along the depth diagonal: slopes facing the lamps lit, slopes '
            'facing away darker, the flat sand under a slab in its shadow, grains running down to each throat; the outlet in the foot of the back wall.</p>'
            '<p><b>The domino within the game\'s timing</b>: a slab still falls only when the game lets it (stepped on, or a chain\'s countdown), 0.5 s later, '
            'and he may walk on it until then, so a neighbour cannot drop early. While it is still floor it leans into the hole beside it, pivoting on its far '
            'edge, by at most 0.08 rad (2.5 px at its open edge) as the sand under that edge slumps away, sand running off the edge while the volume drains; '
            'once it is set off it tips on to 0.22 rad over its half second and then falls turning into the hole (up to 0.7 rad) as one piece, not folding in '
            'two. The first slab of a row (sand on both sides) still sags and folds over its crater as in round 16a. Run over a row, or a chain counting down, '
            'and the slabs go one after another toward the first hole while the whole volume sinks.</p>' +
            fig(img, 'r21b_collapse.png', 'The chain of five giving way (every 0.4 s) and three slabs of a deep pit set off 0.2 s apart (every 0.2 s), '
                'Torchlight and Classic: before (v68) and after') +
            fig(img, 'r21b_collapse.gif', 'The chain of five, Torchlight: before | after') +
            '<p><b>Tests</b>: new <code>wellscan.py</code> (floors 3 to 30, three seeds, 356 rows of two to five slabs, each set off at either end and in the '
            'middle: no slope steeper than the angle of repose, the sand never grows back, every slab breaks exactly 0.5 s after its trigger, a snapshot put back '
            'mid-drain gives the same surface: ok), <code>run2.py</code> 5 to 7, two seeds (all passed, no damage), <code>slabresume.py</code> (0 bad), '
            '<code>rewindrooms.py</code> (0 failures), <code>rendersmoke.py</code> 5 to 7 both modes (no errors; 0.53 against 0.50 ms a frame for the v68 release). '
            'Retired from the page to stay at 505 files: round 10\'s two Torchlight crops at the phone\'s size and its running clip.</p>' +
            links([('Angle of repose (dry sand about 34 degrees)', 'https://en.wikipedia.org/wiki/Angle_of_repose'),
                   ('Al-Hashemi and Al-Amoudi 2018: a review on the angle of repose of granular materials (Powder Technology 330)', 'https://pure.kfupm.edu.sa/en/publications/a-review-on-the-angle-of-repose-of-granular-materials/'),
                   ('Jaeger, Nagel and Behringer 1996: granular solids, liquids and gases (Rev. Mod. Phys. 68; avalanches past the angle of repose)', 'https://doi.org/10.1103/RevModPhys.68.1259'),
                   ('Beverloo law: the rate does not depend on the fill height (Staron, Lagree, Popinet: the granular silo as a continuum plastic flow)', 'https://ar5iv.labs.arxiv.org/html/1211.5916'),
                   ('Flow in an hourglass: steady until the funnel-shaped surface nears the outlet', 'https://arxiv.org/pdf/2104.08186'),
                   ('Funnel flow: a flowing core, stagnant zones by the walls and a surface depression over the outlet (arXiv 2210.14115)', 'https://arxiv.org/pdf/2210.14115'),
                   ('A numerical study of wall pressure and granular flow in a flat-bottomed silo (flow channel and stagnant zones)', 'https://www.pure.ed.ac.uk/ws/files/22087536/A_numerical_study_of_wall_pressure_and_granular_flow_in_a_flat_bottomed_silo.pdf'),
                   ('Hunter 1977: basic types of stratification in small eolian dunes (grainflow and grainfall laminae)', 'https://biblio.library.oregonstate.edu/node/73206'),
                   ('Loope: pin-stripe laminae and grainflow tongues in the Navajo Sandstone', 'https://eas2.unl.edu/~dloope/pdf/DownslopeCoarsening.pdf'),
                   ('Lekner and Dorf 1988: why some things are darker when wet (Applied Optics)', 'https://www.wgtn.ac.nz/scps/staff/pdf/darkerwhenwet.pdf'),
                   ('Oblique projection', 'https://en.wikipedia.org/wiki/Oblique_projection')]) + '</section>']
