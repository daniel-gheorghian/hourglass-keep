# egyptround25c.py: round 25c's section of egypt_themes.html: no haze round the prince (owner, with a photo of floor 7 on the phone: "what is
# that haze around the prince?"). Pictures from egyptr25c.py.
import html
E = html.escape


def fig(img, f, cap):
    return '<figure>%s<figcaption>%s</figcaption></figure>' % (img(f, cap), E(cap))


def links(L):
    return '<ul>' + ''.join('<li><a href="%s">%s</a></li>' % (E(u), E(t)) for t, u in L) + '</ul>'


SOURCES = [
    ('Three-point lighting: the fill light lifts the subject\'s shadow side (the convention the game\'s "lit characters" follow)', 'https://en.wikipedia.org/wiki/Three-point_lighting'),
    ('Unity manual, skyboxes: the sky is drawn behind everything as a far environment, not lit by the scene\'s lights', 'https://docs.unity3d.com/Manual/skyboxes-introduction.html'),
    ('Porter and Duff 1984, compositing digital images: alpha as the share of a pixel a layer covers (the scene\'s alpha used here)', 'https://en.wikipedia.org/wiki/Alpha_compositing'),
]

TESTS = ('Proof: with the fill light removed from gatherLights the halo is gone and nothing else of it changes; with the new code\'s sky term '
         'forced off, wgl_cmp.py quick (34 states) is identical to round 25f to the bit (max 0), so the scene\'s alpha, the blend modes and the '
         'light map\'s alpha change nothing else; with it on, the only pixels that differ are sky beside a figure (worst state 0.28% of pixels). '
         'rendersmoke floors 7 to 9, both modes: no errors (0.59 ms/frame); beamwall.py: no errors; run2 floors 3 to 6: 4 of 4 passed, 0 runs '
         'with damage (0.04 ms/frame).')


def sections(D, REL, img):
    return ['<section class="card" id="r25c"><h2>Round 25c: no haze round the prince</h2>'
            '<p>Owner, with a photo of floor 7 on the phone (the prince in front of an open arch beside a raised block): "what is that haze around '
            'the prince?"</p>'
            '<h3>The cause</h3>'
            '<p>Every figure carries a fill light of its own (since the modern look\'s "lit characters": the prince 84 px wide, a pale lilac, a '
            'guard a weaker one, a snake a small green one). It goes into the light map with the lamps, and the light map multiplies the whole '
            'picture, so it also lit the sky seen through an opening. The sky is far away and shines by itself; lit by him, it got a pale halo '
            'that went with him past every window and arch and stopped at the sill, where the wall begins. That is the haze in the photo. '
            'Proved by toggling: without the fill light the halo is gone, and with it back but kept off the sky the picture is the same as '
            'before everywhere else. Torchlight and Classic both had it, at every resolution scale. The other suspects were checked and ruled out: '
            'the relief\'s rubbed ellipse round him (a few stone edges only), the beam\'s light on figures (inside his outline) and the window glow '
            '(it does not move with him).</p>'
            '<h3>The fix</h3><ul>'
            '<li><b>Torchlight.</b> The light map keeps each fill light\'s share in its alpha (0 for every other light). The scene\'s own alpha now '
            'says how much of each pixel is not the backdrop: the void and the backdrop are drawn without touching it (a G2D flag, na), the rooms '
            'and everything in them cover it, and erasers on the scene leave it alone (ke). The composite and the bloom\'s bright pass take the fill '
            'light off where the backdrop shows. A figure in front of the sky covers it, so he keeps his fill light to his outline, exactly, '
            'at any GLP.rs (1 and .5 shown). The figures\' soft shadows (glShadow) are kept off the sky by the same alpha: on floor 14 the prince\'s '
            'shadow had fallen on the dusk sky beside him.</li>'
            '<li><b>Classic.</b> The fill lights go into a small canvas of their own at the light map\'s size; wherever the room images are clear '
            '(an opening, less any block in front of it) they are taken out, except over a figure\'s silhouette. It is only done when a fill light '
            'reaches an opening in view; elsewhere the lights are drawn as before.</li>'
            '<li>Unchanged: the fill light on the figures and on the stone round them, the lamps\' light on the sky, the beams and their haze, '
            'every other pixel. The fallback without WebGL2 (?wgl=0) still lets the fill light reach the sky: its scene is a 2D canvas, '
            'which cannot keep the backdrop\'s alpha.</li></ul>'
            '<h3>Research</h3>' + links(SOURCES) +
            fig(img, 'r25c_haze.png', 'At the phone\'s resolution, round 25f (before) | 25c (after): Torchlight, Torchlight at GLP.rs .5, Classic; '
                'under each, 3x round the figure. Floor 7 (the owner\'s spot), a guard on floor 7, floors 23 (night) and 14 (dusk)') +
            '<h3>Tests</h3><p>' + E(TESTS) + '</p>'
            '<p class="meta">Retired to keep the page at 505 pictures: round 9\'s r9_hair_bob_torch.jpg (a hair option not built in).</p></section>']
