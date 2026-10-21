# egyptround25e.py: round 25e's section of egypt_themes.html: the view through the windows follows the keep (owner: "the backgrounds that
# are seen through the windows: they sometimes change wildly and are distracting especially when going downwards. Something is broken
# between the camera movement and the background layer"). Pictures and numbers from egyptr25e.py.
import html
E = html.escape


def fig(img, f, cap):
    return '<figure>%s<figcaption>%s</figcaption></figure>' % (img(f, cap), E(cap))


def links(L):
    return '<ul>' + ''.join('<li><a href="%s">%s</a></li>' % (E(u), E(t)) for t, u in L) + '</ul>'


SOURCES = [
    ('Itay Keren, "Scroll Back: The Theory and Practice of Cameras in Side-Scrollers" (GDC 2015; the written version): camera windows, '
     'platform snapping, smoothing, and how the layers behind follow the camera', 'https://www.gamedeveloper.com/design/scroll-back-the-theory-and-practice-of-cameras-in-side-scrollers'),
    ('The talk on the GDC Vault', 'https://gdcvault.com/play/1022243/Scroll-Back-The-Theory-and'),
    ('Celeste (Everest wiki, "Adding Stylegrounds"): every parallax background has its own Scroll X and Scroll Y, "the multiplier at which your '
     'background image scrolls relative to the screen. 0 locks it in place, and 1 causes it to scroll at the same rate as the gameplay layer"; '
     'Loop Y repeats it vertically', 'https://github.com/EverestAPI/Resources/wiki/Adding-Stylegrounds'),
    ('Godot\'s ParallaxBackground and ParallaxLayer: a motion scale per axis for each layer', 'https://docs.godotengine.org/en/stable/classes/class_parallaxlayer.html'),
    ('A vertical parallax gone missing, as a user reports it: "the background stayed centered instead of sinking when the player climbed"',
     'https://forum.gdevelop.io/t/background-parallax-vertical/52812'),
    ('Hollow Knight is reported to place its background art at depth before a perspective camera, so its parallax is the same on both axes '
     '(a Unity forum discussion, not Team Cherry\'s own account)', 'https://discussions.unity.com/t/new-to-unity-help-creating-a-parallax-background/804098'),
    ('Parallax scrolling: layers moved at their own speeds to give depth (arcade and console history)', 'https://en.wikipedia.org/wiki/Parallax_scrolling'),
    ('SDLPoP (Prince of Persia 1989 reimplemented): the rooms are flip-screen, so whatever a window shows never moves while it is on the screen',
     'https://github.com/NagyD/SDLPoP'),
]

TESTS = ("egyptr25e.py: no descent or ascent moves the view through an opening by more than 1 px a frame (0.65 at most; 3.28 before). rendersmoke floors 7 to 9, both modes: no errors (0.69 ms/frame). beamwall: no errors. openscan floors 1 to 48, both modes: 0 of 96 windows, 89 gates and 422 lift mouths with wall art over the opening. wgl_cmp quick against round 25d: 34 states, differences only inside the openings (the view now stands where the opening's storey puts it; worst state 6.1% of pixels over 24, f05_lift, an opening a storey below the camera's rest), none on walls, figures or lights. run2 floors 3 to 6, one seed: 4 of 4 passed, 0 runs with damage (0.04 ms/frame). All twelve looks seen at the top and bottom of their floors in both modes, at night, dusk and dawn, with ?wgl=0 and with GLP.rs 0.5.")
NUMBERS = ("Measured (egyptr25e.py: the bot plays floors 7, 10, 14, 23, 33 and 41; 18 descents, 18 ascents and 18 level runs cut from its camera path are replayed in both builds and both modes with no figures and a frozen clock). The view through an opening moved, computed, by 0.61 px a frame at the median and 3.28 at most during descents before (the camera's own speed; 2.43 in ascents), 0.10 and 0.65 after (0.48 in ascents); level runs are unchanged. Read back from the screen, pixel by pixel in each opening's own coordinates, on the frames that move straight down (lifts, climbs, falls): Classic p95 2.51, max 6.55 before; 0.78 and 1.16 after; Torchlight max 13.1 before, 5.9 after (the rest is Torchlight's light map and arch dust resampled as the camera moves, the same in level runs). Frames that also pan count the horizontal parallax, which did not change.")


def sections(D, REL, img):
    return ['<section class="card" id="r25e"><h2>Round 25e: the view through the windows follows the keep</h2>'
            '<p>Owner: "the backgrounds that are seen through the windows: they sometimes change wildly and are distracting especially when going '
            'downwards. Something is broken between the camera movement and the background layer."</p>'
            '<h3>The cause</h3>'
            '<p>The view through the openings (windows, open arches, breaches: the sky, the stars and moon, and the theme\'s layers of land) was '
            'painted in screen space. Across, each layer moved with the camera at its depth factor f (0.015 for the stars to 0.32 for the nearest), '
            'but up and down it was pinned to the screen: the sky\'s gradient did not move at all, and the layers moved 0.18 of f, clamped at 22 px, '
            'so on most of a floor even the nearest stood still (0.054 px for a px of camera at most, nothing beyond 407 px from the floor\'s middle: '
            'the nearest layer stood clamped in 76 to 100% of the bot\'s frames on floors 7, 10, 14, 23, 33 and 41). The horizon sat at 70% of the screen\'s height whatever the camera did. So every opening, which moves with the keep, '
            'slid over a still picture at the camera\'s full speed: a storey down is a third of the screen, and in it a window passes from the dark '
            'land through the bright band of the horizon into the sky. Going down is when it shows most: the drops, slides and lifts move the '
            'camera up to 197 px a second (3.3 px a frame), twice a run\'s pan, and the picture has all its contrast across, not along. Nothing '
            'jumped in the formula: the camera itself is smooth (no step over 3.3 px a frame down or 7.3 across in the bot\'s runs of those six floors). The landing shake moved the keep '
            'and not the view, too.</p>'
            '<p>' + E(NUMBERS) + '</p>'
            '<h3>The fix</h3><ul>'
            '<li>Each opening looks out at the eye level of its own storey: its view stands where it stood when the camera rests on the floor '
            'under the opening (bgAnchor), and moves with the keep but for a small vertical parallax, BG_VK (0.2) of the camera\'s travel away from '
            'that rest for the farthest layer and (1 - f) of it for a layer of depth f, so the near land goes with the keep more than the sky, as '
            'at depth. When the camera rests on a storey, its openings show exactly the old picture (the land\'s crests at the sill, the sky above); '
            'the openings of the storeys above and below, which showed only deep sky or only the dark land, now show their storey\'s own view.</li>'
            '<li>A pure function of the camera and of the opening: a rewind, a respawn or a snap cannot jump it, and nothing switches as the camera '
            'crosses a row. Openings that touch (a window knocked into a breach) are one hole and share the anchor of the largest (found once a '
            'floor), so no seam runs through a hole and no anchor depends on what is in view; the seams between storeys lie in the stone.</li>'
            '<li>The sky\'s gradient and the dawn sun go with the farthest layer (both made once and moved by the transform: no gradient a frame); '
            'the strips carry on past their edges (the ground below, the Cistern\'s architrave and the hanging ropes above).</li>'
            '<li>The moon is a layer of its own, drawn only for the storey the camera is at, crossfading over 48 px as the camera moves between '
            'storeys: stacked openings do not each show a moon.</li>'
            '<li>The screen shake moves the view with the keep. Across, nothing changed. Both modes and every GLP.rs share the code (the view is '
            'painted at its own size before the scene); round 25c\'s scene alpha is untouched.</li></ul>'
            '<h3>Research</h3><p>Side-scrollers give every background layer its own scroll factor on each axis: Celeste\'s backgrounds have a Scroll X '
            'and a Scroll Y between 0 (locked to the screen) and 1 (with the gameplay layer), Godot a motion scale per axis, and Hollow Knight is '
            'reported to get the same parallax on both axes by placing its art at depth. A background left at 0 vertically is the classic symptom of '
            'a missing vertical factor ("stayed centered instead of sinking when the player climbed"). Keren\'s survey of side-scroller cameras '
            'is about keeping what the eye follows calm: a picture that slides through every opening at the camera\'s speed is the opposite. Prince of '
            'Persia (1989) never had the problem: its rooms are flip-screen, so a window\'s picture never moves while it is on the screen. Here the '
            'view through each opening is anchored to its storey (Celeste\'s Scroll Y near 1, with the parallax as a small remainder), which keeps '
            'every still frame as it was at rest.</p>' + links(SOURCES) +
            fig(img, 'r25e_backdrop.png', 'The view through the openings against the camera through descents (falls, slides, lifts, climbs down) on '
                'six floors: red before, blue after (thick: the sky, thin: the near land; grey: the camera); under each, the measured change of the '
                'view through the openings a frame. Below, two windows of floor 7 through the lift ride down, every 4th frame, before over after, '
                'Torchlight and Classic') +
            fig(img, 'r25e_descent.gif', 'Floor 7, the bot riding the lift down past the hall\'s windows: before (25d) | after (25e), Torchlight over Classic') +
            '<h3>Tests</h3><p>' + E(TESTS) + '</p>'
            '<p class="meta">Retired to keep the page at 505 pictures: round 9\'s last two hair crops, r9_hair_crop_torch.jpg and r9_hair_curls_torch.jpg '
            '(the hair options of round 9, on a body rebuilt since round 23).</p></section>']
