# egyptround28b.py: round 28b's section of egypt_themes.html: no jaggies in the light beams (owner, a phone shot of the Blue Chambers,
# Torchlight, the prince standing in the dusk beam of the open arches, the shadow he casts down the haze circled: "jaggies in the light beams").
# Picture from egyptr28b.py (r28b_beams.png).
import html
E = html.escape


def fig(img, f, cap):
    return '<figure>%s<figcaption>%s</figcaption></figure>' % (img(f, cap), E(cap))


def links(L):
    return '<ul>' + ''.join('<li><a href="%s">%s</a></li>' % (E(u), E(t)) for t, u in L) + '</ul>'


SOURCES = [
    ('Mitchell, Volumetric Light Scattering as a Post-Process (GPU Gems 3, ch. 13): march from each pixel toward the light, occluders cut it',
     'https://developer.nvidia.com/gpugems/gpugems3/part-ii-light-and-shadows/chapter-13-volumetric-light-scattering-post-process'),
    ('Toth and Umenhoffer, Real-time Volumetric Lighting in Participating Media (Eurographics 2009 short papers): a march at low resolution, '
     'interleaved sampling, then a filter over the pattern', 'https://diglib.eg.org/handle/10.2312/egs.20091048'),
    ('Wronski, Volumetric Fog (SIGGRAPH 2014, Assassin\'s Creed IV): a low-resolution volume, filtered and read back smoothly',
     'https://bartwronski.com/publications/'),
    ('Kopf, Cohen, Lischinski and Uyttendaele, Joint Bilateral Upsampling (SIGGRAPH 2007)', 'https://johanneskopf.de/publications/jbu/'),
    ('Reeves, Salesin and Cook, Rendering Antialiased Shadows with Depth Maps (SIGGRAPH 1987): percentage-closer filtering',
     'https://dl.acm.org/doi/10.1145/37402.37435'),
    ('Fernando, Percentage-Closer Soft Shadows (NVIDIA 2005): a penumbra that widens with the distance from the occluder',
     'https://developer.download.nvidia.com/shaderlibrary/docs/shadow_PCSS.pdf'),
]

FOUND = ('Reproduced on floor 11 (the Blue Chambers, seed 1101) at 844x390 CSS px and DPR 3 (the game draws at DPR 2, 1688x780): the prince '
         'standing in the dusk beam of a run of open arches. The shadow he casts down the beam\'s haze had stair-steps along its edge at every GLP.rs '
         '(the shafts\' pass is a quarter of the canvas, 422x195, whatever the scene\'s scale) and larger ones at Battery saver (DPR 1). Read back, the '
         'shafts\' own target showed the cause: the edge was a hard 45-degree line, narrower than one of its texels, which the composite\'s bilinear '
         'upsample draws as a staircase (a step every 4 canvas px). Two things made it hard. The figures\' mask (glcOcc) was an eighth of the canvas '
         '(8 px texels), and each of the march\'s 12 steps multiplied its reading into the light: a dozen readings of the bilinear ramp at 0.1 to 0.3 '
         'hardened it into an edge that traced the mask\'s texels. And the haze over a figure was cut wherever the mask read over 0.15, a dark fringe '
         'up to a texel past his outline on the lit side, stepped the same way. Tried and ruled out alone: 48 march steps instead of 12 (the steps '
         'stayed, sharper); the mask at a quarter alone (smaller steps, still there). Walls, slabs and blades already had soft, widening edges; Classic '
         'draws no figure shadow in its beams (unchanged).')
FIX = ['The figures\' mask is a quarter of the canvas, as the shafts\' pass (the atlas keeps its size: the quarter-size effect mask beside it set its '
       'width already).',
       'Each march step reads it at three points across the light (1-2-1, at least 1.25 texels apart and wider with distance: 1.6 + 0.05 px per px '
       'from him, a penumbra as the walls have) at two places a quarter step either side along it (a figure thinner than a step left scallops).',
       'The figure shades a pixel by the most any step saw of it (one occluder: its cover), not by a product of a dozen readings; walls and blades '
       'still multiply as before.',
       'The haze is cut over him from 0.35 to 0.75 of the mask (inside his outline), not from 0.15: no dark fringe on his lit side.',
       'No jitter (v61b\'s rule: the same steps for every pixel), no new pass. Look only: the beams\' shapes, the footprints, wall faces (round 15), '
       'low ceilings and blades (round 20a) are unchanged (beamwall: before and after identical to the pixel on all six cases).']
CHECKS = ('Perspective: the shadow still runs from him down the light (the same direction, du), from the opening toward the viewer and the floor; '
          'its penumbra widens with distance from him, as the walls\' shadows do. Texture: the haze\'s drift, the dust motes and the dither are '
          'untouched. Non-pixelated: 1:1 at DPR 3 at GLP.rs 1, .75 and .5, 3x crops of the edge and of his head, Battery saver at DPR 1, and the '
          'shafts\' target read back at 10x: no stair-steps, no blocks.')
TESTS = ('From a copy of dev/: beamwall six cases, before = after (Torchlight and Classic, mean difference 0); glauto FAILURES 0; rendersmoke '
         'floors 9 to 11 both modes no errors (0.59 ms/frame at most); run2 floors 3 to 5, one seed: 3 of 3, 0 runs with damage (0.03 ms/frame); '
         'openscan floors 1 to 48 both modes: windows, gates and lift mouths 0 with wall art over them; wgl_maskcmp quick: differences only where '
         'a figure stands near a beam (the mask\'s new resolution), none elsewhere.')
COST = ('GPU time on the owner\'s scene (this Mac, 1688x780, medians of 120 frames, three rounds): the shafts and bloom 0.64 > 0.72 ms, the scene '
        'and masks 3.04 > 3.04 ms, the frame 4.74-4.85 > 4.82-4.84 ms (about 0.08 ms, 2%). The quarter-size mask itself costs nothing measurable; '
        'with no figure near a beam the figure taps are skipped (u_of).')


def sections(D, REL, img):
    return ['<section class="card" id="r28b"><h2>Round 28b: no jaggies in the light beams</h2>'
            '<p>Owner (a phone shot of the Blue Chambers, Torchlight, the prince in the dusk beam of the open arches, the shadow in the haze circled): '
            '"jaggies in the light beams".</p>'
            '<h3>What was found</h3><p>' + E(FOUND) + '</p>'
            '<h3>The fix</h3><ul>' + ''.join('<li>%s</li>' % E(t) for t in FIX) + '</ul>' +
            fig(img, 'r28b_beams.png', 'The owner\'s scene at DPR 3, Torchlight before | after at GLP.rs 1, .75 and .5 (1:1); 3x crops of the shadow\'s '
                'edge, of the haze round his head and at Battery saver; the shafts\' target read back at 10x and the figures\' mask; Classic; the cost') +
            '<h3>Research</h3><p>' + E('Light shafts are marched at low resolution in every game that has them (Mitchell\'s post-process; Toth and '
                                       'Umenhoffer\'s interleaved march; Wronski\'s froxel fog), and each then hides the low resolution by filtering: '
                                       'interleaved sampling with a blur over the pattern, a volume read back with filtering, or a bilateral upsample. '
                                       'Here a per-pixel jitter made crawling squares (v61b), so the softening is in space: the occluder test is '
                                       'filtered (percentage-closer filtering, Reeves 1987) with a kernel that grows with the distance from the '
                                       'occluder (PCSS, Fernando 2005), so the edge is wider than a texel of the pass and the bilinear upsample has '
                                       'nothing to step.') + '</p>' + links(SOURCES) +
            '<h3>Cost</h3><p>' + E(COST) + '</p>'
            '<h3>Checks</h3><p>' + E(CHECKS) + '</p>'
            '<h3>Tests</h3><p>' + E(TESTS) + '</p>'
            '<p class="meta">Retired to keep the page at 505 pictures: round 8\'s sky clock at HUD size, r8_clock_A_hud.png (the sky clock was replaced '
            'by the water clock; its full picture stays).</p></section>']
