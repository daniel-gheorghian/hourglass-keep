# egyptround27c.py: rounds 27c and 27d's section of egypt_themes.html. 27c: the guards' shadows and the beams on them (owner: "Soldiers don't
# seem to cast shadows and the light beams are drawn over them"; "it happens on all levels, torchlight graphics"). 27d: the slanted bars by the
# lamps (owner's screenshot, floor 10: "What are those slanted bars in the red circles? They are moving when the prince is running and are drawn
# over windows and light beams"). Pictures from egyptr27c.py (r27c_guards.png, r27d_bars.png, r27d_bars.gif).
import html
E = html.escape


def fig(img, f, cap):
    return '<figure>%s<figcaption>%s</figcaption></figure>' % (img(f, cap), E(cap))


def links(L):
    return '<ul>' + ''.join('<li><a href="%s">%s</a></li>' % (E(u), E(t)) for t, u in L) + '</ul>'


SOURCES = [
    ('Mitchell, Volumetric Light Scattering as a Post-Process, GPU Gems 3 ch. 13: march from each pixel toward the light; whatever stands in '
     'between (a building, a figure) cuts the shaft behind it', 'https://developer.nvidia.com/gpugems/gpugems3/part-ii-light-and-shadows/chapter-13-volumetric-light-scattering-post-process'),
    ('Zirr and Kaplanyan, Real-time Rendering of Procedural Multiscale Materials (I3D 2016): a glossy surface made of many slightly tilted facets '
     'shows a light as scattered glints round its mirror point, not as a band', 'https://research.nvidia.com/sites/default/files/pubs/2016-02_Real-time-Rendering-of/ZirrKaplanyan_MultiscaleI3D2016.pdf'),
    ('Deliot and Belcour, Real-Time Rendering of Glinty Appearances using Distributed Binomial Laws on Anisotropic Grids (2023): glints counted per '
     'texel, stable as the view moves', 'https://arxiv.org/pdf/2306.05051'),
]

FOUND_C = ('Found first (in game, floor 10, a guard 50 px from a lamp, Torchlight): the prince threw his shadow on the back wall and the guard none. '
           'Every figure\'s shadow, the cut it makes in a sky beam (the figures\' mask the shafts read), the weak capped light a beam puts on a figure, '
           'the carve in the metal mask and the fill cut over the sky all come from one red silhouette per figure (glSilhouette). The guards\' was '
           'drawn with PAL_GSIL, a palette of two keys made for round 6\'s robbers; round 7 gave the robbers\' head cloth tied ends drawn in the '
           'palette\'s khat colour, which PAL_GSIL never had, so shadeHex threw (reading \'slice\' of undefined), the try returned no silhouette, and '
           'since round 7 no guard has cast a shadow, cut a beam or kept a beam\'s footprint and haze off him, in Torchlight and in Classic (whose '
           'beams are cut by the same silhouettes, drawn in 2D). The fallback blobs drew only a faint smear. The comment over the shadow code said '
           'guards share it: they did, but their silhouette was always empty.')
FIX_C = ['The silhouette is drawn in the figure\'s own palette (silPal: the prince\'s, a skeleton\'s, or guardPal for a guard: its tier\'s head cloth '
         'or cap, its weapon); PAL_GSIL is gone. Now a guard casts the prince\'s shadow from up to two lamps (cast away from each, longer the farther '
         'sideways it stands, soft, carved off the walls in front and never on the sky), cuts the beams behind him, gets only the weak cool capped light '
         'on the side facing the light, and the floor patch, pane and rim are no longer drawn on him: in Torchlight at every GLP.rs and in Classic. '
         'Look only: hit boxes, timing and the bot unchanged.']
FOUND_D = ('Reproduced on floor 10 (seed 1234: the same Blue Chambers wall, lamps on the faience dado, a breach with columns) at the phone\'s 844x390 '
           'CSS px and DPR 3. Turning parts off in turn: the shafts pass\'s terms (haze, pane, rim, footprint) left the bars; turning off the theme\'s '
           'own look effects (GLFX.lookfx) removed them. They were the Blue Chambers\' glaze and wallglaze (round 5) in the mist pass: a sine of x and '
           'y (smoothstep(.78, 1, sin(0.11 x - 0.9 t + 0.06 y ...))) that made bright slanted bars 57 px apart sliding along the dado, times the '
           'lamps\' light. Three things made them read as wrong: they slide sideways all the time (they "move"); the prince\'s lamp shadow takes the '
           'light away under them, so where his shadow crosses a bar it shows as a dark slanted bar that goes with him as he runs; and the pass never '
           'asked whether the pixel was wall, so the bars lay over the sky through a breach or a window and over the beams there. Not the figure '
           'shadow\'s geometry, not the beams\' occluders, not the mask atlas (same at GLP.rs 1, .75 and .5).')
FIX_D = ['A glazed tile mirrors the flame near its mirror point, broken up by each tile\'s tilt; it never runs in bands across the wall. The glaze is now '
         'a soft sheen of smooth noise patches in the lamps\' light (strongest by the lamp, nothing in the dark), that swells and fades in place with '
         'the flame\'s sway; the faience walls above get the same, fainter. The single tiles that flash stay in 2D at full resolution (lampGlints), '
         'sharp at the phone\'s scale. Both are multiplied by the scene\'s alpha (round 25c: how much of the pixel is not the backdrop), so nothing of '
         'the wall is drawn over the sky through an opening. Classic had only the 2D glints: unchanged. Look only.']
RESEARCH = ('Shadows of figures in light: a lamp on the back wall throws a figure\'s shadow on the wall away from it, softer and wider the farther it '
            'falls (an area light\'s penumbra), and nothing falls where there is no wall (an opening onto the sky); a figure in a beam both stands in '
            'its light on the side toward it and cuts the shaft behind it, which screen-space light scattering does by marching from each pixel '
            'toward the light through a mask of the occluders (Mitchell, GPU Gems 3). The game did all this for the prince; the guards now go '
            'through the same path. Glossy faience: real glaze over hand-made tiles shows a light as scattered glints around its mirror point that '
            'flicker as the flame moves (the glinty-material work of Zirr and Kaplanyan, and Deliot and Belcour), so a moving diagonal band is the '
            'wrong cue; at the mist pass\'s quarter resolution only a soft lobe can be drawn without blocks, and the sharp glints are left to the 2D '
            'layer.')
TESTS = ('From a copy of dev/: rendersmoke floors 9 to 11, both modes: no errors (0.59 ms/frame at most); run2 floors 9 to 11, one seed: 3 of 3 passed, '
         '0 runs with damage (0.05 ms/frame); run2 floors 9 and 10 fighting: 2 of 2 passed (0.07 ms/frame); glauto FAILURES 0; beamwall: no errors; '
         'openscan: windows 0 of 96, gates 0 of 89, lift mouths 0 of 422 in both modes; wgl_maskcmp (quick, 34 states): the 3 states with a guard on '
         'screen differ (the guard now in the beams\' occluder mask and casting his silhouette\'s shadow instead of blobs), the other 31 identical.')


def sections(D, REL, img):
    return ['<section class="card" id="r27c"><h2>Rounds 27c and 27d: the guards\' shadows, and the bars on the dado</h2>'
            '<p>Owner (27c): "Soldiers don\'t seem to cast shadows and the light beams are drawn over them"; "it happens on all levels, torchlight '
            'graphics". Owner (27d, a screenshot of floor 10): "What are those slanted bars in the red circles? They are moving when the prince is '
            'running and are drawn over windows and light beams."</p>'
            '<h3>27c: what was found</h3><p>' + E(FOUND_C) + '</p>'
            '<h3>27c: the fix</h3><ul>' + ''.join('<li>%s</li>' % E(t) for t in FIX_C) + '</ul>' +
            fig(img, 'r27c_guards.png', 'A guard beside a lamp and in a beam on floors 10 (the owner\'s look), 7, 14, 23 and 31, at the phone\'s resolution: '
                'Torchlight, Torchlight at GLP.rs .5, Classic, each before | after; under each a 3x crop') +
            '<h3>27d: what was found</h3><p>' + E(FOUND_D) + '</p>'
            '<h3>27d: the fix</h3><ul>' + ''.join('<li>%s</li>' % E(t) for t in FIX_D) + '</ul>' +
            fig(img, 'r27d_bars.png', 'The owner\'s scene reproduced (floor 10, seed 1234, 844x390 at DPR 3): before | after; crops at the lamps and the '
                'breach at 0, 0.5 and 1 s (the bars slid), with the look effects off (the cause); GLP.rs .5 and a 3x crop') +
            fig(img, 'r27d_bars.gif', 'In game, Torchlight: the prince running past the lamp toward the breach, before | after') +
            '<h3>Research</h3><p>' + E(RESEARCH) + '</p>' + links(SOURCES) +
            '<h3>Tests</h3><p>' + E(TESTS) + '</p>'
            '<p class="meta">Retired to keep the page at 505 pictures: round 8\'s concept clock C\'s last picture, r8_clock_C_10.png, and the sky clock\'s '
            'half and nearly-out pictures, r8_clock_A_5.png and r8_clock_A_1.png (its run is in the GIF there).</p></section>']
