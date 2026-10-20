# egyptround20b.py: round 20b's section of egypt_themes.html (built in): the prince's blade and kilt on all fours, the portcullis slab's
# flickering light, and a softer blade shadow down a beam in Classic. Pictures and numbers from egyptr20b.py.
import html, json, os
E = html.escape


def links(src):
    return '<ul>' + ''.join('<li><a href="%s">%s</a></li>' % (E(u), E(l)) for l, u in src) + '</ul>'


def fig(img, f, cap):
    return '<figure>%s<figcaption>%s</figcaption></figure>' % (img(f, cap), E(cap))


def table(J):
    rows = J.get('num', [])
    if not rows:
        return ''
    c = lambda d: '%.2f / %.2f' % (d['narrow'], d['broad'])
    return ('<table><tr><th>Slab</th><th>Theme</th><th>Before (v67), rs .5</th><th>After (20b), rs .5</th><th>Before, rs 1</th><th>After, rs 1</th></tr>' +
            ''.join('<tr><td>floor %d (seed %d), column %d</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (q['n'], q['sd'], q['c'], E(q['name']), c(q['old_rs0.5']), c(q['new_rs0.5']), c(q['old_rs1']), c(q['new_rs1'])) for q in rows) + '</table>')


def sections(D, REL, img):
    J = json.load(open(os.path.join(D, 'r20b.json'))) if os.path.exists(os.path.join(D, 'r20b.json')) else {}
    sl = J.get('slabs', [])
    nf = (sum(1 for q in sl if q['flipsOld']), len(sl))
    return ['<section class="card" id="r20b"><h2>Round 20b (built in): the blade and the kilt on all fours, the slab\'s flickering light, a softer blade shadow</h2>'
            '<p>Three bugs from the owner\'s phone. Look only: the generator, floors, moves, hit boxes, timings and the bot are unchanged.</p>'
            # ---- 1
            '<h3>1. "Transparent sword and the prince\'s ass showing"</h3>'
            '<p>The pose is <i>crouch with the blade drawn low</i> (crouch, then Grab: for a snake in a tunnel), on hands and knees (<code>crawlPose</code>, '
            '<code>P.lowSword</code>). <b>The blade, cause</b>: the prince\'s straight bronze sword was one thin curved sliver, about 1.5 px wide at the figure\'s '
            'scale, filled in one flat tan (<code>#cda26a</code>) almost the colour of the sandstone floors it lies on when he holds it low; its 1.1 px outline '
            'covered most of it, so at the phone\'s scale (and at GLP.rs 0.5) only the dark outline read: a curve with the floor showing through. It was never a '
            'missing fill or the metal mask. The khopesh, the axes, the clubs and the skeleton\'s blade are broad enough and were not touched. <b>Fix</b>: the blade of the '
            'period, a straight leaf-shaped bronze blade with a midrib (the New Kingdom\'s long swords and dirks), about 3 px wide, drawn as its two bevels: the one '
            'turned up toward the light bright bronze (tinted by the key light), the other dark bronze, with a bright line where the lit edge catches the light, and a '
            'pommel. Polished metal shows mostly what it reflects (the dark room) and a sharp highlight, not a flat mid-tone, so the blade now reads on a pale floor and '
            'on a dark wall alike, in both modes and at every scale.</p>'
            '<p><b>The kilt, cause</b>: the shendyt is drawn round the hips from the waist to the back of the thigh. On all fours the hips are flexed to about 90 degrees: '
            'the thighs\' round tops (drawn round the hip joint) stood out behind that line, a bare round under the kilt\'s back edge. A wrapped linen kilt is pulled '
            'taut over the buttocks when a man kneels or crawls (the reliefs\' and the kneeling statues\' kilts stretch over the seat and the thighs), so <b>fix</b>: '
            'once both hips flex past about 50 degrees (it fades in from <code>lean+h</code> 0.8 to 1.2), a seat point goes in at the hip\'s place along the kilt\'s back '
            'edge, out just far enough that the drawn curve clears the round by 0.4 px, and a faint tension fold runs from the seat toward the front of the hem. '
            'Every other pose is as it was (crouch, landing and the low leaps get the same small round over the seat; hanging, falling, climbing, kicking, death and '
            'the fight poses are unchanged and showed no skin).</p>' +
            fig(img, 'r20b_prince.png', 'On all fours with the blade drawn low, floors 7 and 3: Torchlight at rs 1 and 0.5, Classic, before and after; '
                'the figure alone at 6x (crawling, the low blade, the thrust); the blade in the fight\'s poses on a pale and a dark ground') +
            # ---- 2
            '<h3>2. "The door slab was flicking between highlighted back and side"</h3>'
            '<p><b>Cause</b>: the granite portcullis (<code>egSlab</code>) is shaded as a block in the oblique view, its narrow face and its broad face lit or in shade '
            'by which side the key light comes from (<code>keyLight</code>). That picked the nearest lamp within 1.6 times its radius, and a lamp\'s radius flickers '
            '(150 px times 0.92 plus the flame\'s flicker). A slab near the edge of a lamp\'s reach switched every few frames between that lamp (lit from the right: '
            'the broad face bright) and no lamp (the default, lit from the left: the narrow face bright), and one between two lamps switched between them. At 30 fps it '
            'reads as the slab flashing. Not the scale, the relief or round 20a\'s beam blocker: it does it at rs 1 too, and in Classic. Replaying the old choice on '
            'floors 5 to 12 (three seeds each, 30 frames): %d of %d slabs changed side within a second. The figures used the same choice for their lit side (O._lx), '
            'so a guard or the prince standing there flickered the same way.</p>'
            '<p><b>Fix</b>: the light\'s direction is no longer one lamp\'s but the balance of all of them in reach (<code>keyLight</code>\'s <code>sx</code>, -1 to 1): '
            'each pulls toward its side by a smooth falloff of its distance over its <i>steady</i> radius (the flame\'s flicker stays in the light map, where it belongs), '
            'with a weak constant pull from the left for the old default, so it is continuous in the lamps\' places and still in time. The slab\'s faces cross-fade '
            'by it (<code>uL</code>, eased over sx -0.35 to 0.35): with lamps in balance both faces are lit alike and its cast shadow shrinks to nothing, which is what a '
            'block between two equal lights looks like (Lambert: each face takes the light that falls on it). This is how games light sprites and moving objects from '
            'several lights: a weighted blend that fades a light in as it comes into reach, never a switch to the nearest (nearest-probe lookup is known to pop; Unity '
            'and Enlighten interpolate between probes). The figures take the same continuous direction.</p>'
            '<p>Frame-to-frame change of the faces\' brightness, narrow / broad (mean absolute change of Rec. 601 luma per frame at 30 fps, 60 frames, Torchlight):</p>' % nf + table(J) +
            fig(img, 'r20b_slab.png', 'Two slabs that flickered, Torchlight at rs 0.5: ten consecutive frames at 30 fps before and after, and the faces\' brightness frame by frame') +
            # ---- 3
            '<h3>3. A softer blade shadow down a beam (Classic)</h3>'
            '<p>Round 20a cut a slicer\'s blades and their shadow out of a sky beam in Classic as one hard-edged wedge, the blade swept along the light all the way to '
            'the floor. The light through an opening comes from an area, not a point: behind a thin blade the umbra ends within a few blade widths and the penumbra '
            'widens and fades with distance. <b>Fix</b> (<code>ryHull</code>, <code>RY_SH</code>): five hulls, each the blade swept a growing share of the way to the '
            'floor (12 to 72%) and spread more about its middle (8 to 70%); the beam is drawn once per layer at a fifth of its strength, each cut by its own hull, so '
            'the shadow is whole at the blade and fades and widens to nothing short of the floor. Clips only, no scratch canvas (20a measured 4 ms a frame for one); '
            'only beams that a blade is in draw the extra layers. Torchlight is unchanged.</p>' +
            fig(img, 'r20b_blade.png', 'Classic, two themes: before (v67, no shadow), round 20a (the hard wedge), after') +
            '<p><b>Tests</b>: <code>run2.py</code> 7 and 8 (two seeds: all passed, no damage), <code>rendersmoke.py</code> 7 to 10 (both modes, no errors), '
            '<code>openscan.py</code> floors 1 to 24 (gates, windows and lift mouths: 0 bad), <code>beamwall.py</code> (unchanged against round 20a), <code>bench.py</code> '
            'floors 7 and 10 in both modes (unchanged against round 20a). Retired from the page to stay at 505 files: round 10\'s two round 9 crops and its round 9 '
            'Torchlight fight crop.</p>' +
            links([('The Met: bronze sword, New Kingdom, 18th Dynasty, from Thebes (52 cm, straight)', 'https://www.metmuseum.org/art/collection/search/545558'),
                   ('World History Encyclopedia: Egyptian bronze sword (the Met\'s piece)', 'https://www.worldhistory.org/image/13566/egyptian-bronze-sword/'),
                   ('British Museum EA5425: bronze sword', 'https://www.britishmuseum.org/collection/object/Y_EA5425'),
                   ('Artists Network: painting metallic surfaces (values come from what the metal reflects)', 'https://artistsnetwork.com/art-mediums/oil-painting/painting-metallic-surfaces-gold-silver-bronze'),
                   ('Shendyt (the wrapped kilt)', 'https://en.wikipedia.org/wiki/Shendyt'),
                   ('Clothing in ancient Egypt', 'https://en.wikipedia.org/wiki/Clothing_in_ancient_Egypt'),
                   ('Unity manual: light probes for moving objects (interpolated, not nearest)', 'https://docs.unity3d.com/2021.1/Documentation/Manual/LightProbes-MovingObjects.html'),
                   ('jMonkeyEngine: BasicProbeBlendingStrategy (the nearest probe pops on moving objects)', 'https://javadoc.jmonkeyengine.org/v3.6.0-beta3/com/jme3/light/BasicProbeBlendingStrategy.html'),
                   ('Enlighten: probe interpolation', 'https://documentation.enlighten.siliconstudio.co.jp/wiki/spaces/SDK310/pages/904999378/Probe+interpolation'),
                   ('Shadow: umbra and penumbra of an extended source', 'https://en.wikipedia.org/wiki/Shadow'),
                   ('Oblique projection', 'https://en.wikipedia.org/wiki/Oblique_projection')]) + '</section>']
