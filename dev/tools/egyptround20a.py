# egyptround20a.py: round 20a's section of egypt_themes.html (built in): three owner bugs in Torchlight's light and shadow. Sky beams on a low
# ceiling's face, beams through a slicer's blades, the figure's shadow on a low ceiling's face. Pictures and numbers from egyptr20a.py.
import html, json, os
E = html.escape


def links(src):
    return '<ul>' + ''.join('<li><a href="%s">%s</a></li>' % (E(u), E(l)) for l, u in src) + '</ul>'


def fig(img, f, cap):
    return '<figure>%s<figcaption>%s</figcaption></figure>' % (img(f, cap), E(cap))


def table(J, kind, key):
    rows = [q for q in J.get('num', []) if q['kind'] == kind]
    if not rows:
        return ''
    f = lambda v: '-' if v is None else '%.1f' % v
    return ('<table><tr><th>Floor</th><th>Theme</th><th>Before (v67)</th><th>After (20a)</th></tr>' +
            ''.join('<tr><td>%d (seed %d)</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (q['n'], q['sd'], E(q['name']), f(q['old'][key]), f(q['new'][key])) for q in rows) + '</table>')


def sections(D, REL, img):
    J = json.load(open(os.path.join(D, 'r20a.json'))) if os.path.exists(os.path.join(D, 'r20a.json')) else {}
    return ['<section class="card" id="r20a"><h2>Round 20a (built in): beams through low walls and blades, a shadow on a near face</h2>'
            '<p>Three bugs from the owner\'s phone, all in Torchlight\'s light and shadow (Classic had the first two as well). Look only: the generator, floors, moves, '
            'hit boxes, timings and the bot are unchanged. The picture sheets are crops of the 1704 px canvas, before (the v67 release) and after, and Torchlight at GLP.rs 0.5 '
            '(the scale the owner\'s phone ran at). The rule behind all three is the oblique view\'s: a block\'s front face stands on the front plane, nearer than anyone walking '
            'the corridor at mid-depth, and nearer than any light or shadow that lies behind it; a thing that stands across the room\'s whole depth is solid to the light at every depth.</p>'
            # ---- 1
            '<h3>1. "Light beams through low wall"</h3>'
            '<p><b>Cause</b>: the stone over him in the picture is a <i>low ceiling</i>, the roof of a crawl tunnel (feature <code>low</code>): a block 30 px high in the top of an open cell, '
            'its face drawn HX left of the cell like a wall\'s (<code>lowCeil</code>). The beams know the level from a tiny texture of its tiles (walls in red) and round 15 cut their light '
            'off every wall block\'s face, but a low ceiling is not a wall tile, so it was missing from that texture: the beam\'s haze and light lay on its face in a band (the wall above '
            'it was cut, which made the band\'s top edge), and the beam was not stopped by it either, so it went on to the floor under the tunnel\'s roof. '
            '<b>Fix</b>: a low ceiling is in the tile texture as its own value (<code>LOW_R</code>), read exactly (<code>lowC</code>): no beam, haze, footprint or rim on its face (the face\'s '
            'lower edge taken as the share of each pixel above it, so it is smooth at every scale), and the shader\'s march treats its block as stone between a pixel and the opening '
            '(three taps across, for a soft end that widens with distance), so only the light that really gets in under its edge at the tunnel\'s mouth lights the floor and the air '
            'under it. Classic cuts the face and, past the tunnel\'s first cell, the space under it, and drops the footprint there (<code>ryLow</code>); the soft bounce light where a beam '
            'lands is dropped when a low ceiling stands in the way (<code>solidFront</code>).</p>'
            '<p>Beam light on the low ceilings\' faces in view (Torchlight, rs 1; the frame with the beams minus the frame without them, mean of R+G+B over the faces\' pixels; '
            'the mist, caustics and sheen off in both):</p>' + table(J, 'low', 'beam') +
            fig(img, 'r20a_low.png', 'Beams over a tunnel\'s roof, the prince crawling under it: three floors, Torchlight and Classic, before and after; below, Torchlight at GLP.rs 0.5') +
            # ---- 2
            '<h3>2. "Light beams through guillotines"</h3>'
            '<p><b>Physically</b>: a slicer\'s blades (and a granite portcullis) are drawn on a plane that runs across the corridor\'s whole depth, from the floor\'s front edge to the back '
            'wall (<code>plane()</code>), so like a wall they are solid to the light at every depth. The haze in the air in front of the blade (nearer the eye) is still seen over it; the '
            'haze behind it is hidden by it; and the beam beyond it, down the light, is in its shadow. In real light shafts this is how god rays get their dark streaks: '
            'the occluders between the medium and the light (GPU Gems 3 ch. 13; Mitchell\'s light shafts). <b>Cause</b>: the beams were cut only by walls and figures; '
            'the blade got the whole depth\'s haze laid over it (it read pale, as if translucent) and the beam went on through it. <b>Fix</b>: '
            '<code>beamBlockers</code> gives each blade (and each slab that is down) as a quad from the same geometry the drawing uses. Torchlight tests them exactly in the shader '
            '(<code>u_bk</code>, <code>blkC</code>, not through the eighth-size figures\' mask: tried first, its texels left a staircase along the blade): over a blade only the near half '
            'of the haze, no footprint and no figure light; in the march a blade between a pixel and the opening shades it, softened over at least the march\'s step (a thin blade between '
            'two samples left a staircase too) and more with distance. Classic, for a blade inside a beam\'s haze (<code>ryBlkLit</code>), clips the blade and its shadow, the quad swept '
            'along the light to the floor (<code>ryHull</code>), out of the haze and the footprint: a sharp edge, as a shadow in sunlight is near the thing that casts it '
            '(a softer cut through a scratch canvas was tried first and cost up to 4 ms a frame in headless Chromium when a figure and a blade were far apart).</p>' +
            fig(img, 'r20a_blade.png', 'A beam across a slicer, two themes (the second the owner\'s): Torchlight at rs 1 and 0.5, and Classic, before and after') +
            # ---- 3
            '<h3>3. "Shadow cast on the front facing wall"</h3>'
            '<p><b>Physically</b>: the lamp is on the back wall behind him; the low ceiling\'s front face faces the viewer, on the front plane, so it faces away from the lamp. A surface '
            'turned away from a light gets none of it (Lambert\'s cosine law, clamped at zero: an attached shadow), so a shadow cast by that light cannot show on it; it can only fall '
            'on surfaces the light reaches, the back wall and the floor\'s top. <b>Cause</b>: Torchlight casts each figure\'s shadow on the back wall (<code>glShadow</code>) and then carves '
            'the stone in front of the wall out of it, as drawn (round 19: walls\' faces, tops and sides; floors\' lips and tops), but not a low ceiling\'s block, which is not a wall '
            'tile. His head\'s shadow lay on its lit face. <b>Fix</b>: the carve takes in a low ceiling\'s front face and, at the tunnel\'s right end, its side face, exactly where '
            '<code>lowCeil</code> draws them (no figure-shaped stripe at an edge); the shadow still falls on the back wall under the roof. The guards share the code.</p>'
            '<p>Figure shadow on the low ceilings\' faces in view (Torchlight, rs 1; the frame without the shadow minus the frame with it):</p>' + table(J, 'lamp', 'shadow') +
            fig(img, 'r20a_shadow.png', 'A lamp casting his shadow toward a tunnel\'s mouth, three themes, Torchlight before and after, at rs 1 and 0.5') +
            '<p><b>Tests</b>: <code>beamwall.py</code> (round 15\'s walls: unchanged), <code>rendersmoke.py</code> 3 to 5 and 9 (both modes, no errors), <code>run2.py</code> 4 and 5 '
            '(two seeds: all passed, no damage), and the numbers above. Retired from the page to stay at 505 files: round 10\'s two v62 crops and its round 9 Classic fight crop.</p>' +
            links([('GPU Gems 3, ch. 13: Volumetric Light Scattering as a Post-Process (occluders cut the light along each ray)', 'https://developer.nvidia.com/gpugems/gpugems3/part-ii-light-and-shadows/chapter-13-volumetric-light-scattering-post-process'),
                   ('J. Mitchell, Light Shafts: Rendering Shadows in Participating Media (GDC 2004)', 'https://web.engr.oregonstate.edu/~mjb/cs557/Projects/Papers/LightShafts.pdf'),
                   ('Godot docs, 2D lights and shadows: occluders drawn to match the sprite\'s outline', 'https://docs.godotengine.org/en/4.4/tutorials/2d/2d_lights_and_shadows.html'),
                   ('A. Yuille, Lambertian lighting: attached and cast shadows (JHU lecture)', 'https://www.cs.jhu.edu/~ayuille/JHUcourses/VisionAsBayesianInference2024/23/Lecture23_LambertianLighting.pdf'),
                   ('Autodesk Maya: light and shadow in the real world', 'https://download.autodesk.com/global/docs/maya2014/en_us/files/BoL_Light_and_shadow_in_the_real_world.htm'),
                   ('SDLPoP seg008.c: wall fronts drawn in the foretable, in front of the Kid', 'https://github.com/NagyD/SDLPoP/blob/master/src/seg008.c'),
                   ('Oblique projection', 'https://en.wikipedia.org/wiki/Oblique_projection')]) + '</section>']
