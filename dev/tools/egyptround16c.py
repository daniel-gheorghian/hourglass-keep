# egyptround16c.py: round 16c's section of egypt_themes.html (built in): the lift's mouth, the portcullis's modelling, the exit stairs,
# and wall art over openings. Pictures from egyptr16c.py and openscan.py; the scans' counts in egypt_themes/r16c.json.
import html, json, os
E = html.escape


def links(src):
    return '<ul>' + ''.join('<li><a href="%s">%s</a></li>' % (E(u), E(l)) for l, u in src) + '</ul>'


def fig(img, f, cap):
    return '<figure>%s<figcaption>%s</figcaption></figure>' % (img(f, cap), E(cap))


def sections(D, REL, img):
    J = json.load(open(os.path.join(D, 'r16c.json')))
    os_ = J['openscan']; st = J['stairscan']
    scan = ('<table><tr><th>openscan.py, floors 1-48, seed 4400+n</th><th>Torchlight before</th><th>after</th><th>Classic before</th><th>after</th></tr>' +
            ''.join('<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (E(k), os_['before'][k]['torch'], os_['after'][k]['torch'], os_['before'][k]['classic'], os_['after'][k]['classic'])
                    for k in ('windows', 'gate openings (portcullis down)', 'lift mouths (slabs down)')) +
            '<tr><td>doors (doorscan.py, round 15)</td><td colspan="4">0 of 192 door views, unchanged</td></tr></table>')
    return ['<section class="card" id="r16c"><h2>Round 16c (built in): the lift\'s mouth, the portcullis\'s edge, the exit stairs, art over openings</h2>'
            '<p>Owner: the top mouth of the lift in the round 14 picture looks sheared; the portcullis\'s thickness should be modelled by the light from the left so its edge is clearly visible; '
            'check the exit stairs\' step height in every theme; extend the scan for decoration over openings to windows, gate openings and lift mouths.</p>'
            '<h3>The lift\'s mouth</h3><ul>'
            '<li><b>Why it looked sheared.</b> Four things, all in the drawing of the mouth slab (play is unchanged). (1) A slab on the shaft\'s left edge was drawn before everything in the shaft, '
            'so the shaft\'s back-wall shade, the counterweight\'s channel and the counterweight were laid over the back half of its broad face, which is the shaft\'s own side wall: the slab looked cut along a slant. '
            '(2) The call plate\'s cell was then covered by drawing the slab\'s foot a second time in a band: its translucent shading doubled there and the ropes in front vanished, a step across the slab. '
            '(3) Its shadow on the floor, cast away from the light, fell into the open shaft and hung there as a tilted plank. (4) The wear chips on its corners were a share of the edge, so on a slab 60 px tall a chip was a 15 px dark slit that split it in two.</li>'
            '<li><b>Now.</b> Across the corridor: the platform in its shaft, the slab whole, then the floor tile; the slab on the left edge is drawn after the back wall and before the ropes, beam and platform; '
            'the plate\'s cell is cut round the slab instead of the slab being drawn again; the floor shadow falls only on floor; chips are at most 3 px. In the oblique view (depth up and to the right, the front face true) '
            'the slab\'s broad face and the shaft\'s side are one plane, its top and foot run along the depth diagonal like the floor tiles\' edges.</li>'
            '<li>The paternoster has no mouth slabs; the sand lift\'s slab is a floor slab of the theme\'s stone and its hole shows the cut floor\'s side. <code>liftscan.py</code> and <code>lifttest.py</code> pass.</li></ul>' +
            fig(img, 'r16c_lift.png', 'A counterweight lift (Nun, floor 3), platform half way: before and after, Torchlight and Classic, 2x; under them mouths in the Blue Chambers, the Green Hall and the Forges with the platform at the top, half way and at the bottom, the sand lift and the paternoster (1:1)') +
            '<h3>The portcullis\'s edge</h3><ul>'
            '<li><b>Light on a box.</b> A block lit from one side shows a lit face, a face in shade whose darkest band (the core shadow) lies next to the edge between them, and a cast shadow that is sharp at its foot (drawing guides on form and cast shadow). '
            'The narrow face toward the key light is now lit more (with a floor of 0.18 even under a weak lamp), the arris is wider and brighter, the broad face carries a core-shadow band beside it and a dark line along its far edge and foot, and the cast shadow on floor and wall is darker. The theme\'s stone and emblem are the same; the broad face is only a little darker so the emblem keeps reading.</li>'
            '<li><b>The wall printed on the slab.</b> The scan below found what most hid the edge in Torchlight: the relief, which takes its bumps from the room\'s picture, embossed the back wall\'s courses, tiles and friezes on any slab that was down (only a gate on the move was rubbed back, by an ellipse). '
            'A slab that is down (portcullis or lift mouth) is now rubbed out of the relief over its whole box (<code>glRelSlab</code>). Aswan granite is pink feldspar with grey quartz and black biotite: speckled, with no courses of its own.</li>'
            '<li>The top corner still runs up in front of the ceiling block\'s side face (round 14); a lift\'s left mouth slab does the same where the shaft is open above it.</li></ul>' +
            fig(img, 'r16c_gate.png', 'The portcullis down in all twelve themes at 1:1: Torchlight before, after; Classic before, after; then Nun, the Green Hall, the Wells and Shali at 2x (Torchlight, then Classic; before left, after right)') +
            '<h3>The exit stairs</h3><ul>'
            '<li><b>Measured.</b> <code>stairscan.py</code> plants him on treads 1 to 4 on every floor 1-48 and finds his lowest pixel against the drawn tread\'s front edge in the render. '
            'The stairs are drawn the same in every style and theme, and the rise per tread was right (6.2 + 1.76 px), but his feet were %s px below the tread\'s edge (mean, in the riser), on all styles alike: he stays at the floor\'s middle depth while the treads start inside the doorway, behind the back wall. '
            'And the stride ran on while he stood, so a planted foot slid %s px. Now the first step also lifts him that depth onto the tread, and the stride moves only while he rises: feet %s px from the edge (on the tread), slide %s px; %s.</li></ul>' % (
                st['before_gap'], st['before_slide'], st['after_gap'], st['after_slide'], E(st['after_result'])) +
            fig(img, 'r16c_stairs.png', 'Planted on the first and third tread in the five drawing styles (Nun, the Halls, the Blue Chambers, the Forges, the Green Hall): before (above) and after, Classic, 2x') +
            '<h3>Art over openings</h3><p><code>openscan.py</code> compares each opening with the same frame drawn without the back wall\'s art (<code>EGP.noart</code>; for windows without what is hung after them, <code>EGP.noover</code>): '
            'a view is bad when more than 6 pixels inside differ. Windows were clean (hangings and lamp scars are already placed off them). The gates and lift mouths were the relief\'s embossing above.</p>' + scan +
            fig(img, 'r16c_scan.png', 'openscan.py before the fix: the worst views, the back wall\'s courses and tiles printed on the slabs (Torchlight)') +
            links([('Oblique projection (cabinet and cavalier: the front true, depth along a diagonal)', 'https://en.wikipedia.org/wiki/Oblique_projection'),
                   ('Proko, how to shade: core shadow, cast shadow, edges', 'https://www.proko.com/course-lesson/how-to-shade-a-drawing/'),
                   ('Light and shadow on a cube: highlight, core shadow, cast shadow sharp near the form', 'https://instructables.com/Light-and-Shadow'),
                   ('The Epigraphic Survey (Karnak hypostyle): sunk relief shows best in raking light; drawn as lit from the upper left', 'https://www.memphis.edu/hypostyle/project/epigraphy-methods.php'),
                   ('Raking light (Conservation Wiki)', 'https://conservation-wiki.com/wiki/Raking_light'),
                   ('Aswan granite: alkali feldspar, plagioclase, quartz, biotite, hornblende (Egyptian geology paper)', 'https://journals.ekb.eg/article_30777.html'),
                   ('Granites of ancient Egypt: coarse, pink to red monumental granite (Hall of Maat)', 'https://www.hallofmaat.com/granite-hornblende-biotite-granite-monumental-red-granite-red-granite-rose-granite-pink-granite-monumental-black-granite-black-granite-grey-granite-syenite-pyrrhopoecilon/'),
                   ('Khufu\'s antechamber: granite portcullis slabs in grooves', 'https://ancientegyptonline.co.uk/kingschambergp/')]) + '</section>']
